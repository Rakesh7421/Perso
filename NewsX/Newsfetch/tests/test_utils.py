"""
Tests for the utils module
"""

import pytest
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils import (
    validate_date,
    validate_country_code,
    validate_language_code,
    parse_sources_list,
    truncate_text,
    format_number,
    clean_url,
    validate_and_format_date_range
)


class TestValidateFunctions:
    """Test validation functions"""
    
    def test_validate_date_valid(self):
        """Test valid date validation"""
        result = validate_date('2025-01-15')
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 15
    
    def test_validate_date_invalid_format(self):
        """Test invalid date format"""
        with pytest.raises(ValueError) as exc_info:
            validate_date('15-01-2025')
        
        assert "Date must be in YYYY-MM-DD format" in str(exc_info.value)
    
    def test_validate_date_invalid_date(self):
        """Test invalid date values"""
        with pytest.raises(ValueError):
            validate_date('2025-13-01')  # Invalid month
        
        with pytest.raises(ValueError):
            validate_date('2025-02-30')  # Invalid day
    
    def test_validate_country_code_valid(self):
        """Test valid country codes"""
        assert validate_country_code('us') is True
        assert validate_country_code('gb') is True
        assert validate_country_code('de') is True
        assert validate_country_code('US') is True  # Case insensitive
    
    def test_validate_country_code_invalid(self):
        """Test invalid country codes"""
        assert validate_country_code('xx') is False
        assert validate_country_code('usa') is False
        assert validate_country_code('') is False
    
    def test_validate_language_code_valid(self):
        """Test valid language codes"""
        assert validate_language_code('en') is True
        assert validate_language_code('es') is True
        assert validate_language_code('fr') is True
        assert validate_language_code('EN') is True  # Case insensitive
    
    def test_validate_language_code_invalid(self):
        """Test invalid language codes"""
        assert validate_language_code('xx') is False
        assert validate_language_code('eng') is False
        assert validate_language_code('') is False


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_parse_sources_list_valid(self):
        """Test parsing valid sources list"""
        result = parse_sources_list('bbc-news,cnn,reuters')
        assert result == 'bbc-news,cnn,reuters'
        
        result = parse_sources_list('bbc-news, cnn , reuters ')
        assert result == 'bbc-news,cnn,reuters'
    
    def test_parse_sources_list_empty(self):
        """Test parsing empty sources list"""
        assert parse_sources_list('') is None
        assert parse_sources_list(None) is None
        assert parse_sources_list('  ,  ,  ') is None
    
    def test_truncate_text_normal(self):
        """Test normal text truncation"""
        text = "This is a long text that needs to be truncated"
        result = truncate_text(text, 20)
        assert result == "This is a long te..."
        assert len(result) == 20
    
    def test_truncate_text_short(self):
        """Test text shorter than max length"""
        text = "Short text"
        result = truncate_text(text, 20)
        assert result == "Short text"
    
    def test_truncate_text_empty(self):
        """Test empty text truncation"""
        assert truncate_text('', 10) == ''
        assert truncate_text(None, 10) == ''
    
    def test_truncate_text_custom_suffix(self):
        """Test truncation with custom suffix"""
        text = "This is a long text"
        result = truncate_text(text, 15, suffix="[...]")
        assert result.endswith("[...]")
        assert len(result) == 15
    
    def test_format_number_valid(self):
        """Test number formatting"""
        assert format_number(1000) == "1,000"
        assert format_number(1234567) == "1,234,567"
        assert format_number(0) == "0"
    
    def test_format_number_invalid(self):
        """Test invalid number formatting"""
        assert format_number("invalid") == "invalid"
        assert format_number(None) == "None"
    
    def test_clean_url_valid(self):
        """Test valid URL cleaning"""
        assert clean_url('https://example.com') == 'https://example.com'
        assert clean_url('http://test.org/path') == 'http://test.org/path'
        assert clean_url('  https://example.com  ') == 'https://example.com'
    
    def test_clean_url_invalid(self):
        """Test invalid URL cleaning"""
        assert clean_url('not-a-url') is None
        assert clean_url('ftp://example.com') is None
        assert clean_url('') is None
        assert clean_url(None) is None
    
    def test_validate_and_format_date_range_valid(self):
        """Test valid date range validation"""
        from_date, to_date = validate_and_format_date_range('2025-01-01', '2025-01-31')
        assert from_date == '2025-01-01'
        assert to_date == '2025-01-31'
    
    def test_validate_and_format_date_range_invalid_order(self):
        """Test invalid date range (from > to)"""
        with pytest.raises(ValueError) as exc_info:
            validate_and_format_date_range('2025-01-31', '2025-01-01')
        
        assert "From date must be before to date" in str(exc_info.value)
    
    def test_validate_and_format_date_range_too_old(self):
        """Test date range too far in the past"""
        with pytest.raises(ValueError) as exc_info:
            validate_and_format_date_range('2020-01-01', '2020-01-31')
        
        assert "From date cannot be more than 30 days ago" in str(exc_info.value)
    
    def test_validate_and_format_date_range_partial(self):
        """Test partial date range validation"""
        # Only from_date
        from_date, to_date = validate_and_format_date_range('2025-01-01', None)
        assert from_date == '2025-01-01'
        assert to_date is None
        
        # Only to_date
        from_date, to_date = validate_and_format_date_range(None, '2025-01-31')
        assert from_date is None
        assert to_date == '2025-01-31'


class TestHelperFunctions:
    """Test helper functions"""
    
    def test_get_available_categories(self):
        """Test getting available categories"""
        from utils import get_available_categories
        categories = get_available_categories()
        
        assert isinstance(categories, list)
        assert 'technology' in categories
        assert 'business' in categories
        assert 'sports' in categories
        assert len(categories) == 7
    
    def test_get_available_sort_options(self):
        """Test getting available sort options"""
        from utils import get_available_sort_options
        options = get_available_sort_options()
        
        assert isinstance(options, list)
        assert 'relevancy' in options
        assert 'popularity' in options
        assert 'publishedAt' in options
        assert len(options) == 3


@pytest.mark.parametrize("country_code,expected", [
    ('us', True),
    ('gb', True),
    ('de', True),
    ('fr', True),
    ('xx', False),
    ('usa', False),
    ('', False),
])
def test_validate_country_code_parametrized(country_code, expected):
    """Parametrized test for country code validation"""
    assert validate_country_code(country_code) == expected


@pytest.mark.parametrize("text,max_length,expected", [
    ("Hello World", 20, "Hello World"),
    ("This is a very long text that should be truncated", 20, "This is a very lo..."),
    ("", 10, ""),
    ("Short", 10, "Short"),
])
def test_truncate_text_parametrized(text, max_length, expected):
    """Parametrized test for text truncation"""
    assert truncate_text(text, max_length) == expected


if __name__ == '__main__':
    pytest.main([__file__])