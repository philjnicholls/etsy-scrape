# TODO Tests in writing will_not_write, I'd rather it did not
# TODO Split unit and functional tests

import pytest
import mock
import tempfile
import csv

import scrape_etsy
import standard_tests

from bs4 import BeautifulSoup

from standard_tests import test_pep8

def __is_type(value, type):
    try:
        type(value)
        return True
    except ValueError as e:
        return False

def __test_fields(csv_path, fields):
    with open(csv_path, 'r') as fp:
        csv_reader = csv.DictReader(fp)
        for row in csv_reader:
            for field_name, field in fields.items():
                for test in field['tests']:
                    if not test(row[field_name]):
                        assert False, (f'Failed on field {field_name} for test '
                                       f'"{test}"')

    assert True

SEARCH_FIELDS = {
    'title': {'tests': [
        lambda value: len(value) > 0,
    ]},
    'price_currency': {'tests': [
        lambda value: len(value) > 0,
    ]},
    'price_value': {'tests': [
        lambda value: len(value) > 0,
        lambda value: __is_type(value, float),
    ]},
    'review_rating': {'tests': [
        lambda value: __is_type(value, float) if len(value) > 0 else True,
    ]},
    'review_count': {'tests': [
        lambda value: __is_type(value, int) if len(value) > 0 else True,
    ]},
    'url': {'tests': [
        lambda value: len(value) > 0,
    ]},
}

DETAIL_FIELDS = {
    'shipping_currency': {'tests': [
    ]},
    'shipping_value': {'tests': [
        lambda value: __is_type(value, float) if len(value) > 0 else True,
    ]},
    'description': {'tests': [
        lambda value: len(value) > 0,
    ]},
    'processing_time': {'tests': [
    ]},
    'materials': {'tests': [
    ]},
    'estimated_delivery': {'tests': [
    ]},
    'shop_sales': {'tests': [
        lambda value: __is_type(value, int) if len(value) > 0 else True,
    ]},
    'dispatch_from': {'tests': [
    ]},
}

def test_basic_results(request):
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()
    request.config.cache.set('search_output', output)
    scrape_etsy.scrape_etsy('https://www.etsy.com/search?q=test', output,
               limit=10)
    line_count = len(open(output).readlines())

    assert line_count == 11

def test_basic_fields(request):
    output = request.config.cache.get('search_output', None)

    __test_fields(output, SEARCH_FIELDS)

def test_detail_results(request):
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()
    request.config.cache.set('page_output', output)
    scrape_etsy.scrape_etsy('https://www.etsy.com/search?q=test', output,
               limit=10, get_details=True)
    line_count = len(open(output).readlines())

    assert line_count == 11

def test_detail_fields(request):
    output = request.config.cache.get('page_output', None)

    __test_fields(output, DETAIL_FIELDS)

def test_cached_detail_results(request):
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()

    for i in range(2):
        scrape_etsy.scrape_etsy('https://www.etsy.com/search?q=bunny+earings', output,
                                limit=10, get_details=True, memcached='localhost:11211')
        line_count = len(open(output).readlines())

        assert line_count == 11

        __test_fields(output, DETAIL_FIELDS)

def test_bad_selector():
    page = scrape_etsy.__get_page('https://www.etsy.com/search?q=test')
    search_results = BeautifulSoup(page, 'html.parser')

    try:
        scrape_etsy.__get_value(search_results, 'not > going > to > find > anything',
                                required=True)
    except scrape_etsy.MissingValueException as e:
        assert True
    else:
        assert False

def test_bad_url():
    try:
        scrape_etsy.__get_page('https://www.etsy.com/not/a/good/url')
    except scrape_etsy.GetPageException as e:
        assert True
    else:
        assert False

def test_bad_domain():
    try:
        scrape_etsy.__get_page('https://www.notactuallyetsy.com/not/a/good/url')
    except scrape_etsy.GetPageException as e:
        assert True
    else:
        assert False

def test_message_callback():
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()

    message = mock.Mock()
    scrape_etsy.scrape_etsy('https://www.etsy.com/search?q=test',
                            output,
                            limit=10,
                            message_callback=message)

    message.assert_called_with('Scraped 10 products, failed to scrape 0.')

def test_progress_callback():
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()

    progress = mock.Mock()
    scrape_etsy.scrape_etsy('https://www.etsy.com/search?q=test',
                            output,
                            limit=10,
                            progress_callback=progress)

    progress.assert_called()

def test_fail_log_callback():
    fp = tempfile.NamedTemporaryFile()
    fail_log = fp.name
    fp.close()

    fail_log = mock.Mock()
    scrape_etsy.scrape_etsy('https://www.ddddetsy.com/search?q=test',
                            'will_not_write',
                            limit=10,
                            fail_log_callback=fail_log)

    fail_log.assert_called_with('https://www.ddddetsy.com/search?q=test',
                                mock.ANY)

def test_fail_log():
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()

    fail_log = fp.name
    fp.close()

    scrape_etsy.scrape_etsy('https://www.notactuallyetsy.com/search?q=test', output,
                            limit=10, fail_log=fail_log)
    line_count = len(open(fail_log).readlines())

    assert line_count > 0

def test_write_to_std_out():
    # TODO Need to capture and test stdout
    scrape_etsy.scrape_etsy('https://www.etsy.com/search?q=test', limit=10)

def test_bad_product_url():
    page = scrape_etsy.__get_page('https://www.etsy.com/search?q=test')
    search_results = BeautifulSoup(page, 'html.parser')
    results = search_results.select('div[data-search-results] > div > '
                                   'ul > li.wt-list-unstyled')
    result = results[0]
    result.select_one('a.listing-link')['href'] = 'http://dsfkhdsf.dsfsdfs'

    try:
        scrape_etsy.__get_product(result, get_details=True)
    except scrape_etsy.ProductScrapeException as e:
        assert True
    else:
        assert False

def test_get_all_results():
    fp = tempfile.NamedTemporaryFile()
    output = fp.name
    fp.close()
    scrape_etsy.scrape_etsy('https://www.etsy.com/il-en/search?q=falcor',
                            output)
    line_count = len(open(output).readlines())

    assert line_count > 1

