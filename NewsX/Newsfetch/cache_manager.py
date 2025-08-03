"""
Cache manager for storing API responses
"""

import json
import hashlib
import os
import time
from datetime import datetime
from config import API_CONFIG


class CacheManager:
    """Simple file-based cache manager"""
    
    def __init__(self, cache_dir='.news_cache'):
        self.cache_dir = cache_dir
        self.cache_duration = API_CONFIG['cache_duration']
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def generate_key(self, endpoint, params):
        """Generate cache key from endpoint and parameters"""
        # Create a string representation of the request
        cache_data = {
            'endpoint': endpoint,
            'params': sorted(params.items())
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        
        # Generate MD5 hash
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key):
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, cache_key):
        """Get cached response if it exists and is not expired"""
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            # Check if cache is expired
            cache_age = time.time() - os.path.getmtime(cache_path)
            if cache_age > self.cache_duration:
                # Remove expired cache
                os.remove(cache_path)
                return None
            
            # Load and return cached data
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except (json.JSONDecodeError, IOError):
            # Remove corrupted cache file
            try:
                os.remove(cache_path)
            except OSError:
                pass
            return None
    
    def set(self, cache_key, data):
        """Store response in cache"""
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            # Fail silently if we can't write to cache
            pass
    
    def clear(self):
        """Clear all cached files"""
        if os.path.exists(self.cache_dir):
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    try:
                        os.remove(os.path.join(self.cache_dir, filename))
                    except OSError:
                        pass
    
    def clear_expired(self):
        """Clear only expired cache files"""
        if not os.path.exists(self.cache_dir):
            return
        
        current_time = time.time()
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    file_age = current_time - os.path.getmtime(filepath)
                    if file_age > self.cache_duration:
                        os.remove(filepath)
                except OSError:
                    pass
