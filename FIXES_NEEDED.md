# What Needs to Be Fixed

## ✅ Code Issues (FIXED)

1. **Worker.py bug** - Fixed variable reference issue in AI filtering
2. **Async scraper** - Already using httpx for async requests
3. **Crawler integration** - Properly integrated

## 🔴 Critical: Database Migration (MUST DO)

### Step 1: Run Migration SQL

Go to Supabase SQL Editor and run:

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

### Step 2: Refresh Schema Cache (CRITICAL!)

1. Go to: https://supabase.com/dashboard/project/owfemagjnosxofmditfw
2. Click **Settings** → **API**
3. Scroll to **Schema Cache** section
4. Click **"Clear Cache"** or **"Reload Schema"**
5. Wait 30-60 seconds

### Step 3: Verify

Run this query:
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'scrape_jobs'
AND column_name IN ('crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript');
```

Should return 6 rows.

## ⚠️ Optional: Test Single Page Mode First

While fixing the migration, you can test with single-page mode:

1. **Don't enable "Web Crawl Mode"**
2. Just enter a URL like `https://example.com`
3. Click "Start Scraping"
4. This should work without the new columns

## 📋 Summary

**To make it work:**

1. ✅ Code is fixed
2. 🔴 **Run database migration** (see Step 1 above)
3. 🔴 **Refresh schema cache** (see Step 2 above) - THIS IS CRITICAL!
4. ✅ Test with single page first
5. ✅ Then test crawl mode

## 🐛 If Still Not Working

1. Check Supabase logs for errors
2. Verify API key permissions
3. Check RLS (Row Level Security) policies
4. Try the verification query in `verify_migration.sql`

