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
        WHEN COUNT(*) = 7 THEN '✅ All new columns exist'
        ELSE '❌ Missing columns: ' || (7 - COUNT(*))::text || ' columns missing'
    END as migration_status
FROM information_schema.columns
WHERE table_name = 'scrape_jobs'
AND column_name IN ('crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript', 'extract_individual_pages');

-- List which columns are missing (using a simpler approach)
WITH expected_columns AS (
    SELECT unnest(ARRAY['crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript', 'extract_individual_pages']) AS column_name
),
existing_columns AS (
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'scrape_jobs'
    AND column_name IN ('crawl_mode', 'search_query', 'max_pages', 'max_depth', 'same_domain', 'use_javascript', 'extract_individual_pages')
)
SELECT 
    'Missing: ' || ec.column_name as missing_column
FROM expected_columns ec
LEFT JOIN existing_columns ex ON ec.column_name = ex.column_name
WHERE ex.column_name IS NULL;

