# Setup Guide

## Supabase Configuration

The application requires Supabase for storing scraping jobs and results. Follow these steps to set up your Supabase credentials:

### Step 1: Create a Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click "New Project"
4. Fill in your project details:
   - **Name**: Choose a project name
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose the closest region
5. Click "Create new project"

### Step 2: Get Your Credentials

Once your project is created:

1. Go to **Settings** → **API** in your Supabase dashboard
2. You'll find:
   - **Project URL** (this is your `SUPABASE_URL`)
   - **anon/public key** (this is your `SUPABASE_ANON_KEY`)

### Step 3: Set Up Database Tables

Run these SQL commands in your Supabase SQL Editor (SQL Editor → New Query):

```sql
-- Create scrape_jobs table
CREATE TABLE scrape_jobs (
  id UUID PRIMARY KEY,
  url TEXT,  -- Made nullable for crawl mode
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

-- Create scrape_results table
CREATE TABLE scrape_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES scrape_jobs(id) ON DELETE CASCADE,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX idx_scrape_results_job_id ON scrape_results(job_id);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
```

### Step 4: Set Environment Variables

#### Option A: Local Development (.env file)

Create a `.env` file in the project root:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
```

**Important**: The `.env` file is already in `.gitignore`, so it won't be committed to git.

#### Option B: System Environment Variables

**Windows (PowerShell):**
```powershell
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_ANON_KEY="your-anon-key-here"
```

**Windows (Command Prompt):**
```cmd
set SUPABASE_URL=https://your-project-id.supabase.co
set SUPABASE_ANON_KEY=your-anon-key-here
```

**Linux/Mac:**
```bash
export SUPABASE_URL=https://your-project-id.supabase.co
export SUPABASE_ANON_KEY=your-anon-key-here
```

#### Option C: Render Deployment

1. Go to your Render dashboard
2. Select your service
3. Go to **Environment** tab
4. Add the following environment variables:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_ANON_KEY` = your Supabase anon key
5. Save and redeploy

### Step 5: Verify Setup

1. Start your application:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Check the health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

   You should see:
   ```json
   {
     "status": "healthy",
     "database": "connected"
   }
   ```

   If you see `"database": "not_configured"`, check that your environment variables are set correctly.

### Troubleshooting

**Error: "Supabase credentials not found in environment"**

- Make sure you've created a `.env` file in the project root
- Verify the variable names are exactly `SUPABASE_URL` and `SUPABASE_ANON_KEY`
- Restart your application after setting environment variables
- For Render: Make sure environment variables are set in the dashboard and the service has been redeployed

**Error: "Failed to create job" or database connection errors**

- Verify your Supabase project is active
- Check that the tables were created correctly
- Ensure your `SUPABASE_ANON_KEY` is the anon/public key (not the service_role key)
- Check Supabase logs in the dashboard for any errors

**Tables not found**

- Make sure you ran the SQL commands in Step 3
- Verify you're using the correct Supabase project
- Check the table names match exactly: `scrape_jobs` and `scrape_results`

### Security Notes

- The `SUPABASE_ANON_KEY` is safe to use in frontend/client code
- Never commit your `.env` file to version control
- For production, use environment variables in your deployment platform
- Consider setting up Row Level Security (RLS) policies in Supabase for production use

