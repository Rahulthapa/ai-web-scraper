# Fix Supabase Schema Cache Error

## The Problem
Supabase caches the database schema. After adding new columns, you need to refresh the cache.

## Solution Steps

### Step 1: Run the Migration SQL

Go to Supabase SQL Editor and run:

```sql
-- Add new columns for web crawling functionality
ALTER TABLE scrape_jobs 
ADD COLUMN IF NOT EXISTS crawl_mode BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS search_query TEXT,
ADD COLUMN IF NOT EXISTS max_pages INTEGER DEFAULT 10,
ADD COLUMN IF NOT EXISTS max_depth INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS same_domain BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS use_javascript BOOLEAN DEFAULT FALSE;

-- Make url nullable since it's optional in crawl mode
ALTER TABLE scrape_jobs 
ALTER COLUMN url DROP NOT NULL;
```

### Step 2: Refresh Schema Cache

**Option A: Via Supabase Dashboard**
1. Go to **Settings** → **API**
2. Scroll down to **Schema Cache**
3. Click **"Clear Cache"** or **"Refresh Schema"**

**Option B: Via SQL (if available)**
```sql
-- This might not work depending on your Supabase plan
NOTIFY pgrst, 'reload schema';
```

**Option C: Restart Supabase (if self-hosted)**
- If you're self-hosting, restart the PostgREST service

### Step 3: Verify Columns Exist

Run this query to verify:

```sql
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
ORDER BY ordinal_position;
```

You should see:
- `crawl_mode` (boolean)
- `search_query` (text)
- `max_pages` (integer)
- `max_depth` (integer)
- `same_domain` (boolean)
- `use_javascript` (boolean)

### Step 4: Wait a Few Seconds

After clearing the cache, wait 10-30 seconds for the schema to refresh.

### Step 5: Test Again

Try creating a job again through the frontend or API.

## Alternative: Recreate Table (Last Resort)

If the above doesn't work, you can recreate the table (⚠️ **WARNING: This deletes all existing jobs**):

```sql
-- BACKUP FIRST! This deletes all data
DROP TABLE IF EXISTS scrape_results CASCADE;
DROP TABLE IF EXISTS scrape_jobs CASCADE;

-- Recreate with all columns
CREATE TABLE scrape_jobs (
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

CREATE TABLE scrape_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES scrape_jobs(id) ON DELETE CASCADE,
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_scrape_results_job_id ON scrape_results(job_id);
CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
```

## Still Not Working?

1. **Check RLS Policies**: Make sure Row Level Security allows inserts
2. **Check API Key**: Ensure you're using the correct anon key
3. **Check Table Permissions**: Verify the anon role has INSERT permission
4. **Contact Support**: If nothing works, contact Supabase support

