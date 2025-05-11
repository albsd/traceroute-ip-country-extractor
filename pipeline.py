import subprocess
import argparse
import requests
import bz2
import shutil
import sys
import datetime
from pathlib import Path

PROJ_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJ_DIR / "data"


def check_and_create_dir(path):
    path.mkdir(parents=True, exist_ok=True)

def prepare_dirs(run_dir):
    check_and_create_dir(DATA_DIR)
    check_and_create_dir(run_dir)
    check_and_create_dir(run_dir / "country_ips")
    check_and_create_dir(run_dir / "archives")
    check_and_create_dir(run_dir / "extracted")
    check_and_create_dir(run_dir / "ips")
    check_and_create_dir(run_dir / "ips_plus_countries")

def download_file(url, dest_path): 
    if dest_path.exists():
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

    with dest_path.open('wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
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


def process(archive_url, run_dir, geoip_db_path, country="The Netherlands"):
    archive_name = Path(archive_url).name
    archive_path = run_dir / "archives" / archive_name
    extract_path = run_dir / "extracted" / archive_name[:-4]  

    try:
        download_file(archive_url, archive_path)
        extract_bz2(archive_path, extract_path)

        base_name = extract_path.name
        ip_file = run_dir / "ips" / f"{base_name}_ips.txt"
        countries_file = run_dir / "ips_plus_countries" / f"{base_name}_ips_countries.txt"
        filtered_file = run_dir / "country_ips" / f"{base_name}_ips_{country.replace(' ', '_')}.txt"

        run_script("extract-ips.py", [str(extract_path), "--output_file", str(ip_file)])
        run_script("extract-countries.py", [str(ip_file), "--output_file", str(countries_file), geoip_db_path])
        run_script("filter_by_country.py", [str(countries_file), country, "--output_file", str(filtered_file)])

    finally:
        if archive_path.exists():
            archive_path.unlink()
            print(f"Deleted archive: {archive_path}")
        if extract_path.exists():
            extract_path.unlink()
            print(f"Deleted extracted file: {extract_path}")

    print(f"Done processing: {archive_name}")
    print("-" * 60)

def combine_ips(run_dir):
    ips = set()
    for file_path in (run_dir / "country_ips").iterdir():
        if file_path.is_file() and file_path.suffix == ".txt":
            print(f"Reading {file_path.name}")
            with file_path.open("r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        ips.add(line)
    
    output_file = run_dir / "results.txt"

    with output_file.open("w") as out:
        for ip in sorted(ips):
            out.write(ip + "\n")
    
    print(f"Wrote {len(ips)} unique IPs to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process .bz2 traceroutes from online resources, extract their IPs and filter them by country.")
    parser.add_argument("url_file", help="Text file with list of archive URLs (one per line)")
    parser.add_argument("geoip_db", help="Path to MaxMind GeoIP2 database file")
    args = parser.parse_args()

    run_id = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = DATA_DIR / run_id

    prepare_dirs(run_dir)

    urls_path = run_dir / "archive_links.txt"
    shutil.copy(args.url_file, urls_path)

    with open(args.url_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            process(url, run_dir, args.geoip_db)
        except Exception as e:
            print(f"Error processing {url}: {e}")
            print("-" * 60)

    combine_ips(run_dir)  
