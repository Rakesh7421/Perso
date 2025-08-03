#!/usr/bin/env python3
"""
CLI News Fetcher - A command-line tool for fetching news articles from NewsAPI
"""

import argparse
import sys
import os
from datetime import datetime, timedelta
from news_fetcher import NewsFetcher
from formatters import ConsoleFormatter, JSONFormatter
from utils import validate_date, validate_country_code


def create_parser():
    """Create and configure the argument parser"""
    parser = argparse.ArgumentParser(
        description="Fetch and filter news articles from NewsAPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --query "artificial intelligence" --country us
  %(prog)s --category technology --language en --from-date 2025-08-01
  %(prog)s --sources "bbc-news,cnn" --output json
  %(prog)s --everything --query "climate change" --sort-by popularity
        """
    )
    
    # API endpoint selection
    endpoint_group = parser.add_mutually_exclusive_group()
    endpoint_group.add_argument(
        '--headlines', 
        action='store_true', 
        help='Fetch top headlines (default)'
    )
    endpoint_group.add_argument(
        '--everything', 
        action='store_true', 
        help='Search through millions of articles'
    )
    
    # Search parameters
    parser.add_argument(
        '--query', '-q',
        type=str,
        help='Keywords or phrases to search for'
    )
    
    parser.add_argument(
        '--category', '-c',
        choices=['business', 'entertainment', 'general', 'health', 'science', 'sports', 'technology'],
        help='Category of news to fetch'
    )
    
    parser.add_argument(
        '--country',
        type=str,
        help='Country code (e.g., us, gb, de, fr)'
    )
    
    parser.add_argument(
        '--language',
        type=str,
        default='en',
        help='Language code (default: en)'
    )
    
    parser.add_argument(
        '--sources',
        type=str,
        help='Comma-separated list of news sources (e.g., bbc-news,cnn)'
    )
    
    # Date filtering
    parser.add_argument(
        '--from-date',
        type=str,
        help='Oldest article date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--to-date',
        type=str,
        help='Newest article date (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--last-days',
        type=int,
        help='Fetch articles from the last N days'
    )
    
    # Sorting and limiting
    parser.add_argument(
        '--sort-by',
        choices=['relevancy', 'popularity', 'publishedAt'],
        default='publishedAt',
        help='Sort articles by (default: publishedAt)'
    )
    
    parser.add_argument(
        '--page-size',
        type=int,
        default=20,
        help='Number of articles to fetch (max 100, default: 20)'
    )
    
    parser.add_argument(
        '--page',
        type=int,
        default=1,
        help='Page number to fetch (default: 1)'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        choices=['console', 'json'],
        default='console',
        help='Output format (default: console)'
    )
    
    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Disable caching of API responses'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser


def validate_arguments(args):
    """Validate command line arguments"""
    errors = []
    
    # Validate country code
    if args.country and not validate_country_code(args.country):
        errors.append(f"Invalid country code: {args.country}")
    
    # Validate dates
    if args.from_date:
        try:
            validate_date(args.from_date)
        except ValueError as e:
            errors.append(f"Invalid from-date: {e}")
    
    if args.to_date:
        try:
            validate_date(args.to_date)
        except ValueError as e:
            errors.append(f"Invalid to-date: {e}")
    
    # Validate page size
    if args.page_size < 1 or args.page_size > 100:
        errors.append("Page size must be between 1 and 100")
    
    # Validate page number
    if args.page < 1:
        errors.append("Page number must be greater than 0")
    
    # Handle last-days parameter
    if args.last_days:
        if args.last_days < 1:
            errors.append("Last days must be greater than 0")
        # Set from_date based on last_days
        from_date = datetime.now() - timedelta(days=args.last_days)
        args.from_date = from_date.strftime('%Y-%m-%d')
    
    if errors:
        for error in errors:
            print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate arguments
    validate_arguments(args)
    
    # Check for API key
    api_key = os.getenv('NEWSAPI_KEY', os.getenv('NEWS_API_KEY'))
    if not api_key:
        print("Error: NewsAPI key not found. Please set NEWSAPI_KEY or NEWS_API_KEY environment variable.", file=sys.stderr)
        print("You can get a free API key from: https://newsapi.org/register", file=sys.stderr)
        sys.exit(1)
    
    # Initialize news fetcher
    fetcher = NewsFetcher(api_key, use_cache=not args.no_cache, verbose=args.verbose)
    
    try:
        # Determine endpoint
        if args.everything:
            endpoint = 'everything'
        else:
            endpoint = 'top-headlines'
        
        # Fetch articles
        articles = fetcher.fetch_news(
            endpoint=endpoint,
            query=args.query,
            category=args.category,
            country=args.country,
            language=args.language,
            sources=args.sources,
            from_date=args.from_date,
            to_date=args.to_date,
            sort_by=args.sort_by,
            page_size=args.page_size,
            page=args.page
        )
        
        # Format and display results
        if args.output == 'json':
            formatter = JSONFormatter()
        else:
            formatter = ConsoleFormatter()
        
        formatter.display(articles, verbose=args.verbose)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
