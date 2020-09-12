# etsy-scrape
Scraping tool for Etsy

## Install
Requires Python 3.5+

Install requirements with ```pip install -r requirements.txt```

### Optional
Install [memcached](https://github.com/memcached/memcached/wiki/Install)

# Usage
You can get stuck in using the module etsy_scrape.py and integrate into your own projects or if you want to just start extracting some CSVs:

```
usage: main.py [-h] [-f FAIL_LOG] [-l LIMIT] [-d] [-m MEMCACHED] url output

Scrape product information from etsy.com into a CSV file.

positional arguments:
  url                   URL for the first page of Etsy search results
  output                Filepath to output csv

optional arguments:
  -h, --help            show this help message and exit
  -f FAIL_LOG, --fail-log FAIL_LOG
                        Filepath to failure log
  -l LIMIT, --limit LIMIT
                        Limit scraping to first LIMITproducts.
  -d, --get-details     Get full details for a listing.
  -m MEMCACHED, --memcached MEMCACHED
                        server:port of memcached server to use for caching
  ```
## Examples
To extract the details of the first 100 face masks found on Etsy:

```main.py 'https://www.etsy.com/search?q=face+mask' 'face_masks.csv' -d -l 100```
