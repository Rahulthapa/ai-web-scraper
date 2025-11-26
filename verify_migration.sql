-- Verification Script: Check if migration was successful
-- Run this FIRST to see what columns exist

-- Check all columns in scrape_jobs table
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
ORDER BY ordinal_position;

-- Specifically check for new columns
SELECT 
    CASE 
        WHEN COUNT(*) = 6 THEN '✅ All new columns exist'
        ELSE '❌ Missing columns: ' || (6 - COUNT(*))::text || ' columns missing'
    END as migration_status
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
AND column_name IN ('crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript');

-- List which columns are missing
SELECT 
    'Missing: ' || unnest(ARRAY['crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript']) as missing_column
WHERE NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'scrape_jobs'
    AND column_name = unnest(ARRAY['crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript'])
);

