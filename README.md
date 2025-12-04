# NASDAQ Analytics Dashboard

A comprehensive Python dashboard to track NASDAQ index movement, analyze stocks, view gainers/losers, news analysis, and analyst ratings.

## Features

### Command Line Tracker (`nasdaq_tracker.py`)
- **Daily Movement Tracking**: Compares current day's closing price with previous day's closing price
- **Intraday Analysis**: Tracks movement from open to close
- **Multi-day Tracking**: Option to track movement over multiple days
- **Detailed Metrics**: Shows price changes, percentage changes, highs, lows, and ranges

### Interactive Dashboard (`nasdaq_dashboard.py`)
- **📊 Market Overview**: Real-time NASDAQ Composite metrics and trends
- **🏆 Gainers & Losers**: Top performing and underperforming stocks with contribution analysis
- **🔍 Stock Analysis**: Detailed analysis for individual stocks including:
  - **News Flow Analysis**: Recent news with sentiment analysis and reasons for price movement
  - **Analyst Ratings**: Buy/Hold/Sell recommendations with rating distribution charts
  - **Price Insights**: Technical indicators and predictions on possible price increases
  - **Historical Data**: Recent price history
- **📈 Visualizations**: Interactive bar charts comparing selected security vs NASDAQ performance

## Quick Start

**New to the project?** See [QUICK_START.md](QUICK_START.md) for step-by-step instructions to get the dashboard running in minutes!

### Quick Commands

```bash
# Clone the repository
git clone https://github.com/zodiac6k/quant.git
cd quant

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run nasdaq_dashboard.py
```

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

### Optional: News API Setup (Recommended)

For better news coverage, set up a free NewsAPI account:

1. **Get Free API Key**: Visit [https://newsapi.org/register](https://newsapi.org/register)
2. **Configure API Key**:
   - **Option A (Recommended)**: Create `.streamlit/secrets.toml`:
     ```toml
     NEWSAPI_KEY = "your_api_key_here"
     ```
   - **Option B**: Set environment variable:
     ```bash
     export NEWSAPI_KEY="your_api_key_here"  # Linux/Mac
     set NEWSAPI_KEY=your_api_key_here       # Windows
     ```

See `NEWS_API_SETUP.md` for detailed instructions.

## Usage

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Dashboard (Recommended)

Launch the Streamlit dashboard:
```bash
streamlit run nasdaq_dashboard.py
```

The dashboard will open in your browser with three main sections:

1. **Market Overview**: View NASDAQ Composite metrics and 5-day trend
2. **Stock Analysis**: 
   - Select any stock from popular NASDAQ stocks
   - View comparison charts vs NASDAQ
   - Analyze news flow and sentiment
   - Check analyst ratings and recommendations
   - Get price insights and predictions
3. **Gainers & Losers**: 
   - Analyze top gainers and losers
   - View contributors to NASDAQ movement
   - Interactive charts and tables

### Command Line Tracker

For a simple command-line interface, run:
```bash
python nasdaq_tracker.py
```

This will:
- Fetch the latest NASDAQ Composite (^IXIC) data
- Compare today's prices with yesterday's closing price
- Display detailed movement information

### Track Different Indexes

You can modify the symbol in the code or call the function directly:

```python
from nasdaq_tracker import track_nasdaq

# Track NASDAQ Composite (default)
track_nasdaq('^IXIC')

# Track NASDAQ-100
track_nasdaq('^NDX')

# Track a specific NASDAQ stock
track_nasdaq('AAPL')
```

### Track Multiple Days

Uncomment the multi-day tracking function in the script or use:

```python
from nasdaq_tracker import track_multiple_days

# Track last 5 days
track_multiple_days(days=5)
```

## Output

The program displays:
- Previous day's closing price
- Current day's open, high, low, and close prices
- Price change and percentage change from previous day
- Intraday movement (open to close)
- High and low relative to previous day's close

## Available Symbols

- `^IXIC` - NASDAQ Composite (default)
- `^NDX` - NASDAQ-100
- Any valid stock ticker symbol

## Dashboard Features Explained

### News Flow Analysis
- Fetches recent news articles from the previous day
- Analyzes sentiment (positive/negative/neutral) based on keywords
- Extracts potential reasons for price movements
- Displays news headlines with summaries and links

### Analyst Ratings
- Shows recent analyst recommendations (Buy/Hold/Sell)
- Displays rating distribution with pie charts
- Table of detailed recommendations with dates and firms
- Helps understand market sentiment from professional analysts

### Price Insights
- Technical analysis using moving averages
- Volume analysis to detect unusual trading activity
- News sentiment correlation
- Volatility indicators
- Predictions on possible price direction

### Comparison Charts
- Side-by-side bar charts comparing selected stock vs NASDAQ
- Daily percentage changes over multiple days
- Visual representation of relative performance

## Notes

- Data is fetched using the `yfinance` library
- Requires an active internet connection
- Data is based on market trading days (excludes weekends and holidays)
- The program uses the most recent trading day as "current day"
- Dashboard uses caching to improve performance (5-minute cache)
- News analysis uses keyword-based sentiment detection

## License

Free to use and modify.
