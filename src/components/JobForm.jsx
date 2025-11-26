import React, { useState } from 'react'
import './JobForm.css'

function JobForm({ onJobCreated, apiUrl, setLoading }) {
  const [crawlMode, setCrawlMode] = useState(false)
  const [url, setUrl] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [aiPrompt, setAiPrompt] = useState('')
  const [exportFormat, setExportFormat] = useState('json')
  const [useJavascript, setUseJavascript] = useState(false)
  const [maxPages, setMaxPages] = useState(10)
  const [maxDepth, setMaxDepth] = useState(2)
  const [sameDomain, setSameDomain] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    setLoading(true)

    try {
      const response = await fetch(`${apiUrl}/jobs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: crawlMode ? null : url,
          search_query: crawlMode ? searchQuery : null,
          crawl_mode: crawlMode,
          max_pages: crawlMode ? maxPages : null,
          max_depth: crawlMode ? maxDepth : null,
          same_domain: crawlMode ? sameDomain : null,
          ai_prompt: aiPrompt || null,
          export_format: exportFormat,
          use_javascript: useJavascript,
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to create job')
      }

      const job = await response.json()
      onJobCreated(job)

      // Reset form
      setUrl('')
      setSearchQuery('')
      setAiPrompt('')
      setExportFormat('json')
      setUseJavascript(false)
      setMaxPages(10)
      setMaxDepth(2)
      setSameDomain(true)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="job-form-card">
      <h2>Create Scraping Job</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="crawlMode" className="checkbox-label">
            <input
              type="checkbox"
              id="crawlMode"
              checked={crawlMode}
              onChange={(e) => setCrawlMode(e.target.checked)}
              disabled={submitting}
            />
            <span>🌐 Web Crawl Mode (Discover & scrape multiple pages)</span>
          </label>
          <small>Enable to crawl the web automatically instead of scraping a single page</small>
        </div>

        {!crawlMode ? (
          <div className="form-group">
            <label htmlFor="url">Website URL *</label>
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
              disabled={submitting}
            />
          </div>
        ) : (
          <>
            <div className="form-group">
              <label htmlFor="searchQuery">Search Query or Starting URL *</label>
              <input
                type="text"
                id="searchQuery"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g., 'artificial intelligence' or 'https://example.com'"
                required
                disabled={submitting}
              />
              <small>Enter a search query to find pages, or a starting URL to crawl from</small>
            </div>

            <div className="form-group-row">
              <div className="form-group">
                <label htmlFor="maxPages">Max Pages</label>
                <input
                  type="number"
                  id="maxPages"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 10)}
                  min="1"
                  max="100"
                  disabled={submitting}
                />
              </div>

              <div className="form-group">
                <label htmlFor="maxDepth">Max Depth</label>
                <input
                  type="number"
                  id="maxDepth"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(parseInt(e.target.value) || 2)}
                  min="1"
                  max="5"
                  disabled={submitting}
                />
                <small>How many link levels to follow</small>
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="sameDomain" className="checkbox-label">
                <input
                  type="checkbox"
                  id="sameDomain"
                  checked={sameDomain}
                  onChange={(e) => setSameDomain(e.target.checked)}
                  disabled={submitting}
                />
                <span>Only crawl same domain</span>
              </label>
            </div>
          </>
        )}

        <div className="form-group">
          <label htmlFor="aiPrompt">AI Prompt (Optional)</label>
          <textarea
            id="aiPrompt"
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder="e.g., Extract all product names and prices"
            rows="3"
            disabled={submitting}
          />
          <small>Use AI to filter and structure the scraped data</small>
        </div>

        <div className="form-group">
          <label htmlFor="exportFormat">Export Format</label>
          <select
            id="exportFormat"
            value={exportFormat}
            onChange={(e) => setExportFormat(e.target.value)}
            disabled={submitting}
          >
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="useJavascript" className="checkbox-label">
            <input
              type="checkbox"
              id="useJavascript"
              checked={useJavascript}
              onChange={(e) => setUseJavascript(e.target.checked)}
              disabled={submitting}
            />
            <span>Use JavaScript Rendering (Playwright)</span>
          </label>
          <small>Enable for websites that require JavaScript to load content (React, Vue, Angular apps)</small>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={submitting || (!crawlMode && !url) || (crawlMode && !searchQuery)}>
          {submitting ? 'Creating...' : crawlMode ? 'Start Crawling' : 'Start Scraping'}
        </button>
      </form>
    </div>
  )
}

export default JobForm

