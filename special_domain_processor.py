#!/usr/bin/env python3
"""
特殊域名分类脚本
"""

import subprocess
import os
from collections import defaultdict

INPUT_FILE = "domain-scan-results-combined/special_status_domains_all.txt"

def run_special_domain_classification():
    """
    运行特殊域名分类
    """
    # 确保输出目录存在
    special_output_dir = "domain-check/special"
    if not os.path.exists(special_output_dir):
        os.makedirs(special_output_dir)
    
    # 运行域名分类器处理特殊域名文件（按字符模式）
    cmd = [
        "python3", "domain_classifier.py",
        "--input", INPUT_FILE,
        "--output", special_output_dir
    ]
    
    print("正在处理特殊域名文件...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("处理特殊域名时出错:")
        print(result.stderr)
        return

    print("字符模式分类完成，开始按状态分类...")

    # 按特殊状态分类到独立文件
    by_status_dir = os.path.join(special_output_dir, "by-status")
    os.makedirs(by_status_dir, exist_ok=True)

    status_map = defaultdict(list)
    total = 0
    if not os.path.exists(INPUT_FILE):
        print(f"未找到输入文件: {INPUT_FILE}")
        return

    with open(INPUT_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 2:
                # 兼容旧格式，仅域名
                domain = parts[0]
                status = "UNKNOWN"
            else:
                domain = parts[0]
                status = parts[1].upper()
            status_map[status].append(domain)
            total += 1

    # 写入各状态文件
    for status, domains in status_map.items():
        out_path = os.path.join(by_status_dir, f"{status}.txt")
        with open(out_path, 'w') as out:
            for d in sorted(domains):
                out.write(d + "\n")

    # 写入汇总
    summary_path = os.path.join(by_status_dir, "summary.txt")
    with open(summary_path, 'w') as s:
        s.write(f"Total special domains: {total}\n")
        for status in sorted(status_map.keys()):
            s.write(f"{status}: {len(status_map[status])}\n")

    print("按状态分类完成!")
    print(f"输出目录: {by_status_dir}")

if __name__ == "__main__":
    run_special_domain_classification()
