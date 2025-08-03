# CLI News Automation - Workflow Canvas

## Visual Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLI NEWS AUTOMATION WORKFLOW                        │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   1. USER   │───▶│  2. CLI PARSER  │───▶│ 3. VALIDATION   │───▶│ 4. NEWS FETCHER │
│   INPUT     │    │   & ARGUMENTS   │    │   & SETUP       │    │  INITIALIZATION │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
      │                      │                      │                      │
      │                      │                      │                      │
      ▼                      ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ • Keywords  │    │ • Parse CLI Args│    │ • Validate Dates│    │ • Initialize    │
│ • Category  │    │ • Set Defaults  │    │ • Check Country │    │   API Client    │
│ • Country   │    │ • Handle Flags  │    │ • Verify Params │    │ • Setup Cache   │
│ • Language  │    │ • Show Help     │    │ • Check API Key │    │ • Rate Limiting │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘

                                    ┌─────────────────┐
                                    │  5. CACHE CHECK │
                                    │  & MANAGEMENT   │
                                    └─────────────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ • Generate Key  │
                                    │ • Check Expired │
                                    │ • Return Cached │
                                    │ • If Available  │
                                    └─────────────────┘
                                             │
                                             ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   9. OUTPUT │◀───│ 8. FORMATTER    │◀───│ 7. API RESPONSE │◀───│ 6. API REQUEST  │
│   DISPLAY   │    │   SELECTION     │    │   PROCESSING    │    │   TO NEWSAPI    │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
      │                      │                      │                      │
      │                      │                      │                      │
      ▼                      ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ • Console   │    │ • Console Format│    │ • Parse JSON    │    │ • Build Request │
│ • JSON      │    │ • JSON Format   │    │ • Extract Data  │    │ • Apply Filters │
│ • Rich Text │    │ • Rich Format   │    │ • Error Handle  │    │ • Send HTTP     │
│ • Formatted │    │ • Truncate Text │    │ • Cache Result  │    │ • Rate Limit    │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Detailed Process Flow

### 1. User Input Stage
- **Command Line Arguments**: Users provide search parameters
- **Available Parameters**:
  - `--query`: Keywords or phrases
  - `--category`: News category (business, sports, tech, etc.)
  - `--country`: Country code (us, gb, de, etc.)
  - `--language`: Language code (en, es, fr, etc.)
  - `--sources`: Specific news sources
  - `--from-date` / `--to-date`: Date range
  - `--output`: Format (console/json)

### 2. CLI Parser & Arguments
- **Argument Parsing**: Using Python's argparse module
- **Default Values**: Set sensible defaults for optional parameters
- **Help System**: Comprehensive help with examples
- **Mutual Exclusions**: Handle conflicting options

### 3. Validation & Setup
- **Date Validation**: Ensure proper YYYY-MM-DD format
- **Country Code Check**: Validate against supported countries
- **API Key Verification**: Check for required NewsAPI key
- **Parameter Constraints**: Enforce API limits and rules

### 4. News Fetcher Initialization
- **API Client Setup**: Initialize with authentication
- **Cache System**: Setup file-based caching
- **Rate Limiting**: Implement request throttling
- **Error Handling**: Prepare exception management

### 5. Cache Check & Management
- **Cache Key Generation**: MD5 hash of request parameters
- **Expiration Check**: Verify cache freshness (5 min default)
- **Cache Retrieval**: Return cached data if available
- **Cache Storage**: Store new responses for future use

### 6. API Request to NewsAPI
- **Request Building**: Construct API call with filters
- **Endpoint Selection**: Choose headlines vs everything
- **HTTP Request**: Send authenticated request
- **Rate Limiting**: Respect API constraints

### 7. API Response Processing
- **JSON Parsing**: Convert response to Python objects
- **Error Detection**: Check for API errors
- **Data Extraction**: Extract article information
- **Cache Storage**: Save successful responses

### 8. Formatter Selection
- **Format Choice**: Console, JSON, or Rich text
- **Text Processing**: Truncate long content
- **Date Formatting**: Convert timestamps
- **Layout Design**: Organize information display

### 9. Output Display
- **Console Output**: Formatted text with separators
- **JSON Output**: Structured data format
- **Rich Output**: Enhanced formatting with colors
- **Summary Stats**: Display result counts

## Error Handling Flow

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ API ERRORS  │───▶│  ERROR CAPTURE  │───▶│ USER FEEDBACK   │
└─────────────┘    └─────────────────┘    └─────────────────┘
      │                      │                      │
      ▼                      ▼                      ▼
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ • Rate Limit│    │ • Log Error     │    │ • Clear Message │
│ • Invalid Key│    │ • Categorize    │    │ • Actionable    │
│ • No Results│    │ • Context Info  │    │ • Exit Graceful │
│ • Network   │    │ • Stack Trace   │    │ • Retry Hints   │
└─────────────┘    └─────────────────┘    └─────────────────┘
```

## Data Flow Architecture

```
Input Layer          Processing Layer         Storage Layer        Output Layer
┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐
│ CLI Args    │───▶│ NewsFetcher     │───▶│ Cache Manager   │───▶│ Formatters  │
│ Environment │    │ Validation      │    │ File System     │    │ Console     │
│ Config      │    │ Rate Limiter    │    │ JSON Storage    │    │ JSON Export │
└─────────────┘    └─────────────────┘    └─────────────────┘    └─────────────┘
```

## Component Responsibilities

### Core Components
1. **main.py**: Entry point and CLI interface
2. **news_fetcher.py**: NewsAPI communication and rate limiting
3. **cache_manager.py**: Local caching system
4. **formatters.py**: Output formatting strategies
5. **config.py**: Configuration and constants
6. **utils.py**: Validation and utility functions

### External Dependencies
- **NewsAPI**: Primary data source
- **requests**: HTTP client library
- **argparse**: Command-line parsing
- **hashlib**: Cache key generation
- **json**: Data serialization

## Example Usage Flows

### Basic News Fetch
```
python main.py --query "artificial intelligence" --country us
      ↓
Validates parameters → Checks cache → Makes API request → Formats output
```

### Category Search with JSON Output
```
python main.py --category technology --output json --verbose
      ↓
Shows verbose logs → Fetches tech news → Returns JSON format
```

### Date-Filtered Search
```
python main.py --everything --query "climate change" --from-date 2025-08-01
      ↓
Uses 'everything' endpoint → Applies date filter → Sorts by relevancy
```