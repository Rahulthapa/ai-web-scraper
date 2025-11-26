# Database Migration Guide

## Adding Web Crawling Support

If you already have the `scrape_jobs` table set up, you need to run a migration to add the new columns for web crawling functionality.

### Quick Migration

Run this SQL in your Supabase SQL Editor:

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

### Step-by-Step Instructions

1. **Go to Supabase Dashboard**
   - Navigate to: https://supabase.com/dashboard
   - Select your project

2. **Open SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New query"

3. **Run the Migration**
   - Copy and paste the SQL from `database_migration.sql`
   - Click "Run" or press `Ctrl+Enter` (Windows) / `Cmd+Enter` (Mac)

4. **Verify the Migration**
   - Go to "Table Editor"
   - Select `scrape_jobs` table
   - You should see the new columns:
     - `crawl_mode`
     - `search_query`
     - `max_pages`
     - `max_depth`
     - `same_domain`
     - `use_javascript`

### If You're Setting Up Fresh

If you haven't created the tables yet, use the updated SQL in `SETUP.md` which includes all the new columns.

### Troubleshooting

**Error: "column already exists"**
- This means the column was already added. The `IF NOT EXISTS` clause should prevent this, but if you see this error, you can safely ignore it.

**Error: "cannot alter column"**
- If you get an error about altering the `url` column, it might already be nullable. You can skip that line.

**Verify Migration Success**
```sql
-- Check if columns exist
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
ORDER BY ordinal_position;
```

You should see all the new columns listed.

