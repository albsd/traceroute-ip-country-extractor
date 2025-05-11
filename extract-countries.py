import geoip2.database
import argparse
import os

def get_country(ip, reader):
    try:
        response = reader.country(ip)
        return response.country.name
    except geoip2.errors.AddressNotFoundError:
        return None

parser = argparse.ArgumentParser(description="Find the country of each IP within a text file")
parser.add_argument("ip_file", help="File with list of IPs (both IPv4 and IPv6)")
parser.add_argument("--output_file", help="Output file of format {IP, Country}")
parser.add_argument("geoip_db", help="Path to MaxMind GeoIP2 database file")

args = parser.parse_args()

if not args.output_file:
    base_name = os.path.splitext(os.path.basename(args.ip_file))[0]
    args.output_file = f"{base_name}_countries.txt"

lines_processed = 0

with geoip2.database.Reader(args.geoip_db) as reader:
    with open(args.ip_file, "r") as ip_file, open(args.output_file, "w") as output_file:
        for line in ip_file:
            ip = line.strip()
            country = get_country(ip, reader)
            if country:
                output_file.write(f"{ip},{country}\n")
            else:
                output_file.write(f"{ip},Unknown\n")

            lines_processed += 1

            if lines_processed % 5000 == 0:
                print(f"\rProcessed {lines_processed} lines...", end="", flush=True)

print(f"\rProcessed {lines_processed} lines...", end="", flush=True)
print(f"\nFinished processing. Results saved to {args.output_file}.")
