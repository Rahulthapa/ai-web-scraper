# 🚀 Deploying AI Web Scraper on Render

This guide walks you through deploying the AI Web Scraper on Render with GitHub integration.

## Prerequisites

1. **GitHub Account** - Your code should be pushed to GitHub
2. **Render Account** - Sign up at https://render.com (free tier available)
3. **Supabase Account** - Sign up at https://supabase.com (free tier available)
4. **Google AI API Key** (FREE) - For AI-powered data extraction

---

## Step 1: Set Up Supabase Database

### 1.1 Create a Supabase Project
1. Go to https://supabase.com and sign in
2. Click **New Project**
3. Name it `ai-web-scraper`
4. Choose a strong database password
5. Select your region
6. Click **Create new project**

### 1.2 Create Database Tables
1. Go to **SQL Editor** in Supabase dashboard
2. Run this SQL:

```sql
-- Create jobs table
CREATE TABLE IF NOT EXISTS scrape_jobs (
  id UUID PRIMARY KEY,
  url TEXT,
  status TEXT NOT NULL,
  filters JSONB,
  ai_prompt TEXT,
  export_format TEXT DEFAULT 'json',
  crawl_mode BOOLEAN DEFAULT FALSE,
  search_query TEXT,
  max_pages INTEGER DEFAULT 10,
  max_depth INTEGER DEFAULT 2,
  same_domain BOOLEAN DEFAULT TRUE,
  use_javascript BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  error TEXT
);

-- Create results table
CREATE TABLE IF NOT EXISTS scrape_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES scrape_jobs(id) ON DELETE CASCADE,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE scrape_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE scrape_results ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (adjust for production)
CREATE POLICY "Allow all on scrape_jobs" ON scrape_jobs FOR ALL USING (true);
CREATE POLICY "Allow all on scrape_results" ON scrape_results FOR ALL USING (true);
```

### 1.3 Get Your Supabase Credentials
1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (e.g., `https://xxxx.supabase.co`)
   - **anon public** key (under Project API keys)

---

## Step 2: Get Google Gemini API Key (FREE)

1. Go to https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Click **Create API Key**
4. Select **Create API key in new project**
5. Copy the API key

**Free Tier Limits:**
- 60 requests per minute
- 1,500 requests per day
- This is plenty for most scraping tasks!

---

## Step 3: Deploy on Render

### 3.1 Connect GitHub Repository
1. Go to https://render.com and sign in
2. Click **New** → **Web Service**
3. Connect your GitHub account if not already connected
4. Select your `ai-web-scraper` repository

### 3.2 Configure the Service
Use these settings:

| Setting | Value |
|---------|-------|
| **Name** | `ai-web-scraper` |
| **Region** | Choose closest to you |
| **Branch** | `main` (or your default branch) |
| **Runtime** | `Python 3` |
| **Build Command** | Leave as auto-detected from `render.yaml` |
| **Start Command** | Leave as auto-detected from `render.yaml` |
| **Plan** | Free |

### 3.3 Add Environment Variables
Click **Environment** and add these variables:

| Key | Value | Required |
|-----|-------|----------|
| `SUPABASE_URL` | Your Supabase project URL | ✅ Yes |
| `SUPABASE_ANON_KEY` | Your Supabase anon key | ✅ Yes |
| `GEMINI_API_KEY` | Your Google Gemini API key | ⭐ Recommended |
| `OPENAI_API_KEY` | Your OpenAI API key | Optional (if using OpenAI instead) |

### 3.4 Deploy
1. Click **Create Web Service**
2. Wait for the build to complete (5-10 minutes first time)
3. Once deployed, click the URL to access your app!

---

## Step 4: Verify Deployment

### Check Health Endpoint
Visit `https://your-app.onrender.com/health`

You should see:
```json
{
  "status": "ok",
  "timestamp": "2024-..."
}
```

### Check API Docs
Visit `https://your-app.onrender.com/docs` to see the interactive API documentation.

---

## How AI Extraction Works

The app supports **three modes** for AI-powered extraction:

### 1. Google Gemini (Recommended - FREE)
- Set `GEMINI_API_KEY` environment variable
- Uses Gemini 1.5 Flash model
- 60 requests/minute, 1500/day free

### 2. OpenAI GPT (Paid)
- Set `OPENAI_API_KEY` environment variable
- Uses GPT-3.5-turbo
- Costs ~$0.002 per request

### 3. Smart Extraction (No API)
- Works automatically if no API keys are set
- Uses pattern matching for:
  - Prices ($, €, £, ₹)
  - Email addresses
  - Phone numbers
  - Links and images
- Less intelligent but completely free

---

## Usage Examples

### Example 1: Extract Product Prices
1. Enter URL: `https://example-store.com/products`
2. AI Prompt: `Extract all product names and prices`
3. The AI will return structured data like:
```json
[
  {"name": "Product A", "price": "$29.99"},
  {"name": "Product B", "price": "$49.99"}
]
```

### Example 2: Extract Contact Info
1. Enter URL: `https://company.com/contact`
2. AI Prompt: `Extract all email addresses and phone numbers`
3. Result:
```json
[
  {"email": "contact@company.com", "phone": "+1-234-567-8900"}
]
```

### Example 3: Crawl Multiple Pages
1. Enable **Web Crawl Mode**
2. Enter search query: `python tutorials`
3. AI Prompt: `Extract article titles and summaries`
4. The crawler will find relevant pages and extract data from each

---

## Troubleshooting

### Build Fails
- Check Render logs for specific error
- Ensure all files are committed to GitHub
- Verify `render.yaml` is in the repository root

### Database Connection Error
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` are set correctly
- Check if database tables exist (run the SQL from Step 1.2)
- Ensure RLS policies allow access

### AI Not Working
- Check if `GEMINI_API_KEY` is set in Render environment variables
- Verify the API key is valid at https://aistudio.google.com
- Check Render logs for specific errors

### Slow Cold Starts (Free Tier)
- Free tier services spin down after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Upgrade to paid tier for always-on service

---

## Updating the App

1. Push changes to GitHub
2. Render automatically redeploys on push
3. Or manually trigger: **Dashboard** → **Manual Deploy** → **Deploy latest commit**

---

## Cost Summary

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Render** | 750 hours/month | Enough for continuous running |
| **Supabase** | 500MB database, 50K requests | Plenty for scraping |
| **Google Gemini** | 1500 requests/day | Very generous |
| **Total** | **$0/month** | All free tiers! |

---

## Need Help?

- Check Render logs: Dashboard → Logs
- Check Supabase logs: Dashboard → Logs
- API Documentation: `/docs` endpoint
- Health check: `/health` endpoint

