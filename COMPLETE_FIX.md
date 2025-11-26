# Complete Fix for Schema Cache Error

## The Problem
Supabase's PostgREST API caches the database schema. After adding columns, the cache must be refreshed.

## Step-by-Step Solution

### Step 1: Verify Migration Status

Run this in Supabase SQL Editor:

```sql
-- Check if columns exist
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'scrape_jobs'
AND column_name IN ('crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript');
```

**Expected Result**: You should see 6 rows (one for each column)

**If you see 0 rows**: The migration wasn't run. Go to Step 2.

**If you see 6 rows**: The columns exist, but the cache needs refreshing. Go to Step 3.

### Step 2: Run the Migration (If Columns Don't Exist)

```sql
-- Add new columns
ALTER TABLE scrape_jobs 
ADD COLUMN IF NOT EXISTS crawl_mode BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS search_query TEXT,
ADD COLUMN IF NOT EXISTS max_pages INTEGER DEFAULT 10,
ADD COLUMN IF NOT EXISTS max_depth INTEGER DEFAULT 2,
ADD COLUMN IF NOT EXISTS same_domain BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS use_javascript BOOLEAN DEFAULT FALSE;

-- Make url nullable
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'scrape_jobs' 
        AND column_name = 'url' 
        AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE scrape_jobs ALTER COLUMN url DROP NOT NULL;
    END IF;
END $$;
```

### Step 3: Refresh Schema Cache (CRITICAL!)

**Method 1: Via Dashboard (Recommended)**
1. Go to: https://supabase.com/dashboard/project/owfemagjnosxofmditfw
2. Click **Settings** (⚙️ icon) in left sidebar
3. Click **API**
4. Scroll down to find **Schema Cache** section
5. Click **"Clear Cache"** or **"Reload Schema"** button
6. Wait 30-60 seconds

**Method 2: Via SQL (May not work on managed Supabase)**
```sql
NOTIFY pgrst, 'reload schema';
```

**Method 3: Restart Service (If self-hosted)**
- Restart your PostgREST service

### Step 4: Verify Cache Refresh

After clearing cache, wait 30 seconds, then test creating a job again.

### Step 5: Alternative - Use Single Page Mode

If you need to use the scraper immediately while fixing the migration:

1. **Don't enable "Web Crawl Mode"** in the frontend
2. Use single-page scraping mode (just enter a URL)
3. This will work without the new columns

## Troubleshooting

### "Columns don't exist" after running migration

1. Check you're in the correct database/project
2. Verify you have permissions to alter tables
3. Check for any error messages in the SQL Editor
4. Try running each ALTER statement individually

### "Cache won't refresh"

1. Wait 2-3 minutes (sometimes takes time)
2. Try logging out and back into Supabase dashboard
3. Check Supabase status page for any issues
4. Contact Supabase support if persistent

### "Still getting error after all steps"

1. Verify columns exist: Run `verify_migration.sql`
2. Check API key: Ensure you're using the correct anon key
3. Check RLS policies: Make sure inserts are allowed
4. Try recreating the table (⚠️ deletes all data - backup first!)

## Quick Test

After completing steps, test with this API call:

```bash
curl -X POST https://ai-web-scraper-7ctv.onrender.com/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
```

Should return a job ID without errors.

## Still Stuck?

1. Run `verify_migration.sql` and share the results
2. Check Supabase logs for any errors
3. Verify your API key has the correct permissions
4. Consider using single-page mode as a temporary workaround

