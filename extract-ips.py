import json
import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser(description="Extract all IPs (dst_addr, src_addr, hops) from traceroute file")
parser.add_argument("file_name", help="Traceroute file")
parser.add_argument("--output_file", help="Output file")
parser.add_argument("num_lines", type=int, nargs="?", default=None, help="Number of lines to process (default: all)")

args = parser.parse_args()

file_path = Path(args.file_name)

if not args.output_file:
    output_dir = file_path.parent.parent / "ips"  
    output_dir.mkdir(parents=True, exist_ok=True) 
    
    base_name = file_path.stem 
    
    args.output_file = output_dir / f"{base_name}_ips.txt"

ips = set()
lines_processed = 0

with open(file_path, "r") as f:
    for line in f:
        if args.num_lines is not None and lines_processed >= args.num_lines:
            break

        entry = json.loads(line)

        for hop in entry.get('result', []):
            for hop_result in hop.get('result', []):
                ip = hop_result.get('from')
                if ip:
                    ips.add(ip) 

        lines_processed += 1
        
        if lines_processed % 5000 == 0:
            print(f"\rProcessed {lines_processed} lines...", end="", flush=True)

print(f"\rProcessed {lines_processed} lines...", end="", flush=True)

with open(args.output_file, "w") as output_file:
    for ip in sorted(ips):
        output_file.write(f"{ip}\n")
        
print(f"\nProcessing complete. Extracted {len(ips)} unique IPs to {args.output_file}.")
