SEARCH_RESULT = 'div[data-search-results] > div > ul > li.wt-list-unstyled'
SEARCH_PAGE_BUTTON='nav.search-pagination a.wt-btn'
RESULT_LINK = 'a.listing-link'

SEARCH_FIELDS = {
    'price_currency': {'path': 'span.currency-symbol'},
    'price_value': {'path': 'span.currency-value'},
    'url': {'path': 'a.listing-link', 'attribute': 'href'}
}

DETAIL_FIELDS = {
    'title': {'path': 'div[data-component=listing-page-title-component] > h1'},
    'shipping_currency': {'path': ('div[data-estimated-shipping] > div > p >'
                                   'span.currency-symbol'), 'required': False},
    'shipping_value': {'path': ('div[data-estimated-shipping] > div > p >'
                                'span.currency-value'), 'required': False},
}
