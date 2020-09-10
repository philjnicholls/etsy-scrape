# TODO Make generic, pull fields and select strings from dictionary
# TODO Option to autoprocess failures
# TODO Create a test mode which requires no internet/caching
# TODO Tests
# TODO Check for memcached and cope if not installed

import csv
import requests
from bs4 import BeautifulSoup
from pymemcache.client import base

import constants as CT
import paths as PATH

def __get_page(url, retry_count=0):
    """Recursive function to try getting
    page TIMEOUT times before failing

    Parameters:
    url (str): URL to get
    retry_count (int): Count of retries to track
    during recursion

    Returns:
    str: Content of the page
    """

    #TODO Set cache time limit
    client = base.Client(('localhost', 11211))
    cached_page = client.get(url)
    if cached_page:
        return cached_page
    else:
        try:
            page = requests.get(url, timeout=CT.TIMEOUT)
        except requests.ConnectionError as error:
            if retry_count < CT.RETRY_COUNT:
                page = __get_page(url, retry_count=retry_count+1)
            else:
                raise requests.ConnectionError
        except requests.Timeout as error:
            if retry_count < 5:
                page = __get_page(url, retry_count=retry_count+1)
            else:
                raise requests.ConnectionError

        client.set(url, page.content, expiry=CT.CACHE_EXPIRY)

        return page.content

def __log_error(url, error, fail_log):
    """Log errors to a CSV file

    Parameters:
    url (str): URL for which the error occured
    error (Exception): The error whic occured

    Returns:
    None
    """

    err_string = str(error) if len(str(error)) > 0 else type(error).__name__

    if fail_log:
        with open(fail_log, 'a') as f:
            f.write(','.join([url, err_string]))
            f.write('\n')

def __get_field_names(get_details):
    """Get an list of field name for the output
    CSV. Extra field names are added if details
    are being retreieved.

    Parameters:
    get_details (bool): True if full details for products
    are requested

    Returns:
    list: Field names for output CSV
    """

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

def __get_default_fields(get_details):
    """Get a default dictionary for a row in the
    output CSV

    Parameters:
    get_details (bool): True if full details for products
    are requested

    Returns:
    dict: A dictionary with default values for all fields
    """

    fields = __get_field_names(get_details)
    return dict((field, None) for field in fields)

def __write_csv_header(output, get_details):
    """Write header row to CSV output file

    Parameters:
    output (str): Path to the output CSV file
    get_details (bool): True if full details for products
    are requested

    Returns:
    None
    """

    fields = __get_field_names(get_details)
    with open(output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fields, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL,
                            doublequote=True)
        writer.writeheader()

def __write_csv_line(output, values):
    """Write row to CSV output file

    Parameters:
    output (str): Path to the output CSV file
    values (list): List of valus to write to the CSV
    output file

    Returns:
    None
    """

    with open(output, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL,
                            doublequote=True)
        writer.writerow(values)

def __get_product(result, get_details):
    """Extract the basic details of a product from a search result
    and if requested, retrieve detail product page and extract
    further details.

    Parameters:
    output (str): Path to the output CSV file
    get_details (bool): True if full details for products
    are requested

    Returns:
    dict: A dictionary of product details
    """

    csv_entry = __get_default_fields(get_details)
    csv_entry['url'] = result.select_one(PATH.RESULT_LINK)['href']

    # TODO Deal with promotions properly
    csv_entry['currency'] = result.select_one(PATH.PRICE_CURRENCY).text
    csv_entry['cost'] = result.select_one(PATH.PRICE_VALUE).text

    if get_details:
        # Get the product listing page
        detail_page = __get_page(csv_entry['url'])

        detail = BeautifulSoup(detail_page, 'html.parser')
        csv_entry['title'] = detail.select_one(PATH.TITLE).text.strip()

        if detail.select_one(PATH.SHIPPING_CURRENCY):
            # If there is a shipping cost
            csv_entry['shipping_currency'] = detail.select_one(
                PATH.SHIPPING_CURRENCY).text
            csv_entry['shipping_cost'] = detail.select_one(
                PATH.SHIPPING_VALUE).text
    return csv_entry


def scrape_etsy(url,
                limit=None,
                get_details=False,
                output='output.csv',
                fail_log='fail.log',
                message_callback=None,
                progress_callback=None):
    """Navigate through the results of an Etsy search, extract
    product details to a CSV file and log failures

    Parameters:
    url (str): First page of Etsy search results to extract
    limit (int): Limit scraping to n products
    get_details (bool): True if full details for products
    are requested
    output (str): Path to the output CSV file
    fail_log (str): Path to the failure log
    message_callback (function): Callback function for dealing
    with messages

    Returns:
    None
    """

    product_count = 1
    success_count = 0
    fail_count = 0

    __write_csv_header(output, get_details)

    while not limit or (limit and product_count <= limit):
        if message_callback:
            message_callback(f'Processing {url}')

        try:
            page = __get_page(url)
        except requests.exceptions.RequestException as e:
            fail_count += 1
            __log_error(url, e, fail_log)
            break

        search_results = BeautifulSoup(page, 'html.parser')
        results = search_results.select(PATH.SEARCH_RESULT)

        for result in results:
            if result.select_one(PATH.RESULT_LINK) and (not limit or
                                                        product_count <=
                                                        limit):
                if progress_callback:
                    progress_callback(result.select_one(PATH.RESULT_LINK))

                try:
                    csv_entry = __get_product(result, get_details)
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.MissingSchema) as e:
                    fail_count += 1
                    __log_error(result.select_one(PATH.RESULT_LINK), e, fail_log)
                    next

                __write_csv_line(output, csv_entry.values())

                success_count += 1
                product_count += 1

        try:
            url = search_results.select(PATH.SEARCH_PAGE_BUTTON)[-1]['href']
        except KeyError:
            break

    if message_callback:
        message_callback(f'Scraped {success_count} products, failed to scrape '
                     f'{fail_count}.')
