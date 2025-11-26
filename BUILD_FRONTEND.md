# Building the Frontend

## Prerequisites

You need Node.js 18+ installed. Download from [nodejs.org](https://nodejs.org/)

## Local Development

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Build the frontend:**
   ```bash
   npm run build
   ```

   This creates a `dist/` folder with the built frontend files.

3. **Run the backend:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

   The frontend will now be served automatically at `http://localhost:8000`

## Render Deployment

If you're deploying to Render, you need to build the frontend as part of the build process. Here are two options:

### Option 1: Update Dockerfile to Build Frontend

Add Node.js installation and frontend build steps to your Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

WORKDIR /app

# Install system dependencies for Playwright
# ... (existing Playwright setup) ...

# Copy package files and install frontend dependencies
COPY package*.json ./
RUN npm install

# Copy frontend source and build
COPY src/ ./src/
COPY index.html ./
COPY vite.config.js ./
RUN npm run build

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 2: Build Script in Render

1. In Render dashboard, go to your service settings
2. Add a **Build Command**:
   ```bash
   npm install && npm run build && pip install -r requirements.txt
   ```
3. Set **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Option 3: Separate Frontend Service (Recommended for Production)

1. Create a separate **Static Site** service in Render
2. Build command: `npm install && npm run build`
3. Publish directory: `dist`
4. Set environment variable: `VITE_API_URL=https://your-api-url.onrender.com`

## Verify Build

After building, check that the `dist/` folder exists and contains:
- `index.html`
- `assets/` folder with JS and CSS files

Then restart your backend server. The root endpoint should now serve the frontend instead of the JSON message.

