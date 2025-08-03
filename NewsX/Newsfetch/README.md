# CLI News Automation Tool

A powerful Python command-line tool for fetching and filtering news articles from NewsAPI with advanced features like caching, multiple output formats, and comprehensive filtering options.

## Features

### 🔍 **Advanced Search Options**
- **Keywords**: Search for specific terms or phrases
- **Categories**: Filter by business, technology, sports, health, science, entertainment, general
- **Countries**: Get news from specific countries using country codes (us, gb, de, fr, etc.)
- **Languages**: Filter articles by language (en, es, fr, de, etc.)
- **Sources**: Target specific news sources (bbc-news, cnn, reuters, etc.)
- **Date Ranges**: Filter articles by publication date

### 📊 **Multiple Output Formats**
- **Console**: Clean, formatted text output with article summaries
- **JSON**: Structured data for integration with other tools
- **Verbose Mode**: Additional details including author and image URLs

### ⚡ **Performance Features**
- **Smart Caching**: Automatic caching of API responses to reduce redundant requests
- **Rate Limiting**: Built-in protection against API rate limits
- **Batch Processing**: Configurable page sizes up to 100 articles

### 🎯 **Two Search Modes**
- **Headlines**: Get top headlines (default mode)
- **Everything**: Search through millions of articles with advanced filtering

## Installation & Setup

1. **Get NewsAPI Key**: 
   - Visit [newsapi.org](https://newsapi.org/register)
   - Create a free account (1,000 requests/day)
   - Copy your API key

2. **Set Environment Variable**:
   ```bash
   export NEWSAPI_KEY="your-api-key-here"
   ```

3. **Install Dependencies**:
   ```bash
   pip install requests
   ```

## Usage Examples

### Basic Usage
```bash
# Get US technology headlines
python main.py --category technology --country us

# Search for AI articles
python main.py --query "artificial intelligence" --country us

# Get business news in JSON format
python main.py --category business --output json
```

### Advanced Filtering
```bash
# Search everything with date range
python main.py --everything --query "climate change" --from-date 2025-07-01 --sort-by popularity

# Specific sources with verbose output
python main.py --sources "bbc-news,cnn,reuters" --verbose

# Recent articles (last 3 days)
python main.py --last-days 3 --page-size 10
```

### Output Formats
```bash
# Console output (default)
python main.py --category technology

# JSON output for scripts
python main.py --category technology --output json

# Verbose mode with extra details
python main.py --category technology --verbose
```

## Command Line Options

### Search Parameters
- `--query, -q`: Keywords or phrases to search for
- `--category, -c`: News category (business, entertainment, general, health, science, sports, technology)
- `--country`: Country code (us, gb, de, fr, etc.)
- `--language`: Language code (default: en)
- `--sources`: Comma-separated news sources

### Date Filtering
- `--from-date`: Start date (YYYY-MM-DD format)
- `--to-date`: End date (YYYY-MM-DD format)
- `--last-days`: Articles from last N days

### Search Modes
- `--headlines`: Top headlines (default)
- `--everything`: Search all articles

### Output Options
- `--output, -o`: Format (console, json)
- `--verbose, -v`: Show additional details
- `--page-size`: Articles per page (1-100, default: 20)
- `--page`: Page number (default: 1)
- `--sort-by`: Sort order (relevancy, popularity, publishedAt)

### Performance
- `--no-cache`: Disable response caching
- `--help, -h`: Show help message

## Example Output

### Console Format
```
================================================================================
NEWS ARTICLES
Total Results: 34
Showing: 5 articles
================================================================================

 1. ChatGPT users shocked to learn their chats were in Google search results
    Source: Ars Technica
    Published: 2025-08-01 17:21:54
    Description: OpenAI scrambles to remove personal ChatGPT conversations from Google results.
    URL: https://arstechnica.com/tech-policy/2025/08/chatgpt-users-shocked-to-learn-their-chats-were-in-google-search-results/

 2. Director's Take: The More You Know — Overwatch 2
    Source: Blizzard.com
    Published: 2025-08-01 16:00:00
    Description: If knowledge is power, Overwatch players are about to hit Champion...
    URL: https://news.blizzard.com/en-us/article/24226466/directors-take-the-more-you-know
```

### JSON Format
```json
{
  "status": "ok",
  "totalResults": 14764,
  "articles": [
    {
      "source": {"id": "wired", "name": "Wired"},
      "author": "Paresh Dave",
      "title": "Microsoft, OpenAI, and a US Teachers' Union Are Hatching a Plan...",
      "description": "The National Academy for AI Instruction will make artificial intelligence...",
      "url": "https://www.wired.com/story/microsoft-openai-and-a-us-teachers-union...",
      "publishedAt": "2025-07-08T11:30:08Z"
    }
  ]
}
```

## Features Demonstrated

✅ **Working CLI Interface**: Complete command-line argument parsing with help
✅ **Real NewsAPI Integration**: Fetches live news data from NewsAPI
✅ **Multiple Search Modes**: Both headlines and everything endpoints
✅ **Smart Caching**: Automatic caching reduces API calls (see "Using cached response...")
✅ **Multiple Output Formats**: Console and JSON output formats
✅ **Comprehensive Filtering**: Category, country, date, source filtering
✅ **Error Handling**: Graceful handling of API errors and invalid parameters
✅ **Verbose Mode**: Additional debugging and article details
✅ **Rate Limiting**: Built-in request throttling

## Architecture Components

- **main.py**: CLI interface and argument parsing
- **news_fetcher.py**: NewsAPI communication with rate limiting
- **cache_manager.py**: File-based caching system
- **formatters.py**: Multiple output format strategies
- **config.py**: Configuration settings and validation
- **utils.py**: Utility functions for validation
- **workflow_canvas.md**: Visual workflow documentation

## Cache Management

The tool automatically caches API responses for 5 minutes to:
- Reduce API usage
- Improve response times
- Prevent duplicate requests

Cache files are stored in `.news_cache/` directory and automatically expire.

## Country Codes
Common country codes: `us` (USA), `gb` (UK), `de` (Germany), `fr` (France), `it` (Italy), `jp` (Japan), `ca` (Canada), `au` (Australia)

## News Sources
Popular sources: `bbc-news`, `cnn`, `reuters`, `associated-press`, `abc-news`, `techcrunch`, `the-verge`, `bloomberg`

---

**Ready to use!** The CLI News Automation tool is fully functional and tested with real NewsAPI data.