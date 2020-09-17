# TODO Split unit and functional tests
# TODO Re-think how URLs are created,  stored and used, maybe add a nocache to
# querystring

import pytest
import mock
import tempfile
import csv
import random
import os
import urllib.parse

from scrape_etsy.scrape_etsy import scrape
from scrape_etsy import scrape_etsy
from scrape_etsy import paths

from bs4 import BeautifulSoup

def _test_fields(csv_path, fields):
    with open(csv_path, 'r') as fp:
        csv_reader = csv.DictReader(fp)
        for row in csv_reader:
            for field_name, field in fields.items():
                for idx, test in enumerate(field['tests']):
                    if not test(row[field_name]):
                        assert False, (f'Failed on field {field_name} for test '
                                       f'#{idx}')

    assert True

@pytest.fixture
def search_url():
    return get_search_url()

def get_search_url():
    products = ('shirt', 'clock', 'doll')
    colors = ('blue', 'green', 'red')

    product = products[random.randrange(len(products))]
    color = colors[random.randrange(len(colors))]

    query_string = urllib.parse.quote(f'{color} {product}')
    return f'https://www.etsy.com/il-en/search?q={query_string}'

class TestBasicResults():
    def setup(self):
        fp = tempfile.NamedTemporaryFile()
        self.output = fp.name
        fp.close()
        scrape(get_search_url(), self.output,
               limit=10)

    def teardown(self):
        os.remove(self.output)

    def test_basic_results(self):
        line_count = len(open(self.output).readlines())

        assert line_count == 11

    def test_basic_fields(self):
        _test_fields(self.output, paths.SEARCH_FIELDS)

    def test_message_callback(self, search_url):
        message = mock.Mock()
        scrape(search_url,
               limit=10,
               message_callback=message)

        message.assert_called_with('Scraped 10 products, failed to scrape 0.')

    def test_progress_callback(self, search_url):
        progress = mock.Mock()
        scrape(search_url,
               limit=10,
               progress_callback=progress)

        progress.assert_called()


class TestDetailedResults():
    def setup(self):
        self.search_url = get_search_url()
        fp = tempfile.NamedTemporaryFile()
        self.output = fp.name
        fp.close()
        scrape(self.search_url, self.output,
               limit=10, get_details=True,
               memcached='localhost:11211')

    def teardown(self):
        os.remove(self.output)

    def test_detail_results(self):
        line_count = len(open(self.output).readlines())

        assert line_count == 11

    def test_detail_fields(self):
        _test_fields(self.output, paths.DETAIL_FIELDS)

    def test_cached_detail_results(self):
        scrape(self.search_url, self.output,
               limit=10, get_details=True,
               memcached='localhost:11211')
        line_count = len(open(self.output).readlines())

        assert line_count == 11

    def test_cached_detail_fields(self):
        scrape(self.search_url, self.output,
               limit=10, get_details=True,
               memcached='localhost:11211')
        _test_fields(self.output, paths.DETAIL_FIELDS)


def test_bad_selector(search_url):
    page = scrape_etsy.__get_page(search_url)
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


def test_fail_log_callback():
    fp = tempfile.NamedTemporaryFile()
    fail_log = fp.name
    fp.close()

    fail_log = mock.Mock()
    scrape('https://www.ddddetsy.com/search?q=test',
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

    scrape('https://www.notactuallyetsy.com/search?q=test', output,
           limit=10, fail_log=fail_log)
    line_count = len(open(fail_log).readlines())

    assert line_count > 0

def test_write_to_std_out(search_url):
    # TODO Need to capture and test stdout
    scrape(search_url, limit=10)

def test_bad_product_url(search_url):
    page = scrape_etsy.__get_page(search_url)
    search_results = BeautifulSoup(page, 'html.parser')
    results = search_results.select('div[data-search-results] '
                                    'li.wt-list-unstyled')
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
    scrape('https://www.etsy.com/il-en/search?q=bunny%20wizard%20hat',
           output)
    line_count = len(open(output).readlines())

    assert line_count > 1

