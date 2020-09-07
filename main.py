# TODO Make generic, pull fields and select strings from dictionary
# TODO Option to autoprocess failures

# TODO Create a test mode which requires no internet

import csv
import os
import click
import requests
import argparse
from bs4 import BeautifulSoup

def get_page(url, retry_count=0):
    # Recursive function to try getting page 5 times before failing

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

def log_error(url, error, fail_log):
    # Log error to a file
    err_string = str(error) if len(str(error)) > 0 else type(error).__name__

    if fail_log:
        with open(fail_log, 'a') as f:
            f.write(','.join([url, err_string]))
            f.write('\n')

def get_field_names(get_details):
    fields = {
        'url': '',
        'currency': '',
        'cost': '',
    }
    if fields:
        fields['shipping_currency'] = ''
        fields['shipping_cost'] = ''
        fields['title'] = ''

    return fields

def get_default_fields(get_details):
    fields = get_field_names(get_details)
    return dict((field, None) for field in fields)

def write_csv_header(output, get_details):
    fields = get_field_names(get_details)
    with open(output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fields, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL,
                            doublequote=True)
        writer.writeheader()

def write_csv_line(output, values):
    with open(output, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL,
                            doublequote=True)
        writer.writerow(values)

def get_product(result, get_details):
    csv_entry = get_default_fields(get_details)
    csv_entry['url'] = result.select_one('a.listing-link')['href']

    # TODO Deal with promotions properly
    csv_entry['currency'] = result.select_one('span.currency-symbol').text
    csv_entry['cost'] = result.select_one('span.currency-value').text

    if get_details:
        # Get the product listing page
        detail_page = get_page(csv_entry['url'])

        detail = BeautifulSoup(detail_page.content, 'html.parser')
        csv_entry['title'] = detail.select_one('div[data-component='
                                       'listing-page-title-component] '
                                       '> h1').text.strip()

        if detail.select_one('div[data-estimated-shipping] > '
                             'div > p > '
                             'span.currency-symbol'):
            # If there is a shipping cost
            csv_entry['shipping_currency'] = detail.select_one('div[data-estimated-shipping] > '
                                                               'div > p > '
                                                               'span.currency-symbol').text
            csv_entry['shipping_cost'] = detail.select_one('div[data-estimated-shipping] > '
                                                               'div > p > '
                                                               'span.currency-value').text
    return csv_entry


def scrape_etsy(url, limit, get_details=False, output='output.csv',
                fail_log='fail.log', message_callback=lambda m: print(m,
                                                                      flush=True,
                                                                     end='')):
    product_count = 1
    success_count = 0
    fail_count = 0

    write_csv_header(output, get_details)

    while not limit or (limit and product_count <= limit):
        message_callback(f'Processing {url}\n')

        try:
            page = get_page(url)
        except requests.exceptions.RequestException as e:
            fail_count += 1
            log_error(url, e, fail_log)
            break

        search_results = BeautifulSoup(page.content, 'html.parser')
        results = search_results.select('div[data-search-results] > div > '
                                        'ul > li.wt-list-unstyled')

        for result in results:
            if result.select_one('a.listing-link') and (not limit or product_count <= limit):
                message_callback('.')

                try:
                    csv_entry = get_product(result, get_details)
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.MissingSchema) as e:
                    fail_count += 1
                    log_error(csv_entry['url'], e, fail_log)
                    next

                write_csv_line(output, csv_entry.values())

                success_count += 1
                product_count += 1

        message_callback('\n')
        try:
            url = search_results.select('nav.search-pagination a.wt-btn')[-1]['href']
        except KeyError:
            break

    message_callback(f'Scraped {success_count} products, failed to scrape '
                     f'{fail_count}.\n')

def parse_args():
    parser = argparse.ArgumentParser(description='Scrape product information'
                                     ' from etsy.com into a CSV file.')
    parser.add_argument('url', help='URL for the first page of Etsy search'
                        'results', type=str)
    parser.add_argument('output', help='Filepath to output csv',
                        type=str,
                        default='output.csv')
    parser.add_argument('-f', '--fail-log', help='Filepath to failure log',
                        type=str, default='fail.log')
    parser.add_argument('-l', '--limit', help='Limit scraping to first LIMIT'
                        'products.', type=int)
    parser.add_argument('-d', '--get-details', help='Get full details for a'
                        ' listing.', action='store_true')
    args = parser.parse_args()

    return vars(args)

def check_existing_files(output, fail_log):
    if os.path.exists(output):
        if not click.confirm(f'{output} already exists, do you want to '
                             f'overwrite?', default=True):
            return False
    if os.path.exists(fail_log):
        if not click.confirm(f'{fail_log} already exists, do you want to '
                             f'overwrite?', default=True):
            return False

    return True


if __name__ == '__main__':
    args = parse_args()

    if check_existing_files(args['output'], args['fail_log']):
        scrape_etsy(**args)
