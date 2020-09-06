# TODO Option to autoprocess failures
# TODO Create a test mode which requires no internet

import sys
import requests
import argparse
from bs4 import BeautifulSoup

def get_page(url, retry_count=0):
    try:
        page = requests.get(url, timeout=5)
    except requests.ConnectionError as error:
        if retry_count < 5:
            page = get_page(url, retry_count=retry_count+1)
        else:
            raise requests.ConnectionError
    except requests.Timeout as error:
        if retry_count < 5:
            page = get_page(url, retry_count=retry_count+1)
        else:
            raise requests.ConnectionError

    return page

def log_error(url, error, fail_path):
    if fail_path:
        with open(fail_path, 'a') as f:
            f.write(','.join([url, error]))

def scrape_etsy(url, limit, get_details, output, fail_path):
    count = 1
    success_count = 0
    fail_count = 0

    while not limit or (limit and count <= limit):
        print(f'Processing {url}')
        try:
            page = get_page(url)
        except requests.exceptions.RequestException as e:
            fail_count += 1
            log_error(url, e, fail_path)
            break

        search_results = BeautifulSoup(page.content, 'html.parser')
        search_listings = [item for item in search_results.find_all() if
                          'data-search-results' in item.attrs]
        results = search_listings[0].find_all('li', 'wt-list-unstyled')

        for result in results:
            csv_entry = {
                'url': '',
                'currency': '',
                'cost': '',
            }
            print('.', end='', flush=True)
            links = result.find_all('a', 'listing-link')
            if len(links) > 0:
                # Found some links
                csv_entry['url'] = links[0]['href']

            currencies = result.find_all('span', 'currency-symbol')
            if len(currencies) > 0:
                # Found some links
                csv_entry['currency'] = currencies[0].text

            costs = result.find_all('span', 'currency-value')
            if len(costs) > 0:
                # Found some links
                csv_entry['cost'] = costs[0].text.replace(',','')

            if get_details:
                csv_entry['shipping_currency'] = ''
                csv_entry['shipping_cost'] = ''
                try:
                    detail_page = get_page(csv_entry['url'])
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.MissingSchema) as e:
                    fail_count += 1
                    log_error(csv_entry['url'], e, fail_path)
                    next

                detail = BeautifulSoup(detail_page.content, 'html.parser')
                shipping_items = [item for item in detail.find_all() if
                                  "data-estimated-shipping" in item.attrs]
                if len(shipping_items) > 0:
                    if len(shipping_items[0].select('span.currency-symbol')) > 0:
                        csv_entry['shipping_currency'] = shipping_items[0].select('span.currency-symbol')[0].text
                        csv_entry['shipping_cost']  = shipping_items[0].select('span.currency-value')[0].text

            with open(output, 'a') as f:
                f.write(','.join(csv_entry.values()))
                f.write('\n')

            success_count += 1

        print('')
        try:
            url = search_results.select('nav.search-pagination a.wt-btn')[-1]['href']
        except KeyError:
            break

        count += 1

    print(f'Scraped {success_count} products, failed to scrap {fail_count}.')

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape product information'
                                     ' from etsy.com into a CSV file.')
    parser.add_argument('url', help='URL for the first page of Etsy search'
                        'results', type=str)
    parser.add_argument('output', help='Filepath to output csv',
                        type=str,
                        default='output.csv')
    parser.add_argument('-f', '--fail-log', help='Filepath to failure log',
                        type=argparse.FileType('a'))
    parser.add_argument('-l', '--limit', help='Limit scraping to first n pages.',
                        type=int)
    parser.add_argument('-d', '--get-details', help='Get full details for a'
                        ' listing.', action='store_true')
    args = parser.parse_args()

    return vars(args)


if __name__ == '__main__':
    args = parse_args()

    scrape_etsy(url=args['url'], limit=args['limit'],
                get_details=args['get_details'],
                output=args['output'], fail_path=args['fail_log'])
