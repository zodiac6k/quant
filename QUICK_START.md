# Quick Start Guide - Running the NASDAQ Dashboard

## Step-by-Step Instructions

### Step 1: Clone the Repository

Open your terminal/command prompt and run:

```bash
git clone https://github.com/zodiac6k/quant.git
```

Or if you prefer SSH:
```bash
git clone git@github.com:zodiac6k/quant.git
```

This will create a folder called `quant` with all the project files.

### Step 2: Navigate to the Project Directory

```bash
cd quant
```

### Step 3: Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- streamlit
- yfinance
- pandas
- plotly
- newsapi-python
- requests

### Step 5: Set Up NewsAPI (Optional but Recommended)

For better news coverage, set up your NewsAPI key:

**Option A: Using Streamlit Secrets (Recommended)**

1. Create a `.streamlit` folder in the project directory:
   ```bash
   mkdir .streamlit
   ```

2. Create a `secrets.toml` file inside `.streamlit`:
   ```bash
   # Windows
   notepad .streamlit\secrets.toml
   
   # Linux/Mac
   nano .streamlit/secrets.toml
   ```

3. Add your API key:
   ```toml
   NEWSAPI_KEY = "your_api_key_here"
   ```

**Option B: Using Environment Variable**

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

Get your free API key at: https://newsapi.org/register

### Step 6: Run the Dashboard

**Windows:**
```bash
streamlit run nasdaq_dashboard.py
```

**Or use the batch file:**
```bash
run_dashboard.bat
```

**Linux/Mac:**
```bash
streamlit run nasdaq_dashboard.py
```

**Or use the shell script:**
```bash
chmod +x run_dashboard.sh
./run_dashboard.sh
```

### Step 7: Access the Dashboard

The dashboard will automatically open in your default web browser at:
```
http://localhost:8501
```

If it doesn't open automatically, copy the URL from the terminal and paste it into your browser.

## Troubleshooting

### Issue: "streamlit: command not found"
**Solution:** Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

### Issue: "Module not found"
**Solution:** Activate your virtual environment and reinstall:
```bash
pip install -r requirements.txt
```

### Issue: "No news found"
**Solution:** Set up your NewsAPI key (Step 5). The dashboard will still work without it, but with limited news coverage.

### Issue: Port already in use
**Solution:** Streamlit will automatically try the next port (8502, 8503, etc.) or you can specify a port:
```bash
streamlit run nasdaq_dashboard.py --server.port 8502
```

## Quick Reference

```bash
# Clone repository
git clone https://github.com/zodiac6k/quant.git
cd quant

# Setup (first time only)
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Run dashboard
streamlit run nasdaq_dashboard.py
```

## Features Available

Once running, you'll have access to:
- 📊 Market Overview
- 🔍 Stock Analysis (with news, ratings, forecasts)
- 📊 Stock Summary (multiple stocks with confidence levels)
- 🏆 Gainers & Losers

Enjoy analyzing NASDAQ stocks! 📈

