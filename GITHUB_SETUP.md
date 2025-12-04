# GitHub Setup Instructions

## After Creating Your GitHub Repository

Once you've created your repository on GitHub, run these commands (replace `YOUR_USERNAME` and `REPO_NAME` with your actual values):

```bash
# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Example

If your repository URL is: `https://github.com/johndoe/nasdaq-analytics-dashboard.git`

```bash
git remote add origin https://github.com/johndoe/nasdaq-analytics-dashboard.git
git branch -M main
git push -u origin main
```

## Authentication

If prompted for authentication:
- **Personal Access Token**: Use a GitHub Personal Access Token (not your password)
- Create one at: https://github.com/settings/tokens
- Select `repo` scope for full repository access

## Verify

After pushing, visit your repository on GitHub to verify all files are uploaded correctly.

## Important Notes

✅ **Protected**: Your `.streamlit/secrets.toml` file with the API key is automatically excluded (via .gitignore)

✅ **Safe to Push**: All sensitive information is protected

✅ **Ready to Share**: The repository is ready to be shared publicly or privately

