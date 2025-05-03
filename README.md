# IP Country Extraction from Traceroute

Set of scripts allowing the extraction of all IPs (dst_addr, src_addr, hops) from a traceroute file.

## Requirements:
  - Python
  - [geoip2](https://pypi.org/project/geoip2/)
  - [GeoLite2-Country database](https://dev.maxmind.com/geoip/docs/databases/city-and-country/)

## Usage:

To extract all the IPs from the traceroute:

```
python extract-ips.py <path-to-traceroute-file>
```

To find the country for each IP address:

```
python extract-countries.py <ip-file> <output-file> <path-to-geoip-db>
```
- `<ip-file>`: File containing the IP addresses (either from the previous extraction or any other source)
- `<output-file>`: File where results will be saved, formatted as `{IP, Country}`
- `<path-to-geoip-db>`: Path to local GeoIP2 database (`.mmdb` file)


To filter the results for only a specific country:

```
python filter_by_country.py <ip-with-country-file> <country-name> --output_file <output-file-name>
```

- `<ip-with-country-file>`: File with IP addresses and their corresponding countries
- `<country-name>`: Country to filter by (e.g., "The Netherlands")
- `<output-file-name>`: (Optional) File to save the filtered IPs
