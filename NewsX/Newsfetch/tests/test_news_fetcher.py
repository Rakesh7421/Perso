"""
Tests for the news_fetcher module
"""

import pytest
import responses
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from news_fetcher import NewsFetcher, NewsAPIError


class TestNewsFetcher:
    """Test cases for NewsFetcher class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.api_key = "test_api_key"
        self.fetcher = NewsFetcher(self.api_key, use_cache=False, verbose=False)
    
    def test_init(self):
        """Test NewsFetcher initialization"""
        assert self.fetcher.api_key == self.api_key
        assert self.fetcher.base_url == "https://newsapi.org/v2"
        assert self.fetcher.cache is None  # Cache disabled
        assert self.fetcher.verbose is False
    
    def test_init_with_cache(self):
        """Test NewsFetcher initialization with cache enabled"""
        fetcher = NewsFetcher(self.api_key, use_cache=True)
        assert fetcher.cache is not None
    
    @responses.activate
    def test_successful_api_request(self):
        """Test successful API request"""
        # Mock API response
        mock_response = {
            "status": "ok",
            "totalResults": 1,
            "articles": [
                {
                    "title": "Test Article",
                    "description": "Test description",
                    "url": "https://example.com/test",
                    "source": {"name": "Test Source"}
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://newsapi.org/v2/top-headlines",
            json=mock_response,
            status=200
        )
        
        result = self.fetcher.fetch_news(query="test")
        
        assert result["status"] == "ok"
        assert result["totalResults"] == 1
        assert len(result["articles"]) == 1
        assert result["articles"][0]["title"] == "Test Article"
    
    @responses.activate
    def test_api_error_response(self):
        """Test API error response handling"""
        mock_response = {
            "status": "error",
            "code": "apiKeyInvalid",
            "message": "Your API key is invalid"
        }
        
        responses.add(
            responses.GET,
            "https://newsapi.org/v2/top-headlines",
            json=mock_response,
            status=401
        )
        
        with pytest.raises(NewsAPIError) as exc_info:
            self.fetcher.fetch_news(query="test")
        
        assert "apiKeyInvalid" in str(exc_info.value)
        assert "Your API key is invalid" in str(exc_info.value)
    
    @responses.activate
    def test_network_error(self):
        """Test network error handling"""
        responses.add(
            responses.GET,
            "https://newsapi.org/v2/top-headlines",
            body=Exception("Network error")
        )
        
        with pytest.raises(NewsAPIError) as exc_info:
            self.fetcher.fetch_news(query="test")
        
        assert "Request failed" in str(exc_info.value)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        import time
        
        start_time = time.time()
        self.fetcher._rate_limit()
        first_call_time = time.time()
        
        # Second call should be rate limited
        self.fetcher._rate_limit()
        second_call_time = time.time()
        
        # Should have waited at least the minimum interval
        time_diff = second_call_time - first_call_time
        assert time_diff >= self.fetcher.min_request_interval - 0.1  # Allow small tolerance
    
    def test_fetch_news_parameters(self):
        """Test parameter handling in fetch_news"""
        with patch.object(self.fetcher, '_make_request') as mock_request:
            mock_request.return_value = {"status": "ok", "articles": []}
            
            self.fetcher.fetch_news(
                endpoint='top-headlines',
                query='test',
                category='technology',
                country='us',
                language='en',
                page_size=10,
                page=1
            )
            
            # Verify the request was made with correct parameters
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            
            assert call_args[0][0] == 'top-headlines'  # endpoint
            params = call_args[0][1]  # parameters
            
            assert params['q'] == 'test'
            assert params['category'] == 'technology'
            assert params['country'] == 'us'
            assert params['language'] == 'en'
            assert params['pageSize'] == 10
            assert params['page'] == 1
    
    def test_everything_endpoint_parameters(self):
        """Test parameters for everything endpoint"""
        with patch.object(self.fetcher, '_make_request') as mock_request:
            mock_request.return_value = {"status": "ok", "articles": []}
            
            self.fetcher.fetch_news(
                endpoint='everything',
                query='test',
                sources='bbc-news,cnn',
                from_date='2025-01-01',
                to_date='2025-01-31',
                sort_by='popularity'
            )
            
            call_args = mock_request.call_args
            params = call_args[0][1]
            
            assert params['q'] == 'test'
            assert params['sources'] == 'bbc-news,cnn'
            assert params['from'] == '2025-01-01'
            assert params['to'] == '2025-01-31'
            assert params['sortBy'] == 'popularity'
    
    def test_sources_override_country_category(self):
        """Test that sources parameter overrides country and category for headlines"""
        with patch.object(self.fetcher, '_make_request') as mock_request:
            mock_request.return_value = {"status": "ok", "articles": []}
            
            self.fetcher.fetch_news(
                endpoint='top-headlines',
                sources='bbc-news',
                country='us',
                category='technology'
            )
            
            call_args = mock_request.call_args
            params = call_args[0][1]
            
            assert params['sources'] == 'bbc-news'
            assert 'country' not in params
            assert 'category' not in params


@pytest.mark.integration
class TestNewsFetcherIntegration:
    """Integration tests that require actual API calls"""
    
    @pytest.mark.skipif(not os.getenv('NEWSAPI_KEY'), reason="No API key provided")
    def test_real_api_call(self):
        """Test with real API (requires NEWSAPI_KEY environment variable)"""
        api_key = os.getenv('NEWSAPI_KEY')
        fetcher = NewsFetcher(api_key, use_cache=False)
        
        try:
            result = fetcher.fetch_news(
                endpoint='top-headlines',
                country='us',
                page_size=1
            )
            
            assert result['status'] == 'ok'
            assert 'articles' in result
            assert isinstance(result['articles'], list)
            
        except NewsAPIError as e:
            pytest.skip(f"API call failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__])