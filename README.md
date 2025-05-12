# IP Country Extraction from Traceroute

Set of scripts allowing the extraction of IPs (hops excluding the first one) from a [traceroute file](https://data-store.ripe.net/datasets/atlas-daily-dumps/).

## Requirements:
  - Python
  - [geoip2](https://pypi.org/project/geoip2/)
  - [GeoLite2-Country database](https://dev.maxmind.com/geoip/docs/databases/city-and-country/)

## Simplified version

For all the IPs from a single day only through a link, i.e. [the 11th of May](https://data-store.ripe.net/datasets/atlas-daily-dumps/2025-05-11/):

```
python pipeline.py --url https://data-store.ripe.net/datasets/atlas-daily-dumps/{day} <geoip_db>
```
- `<geoip-db>`: Path to local GeoIP2 database (`.mmdb` file)

For all the IPs from a set of custom links, each pointing to a .bz2 archive, add them to a file, with each of them on a separate line, then:

```
python pipeline.py --url-file <url-file-name> <geoip_db>
```
- `<geoip-db>`: Path to local GeoIP2 database (`.mmdb` file)
- `<url-file-name>`: Name of file with links to .bz2 archives

**The results can be found in data/{run}/results.txt.** You may also inspect the rest of data/{run} for the list of all unique IPs and their respective countries. There is a separate file for each archive included. 

{run} is determined by the time of running the script. 

## Individual scripts:

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
