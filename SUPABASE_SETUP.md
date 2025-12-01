# Supabase Database Setup Guide

## Quick Setup

1. **Go to Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"

3. **Run the Complete Setup Script**
   - Copy the entire contents of `supabase_setup.sql`
   - Paste into the SQL Editor
   - Click "Run" or press `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)

4. **Refresh Schema Cache (CRITICAL)**
   - Go to **Settings** → **API**
   - Scroll down to **Schema Cache**
   - Click **"Clear Cache"** or **"Refresh Schema"**
   - Wait 30-60 seconds

5. **Verify Setup**
   - Go to **Table Editor**
   - You should see:
     - `scrape_jobs` table
     - `scrape_results` table
   - Check that `scrape_jobs` has all columns including:
     - `crawl_mode`
     - `search_query`
     - `max_pages`
     - `max_depth`
     - `same_domain`
     - `use_javascript`

## What the Script Does

The `supabase_setup.sql` script:

1. ✅ Creates `scrape_jobs` table (if it doesn't exist)
2. ✅ Creates `scrape_results` table (if it doesn't exist)
3. ✅ Adds all migration columns safely (won't fail if they exist)
4. ✅ Makes `url` column nullable
5. ✅ Creates indexes for performance
6. ✅ Adds documentation comments
7. ✅ Verifies the setup

## Table Structure

### scrape_jobs
- `id` (UUID, Primary Key)
- `url` (TEXT, Nullable) - Optional for keyword search mode
- `status` (TEXT, Required) - pending, running, completed, failed
- `filters` (JSONB) - Additional filters
- `ai_prompt` (TEXT) - AI filtering prompt
- `export_format` (TEXT) - json, csv, excel
- `crawl_mode` (BOOLEAN) - Enable crawling
- `search_query` (TEXT) - Search keywords
- `max_pages` (INTEGER) - Max pages to scrape
- `max_depth` (INTEGER) - Max crawl depth
- `same_domain` (BOOLEAN) - Same domain only
- `use_javascript` (BOOLEAN) - Use Playwright
- `created_at` (TIMESTAMP)
- `completed_at` (TIMESTAMP)
- `error` (TEXT) - Error message if failed

### scrape_results
- `id` (UUID, Primary Key)
- `job_id` (UUID, Foreign Key) - References scrape_jobs
- `data` (JSONB, Required) - Scraped data
- `created_at` (TIMESTAMP)

## Troubleshooting

### Error: "column already exists"
- This is safe to ignore - the script uses `IF NOT EXISTS` checks
- The script will continue and add only missing columns

### Error: "relation already exists"
- Tables already exist - this is fine
- The script will only add missing columns

### Still getting "column not found" errors
- **You must refresh the schema cache!**
- Go to Settings → API → Schema Cache → Clear Cache
- Wait 30-60 seconds
- Try your operation again

### Verify Columns Exist
Run this query to check:

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
ORDER BY column_name;
```

You should see all columns including:
- crawl_mode
- search_query
- max_pages
- max_depth
- same_domain
- use_javascript

## Row Level Security (RLS)

If you're using Row Level Security, make sure to set up policies:

```sql
-- Allow anonymous users to insert jobs
CREATE POLICY "Allow anonymous insert" ON scrape_jobs
FOR INSERT TO anon
WITH CHECK (true);

-- Allow anonymous users to read their own jobs
CREATE POLICY "Allow anonymous read" ON scrape_jobs
FOR SELECT TO anon
USING (true);

-- Allow anonymous users to update jobs
CREATE POLICY "Allow anonymous update" ON scrape_jobs
FOR UPDATE TO anon
USING (true);

-- Similar policies for scrape_results
CREATE POLICY "Allow anonymous insert results" ON scrape_results
FOR INSERT TO anon
WITH CHECK (true);

CREATE POLICY "Allow anonymous read results" ON scrape_results
FOR SELECT TO anon
USING (true);
```

## Next Steps

After running the setup:

1. ✅ Verify tables exist in Table Editor
2. ✅ Refresh schema cache
3. ✅ Test creating a job via API
4. ✅ Check that all columns are accessible

Your database is now ready for the web scraper!

