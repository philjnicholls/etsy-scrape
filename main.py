# TODO Pass a search string instead of s search URL
# TODO Check for existing file and prompt for overwriting
# TODO Option to autoprocess failures
# TODO Create a test mode which requires no internet

import sys
import requests
import argparse
from bs4 import BeautifulSoup

import element_paths as ep


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

    if fail_log:
        with open(fail_log, 'a') as f:
            f.write(','.join([url, str(error)]))
            f.write('\n')

def get_elements(soup, element=None, attribute=None,
                attribute_value=None):
    if element:
        return soup.select(element)
    elif not element and attribute and not attribute_value:
        return [item for item in soup.find_all() if
                          attribute in item.attrs]

def get_element(*args, **kwargs):
    elements = get_elements(*args, **kwargs)
    if len(elements) > 1:
        raise ValueError(f'Found more than one element for {kwargs}')
    if len(elements) < 1:
        raise ValueError(f'Failed to find an element for {kwargs}')
    else:
        return elements[0]

def scrape_etsy(url, limit, get_details=False, output='output.csv',
                fail_log='fail.log', message_callback=print):
    count = 1
    success_count = 0
    fail_count = 0

    while not limit or (limit and count <= limit):
        message_callback(f'Processing {url}')
        try:
            page = get_page(url)
        except requests.exceptions.RequestException as e:
            fail_count += 1
            log_error(url, e, fail_log)
            break

        search_results = BeautifulSoup(page.content, 'html.parser')
        search_listing = get_element(search_results,
                                       attribute='data-search-results')
        results = get_elements(search_listing, element='li.wt-list-unstyled')

        for result in results:
            csv_entry = {
                'url': '',
                'currency': '',
                'cost': '',
            }
            message_callback('.', end='', flush=True)

            try:
                csv_entry['url'] = get_element(result, element='a.listing-link')['href']
            except ValueError as e:
                fail_count += 1
                log_error(url, e, fail_log)
                next

            # TODO Deal with promotions properly
            try:
                csv_entry['currency'] = get_element(result,
                                                    element='span.currency-symbol').text
            except ValueError as e:
                fail_count += 1
                log_error(url, e, fail_log)
                next

            try:
                csv_entry['cost'] = get_element(result,
                                                    element='span.currency-value').text.replace(',',
                                                                                                '')
            except ValueError as e:
                fail_count += 1
                log_error(url, e, fail_log)
                next

            if get_details:
                csv_entry['shipping_currency'] = ''
                csv_entry['shipping_cost'] = ''
                try:
                    detail_page = get_page(csv_entry['url'])
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.MissingSchema) as e:
                    fail_count += 1
                    log_error(csv_entry['url'], e, fail_log)
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

        message_callback('')
        try:
            url = search_results.select('nav.search-pagination a.wt-btn')[-1]['href']
        except KeyError:
            break

        count += 1

    message_callback(f'Scraped {success_count} products, failed to scrap {fail_count}.')

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
    parser.add_argument('-l', '--limit', help='Limit scraping to first n pages.',
                        type=int)
    parser.add_argument('-d', '--get-details', help='Get full details for a'
                        ' listing.', action='store_true')
    args = parser.parse_args()

    return vars(args)


if __name__ == '__main__':
    args = parse_args()

    scrape_etsy(**args)
