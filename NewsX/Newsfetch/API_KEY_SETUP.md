# NewsAPI Key Setup Guide

This guide shows you exactly where and how to set up your NewsAPI key to fix the SystemExit error.

## ⚡ Quick Start (Fastest Method)

**If you just want to test it quickly:**

1. Open your terminal in VSCode
2. Run this command (replace `e4ba1f3ab14d4a56a0f9c6ed5d9efec7` with your real API key):
   ```bash
   export NEWSAPI_KEY="your-actual-api-key-here"
   export NEWSAPI_KEY="e4ba1f3ab14d4a56a0f9c6ed5d9efec7"
   ```
3. Navigate to your project:
   ```bash
   cd /home/rakesh/Coderex/NewsX/Newsfetch
   ```
4. Test the application:
   ```bash
   python main.py --category technology --country us
   ```

**That's it!** Your SystemExit error should be fixed.

---

## 🔑 Where to Paste Your API Key (All Methods)

You have **4 different options** to set up your API key. Choose the one that works best for you:

---

## Option 1: Environment Variable (Recommended)

### For Current Terminal Session (Temporary)
```bash
# In your terminal, run this command (replace YOUR_API_KEY with your actual key):
export NEWSAPI_KEY="your-actual-api-key-here"

# Then run your program:
cd /home/rakesh/Coderex/NewsX/Newsfetch
python main.py --category technology --country us
```

### For Permanent Setup (All Terminal Sessions)
```bash
# Add this line to your ~/.bashrc file:
echo 'export NEWSAPI_KEY="your-actual-api-key-here"' >> ~/.bashrc

# Reload your shell configuration:
source ~/.bashrc

# Or restart your terminal
```

---

## Option 2: .env File (Easy and Secure)

### Step 1: Create a .env file
```bash
# Navigate to your project directory
cd /home/rakesh/Coderex/NewsX/Newsfetch

# Create .env file
touch .env
```

### Step 2: Add your API key to .env file
Create a `.env` file with this content:
```
# NewsAPI Configuration
# Replace 'your-actual-api-key-here' with your real API key from newsapi.org
NEWSAPI_KEY=your-actual-api-key-here

# Optional: You can also use this alternative name
# NEWS_API_KEY=your-actual-api-key-here

# Note: Never commit this file to version control
# Add .env to your .gitignore file
```

### Step 3: Install python-dotenv (if not already installed)
```bash
pip install python-dotenv
```

### Step 4: Modify main.py to load .env file
Add these lines at the top of main.py (after the imports):
```python
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file
```

---

## Option 3: Direct Code Modification (Not Recommended for Security)

### Modify main.py directly
Find line 190-194 in main.py and replace:
```python
# Check for API key
api_key = os.getenv('NEWSAPI_KEY', os.getenv('NEWS_API_KEY'))
if not api_key:
    print("Error: NewsAPI key not found. Please set NEWSAPI_KEY or NEWS_API_KEY environment variable.", file=sys.stderr)
    print("You can get a free API key from: https://newsapi.org/register", file=sys.stderr)
    sys.exit(1)
```

With:
```python
# Check for API key
api_key = os.getenv('NEWSAPI_KEY', os.getenv('NEWS_API_KEY'))
if not api_key:
    api_key = "your-actual-api-key-here"  # Paste your key here
    
if not api_key:
    print("Error: NewsAPI key not found. Please set NEWSAPI_KEY or NEWS_API_KEY environment variable.", file=sys.stderr)
    print("You can get a free API key from: https://newsapi.org/register", file=sys.stderr)
    sys.exit(1)
```

---

## Option 4: VSCode Terminal Environment Variable

### In VSCode Terminal:
```bash
# Set the environment variable in VSCode terminal:
export NEWSAPI_KEY="your-actual-api-key-here"

# Navigate to project directory:
cd /home/rakesh/Coderex/NewsX/Newsfetch

# Run your program:
python main.py --category technology --country us
```

---

## 🚀 Quick Test Commands

After setting up your API key using any method above, test with these commands:

```bash
# Basic test
python main.py --category technology --country us

# Verbose test to see more details
python main.py --category technology --country us --verbose

# JSON output test
python main.py --query "artificial intelligence" --output json
```

---

## 🔍 How to Get Your NewsAPI Key

If you don't have an API key yet:

1. Go to: https://newsapi.org/register
2. Create a free account
3. Verify your email
4. Copy your API key from the dashboard
5. Use it in any of the methods above

---

## ✅ Verification

To verify your setup worked:

1. The program should run without the SystemExit error
2. You should see news articles displayed
3. In verbose mode, you should see "Making request to: top-headlines"

---

## 🛠️ Troubleshooting

### Still getting SystemExit error?
- Double-check your API key is correct (no extra spaces)
- Make sure you're using the right environment variable name: `NEWSAPI_KEY`
- Try the temporary export method first to test

### API key not working?
- Verify your key at https://newsapi.org/account
- Check if you've exceeded your daily limit (1000 requests for free accounts)
- Ensure your key is active and not expired

---

## 📝 Recommended Approach

**For beginners**: Use Option 1 (Environment Variable - Temporary) first to test, then make it permanent.

**For developers**: Use Option 2 (.env file) for better security and project management.

**For quick testing**: Use Option 4 (VSCode Terminal) if you're working in VSCode.