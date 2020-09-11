SEARCH_RESULT = 'div[data-search-results] > div > ul > li.wt-list-unstyled'
SEARCH_PAGE_BUTTON='nav.search-pagination a.wt-btn'
RESULT_LINK = 'a.listing-link'

SEARCH_FIELDS = {
    'price_currency': {'selector': 'span.currency-symbol'},
    'price_value': {'selector': 'span.currency-value'},
    'url': {'selector': 'a.listing-link', 'attribute': 'href'}
}

DETAIL_FIELDS = {
    'title': {'selector': 'div[data-component=listing-page-title-component] > h1'},
    'shipping_currency': {'selector': ('div[data-estimated-shipping] '
                                   'span.currency-symbol'), 'required': False},
    'shipping_value': {'selector': ('div[data-estimated-shipping] '
                                'span.currency-value'), 'required': False},
    'description': {'selector': 'p[data-product-details-description-text-content]'},
    'review_rating': {'selector': ('div#reviews h3 span.wt-screen-reader-only'),
                      'required': False, 'remove': r' out of 5 stars'},
    'processing_time': {'selector': 'div[data-processing-time] > p', 'required': False},
    'materials': {'selector': 'span[data-legacy-materials-text]', 'required': False},
    'estimated_delivery': {'selector': 'p[data-edd-absolute]', 'required': False},
    'shop_sales': {'selector': ('a[href=\#shop_overview] '
                                 'span.wt-screen-reader-only'), 'required':False,
                        'remove': r',|\ sales'},
    'dispatch_from': {'selector': ('div[data-estimated-shipping-form] '
                               'div.wt-text-caption'), 'required': False},
}
