import os
import subprocess
import argparse
import requests
import bz2
import shutil
import sys

def download_file(url, dest_path): 
    if os.path.exists(dest_path):
        print(f"File {dest_path} already exists. Skipping download.")
        return

    print(f"Starting download: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    chunk_size = 1024 * 1024

    if not url.endswith('.bz2'):
        print("Error: URL doesn't end with .bz2.")
        return

    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                if total_size:
                    done = int(50 * downloaded / total_size)
                    sys.stdout.write(f"\r    [{'=' * done}{' ' * (50 - done)}] {100 * downloaded // total_size}%")
                    sys.stdout.flush()
    print(f"\nDownload completed: {dest_path}")

def extract_bz2(bz2_path, extract_path):
    print(f"Extracting {bz2_path} to {extract_path}")
    with bz2.BZ2File(bz2_path, 'rb') as f_in:
        with open(extract_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out, length=1024*1024)
    print("Extraction complete")

def run_script(script_name, args):
    print(f"Running script: {script_name} {' '.join(args)}")
    subprocess.run(["python", script_name] + args, check=True)
    print(f"Finished script: {script_name}")

def process_archive(archive_url, geoip_db_path, country="The Netherlands"):
    archive_name = os.path.basename(archive_url)
    archive_path = os.path.join(os.getcwd(), archive_name)
    extract_path = archive_path[:-4]  

    try:
        download_file(archive_url, archive_path)
        extract_bz2(archive_path, extract_path)

        base_name = os.path.basename(extract_path)
        ip_file = f"{base_name}_ips.txt"
        countries_file = f"{base_name}_ips_countries.txt"
        filtered_file = f"{base_name}_ips_{country.replace(' ', '_')}.txt"

        run_script("extract-ips.py", [extract_path])
        run_script("extract-countries.py", [ip_file, "--output_file", countries_file, geoip_db_path])
        run_script("filter_by_country.py", [countries_file, country, "--output_file", filtered_file])

    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)
            print(f"Deleted archive: {archive_path}")
        if os.path.exists(extract_path):
            os.remove(extract_path)
            print(f"Deleted extracted file: {extract_path}")

    print(f"Done processing: {archive_name}")
    print("-" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .bz2 traceroutes from online resources, extract their IPs and filter them by country.")
    parser.add_argument("url_file", help="Text file with list of archive URLs (one per line)")
    parser.add_argument("geoip_db", help="Path to MaxMind GeoIP2 database file")
    args = parser.parse_args()

    with open(args.url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            process_archive(url, args.geoip_db)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            print("-" * 60)
