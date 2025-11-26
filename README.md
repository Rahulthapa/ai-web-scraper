# AI Web Scraper

Intelligent web scraping API with AI-powered filtering and data extraction, featuring a modern React frontend.

## Features

- 🕷️ **Web Scraping**: Extract data from any website
- 🤖 **AI Filtering**: Use AI prompts to filter and structure scraped data
- 📊 **Multiple Export Formats**: Export results as JSON, CSV, or Excel
- 🎨 **Modern Frontend**: Beautiful React-based web interface
- ⚡ **Async Processing**: Background job processing with real-time status updates
- 💾 **Persistent Storage**: Jobs and results stored in Supabase

## Tech Stack

### Backend
- FastAPI (Python)
- BeautifulSoup4 (Web scraping)
- Supabase (Database)
- Playwright (JavaScript rendering support)

### Frontend
- React 18
- Vite (Build tool)
- Axios (HTTP client)

## Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Supabase account (for database)

### Backend Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
Create a `.env` file:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

3. **Set up Supabase tables:**
Create the following tables in your Supabase project:

**scrape_jobs table:**
```sql
CREATE TABLE scrape_jobs (
  id UUID PRIMARY KEY,
  url TEXT NOT NULL,
  status TEXT NOT NULL,
  filters JSONB,
  ai_prompt TEXT,
  export_format TEXT DEFAULT 'json',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  completed_at TIMESTAMP WITH TIME ZONE,
  error TEXT
);
```

**scrape_results table:**
```sql
CREATE TABLE scrape_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_id UUID REFERENCES scrape_jobs(id),
  data JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Frontend Setup

1. **Install Node dependencies:**
```bash
npm install
```

2. **Set up environment variables:**
Create a `.env` file in the root:
```env
VITE_API_URL=http://localhost:8000
```

3. **Build the frontend:**
```bash
npm run build
```

## Running the Application

### Development Mode

**Backend:**
```bash
uvicorn app.main:app --reload --port 8000
```

**Frontend (separate terminal):**
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000` and will proxy API requests to `http://localhost:8000`.

### Production Mode

1. **Build the frontend:**
```bash
npm run build
```

2. **Run the backend (serves frontend automatically):**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at `http://localhost:8000` with both API and frontend.

## Docker Deployment

1. **Build the Docker image:**
```bash
docker build -t ai-web-scraper .
```

2. **Run the container:**
```bash
docker run -p 8000:8000 --env-file .env ai-web-scraper
```

## API Endpoints

### Create Job
```bash
POST /jobs
Content-Type: application/json

{
  "url": "https://example.com",
  "ai_prompt": "Extract all product names and prices",
  "export_format": "json"
}
```

### Get Job Status
```bash
GET /jobs/{job_id}
```

### Get Results
```bash
GET /jobs/{job_id}/results
```

### Export Results
```bash
GET /jobs/{job_id}/export?format=json
GET /jobs/{job_id}/export?format=csv
GET /jobs/{job_id}/export?format=excel
```

## Usage

1. **Open the web interface** at `http://localhost:3000` (dev) or `http://localhost:8000` (production)

2. **Create a scraping job:**
   - Enter the URL you want to scrape
   - Optionally add an AI prompt to filter/structure the data
   - Choose export format
   - Click "Start Scraping"

3. **Monitor job status:**
   - Jobs appear in the left panel
   - Status updates automatically (pending → running → completed)
   - Click on a job to view details and results

4. **Export results:**
   - When a job is completed, use the export buttons
   - Download results as JSON, CSV, or Excel

## Project Structure

```
ai-web-scraper/
├── app/                 # Backend Python application
│   ├── main.py         # FastAPI application and routes
│   ├── scraper.py       # Web scraping logic
│   ├── ai_filter.py    # AI filtering (to be implemented)
│   ├── worker.py        # Job processing
│   ├── storage.py      # Supabase integration
│   ├── exporter.py     # Data export utilities
│   └── models.py       # Pydantic models
├── src/                 # Frontend React application
│   ├── components/     # React components
│   ├── App.jsx         # Main app component
│   └── main.jsx        # Entry point
├── dist/               # Built frontend (generated)
├── Dockerfile          # Docker configuration
└── requirements.txt    # Python dependencies
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
# Python
black app/
isort app/

# JavaScript
npm run format  # (if configured)
```

## License

MIT
