"""
Configuration settings for the news fetcher
"""

# API Configuration
API_CONFIG = {
    'base_url': 'https://newsapi.org/v2',
    'rate_limit_interval': 1.0,  # Minimum seconds between requests
    'cache_duration': 300,  # Cache duration in seconds (5 minutes)
}

# Valid country codes for NewsAPI
VALID_COUNTRY_CODES = {
    'ae', 'ar', 'at', 'au', 'be', 'bg', 'br', 'ca', 'ch', 'cn', 'co', 'cu',
    'cz', 'de', 'eg', 'fr', 'gb', 'gr', 'hk', 'hu', 'id', 'ie', 'il', 'in',
    'it', 'jp', 'kr', 'lt', 'lv', 'ma', 'mx', 'my', 'ng', 'nl', 'no', 'nz',
    'ph', 'pl', 'pt', 'ro', 'rs', 'ru', 'sa', 'se', 'sg', 'si', 'sk', 'th',
    'tr', 'tw', 'ua', 'us', 've', 'za'
}

# Valid language codes for NewsAPI
VALID_LANGUAGE_CODES = {
    'ar', 'de', 'en', 'es', 'fr', 'he', 'it', 'nl', 'no', 'pt', 'ru', 'sv',
    'ud', 'zh'
}

# Output formatting
OUTPUT_CONFIG = {
    'max_title_length': 80,
    'max_description_length': 200,
    'date_format': '%Y-%m-%d %H:%M:%S',
    'console_width': 80,
}
