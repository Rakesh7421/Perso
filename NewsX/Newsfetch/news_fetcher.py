"""
News fetcher module for interacting with NewsAPI
"""

import requests
import time
from datetime import datetime
from cache_manager import CacheManager
from config import API_CONFIG


class NewsAPIError(Exception):
    """Custom exception for NewsAPI errors"""
    pass


class NewsFetcher:
    """Class for fetching news from NewsAPI"""
    
    def __init__(self, api_key, use_cache=True, verbose=False):
        self.api_key = api_key
        self.base_url = API_CONFIG['base_url']
        self.cache = CacheManager() if use_cache else None
        self.verbose = verbose
        self.last_request_time = 0
        self.min_request_interval = API_CONFIG['rate_limit_interval']
    
    def _rate_limit(self):
        """Implement basic rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            if self.verbose:
                print(f"Rate limiting: waiting {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint, params):
        """Make HTTP request to NewsAPI"""
        url = f"{self.base_url}/{endpoint}"
        
        # Add API key to params
        params['apiKey'] = self.api_key
        
        # Check cache first
        cache_key = None
        if self.cache:
            cache_key = self.cache.generate_key(endpoint, params)
            cached_response = self.cache.get(cache_key)
            if cached_response:
                if self.verbose:
                    print("Using cached response...")
                return cached_response
        
        # Apply rate limiting
        self._rate_limit()
        
        if self.verbose:
            print(f"Making request to: {endpoint}")
            print(f"Parameters: {{k: v for k, v in params.items() if k != 'apiKey'}}")
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if data.get('status') != 'ok':
                error_code = data.get('code', 'unknown')
                error_message = data.get('message', 'Unknown error')
                raise NewsAPIError(f"API Error ({error_code}): {error_message}")
            
            # Cache successful response
            if self.cache and cache_key:
                self.cache.set(cache_key, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            raise NewsAPIError(f"Request failed: {e}")
        except requests.exceptions.JSONDecodeError:
            raise NewsAPIError("Invalid JSON response from API")
    
    def fetch_news(self, endpoint='top-headlines', **kwargs):
        """
        Fetch news articles from NewsAPI
        
        Args:
            endpoint: 'top-headlines' or 'everything'
            **kwargs: Various filter parameters
        
        Returns:
            dict: API response containing articles
        """
        # Build parameters
        params = {}
        
        # Common parameters
        if kwargs.get('query'):
            params['q'] = kwargs['query']
        
        if kwargs.get('language'):
            params['language'] = kwargs['language']
        
        if kwargs.get('page_size'):
            params['pageSize'] = min(kwargs['page_size'], 100)
        
        if kwargs.get('page'):
            params['page'] = kwargs['page']
        
        # Endpoint-specific parameters
        if endpoint == 'top-headlines':
            if kwargs.get('country'):
                params['country'] = kwargs['country']
            
            if kwargs.get('category'):
                params['category'] = kwargs['category']
            
            if kwargs.get('sources'):
                params['sources'] = kwargs['sources']
                # Remove country and category if sources is specified
                params.pop('country', None)
                params.pop('category', None)
        
        elif endpoint == 'everything':
            if kwargs.get('sources'):
                params['sources'] = kwargs['sources']
            
            if kwargs.get('from_date'):
                params['from'] = kwargs['from_date']
            
            if kwargs.get('to_date'):
                params['to'] = kwargs['to_date']
            
            if kwargs.get('sort_by'):
                params['sortBy'] = kwargs['sort_by']
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        # Make request
        response = self._make_request(endpoint, params)
        
        if self.verbose:
            total_results = response.get('totalResults', 0)
            articles_count = len(response.get('articles', []))
            print(f"Found {total_results} total results, displaying {articles_count} articles")
        
        return response
    
    def get_sources(self, category=None, language=None, country=None):
        """
        Get available news sources
        
        Args:
            category: Filter by category
            language: Filter by language
            country: Filter by country
        
        Returns:
            dict: API response containing sources
        """
        params = {}
        
        if category:
            params['category'] = category
        
        if language:
            params['language'] = language
        
        if country:
            params['country'] = country
        
        return self._make_request('sources', params)
