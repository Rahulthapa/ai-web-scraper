# Troubleshooting Guide

## Webapp Not Working

### Issue: Frontend Not Built

If you see a JSON message instead of the web interface when visiting the root URL, the frontend hasn't been built.

**Solution:**

1. **Install Node.js** (if not already installed):
   - Download from: https://nodejs.org/
   - Install Node.js 18 or higher
   - Restart your terminal/command prompt after installation

2. **Build the frontend:**
   ```bash
   npm install
   npm run build
   ```

3. **Restart your server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Alternative: Development Mode

If you can't build the frontend, you can run it in development mode:

**Terminal 1 (Backend):**
```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```bash
npm install
npm run dev
```

Then access the app at `http://localhost:3000` (the frontend dev server will proxy API requests to the backend).

## Common Issues

### 1. "Could not find the 'crawl_mode' column" Error

**Solution:** Run the database migration:
1. Go to Supabase SQL Editor
2. Run the SQL from `database_migration.sql`
3. Refresh the schema cache in Supabase Dashboard → Settings → API → Schema Cache

### 2. Jobs Stuck in "Processing"

**Check:**
- Server logs for error messages
- Browser console for JavaScript errors
- Database to see if job status is actually updating

**Solution:** The logs should now show detailed information about what's happening. Check the server console output.

### 3. "Internal Server Error" or JSON Parse Errors

**Solution:** 
- Check server logs for the actual error
- Ensure all environment variables are set (SUPABASE_URL, SUPABASE_ANON_KEY)
- Verify the database migration has been run

### 4. Frontend Shows "Failed to create job"

**Check:**
- Server logs for detailed error messages
- Database connection (visit `/health` endpoint)
- Database schema matches the code (run migration if needed)

## Quick Health Check

1. **Check if backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy","database":"connected"}`

2. **Check if frontend is built:**
   ```bash
   # Windows
   dir dist
   
   # Linux/Mac
   ls dist
   ```
   Should show `index.html` and `assets/` folder

3. **Check environment variables:**
   - `SUPABASE_URL` should be set
   - `SUPABASE_ANON_KEY` should be set

## Still Not Working?

1. Check server logs for error messages
2. Check browser console (F12) for JavaScript errors
3. Verify all dependencies are installed:
   - Python packages: `pip install -r requirements.txt`
   - Node packages: `npm install`
4. Ensure database tables exist and migration has been run

