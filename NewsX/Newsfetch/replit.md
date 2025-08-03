# Overview

This is a CLI News Fetcher application built in Python that retrieves news articles from NewsAPI. The application provides a command-line interface for fetching and filtering news based on various parameters like keywords, categories, countries, and languages. It features caching capabilities to reduce API calls and supports multiple output formats including console and JSON display.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Components

**CLI Interface**: Built using Python's argparse module to handle command-line arguments and provide a user-friendly interface with examples and help text. The main entry point supports multiple search modes (headlines vs everything) and various filtering options.

**News Fetcher Module**: Central component that handles all NewsAPI interactions. Implements rate limiting to respect API constraints and integrates with the caching system to optimize performance. Uses requests library for HTTP communication and includes comprehensive error handling for API failures.

**Cache Management**: File-based caching system that stores API responses locally to reduce redundant requests. Uses MD5 hashing to generate unique cache keys based on endpoint and parameters. Cache entries have configurable expiration times (default 5 minutes) to balance performance with data freshness.

**Output Formatting**: Modular formatter system with base class architecture supporting multiple output formats. Currently implements console formatter with text truncation and date formatting, plus JSON formatter for structured output. Designed for easy extension to additional formats.

**Configuration Management**: Centralized configuration system storing API settings, rate limiting parameters, cache duration, and validation rules. Includes comprehensive lists of valid country and language codes supported by NewsAPI.

**Utility Functions**: Validation helpers for date formats, country codes, and language codes to ensure API compliance before making requests.

## Design Patterns

**Strategy Pattern**: Used in the formatter system where different output strategies (console, JSON) can be selected at runtime without changing the core logic.

**Singleton-like Caching**: Cache manager creates and manages a dedicated cache directory structure for persistent storage across application runs.

**Error Handling**: Custom exception classes for API-specific errors, allowing for more precise error reporting and handling.

## Data Flow

1. CLI arguments are parsed and validated using utility functions
2. NewsFetcher is initialized with API key and configuration
3. Cache is checked for existing responses before making API calls
4. API requests are rate-limited and cached upon successful response
5. Responses are processed through the selected formatter for display

# External Dependencies

**NewsAPI Service**: Primary data source requiring API key authentication. Supports both top headlines and comprehensive article search endpoints with various filtering parameters.

**Python Standard Library**: Relies on argparse for CLI handling, json for data serialization, hashlib for cache key generation, os for file system operations, time and datetime for temporal operations, and requests for HTTP communication.

**File System**: Uses local file system for cache storage in `.news_cache` directory, storing responses as JSON files with MD5-hashed filenames for quick retrieval.