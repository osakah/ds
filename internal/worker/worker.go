package worker

import (
    "fmt"
    "time"

    "domain-scanner/internal/domain"
    "domain-scanner/internal/types"
)

// Worker processes domain availability checks
func Worker(id int, jobs <-chan string, results chan<- types.DomainResult, delay time.Duration, includeSignatures bool) {
    for domainName := range jobs {
        jobDone := make(chan struct{})
        var available bool
        var err error
        var signatures []string

        go func() {
            available, err = domain.CheckDomainAvailability(domainName)
            if includeSignatures && !available {
                signatures, _ = domain.CheckDomainSignatures(domainName)
            }
            close(jobDone)
        }()

        // Hard timeout per domain to avoid rare hangs
        timeout := 45 * time.Second
        select {
        case <-jobDone:
            // proceed
        case <-time.After(timeout):
            // Mark timeout and continue to next
            domain.ReportSpecialStatus(domainName, "CHECK_TIMEOUT")
            err = fmt.Errorf("domain check timeout")
            available = false
            signatures = nil
        }

        // Check for special status (placeholder for future implementation)
        specialStatus := ""

        results <- types.DomainResult{
            Domain:        domainName,
            Available:     available,
            Error:         err,
            Signatures:    signatures,
            SpecialStatus: specialStatus,
        }
        time.Sleep(delay)
    }
}
