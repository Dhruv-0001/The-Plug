# The Plug - Streamlit Cloud Deployment Guide

This guide will walk you through deploying your video analysis app to Streamlit Community Cloud.

## 🚨 Important Cloud Limitations & Solutions

### Video Download Restrictions
Streamlit Cloud has several limitations that affect video downloading:

1. **Network Restrictions**: Limited outbound connections may block some video downloads
2. **File Size Limits**: Large videos (>50MB) may cause timeouts or memory issues
3. **Processing Time**: Long videos may exceed processing time limits
4. **Temporary Storage**: Limited disk space for temporary files

### Our Solutions
- **File Size Limits**: Automatically limit downloads to <50MB in cloud environment
- **Timeout Handling**: Reduced retry attempts and shorter timeouts
- **Cloud Detection**: App automatically detects cloud environment and adjusts behavior
- **Alternative Upload**: Users can upload video files directly as backup

## 📋 Prerequisites

Before deploying, ensure you have:

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Google AI API Key**: For Gemini AI functionality
3. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## 🚀 Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Create GitHub Repository**:
   ```bash
   # If you haven't already, initialize git and push to GitHub
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Verify Required Files**:
   Ensure these files are in your repository root:
   - `app.py` (or `app_cloud.py` for enhanced cloud version)
   - `requirements.txt`
   - `.streamlit/config.toml`
   - `.streamlit/secrets.toml` (template only - don't commit actual secrets!)

### Step 2: Set Up Streamlit Cloud

1. **Sign In**: Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub

2. **Create New App**:
   - Click "New app"
   - Choose your repository
   - Select branch (usually `main`)
   - Set main file path: `app.py` (or `app_cloud.py`)
   - Click "Deploy!"

### Step 3: Configure Secrets

1. **In Streamlit Cloud Dashboard**:
   - Go to your app settings
   - Click "Secrets" tab
   - Add your secrets in TOML format:

   ```toml
   GOOGLE_API_KEY = "your_actual_google_api_key_here"
   ```

2. **Get Google AI API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy and paste it into Streamlit secrets

### Step 4: Monitor Deployment

1. **Check Build Logs**: Monitor the deployment logs for any errors
2. **Test Functionality**: Once deployed, test both file upload and URL download features
3. **Debug if Needed**: Check logs for any issues and adjust accordingly

## 📁 File Structure

Your repository should look like this:

```
your-repo/
├── app.py                    # Main Streamlit app
├── app_cloud.py             # Enhanced cloud version (optional)
├── requirements.txt         # Python dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # Secrets template (don't commit real secrets!)
├── DEPLOYMENT_GUIDE.md      # This guide
└── README.md               # Project documentation
```

## 🔧 Configuration Files Explained

### `requirements.txt`
```txt
streamlit>=1.28.0
phidata>=2.4.0
google-generativeai>=0.3.0
python-dotenv>=1.0.0
requests>=2.31.0
duckduckgo-search>=4.0.0
yt-dlp>=2023.12.30
Pillow>=10.0.0
```

### `.streamlit/config.toml`
```toml
[global]
# Streamlit configuration for cloud deployment

[server]
maxUploadSize = 500
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

### Streamlit Cloud Secrets (in dashboard)
```toml
GOOGLE_API_KEY = "your_google_api_key_here"
```

## 🐛 Troubleshooting

### Common Issues and Solutions

1. **Video Download Fails**:
   - **Issue**: yt-dlp blocked or times out
   - **Solution**: Use smaller videos (<10MB) or upload files directly
   - **Workaround**: The app automatically detects cloud environment and adjusts limits

2. **API Key Not Found**:
   - **Issue**: Google API key not configured
   - **Solution**: Add `GOOGLE_API_KEY` to Streamlit Cloud secrets

3. **Module Not Found**:
   - **Issue**: Missing dependencies
   - **Solution**: Check `requirements.txt` and ensure all packages are listed with versions

4. **Memory/Timeout Issues**:
   - **Issue**: Large videos cause crashes
   - **Solution**: App automatically limits file sizes in cloud environment

5. **Build Fails**:
   - **Issue**: Dependencies conflict or installation fails
   - **Solution**: Check build logs and update `requirements.txt` with compatible versions

### Debug Tips

1. **Check Logs**: Always check the deployment logs in Streamlit Cloud dashboard
2. **Test Locally First**: Run `streamlit run app.py` locally to catch issues early
3. **Use Cloud Version**: Consider using `app_cloud.py` for better cloud compatibility
4. **Monitor Resource Usage**: Watch for memory and processing time limits

## 🎯 Performance Optimization for Cloud

### Recommended Settings for Cloud Deployment

1. **Use `app_cloud.py`**: Enhanced version with better cloud compatibility
2. **File Size Limits**: 
   - Local: 200MB max
   - Cloud: 50MB max (automatically enforced)
3. **Timeout Settings**:
   - Local: 5 minutes processing
   - Cloud: 2 minutes processing
4. **Retry Logic**:
   - Local: 3 attempts with backoff
   - Cloud: 1 attempt, fail fast

### User Experience in Cloud

- **File Upload**: Always works, preferred method
- **URL Download**: Works for smaller videos, may fail for large ones
- **Processing**: Faster for shorter videos (<5 minutes)
- **Storage**: Temporary files automatically cleaned up

## 🔄 Updating Your Deployment

To update your deployed app:

1. **Make Changes**: Update your code locally
2. **Push to GitHub**: 
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. **Auto-Deploy**: Streamlit Cloud automatically redeploys when you push to the connected branch

## 📞 Support and Resources

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Google AI Docs**: [ai.google.dev](https://ai.google.dev)

## 🎉 Post-Deployment Checklist

- [ ] App deploys successfully
- [ ] File upload works
- [ ] URL download works (for small videos)
- [ ] Chat functionality works
- [ ] API key is configured
- [ ] No console errors
- [ ] Mobile-friendly interface
- [ ] Share your app URL!

---

## 🚀 Ready to Deploy?

1. Push your code to GitHub
2. Sign in to Streamlit Cloud
3. Create new app
4. Add your Google API key to secrets
5. Deploy and enjoy!

Your app will be available at: `https://your-app-name.streamlit.app`

**Happy Deploying! 🎊**
