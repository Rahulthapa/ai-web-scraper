# Database Migration Instructions

## Issue
The `extract_individual_pages` column is missing from the `scrape_jobs` table in Supabase.

## Solution

### Step 1: Run the Migration SQL

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Open or create a new query
4. Copy and paste the contents of `database_migration.sql`
5. Click **Run** to execute the migration

The migration will:
- Add the `extract_individual_pages` column (if it doesn't exist)
- Set the default value to `TRUE` (enabled by default)
- Add documentation comments

### Step 2: Refresh Schema Cache

After running the migration:

1. In Supabase Dashboard, go to **Settings** → **API**
2. Scroll down to **Schema Cache**
3. Click **Refresh** or **Reload Schema**

Alternatively, you can run this SQL command (if you have permissions):
```sql
NOTIFY pgrst, 'reload schema';
```

### Step 3: Verify the Migration

Run the verification script in `verify_migration.sql` to confirm:
- The column was added successfully
- All expected columns exist
- No columns are missing

### Quick Migration SQL (Copy-Paste Ready)

```sql
-- Add extract_individual_pages column
ALTER TABLE scrape_jobs 
ADD COLUMN IF NOT EXISTS extract_individual_pages BOOLEAN DEFAULT TRUE;

-- Add comment
COMMENT ON COLUMN scrape_jobs.extract_individual_pages IS 'Extract data from individual restaurant pages (default: true for restaurant listings)';

-- Verify it was added
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
AND column_name = 'extract_individual_pages';
```

## What This Column Does

- **Purpose**: Controls whether to extract data from individual restaurant pages when scraping listing pages
- **Default**: `TRUE` (enabled by default)
- **When Used**: 
  - Restaurant listing pages (Yelp, OpenTable, etc.)
  - Restaurant search queries
  - Any page that contains multiple restaurant links

## After Migration

Once the migration is complete:
1. The application will automatically use the new column
2. Existing jobs will use the default value (`TRUE`)
3. New jobs can explicitly set `extract_individual_pages: false` to disable it

## Troubleshooting

If you still see errors after migration:

1. **Check column exists**:
   ```sql
   SELECT column_name FROM information_schema.columns 
   WHERE table_name = 'scrape_jobs' AND column_name = 'extract_individual_pages';
   ```

2. **Refresh schema cache** in Supabase Dashboard

3. **Restart your application** to reload database connections

4. **Check default value**:
   ```sql
   SELECT column_default FROM information_schema.columns 
   WHERE table_name = 'scrape_jobs' AND column_name = 'extract_individual_pages';
   ```
   Should return: `true`

