"""
Utility functions for the news fetcher
"""

import re
from datetime import datetime
from config import VALID_COUNTRY_CODES, VALID_LANGUAGE_CODES


def validate_date(date_string):
    """
    Validate date string in YYYY-MM-DD format
    
    Args:
        date_string: Date string to validate
    
    Returns:
        datetime: Parsed datetime object
    
    Raises:
        ValueError: If date format is invalid
    """
    try:
        return datetime.strptime(date_string, '%Y-%m-%d')
    except ValueError:
        raise ValueError(f"Date must be in YYYY-MM-DD format, got: {date_string}")


def validate_country_code(country_code):
    """
    Validate country code against NewsAPI supported countries
    
    Args:
        country_code: Two-letter country code
    
    Returns:
        bool: True if valid, False otherwise
    """
    return country_code.lower() in VALID_COUNTRY_CODES


def validate_language_code(language_code):
    """
    Validate language code against NewsAPI supported languages
    
    Args:
        language_code: Two-letter language code
    
    Returns:
        bool: True if valid, False otherwise
    """
    return language_code.lower() in VALID_LANGUAGE_CODES


def parse_sources_list(sources_string):
    """
    Parse comma-separated sources string
    
    Args:
        sources_string: Comma-separated sources
    
    Returns:
        str: Cleaned sources string
    """
    if not sources_string:
        return None
    
    # Split by comma and clean up
    sources = [source.strip() for source in sources_string.split(',')]
    sources = [source for source in sources if source]  # Remove empty strings
    
    return ','.join(sources) if sources else None


def truncate_text(text, max_length, suffix="..."):
    """
    Truncate text to specified length with suffix
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
    
    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text or ""
    
    return text[:max_length - len(suffix)] + suffix


def format_number(number):
    """
    Format number with thousand separators
    
    Args:
        number: Number to format
    
    Returns:
        str: Formatted number string
    """
    try:
        return f"{int(number):,}"
    except (ValueError, TypeError):
        return str(number)


def clean_url(url):
    """
    Clean and validate URL
    
    Args:
        url: URL to clean
    
    Returns:
        str: Cleaned URL or None if invalid
    """
    if not url:
        return None
    
    # Basic URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if url_pattern.match(url):
        return url.strip()
    
    return None


def get_available_categories():
    """
    Get list of available news categories
    
    Returns:
        list: Available categories
    """
    return ['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology']


def get_available_sort_options():
    """
    Get list of available sort options for 'everything' endpoint
    
    Returns:
        list: Available sort options
    """
    return ['relevancy', 'popularity', 'publishedAt']


def print_sources_help():
    """Print help for finding news sources"""
    help_text = """
Popular News Sources:
  International: bbc-news, cnn, reuters, associated-press
  US: abc-news, cbs-news, nbc-news, fox-news, usa-today
  Tech: techcrunch, the-verge, ars-technica, wired, engadget
  Business: bloomberg, financial-times, wall-street-journal
  
Use the --sources parameter with comma-separated source IDs:
  Example: --sources "bbc-news,cnn,reuters"
"""
    print(help_text)


def print_country_codes_help():
    """Print help for country codes"""
    help_text = """
Common Country Codes:
  us - United States    gb - United Kingdom   de - Germany
  fr - France          it - Italy            jp - Japan
  ca - Canada          au - Australia        in - India
  br - Brazil          mx - Mexico           ru - Russia
  
Use two-letter ISO country codes with --country parameter.
"""
    print(help_text)


def validate_and_format_date_range(from_date, to_date):
    """
    Validate and format date range
    
    Args:
        from_date: Start date string
        to_date: End date string
    
    Returns:
        tuple: (formatted_from_date, formatted_to_date)
    
    Raises:
        ValueError: If date range is invalid
    """
    from_dt = None
    to_dt = None
    
    if from_date:
        from_dt = validate_date(from_date)
    
    if to_date:
        to_dt = validate_date(to_date)
    
    # Validate date range
    if from_dt and to_dt and from_dt > to_dt:
        raise ValueError("From date must be before to date")
    
    # Check if dates are not too far in the past (NewsAPI limitation)
    if from_dt:
        days_ago = (datetime.now() - from_dt).days
        if days_ago > 30:
            raise ValueError("From date cannot be more than 30 days ago")
    
    return (from_date, to_date)
