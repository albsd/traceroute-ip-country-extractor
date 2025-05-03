import json
import argparse

parser = argparse.ArgumentParser(description="Extract all IPs (dst_addr, src_addr, hops) from traceroute file")
parser.add_argument("file_name", help="Traceroute file")
parser.add_argument("num_lines", type=int, nargs="?", default=None, help="Number of lines to process (default: all)")

args = parser.parse_args()


ips = set()
lines_processed = 0

with open(args.file_name, "r") as f:
    for line in f:
        if args.num_lines is not None and lines_processed >= args.num_lines:
            break

        entry = json.loads(line)

        dst_addr = entry.get('dst_addr')
        if dst_addr:
            ips.add(dst_addr)
        
        src_addr = entry.get('src_addr')
        if src_addr:
            ips.add(src_addr)

        for hop in entry.get('result', []):
            for hop_result in hop.get('result', []):
                ip = hop_result.get('from')
                if ip:
                    ips.add(ip) 

        lines_processed += 1
        
        if lines_processed % 5000 == 0:
            print(f"\rProcessed {lines_processed} lines...", end="", flush=True)

print(f"\rProcessed {lines_processed} lines...", end="", flush=True)

with open("ip_list.txt", "w") as output_file:
    for ip in sorted(ips):
        output_file.write(f"{ip}\n")
        
print(f"\nProcessing complete. Extracted {len(ips)} unique IPs.")