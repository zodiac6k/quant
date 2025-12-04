# News API Setup Guide

This dashboard supports multiple news sources to provide comprehensive news coverage for stocks.

## Current News Sources

1. **NewsAPI** (Primary - Recommended)
   - High-quality financial news
   - Free tier: 100 requests/day
   - Better coverage and relevance

2. **Yahoo Finance** (Fallback)
   - Built-in with yfinance
   - No API key required
   - Limited coverage for some stocks

## Setting Up NewsAPI

### Step 1: Get Your Free API Key

1. Visit [https://newsapi.org/register](https://newsapi.org/register)
2. Sign up for a free account
3. Copy your API key from the dashboard

### Step 2: Configure API Key

You have two options to set your API key:

#### Option A: Using Streamlit Secrets (Recommended)

1. Create a `.streamlit` folder in your project directory (if it doesn't exist)
2. Create a file named `secrets.toml` inside `.streamlit` folder
3. Add your API key:

```toml
NEWSAPI_KEY = "your_api_key_here"
```

**Example directory structure:**
```
Quant Analytics/
├── .streamlit/
│   └── secrets.toml
├── nasdaq_dashboard.py
└── ...
```

#### Option B: Using Environment Variables

**Windows (PowerShell):**
```powershell
$env:NEWSAPI_KEY="your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set NEWSAPI_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export NEWSAPI_KEY="your_api_key_here"
```

**Note**: Environment variables set this way are temporary. To make them permanent:
- **Windows**: Add to System Environment Variables
- **Linux/Mac**: Add to `~/.bashrc` or `~/.zshrc`

### Step 3: Restart Dashboard

After setting the API key, restart your Streamlit dashboard:

```bash
streamlit run nasdaq_dashboard.py
```

## Verifying Setup

Once configured, you should see:
- More news articles for stocks
- "Source: NewsAPI" or "Source: NewsAPI & Yahoo Finance" in the news section
- Better news coverage, especially for popular stocks

## NewsAPI Free Tier Limits

- **100 requests per day**
- **1,000 requests per month**
- Perfect for personal use and testing

## Alternative News APIs

If you need more requests or different features, consider:

1. **Alpha Vantage News & Sentiment API**
   - Free tier available
   - Financial news focused
   - Visit: https://www.alphavantage.co/support/#api-key

2. **Financial Modeling Prep API**
   - Free tier: 250 requests/day
   - Financial data and news
   - Visit: https://site.financialmodelingprep.com/developer/docs/

3. **Polygon.io**
   - Free tier available
   - Real-time financial data
   - Visit: https://polygon.io/

## Troubleshooting

### "No recent news found"
- Check if API key is set correctly
- Verify you haven't exceeded daily limit
- Try a different stock (some have limited coverage)

### API Key Not Working
- Ensure no extra spaces in the key
- Check if key is active in NewsAPI dashboard
- Verify the key format (should be a long string)

### Rate Limit Exceeded
- Free tier: 100 requests/day
- Wait until next day or upgrade plan
- Dashboard will fall back to Yahoo Finance

## Security Note

⚠️ **Never commit your API key to version control!**

- `.streamlit/secrets.toml` is automatically ignored by git
- Never share your API key publicly
- If key is exposed, regenerate it immediately

## Support

For issues with:
- **NewsAPI**: Visit https://newsapi.org/docs
- **Dashboard**: Check the dashboard error messages
- **Setup**: Review this guide

