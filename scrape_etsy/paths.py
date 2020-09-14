SEARCH_RESULT = 'div[data-search-results] li.wt-list-unstyled'
SEARCH_PAGE_BUTTON='nav.search-pagination a.wt-btn'
RESULT_LINK = 'a.listing-link'

def __is_type(value, type):
    try:
        type(value)
        return True
    except ValueError as e:
        return False

SEARCH_FIELDS = {
    'title': {'selector': 'a.listing-link h3',
              'tests': [
                  lambda value: len(value) > 0,
              ]},
    'price_currency': {'selector': [
        'span.promotion-price span.currency-symbol',
        'span.n-listing-card__price > '
                      'span.currency-symbol',
    ], 'required': True,
        'tests': [
            lambda value: len(value) > 0,
        ]},
    'price_value': {'selector': [
        'span.promotion-price span.currency-value',
        'span.n-listing-card__price > '
                      'span.currency-value',
    ], 'required': True,
        'tests': [
            lambda value: len(value) > 0,
            lambda value: __is_type(value, float),
        ]},
    'sale_currency': {'selector': 'span.n-listing-card__price > span > '
                      'span.currency-symbol', 'required': False,
                      'tests': [
                      ]},
    'sale_value': {'selector': 'span.n-listing-card__price > span '
                   '> span.currency-value', 'required': False,
                   'tests': [
                   ]},
    'review_rating': {'selector': ('a.listing-link span.v2-listing-card__rating '
                                   '> span > span.screen-reader-only'),
                      'required': False, 'remove': r'\ out of 5 stars',
                      'tests': [
                          lambda value: __is_type(value, float) if len(value) > 0 else True,
                      ]},
    'review_count': {'selector': ('a.listing-link span.v2-listing-card__rating '
                                   '> span.screen-reader-only'),
                      'required': False, 'remove': r',|\ reviews',
                      'tests': [
                          lambda value: __is_type(value, int) if len(value) > 0 else True,
                      ]},
    'url': {'selector': 'a.listing-link', 'attribute': 'href',
            'tests': [
                lambda value: len(value) > 0,
            ]},
    'search_rank': {'tests': [
        lambda value: __is_type(value, int),
    ]},
}

DETAIL_FIELDS = {
    'shipping_currency': {'selector': ('div[data-estimated-shipping] '
                                   'span.currency-symbol'), 'required': False,
                          'tests': [
                          ]},
    'shipping_value': {'selector': ('div[data-estimated-shipping] '
                                'span.currency-value'), 'required': False,
                       'tests': [
                           lambda value: __is_type(value, float) if len(value) > 0 else True,
                       ]},
    'description': {'selector': 'p[data-product-details-description-text-content]',
                    'tests': [
                        lambda value: len(value) > 0,
                    ]},
    'processing_time': {'selector': 'div[data-processing-time] > p', 'required': False,
                        'tests': [
                        ]},
    'materials': {'selector': 'span[data-legacy-materials-text]', 'required': False,
                  'tests': [
                  ]},
    'estimated_delivery': {'selector': 'p[data-edd-absolute]', 'required': False,
                           'tests': [
                           ]},
    'shop_sales': {'selector': ('a[href=\#shop_overview] '
                                 'span.wt-screen-reader-only'), 'required':False,
                   'remove': r',|\ sales',
                   'tests': [
                       lambda value: __is_type(value, int) if len(value) > 0 else True,
                   ]},
    'dispatch_from': {'selector': ('div[data-estimated-shipping-form] '
                               'div.wt-text-caption'), 'required': False,
                      'tests': [
                      ]},
}
