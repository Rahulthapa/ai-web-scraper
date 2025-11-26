-- Migration: Add web crawling columns to scrape_jobs table
-- Run this in your Supabase SQL Editor

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

-- Add comments for documentation
COMMENT ON COLUMN scrape_jobs.crawl_mode IS 'Enable web crawling mode to discover and scrape multiple pages';
COMMENT ON COLUMN scrape_jobs.search_query IS 'Search query for finding pages to crawl';
COMMENT ON COLUMN scrape_jobs.max_pages IS 'Maximum number of pages to crawl';
COMMENT ON COLUMN scrape_jobs.max_depth IS 'Maximum depth of links to follow';
COMMENT ON COLUMN scrape_jobs.same_domain IS 'Only crawl pages on the same domain';
COMMENT ON COLUMN scrape_jobs.use_javascript IS 'Use Playwright for JavaScript-rendered pages';

