"""
Output formatters for news articles
"""

import json
from datetime import datetime
from config import OUTPUT_CONFIG


class BaseFormatter:
    """Base class for output formatters"""
    
    def display(self, response, verbose=False):
        """Display the news response"""
        raise NotImplementedError


class ConsoleFormatter(BaseFormatter):
    """Console output formatter with rich text support"""
    
    def __init__(self):
        self.max_title_length = OUTPUT_CONFIG['max_title_length']
        self.max_description_length = OUTPUT_CONFIG['max_description_length']
        self.console_width = OUTPUT_CONFIG['console_width']
    
    def _truncate_text(self, text, max_length):
        """Truncate text to specified length"""
        if not text:
            return ""
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length - 3] + "..."
    
    def _format_date(self, date_string):
        """Format date string for display"""
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime(OUTPUT_CONFIG['date_format'])
        except (ValueError, AttributeError):
            return date_string or "Unknown date"
    
    def _print_separator(self, char='-'):
        """Print a separator line"""
        print(char * self.console_width)
    
    def _print_header(self, total_results, articles_count):
        """Print header information"""
        self._print_separator('=')
        print(f"NEWS ARTICLES")
        print(f"Total Results: {total_results:,}")
        print(f"Showing: {articles_count} articles")
        self._print_separator('=')
        print()
    
    def _print_article(self, article, index, verbose=False):
        """Print a single article"""
        # Article number and title
        title = self._truncate_text(article.get('title', 'No title'), self.max_title_length)
        print(f"{index + 1:2d}. {title}")
        
        # Source and date
        source_name = article.get('source', {}).get('name', 'Unknown source')
        published_at = self._format_date(article.get('publishedAt'))
        print(f"    Source: {source_name}")
        print(f"    Published: {published_at}")
        
        # Description
        description = article.get('description')
        if description:
            description = self._truncate_text(description, self.max_description_length)
            print(f"    Description: {description}")
        
        # URL
        url = article.get('url')
        if url:
            print(f"    URL: {url}")
        
        # Additional info in verbose mode
        if verbose:
            author = article.get('author')
            if author:
                print(f"    Author: {author}")
            
            url_to_image = article.get('urlToImage')
            if url_to_image:
                print(f"    Image: {url_to_image}")
        
        print()  # Empty line after each article
    
    def display(self, response, verbose=False):
        """Display news articles in console format"""
        if not response:
            print("No response received.")
            return
        
        articles = response.get('articles', [])
        total_results = response.get('totalResults', 0)
        
        if not articles:
            print("No articles found matching your criteria.")
            return
        
        # Print header
        self._print_header(total_results, len(articles))
        
        # Print articles
        for index, article in enumerate(articles):
            self._print_article(article, index, verbose)
        
        # Print footer
        self._print_separator()
        print(f"End of results. Showing {len(articles)} of {total_results:,} total articles.")


class JSONFormatter(BaseFormatter):
    """JSON output formatter"""
    
    def display(self, response, verbose=False):
        """Display news response in JSON format"""
        if verbose:
            # Pretty print with indentation
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            # Compact JSON output
            print(json.dumps(response, ensure_ascii=False))


class RichConsoleFormatter(BaseFormatter):
    """Enhanced console formatter using Rich library"""
    
    def __init__(self):
        try:
            from rich.console import Console
            from rich.table import Table
            from rich.text import Text
            from rich.panel import Panel
            from rich.columns import Columns
            
            self.console = Console()
            self.Table = Table
            self.Text = Text
            self.Panel = Panel
            self.Columns = Columns
            self.rich_available = True
        except ImportError:
            self.rich_available = False
            # Fallback to regular console formatter
            self.console_formatter = ConsoleFormatter()
    
    def display(self, response, verbose=False):
        """Display news articles using Rich formatting"""
        if not self.rich_available:
            self.console_formatter.display(response, verbose)
            return
        
        if not response:
            self.console.print("No response received.", style="red")
            return
        
        articles = response.get('articles', [])
        total_results = response.get('totalResults', 0)
        
        if not articles:
            self.console.print("No articles found matching your criteria.", style="yellow")
            return
        
        # Header
        header_text = f"NEWS ARTICLES\nTotal Results: {total_results:,} | Showing: {len(articles)} articles"
        self.console.print(self.Panel(header_text, title="📰 News Fetcher", border_style="blue"))
        
        # Articles
        for index, article in enumerate(articles):
            self._print_rich_article(article, index + 1, verbose)
    
    def _print_rich_article(self, article, number, verbose=False):
        """Print a single article with Rich formatting"""
        # Title
        title = article.get('title', 'No title')
        title_text = self.Text(f"{number}. {title}", style="bold cyan")
        
        # Content
        content_lines = []
        
        # Source and date
        source_name = article.get('source', {}).get('name', 'Unknown source')
        published_at = article.get('publishedAt', 'Unknown date')
        try:
            dt = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            published_at = dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, AttributeError):
            pass
        
        content_lines.append(f"[green]Source:[/green] {source_name}")
        content_lines.append(f"[green]Published:[/green] {published_at}")
        
        # Description
        description = article.get('description')
        if description:
            content_lines.append(f"[green]Description:[/green] {description}")
        
        # URL
        url = article.get('url')
        if url:
            content_lines.append(f"[green]URL:[/green] [link]{url}[/link]")
        
        # Verbose info
        if verbose:
            author = article.get('author')
            if author:
                content_lines.append(f"[green]Author:[/green] {author}")
            
            url_to_image = article.get('urlToImage')
            if url_to_image:
                content_lines.append(f"[green]Image:[/green] [link]{url_to_image}[/link]")
        
        content = "\n".join(content_lines)
        
        # Create panel
        panel = self.Panel(content, title=title, border_style="dim")
        self.console.print(panel)
        self.console.print()  # Empty line
