# TODO Raise errors if no log or callback, otherwise don't raise
# TODO Store search position
# TODO Callback for failures
# TODO Option to autoprocess failures
# TODO Create a test mode which requires no internet/caching
# TODO Tests
# TODO Check for memcached and cope if not installed
# TODO Add commmand line and library options for caching
# TODO Create module levels variables for settings

import re
import csv
import requests
from bs4 import BeautifulSoup
from pymemcache.client import base
from datetime import datetime

import constants as CT
import paths as PATH
from exceptions import (MissingValueException,
                        GetPageException,
                        ProductScrapeException)

__memcached__ = None
__fail_log__ = None

def __get_page(url, retry_count=0):
    """Recursive function to try getting
    page CT.RETRY_COUNT times before failing, and
    cache using memcached

    Parameters:
    url (str): URL to get
    retry_count (int): Count of retries to track
    during recursion

    Returns:
    str: Content of the page
    """
    global __memcached__

    if __memcached__:
        memcached = tuple(__memcached__.split(':'))
        client = base.Client((memcached[0], int(memcached[1])))
        cached_page = client.get(url)

    if __memcached__ and cached_page:
        return cached_page
    else:
        try:
            page = requests.get(url, timeout=CT.RETRY_COUNT)
            if page.status_code != 200:
                if retry_count < CT.RETRY_COUNT:
                    page = __get_page(url, retry_count=retry_count+1)
                else:
                    __log_error(url, requests.ConnectionError,
                                GetPageException())
        except (requests.ConnectionError, requests.Timeout) as error:
            if retry_count < CT.RETRY_COUNT:
                page = __get_page(url, retry_count=retry_count+1)
            else:
                __log_error(url, requests.ConnectionError, GetPageException())

        #TODO Handle returning of a byte array from requests.get

        if __memcached__ and client:
            client.set(url, page.content, expire=CT.CACHE_EXPIRE)

        return page.content

def __log_error(url, error, raise_error=None):
    """Log errors to a CSV file

    Parameters:
    url (str): URL for which the error occured
    error (Exception): The error whic occured

    Returns:
    None
    """

    global __fail_log__

    err_string = str(error) if len(str(error)) > 0 else type(error).__name__

    if __fail_log__:
        with open(__fail_log__, 'a') as f:
            # TODO Add a time/date stamp
            f.write(','.join([str(datetime.now()), url, err_string]))
            f.write('\n')

    if raise_error:
        raise raise_error
    else:
        raise error

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

    if get_details:
        # Combine basic fields and details fields
        return {**PATH.SEARCH_FIELDS, **PATH.DETAIL_FIELDS}
    else:
        return PATH.SEARCH_FIELDS

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

def __write_csv_header(get_details):
    """Write header row to CSV output file

    Parameters:
    get_details (bool): True if full details for products
    are requested

    Returns:
    None
    """

    global __output__

    fields = __get_field_names(get_details)
    with open(__output__, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=fields, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL,
                            doublequote=True)
        writer.writeheader()

def __get_value(tag, selector, attribute=None, required=True, remove=None):
    """Retrieve a value from a BeautifulSoup

    Parameters:
    tag (bs4.element.Tag): The tag to get the value from
    selector (str): BeautifulSoup selection string to find the value
    attribute (str): Name if the attribute that contains the value
    required (bool): If not required, do not raise an exception,
    just return an empty value
    remove (str): Regex for anything to strip out

    Returns:
        str: The value found
    """
    try:
        if attribute:
            value = tag.select_one(
                selector
            )[attribute]
        else:
            value = tag.select_one(selector).text.strip()
    except AttributeError as e:
        if not required:
            return ''
        else:
            __log_error(tag.url, MissingValueException(f'Failed to find'
                                                       f'"{selector}".'))

    if remove:
        return re.sub(remove, '', value)
    else:
        return value

def __write_csv_line(values):
    """Write row to CSV output file

    Parameters:
    values (list): List of valus to write to the CSV
    output file

    Returns:
    None
    """

    global __output__

    with open(__output__, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"',
                            quoting=csv.QUOTE_MINIMAL,
                            doublequote=True)
        writer.writerow(values)

def __get_product(tag, get_details):
    """Extract the basic details of a product from a search result
    and if requested, retrieve detail product page and extract
    further details.

    Parameters:
    tag (bs4.element.Tag): The tag to get the product from
    get_details (bool): True if full details for products
    are requested

    Returns:
    dict: A dictionary of product details
    """

    csv_entry = __get_default_fields(get_details)

    # TODO Deal with promotions properly
    for field_name, field in PATH.SEARCH_FIELDS.items():
        csv_entry[field_name] = __get_value(tag, **field)

    if get_details:
        # Get the product listing page
        try:
            detail_page = __get_page(csv_entry['url'])
        except GetPageException as e:
            raise ProductScrapeException()

        detail = BeautifulSoup(detail_page, 'html.parser')
        for field_name, field in PATH.DETAIL_FIELDS.items():
            csv_entry[field_name] = __get_value(detail, **field)

    return csv_entry

def scrape_etsy(url,
                output='output.csv',
                get_details=False,
                fail_log=None,
                limit=None,
                message_callback=None,
                progress_callback=None,
                memcached=None
               ):
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
    progress_callback (function): Callback function for dealing
    with progress, called for each product
    memcached (str): server:port of memcached server to use for
    caching

    Returns:
    None
    """

    # Store settings in global variables for use elsewhere
    if memcached:
        global __memcached__
        __memcached__ = memcached

    global __output__
    __output__ = output

    global __fail_log__
    __fail_log__ = fail_log


    product_count = 1
    success_count = 0
    fail_count = 0

    __write_csv_header(get_details)

    while not limit or (limit and product_count <= limit):
        if message_callback:
            message_callback(f'Processing {url}')

        try:
            page = __get_page(url)
        except GetPageException as e:
            fail_count += 1
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
                except (ProductScrapeException) as e:
                    fail_count += 1
                    next

                __write_csv_line(csv_entry.values())

                success_count += 1
                product_count += 1

        try:
            url = search_results.select(PATH.SEARCH_PAGE_BUTTON)[-1]['href']
        except KeyError:
            break

    if message_callback:
        message_callback(f'Scraped {success_count} products, failed to scrape '
                     f'{fail_count}.')
