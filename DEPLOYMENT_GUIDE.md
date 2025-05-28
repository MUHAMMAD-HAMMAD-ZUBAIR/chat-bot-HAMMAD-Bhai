# 🚀 Deployment Guide - HAMMAD Bhai's Chatbot

## Quick Vercel Deployment (Recommended)

### Method 1: Direct Vercel Import (Easiest)
1. Go to [vercel.com](https://vercel.com)
2. Sign in with your GitHub account
3. Click "New Project"
4. Import this repository: `https://github.com/MUHAMMAD-HAMMAD-ZUBAIR/chat-bot-Hammad-Bhai.git`
5. Vercel will automatically detect it's a Python app
6. Click "Deploy"
7. Done! Your app will be live in minutes

### Method 2: Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from your project directory
vercel

# For production deployment
vercel --prod
```

## Environment Variables Setup

If your app needs API keys, add them in Vercel dashboard:
1. Go to your project in Vercel dashboard
2. Settings → Environment Variables
3. Add your variables:
   - `GOOGLE_API_KEY` (if using Gemini API)
   - Any other API keys your app needs

## GitHub Actions Auto-Deployment (Optional)

To enable automatic deployment on every push:

1. Get your Vercel tokens:
   ```bash
   # Install Vercel CLI if not already installed
   npm i -g vercel
   
   # Login and get tokens
   vercel login
   vercel link  # Link your project
   ```

2. Add these secrets to your GitHub repository:
   - Go to GitHub repo → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VERCEL_TOKEN`: Your Vercel token
     - `VERCEL_ORG_ID`: Your Vercel organization ID
     - `VERCEL_PROJECT_ID`: Your Vercel project ID

3. Uncomment the deploy job in `.github/workflows/deploy.yml`

## Alternative Deployment Options

### Heroku
1. Create `Procfile`:
   ```
   web: python app.py
   ```
2. Deploy via Heroku CLI or GitHub integration

### Railway
1. Connect your GitHub repo to Railway
2. Deploy automatically

### PythonAnywhere
1. Upload your code
2. Configure WSGI file
3. Set up web app

## Troubleshooting

### Common Issues:
1. **Port Issues**: Make sure your app uses `PORT` environment variable
2. **Dependencies**: Ensure all dependencies are in `requirements.txt`
3. **Python Version**: Check `runtime.txt` for correct Python version

### Vercel Specific:
- Vercel automatically detects Python apps
- Uses `api/` folder for serverless functions
- Main app should be in `api/index.py` or `api/app.py`

## Support

If you face any deployment issues:
1. Check Vercel deployment logs
2. Ensure all files are committed to GitHub
3. Verify environment variables are set correctly

---
**Created by HAMMAD bhai** 🚀
