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
    'shipping_currency': {'path': ('div[data-estimated-shipping] '
                                   'span.currency-symbol'), 'required': False},
    'shipping_value': {'path': ('div[data-estimated-shipping] '
                                'span.currency-value'), 'required': False},
    'description': {'path': 'p[data-product-details-description-text-content]'},
    'review_rating': {'path': ('div#reviews h3 span.wt-screen-reader-only'),
                      'required': False},
    'processing_time': {'path': 'div[data-processing-time] > p', 'required': False},
    'number_of_sales': {'path': ('a[href=\#shop_overview] '
                                 'span.wt-screen-reader-only'), 'required':False,
                        'remove': r',|\ sales'},
    'dispatch_from': {'path': ('div[data-estimated-shipping-form] '
                               'div.wt-text-caption'), 'required': False},
}
