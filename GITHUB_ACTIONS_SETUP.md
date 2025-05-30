# GitHub Actions Setup Guide

This guide explains how to set up the automated Indian News Pipeline that runs daily at 9:00 AM IST.

## 🚀 What the Workflow Does

The GitHub Actions workflow (`indian-news-pipeline.yml`) automatically:

1. **Runs Daily**: Executes at 9:00 AM IST (3:30 UTC) every day
2. **Fetches News**: Gets top 3 Indian news articles
3. **Generates Tweets**: Uses Gemini AI to create funny, informational tweets
4. **Stores Data**: Saves results to your Supabase database
5. **Logs Results**: Updates `logs/pipeline.log` with execution details
6. **Commits Changes**: Automatically commits log updates to the repository

## 🔐 Required GitHub Secrets

You need to add these secrets to your GitHub repository:

### How to Add Secrets:
1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret below:

### Required Secrets:

```
GEMINI_API_KEY
├── Description: Google Gemini AI API key for tweet generation
├── Value: Your Gemini API key from Google AI Studio
└── Example: AIza...

NEWS_API_KEY
├── Description: NewsAPI.org API key for fetching Indian news
├── Value: Your NewsAPI key (free tier available)
└── Example: 1234567890abcdef...

SUPARBASE_DATA_PIP_PROJECT_URL
├── Description: Your Supabase project URL
├── Value: Your Supabase project URL
└── Example: https://abcdefgh.supabase.co

SUPABASE_DATA_PIP_KEY
├── Description: Your Supabase service key
├── Value: Your Supabase anon/public key
└── Example: eyJhbGciOiJIUzI1NiIs...
```

## ⏰ Schedule Details

- **Daily Execution**: 9:00 AM IST (3:30 UTC)
- **Timezone**: Coordinated Universal Time (UTC)
- **Frequency**: Once per day, every day
- **Manual Trigger**: Available via "Actions" tab → "Run workflow"

## 📝 Log File Structure

The workflow creates/updates `logs/pipeline.log` with:

```
[YYYY-MM-DD HH:MM:SS UTC] ✅ Indian News Pipeline completed successfully!
[YYYY-MM-DD HH:MM:SS UTC] Pipeline execution finished with success status
[YYYY-MM-DD HH:MM:SS UTC] Generated AI tweet: "..."
[YYYY-MM-DD HH:MM:SS UTC] Data stored successfully in Supabase

```

## 🔄 Auto-Commit Process

After each run, the workflow:
1. Updates the log file with execution results
2. Commits changes with message: `📰 Auto-update: Indian News Pipeline run at [timestamp]`
3. Pushes changes back to the repository

## 🎯 Workflow Triggers

### Automatic (Scheduled):
- **Daily at 9:00 AM IST**
- Uses cron expression: `'30 3 * * *'`

### Manual:
- Go to **Actions** tab in GitHub
- Select **Indian News Pipeline**
- Click **Run workflow**

## 📊 Monitoring

### View Workflow Status:
1. Go to **Actions** tab in your repository
2. Click on **Indian News Pipeline**
3. View execution history and logs

### Download Logs:
- Each run creates an artifact with detailed logs
- Available for 30 days after execution
- Download from the workflow run page

## 🛠️ Troubleshooting

### Common Issues:

**Workflow doesn't run:**
- Check if all required secrets are added
- Verify secret names match exactly
- Ensure repository has Actions enabled

**Pipeline fails:**
- Check API key validity (Gemini, NewsAPI)
- Verify Supabase credentials
- Review workflow logs for specific errors

**No commits showing:**
- Workflow only commits if there are log changes
- Check workflow permissions for repository write access

### Debug Steps:
1. Run workflow manually to test
2. Check **Actions** tab for detailed error logs
3. Verify all environment variables are set correctly
4. Test pipeline locally first: `python src/indian_news_pipeline.py`

## 🎉 Success Indicators

When working correctly, you'll see:
- ✅ Green checkmarks in Actions tab
- Daily commits with pipeline run messages
- Updated `logs/pipeline.log` file
- New records in your Supabase `news_daily` table
- Fresh Indian news with AI-generated tweets

## 📈 Next Steps

After setup:
1. **Test manually** by running the workflow once
2. **Monitor first few runs** to ensure stability
3. **Check Supabase data** to verify news storage
4. **Review generated tweets** for quality and humor
5. **Enjoy automated daily Indian news updates!** 🇮🇳

---

*The workflow will continue running daily, keeping your Supabase database updated with the latest Indian news and AI-generated tweets!* 