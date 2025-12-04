# API Key Setup Guide

## ⚠️ IMPORTANT: Never Add API Keys to GitHub!

**API keys should NEVER be committed to GitHub or any public repository.** They are secrets and must be kept private.

## Where to Add Your NewsAPI Key

### Option 1: Local Development (Your Computer)

The API key should be stored in `.streamlit/secrets.toml` on your local machine. This file is already protected by `.gitignore` and will NOT be uploaded to GitHub.

**Steps:**

1. **Create the secrets file** (if it doesn't exist):
   ```bash
   mkdir .streamlit
   ```

2. **Create/edit `.streamlit/secrets.toml`**:
   ```toml
   NEWSAPI_KEY = "d11ec4ba9c7c46ddba805549bff4c969"
   ```

3. **Verify it's ignored by git**:
   ```bash
   git status
   ```
   You should NOT see `.streamlit/secrets.toml` in the list.

### Option 2: Streamlit Cloud (For Deployed Apps)

If you've deployed your app to Streamlit Cloud (like `qqq-tracking.streamlit.app`), add the API key through Streamlit Cloud's interface:

**Steps:**

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in and select your app
3. Click **"Settings"** (⚙️ icon) or **"Manage app"**
4. Click **"Secrets"** in the sidebar
5. Click **"Open secrets editor"**
6. Add your API key:
   ```toml
   NEWSAPI_KEY = "d11ec4ba9c7c46ddba805549bff4c969"
   ```
7. Click **"Save"**
8. Your app will automatically redeploy

## Why Not GitHub?

### Security Reasons:
- ✅ **`.streamlit/secrets.toml` is in `.gitignore`** - It won't be committed
- ✅ **Streamlit Cloud Secrets are encrypted** - Safe for cloud deployment
- ❌ **GitHub is public** - Anyone can see your repository
- ❌ **API keys in code = Security risk** - Could be abused

### What's Protected:

Your `.gitignore` file already protects:
```
.streamlit/secrets.toml  ← Your API key (local)
.streamlit/config.toml
.env
*.log
```

## Verification

### Check if secrets.toml is ignored:
```bash
git check-ignore .streamlit/secrets.toml
```
Should return: `.streamlit/secrets.toml`

### Check what's tracked by git:
```bash
git ls-files | grep secrets
```
Should return: **nothing** (secrets.toml should not appear)

### Verify your local setup:
```bash
# Check if file exists locally
ls .streamlit/secrets.toml

# View contents (be careful - contains your key!)
cat .streamlit/secrets.toml  # Linux/Mac
type .streamlit\secrets.toml  # Windows
```

## Current Status

✅ **Your repository is safe:**
- `.streamlit/secrets.toml` is in `.gitignore`
- API keys are NOT in GitHub
- Your local secrets file exists and works

✅ **For Streamlit Cloud:**
- Add the key through Streamlit Cloud's Secrets interface
- NOT through GitHub

## Quick Reference

| Location | Where to Add Key | How |
|----------|-----------------|-----|
| **Local Development** | `.streamlit/secrets.toml` | Create file on your computer |
| **Streamlit Cloud** | Streamlit Cloud Secrets | Via share.streamlit.io interface |
| **GitHub** | ❌ **NEVER** | Never commit API keys |

## Need Help?

- **Local setup**: See `NEWS_API_SETUP.md`
- **Streamlit Cloud**: See `STREAMLIT_CLOUD_SETUP.md`
- **Quick Start**: See `QUICK_START.md`

## Your API Key

Your NewsAPI key: `d11ec4ba9c7c46ddba805549bff4c969`

**Keep it secret!** Only use it in:
- `.streamlit/secrets.toml` (local)
- Streamlit Cloud Secrets (deployed app)

