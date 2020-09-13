SEARCH_RESULT = 'div[data-search-results] > div > ul > li.wt-list-unstyled'
SEARCH_PAGE_BUTTON='nav.search-pagination a.wt-btn'
RESULT_LINK = 'a.listing-link'

SEARCH_FIELDS = {
    'title': {'selector': 'a.listing-link h3'},
    'price_currency': {'selector': [
        'span.promotion-price span.currency-symbol',
        'span.n-listing-card__price > '
                      'span.currency-symbol',
    ], 'required': True},
    'price_value': {'selector': [
        'span.promotion-price span.currency-value',
        'span.n-listing-card__price > '
                      'span.currency-value',
    ], 'required': True},
    'sale_currency': {'selector': 'span.n-listing-card__price > span > '
                      'span.currency-symbol', 'required': False},
    'sale_value': {'selector': 'span.n-listing-card__price > span '
                   '> span.currency-value', 'required': False},
    'review_rating': {'selector': ('a.listing-link span.v2-listing-card__rating '
                                   '> span > span.screen-reader-only'),
                      'required': False, 'remove': r'\ out of 5 stars'},
    'review_count': {'selector': ('a.listing-link span.v2-listing-card__rating '
                                   '> span.screen-reader-only'),
                      'required': False, 'remove': r',|\ reviews'},
    'url': {'selector': 'a.listing-link', 'attribute': 'href'},
    'search_rank': {},
}

DETAIL_FIELDS = {
    'shipping_currency': {'selector': ('div[data-estimated-shipping] '
                                   'span.currency-symbol'), 'required': False},
    'shipping_value': {'selector': ('div[data-estimated-shipping] '
                                'span.currency-value'), 'required': False},
    'description': {'selector': 'p[data-product-details-description-text-content]'},
    'processing_time': {'selector': 'div[data-processing-time] > p', 'required': False},
    'materials': {'selector': 'span[data-legacy-materials-text]', 'required': False},
    'estimated_delivery': {'selector': 'p[data-edd-absolute]', 'required': False},
    'shop_sales': {'selector': ('a[href=\#shop_overview] '
                                 'span.wt-screen-reader-only'), 'required':False,
                        'remove': r',|\ sales'},
    'dispatch_from': {'selector': ('div[data-estimated-shipping-form] '
                               'div.wt-text-caption'), 'required': False},
}
