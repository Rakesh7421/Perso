# 📈 Stock Data Fetcher Project

A robust Python application for fetching and storing stock market data using the yfinance library.

## 🚀 Features

- ✅ Fetch stock data from Yahoo Finance
- ✅ Support for Indian stock exchanges (NSE/BSE)
- ✅ Comprehensive error handling and logging
- ✅ Configurable time periods and intervals
- ✅ CSV export functionality
- ✅ Stock information retrieval
- ✅ Test suite included

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

1. **Clone or navigate to the project directory:**
   ```bash
   cd /home/rakesh/Coderex/trade
   ```

2. **Activate the virtual environment:**
   ```bash
   source trade_venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📋 Usage

### Basic Usage

Run the main script to fetch Reliance stock data:
```bash
python import_data.py
```

### Advanced Usage

Use the StockDataFetcher class directly:

```python
from stock_data_fetcher import StockDataFetcher

# Initialize fetcher
fetcher = StockDataFetcher()

# Fetch and save data
success = fetcher.fetch_and_save("RELIANCE.NS", period="1y", interval="1d")

# Get stock information
info = fetcher.get_stock_info("RELIANCE.NS")
print(info)
```

### Supported Parameters

**Periods:** `1d`, `5d`, `1mo`, `3mo`, `6mo`, `1y`, `2y`, `5y`, `10y`, `ytd`, `max`

**Intervals:** `1m`, `2m`, `5m`, `15m`, `30m`, `60m`, `90m`, `1h`, `1d`, `5d`, `1wk`, `1mo`, `3mo`

**Indian Stock Symbols:**
- Reliance: `RELIANCE.NS`
- TCS: `TCS.NS`
- Infosys: `INFY.NS`
- HDFC Bank: `HDFCBANK.NS`
- ICICI Bank: `ICICIBANK.NS`

## 🧪 Testing

Run the test suite:
```bash
# Run all tests
pytest test_stock_fetcher.py -v

# Run basic functionality tests
python test_stock_fetcher.py
```

## 📁 Project Structure

```
trade/
├── import_data.py          # Main script (fixed version)
├── stock_data_fetcher.py   # Core fetcher class
├── config.py              # Configuration settings
├── test_stock_fetcher.py   # Test suite
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── README.md             # This file
├── trade_venv/           # Virtual environment
├── data/                 # Output directory for CSV files
└── trade.log             # Log file
```

## 🔧 Configuration

Edit `.env` file to customize default settings:
```env
DEFAULT_PERIOD=1y
DEFAULT_INTERVAL=1d
DEFAULT_OUTPUT_DIR=data
LOG_LEVEL=INFO
```

## 📊 Output

CSV files are saved in the `data/` directory with the following naming convention:
```
{symbol}_{period}_{timestamp}.csv
```

Example: `reliance_1y_20240101_120000.csv`

## 🐛 Issues Fixed

The original `import_data.py` had several issues that have been resolved:

1. ❌ **Period/Filename Mismatch**: Comment said "5 years" but code used "1y"
   - ✅ **Fixed**: Aligned period with actual usage and clear documentation

2. ❌ **No Error Handling**: Script would crash on network/API errors
   - ✅ **Fixed**: Comprehensive error handling and logging

3. ❌ **Hard-coded Values**: No configuration flexibility
   - ✅ **Fixed**: Configurable settings via config.py and .env

4. ❌ **No Data Validation**: No checks for empty or invalid data
   - ✅ **Fixed**: Data validation and informative error messages

5. ❌ **Poor File Organization**: Single script with mixed concerns
   - ✅ **Fixed**: Modular design with separate classes and functions

## 📝 Logging

The application logs to both console and `trade.log` file:
- INFO: General information about operations
- WARNING: Non-critical issues (e.g., no data found)
- ERROR: Critical errors that prevent operation

## 🤝 Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## 📄 License

This project is for educational and personal use.

## 🆘 Troubleshooting

### Common Issues

1. **No data returned**: Check if the stock symbol is correct and markets are open
2. **Network errors**: Ensure internet connection and try again
3. **Permission errors**: Check write permissions for the data directory

### Getting Help

Check the log file (`trade.log`) for detailed error messages and troubleshooting information.