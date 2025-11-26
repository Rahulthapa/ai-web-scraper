# Render Deployment Setup

## Adding Supabase Environment Variables in Render

### Step 1: Go to Your Render Dashboard
1. Log in to [render.com](https://render.com)
2. Navigate to your service: `ai-web-scraper-7ctv`

### Step 2: Add Environment Variables
1. Click on your service name
2. Go to the **Environment** tab (in the left sidebar)
3. Click **Add Environment Variable**
4. Add the following two variables:

**Variable 1:**
- **Key**: `SUPABASE_URL`
- **Value**: `https://owfemagjnosxofmditfw.supabase.co`

**Variable 2:**
- **Key**: `SUPABASE_ANON_KEY`
- **Value**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im93ZmVtYWdqbm9zeG9mbWRpdGZ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQxNzQxNjgsImV4cCI6MjA3OTc1MDE2OH0.5OwRWkw8NhJ5DqQscPJoNLuDe8TJ5xqp5TBC9BWaW6g`

### Step 3: Save and Redeploy
1. Click **Save Changes**
2. Render will automatically trigger a new deployment
3. Wait for the deployment to complete (usually 2-3 minutes)

### Step 4: Verify Setup
After deployment, test the health endpoint:
```bash
curl https://ai-web-scraper-7ctv.onrender.com/health
```

You should see:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Important Security Notes

⚠️ **Never commit credentials to your code repository!**

- Environment variables in Render are encrypted and secure
- They are only accessible to your service
- They are not visible in logs or code

## Next Steps

After adding the environment variables:
1. ✅ Supabase connection will be established
2. ✅ You can create scraping jobs via the API
3. ✅ Jobs and results will be stored in Supabase
4. ✅ The web interface will be fully functional

## Setting Up Supabase Tables

Make sure you've created the required tables in your Supabase project. Run this SQL in your Supabase SQL Editor:

```sql
-- Create scrape_jobs table
CREATE TABLE scrape_jobs (
  id UUID PRIMARY KEY,
  url TEXT NOT NULL,
  status TEXT NOT NULL,
  filters JSONB,
  ai_prompt TEXT,
  export_format TEXT DEFAULT 'json',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  error TEXT
);

-- Create scrape_results table
CREATE TABLE scrape_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES scrape_jobs(id) ON DELETE CASCADE,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_scrape_results_job_id ON scrape_results(job_id);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
```

