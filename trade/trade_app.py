"""
source /home/rakesh/Coderex/trade_venv/bin/activate
python3 /home/rakesh/Coderex/trade/trade_app.py
Enhanced Stock Data Trading Application
Combined all functionality into a single comprehensive file
"""
import yfinance as yf
import pandas as pd
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration Constants
DEFAULT_PERIOD = "1y"  # 1 year
DEFAULT_INTERVAL = "1d"  # Daily data
DEFAULT_OUTPUT_DIR = "data"

# Stock symbols
INDIAN_STOCKS = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS", 
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS"
}

# Ensure data directory exists
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Class to fetch and save stock data with error handling"""
    
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def fetch_stock_data(
        self, 
        symbol: str, 
        period: str = DEFAULT_PERIOD, 
        interval: str = DEFAULT_INTERVAL
    ) -> Optional[pd.DataFrame]:
        """
        Fetch stock data for a given symbol
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
        
        Returns:
            DataFrame with stock data or None if failed
        """
        try:
            logger.info(f"Fetching data for {symbol} with period={period}, interval={interval}")
            
            # Create ticker object
            ticker = yf.Ticker(symbol)
            
            # Fetch historical data
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return None
            
            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def save_to_csv(
        self, 
        data: pd.DataFrame, 
        symbol: str, 
        period: str = DEFAULT_PERIOD
    ) -> Optional[str]:
        """
        Save DataFrame to CSV file
        
        Args:
            data: DataFrame to save
            symbol: Stock symbol for filename
            period: Period for filename
        
        Returns:
            Filename if successful, None if failed
        """
        try:
            # Clean symbol for filename (remove .NS, .BO etc.)
            clean_symbol = symbol.split('.')[0].lower()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{clean_symbol}_{period}_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            # Save to CSV
            data.to_csv(filepath)
            logger.info(f"Data saved to {filepath}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving data to CSV: {str(e)}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information about the stock
        
        Args:
            symbol: Stock symbol
        
        Returns:
            Dictionary with stock info or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key information
            stock_info = {
                'symbol': symbol,
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'currency': info.get('currency', 'N/A')
            }
            
            return stock_info
            
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            return None
    
    def fetch_and_save(
        self, 
        symbol: str, 
        period: str = DEFAULT_PERIOD, 
        interval: str = DEFAULT_INTERVAL
    ) -> bool:
        """
        Fetch stock data and save to CSV in one operation
        
        Args:
            symbol: Stock symbol
            period: Time period
            interval: Data interval
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get stock info first
            stock_info = self.get_stock_info(symbol)
            if stock_info:
                logger.info(f"Processing: {stock_info['company_name']} ({symbol})")
            
            # Fetch data
            data = self.fetch_stock_data(symbol, period, interval)
            if data is None:
                return False
            
            # Save data
            filename = self.save_to_csv(data, symbol, period)
            if filename is None:
                return False
            
            # Log summary
            logger.info(f"Summary for {symbol}:")
            logger.info(f"  - Records: {len(data)}")
            logger.info(f"  - Date range: {data.index.min()} to {data.index.max()}")
            logger.info(f"  - File: {filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error in fetch_and_save for {symbol}: {str(e)}")
            return False

    def fetch_multiple_stocks(self, stocks: Dict[str, str], period: str = DEFAULT_PERIOD) -> Dict[str, bool]:
        """
        Fetch data for multiple stocks
        
        Args:
            stocks: Dictionary of stock names and symbols
            period: Time period for data fetching
            
        Returns:
            Dictionary showing success/failure for each stock
        """
        results = {}
        logger.info(f"Starting batch fetch for {len(stocks)} stocks")
        
        for name, symbol in stocks.items():
            logger.info(f"Processing {name} ({symbol})")
            success = self.fetch_and_save(symbol, period)
            results[name] = success
            
            if success:
                print(f"✅ {name} - Success")
            else:
                print(f"❌ {name} - Failed")
                
        return results


def demo_single_stock():
    """Demonstrate fetching a single stock"""
    fetcher = StockDataFetcher()
    
    # Example: Fetch Reliance data
    symbol = "RELIANCE.NS"
    success = fetcher.fetch_and_save(symbol, period="1y", interval="1d")
    
    if success:
        print(f"✅ Successfully processed {symbol}")
    else:
        print(f"❌ Failed to process {symbol}")


def demo_multiple_stocks():
    """Demonstrate fetching multiple stocks"""
    fetcher = StockDataFetcher()
    
    # Fetch all Indian stocks
    results = fetcher.fetch_multiple_stocks(INDIAN_STOCKS, period="1y")
    
    # Summary
    successful = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\n📊 Summary: {successful}/{total} stocks processed successfully")
    
    # Show failed stocks
    failed_stocks = [name for name, success in results.items() if not success]
    if failed_stocks:
        print(f"❌ Failed stocks: {', '.join(failed_stocks)}")


def interactive_mode():
    """Interactive mode for custom stock fetching"""
    fetcher = StockDataFetcher()
    
    print("🚀 Stock Data Fetcher - Interactive Mode")
    print("Available predefined stocks:")
    for name, symbol in INDIAN_STOCKS.items():
        print(f"  - {name}: {symbol}")
    
    while True:
        print("\nOptions:")
        print("1. Fetch predefined stock")
        print("2. Fetch custom stock symbol")
        print("3. Fetch all predefined stocks")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\nAvailable stocks:")
            for i, (name, symbol) in enumerate(INDIAN_STOCKS.items(), 1):
                print(f"{i}. {name} ({symbol})")
            
            try:
                stock_choice = int(input("Select stock number: ")) - 1
                stock_list = list(INDIAN_STOCKS.items())
                if 0 <= stock_choice < len(stock_list):
                    name, symbol = stock_list[stock_choice]
                    period = input(f"Period (default: {DEFAULT_PERIOD}): ").strip() or DEFAULT_PERIOD
                    
                    success = fetcher.fetch_and_save(symbol, period)
                    if success:
                        print(f"✅ Successfully processed {name}")
                    else:
                        print(f"❌ Failed to process {name}")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Invalid input")
                
        elif choice == "2":
            symbol = input("Enter stock symbol (e.g., RELIANCE.NS): ").strip().upper()
            if symbol:
                period = input(f"Period (default: {DEFAULT_PERIOD}): ").strip() or DEFAULT_PERIOD
                success = fetcher.fetch_and_save(symbol, period)
                if success:
                    print(f"✅ Successfully processed {symbol}")
                else:
                    print(f"❌ Failed to process {symbol}")
            else:
                print("❌ Symbol cannot be empty")
                
        elif choice == "3":
            period = input(f"Period for all stocks (default: {DEFAULT_PERIOD}): ").strip() or DEFAULT_PERIOD
            demo_multiple_stocks()
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice")


def main():
    """Main function with multiple operation modes"""
    print("🚀 Stock Data Trading Application")
    print("=" * 50)
    
    if len(os.sys.argv) > 1:
        mode = os.sys.argv[1].lower()
        
        if mode == "single":
            demo_single_stock()
        elif mode == "multiple":
            demo_multiple_stocks()
        elif mode == "interactive":
            interactive_mode()
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Available modes: single, multiple, interactive")
    else:
        # Default behavior - run the original import logic
        try:
            # Initialize the fetcher
            fetcher = StockDataFetcher()
            
            # Example: Fetch Reliance data for 1 year
            symbol = "RELIANCE.NS"
            period = "1y"
            
            logger.info("Starting stock data import...")
            logger.info(f"Fetching {period} data for {symbol}")
            
            # Fetch and save data
            success = fetcher.fetch_and_save(symbol, period=period, interval="1d")
            
            if success:
                print("✅ Done! Data successfully fetched and saved.")
                print("📁 Check the 'data' directory for the CSV file.")
            else:
                print("❌ Failed to fetch or save data. Check the logs for details.")
                
        except Exception as e:
            logger.error(f"Unexpected error in main: {str(e)}")
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()