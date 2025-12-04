# Streamlit Cloud Deployment Guide

## Quick Setup for Streamlit Cloud

### Step 1: Push Your Code to GitHub

Your code is already on GitHub at: https://github.com/zodiac6k/quant

### Step 2: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `zodiac6k/quant`
5. Set main file path: `nasdaq_dashboard.py`
6. Click **"Deploy"**

### Step 3: Configure NewsAPI Key (Optional but Recommended)

After deployment, configure your NewsAPI key for better news coverage:

1. In your Streamlit Cloud app dashboard, click **"Settings"** (⚙️ icon)
2. Scroll down to **"Secrets"** section
3. Click **"Open secrets editor"**
4. Add your NewsAPI key:

```toml
NEWSAPI_KEY = "d11ec4ba9c7c46ddba805549bff4c969"
```

5. Click **"Save"**
6. The app will automatically redeploy with the new configuration

### Step 4: Access Your App

Your app will be available at: `https://your-app-name.streamlit.app`

## Important Notes

### ✅ What's Already Configured

- `.gitignore` excludes `.streamlit/secrets.toml` (local secrets)
- All dependencies are in `requirements.txt`
- Dashboard works without NewsAPI (uses Yahoo Finance as fallback)

### 🔒 Security

- **Never commit API keys to GitHub**
- Streamlit Cloud Secrets are encrypted and secure
- Your local `.streamlit/secrets.toml` is automatically ignored by git

### 📊 Features Available

Once deployed, your app includes:
- 📊 Market Overview
- 🔍 Stock Analysis (with news, ratings, forecasts)
- 📊 Stock Summary (multiple stocks with confidence levels)
- 🏆 Gainers & Losers

## Troubleshooting

### App Won't Deploy

1. **Check requirements.txt**: Make sure all dependencies are listed
2. **Check main file**: Ensure `nasdaq_dashboard.py` is the correct entry point
3. **Check logs**: Click "Manage app" → "Logs" to see error messages

### NewsAPI Not Working

1. **Verify key is set**: Check Streamlit Cloud Secrets
2. **Check key format**: No extra spaces or quotes needed
3. **Rate limits**: Free tier is 100 requests/day
4. **Fallback**: App will use Yahoo Finance if NewsAPI fails

### Dependencies Issues

If you see import errors:
1. Check `requirements.txt` has all packages
2. Check Streamlit Cloud logs for specific errors
3. Ensure package versions are compatible

## Updating Your App

After making changes to your code:

1. **Commit and push to GitHub**:
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```

2. **Streamlit Cloud auto-deploys**: Your app will automatically update

Or manually trigger redeploy:
- Go to app settings → "Reboot app"

## Environment Variables

If you need to set environment variables (alternative to Secrets):

1. Go to app settings
2. Click "Advanced settings"
3. Add environment variables
4. Redeploy

## Support

- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-community-cloud
- **Streamlit Forum**: https://discuss.streamlit.io
- **Your Repository**: https://github.com/zodiac6k/quant

## Your Current Setup

- **Repository**: https://github.com/zodiac6k/quant
- **Main File**: `nasdaq_dashboard.py`
- **NewsAPI Key**: Configure in Streamlit Cloud Secrets (see Step 3 above)

Happy deploying! 🚀

