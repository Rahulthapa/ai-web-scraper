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
        headers: { 'Content-Type': 'application/json' },
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
        let errorMessage = `Request failed (${response.status})`
        try {
          const contentType = response.headers.get('content-type')
          if (contentType && contentType.includes('application/json')) {
            const errorData = await response.json()
            errorMessage = errorData.detail || errorMessage
          }
        } catch {}
        throw new Error(errorMessage)
      }

      const job = await response.json()
      onJobCreated(job)

      setUrl('')
      setSearchQuery('')
      setAiPrompt('')
    } catch (err) {
      setError(err.message)
      setLoading(false)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="job-form">
      <h2>New Scraping Job</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="checkbox-group">
            <input
              type="checkbox"
              checked={crawlMode}
              onChange={(e) => setCrawlMode(e.target.checked)}
              disabled={submitting}
            />
            <span>Crawl Mode (multiple pages)</span>
          </label>
        </div>

        {!crawlMode ? (
          <div className="form-group">
            <label>URL</label>
            <input
              type="url"
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
              <label>Search Query or URL</label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="steakhouses in Houston, TX"
                required
                disabled={submitting}
              />
              <small>Enter a search term or starting URL</small>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Max Pages</label>
                <input
                  type="number"
                  value={maxPages}
                  onChange={(e) => setMaxPages(parseInt(e.target.value) || 10)}
                  min="1"
                  max="50"
                  disabled={submitting}
                />
              </div>
              <div className="form-group">
                <label>Max Depth</label>
                <input
                  type="number"
                  value={maxDepth}
                  onChange={(e) => setMaxDepth(parseInt(e.target.value) || 2)}
                  min="1"
                  max="5"
                  disabled={submitting}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="checkbox-group">
                <input
                  type="checkbox"
                  checked={sameDomain}
                  onChange={(e) => setSameDomain(e.target.checked)}
                  disabled={submitting}
                />
                <span>Same domain only</span>
              </label>
            </div>
          </>
        )}

        <div className="form-group">
          <label>AI Extraction Prompt (optional)</label>
          <textarea
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder="Extract product names and prices..."
            disabled={submitting}
          />
          <small>Describe what data you want to extract</small>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Export Format</label>
            <select
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
            <label>&nbsp;</label>
            <label className="checkbox-group" style={{ height: '42px', display: 'flex' }}>
              <input
                type="checkbox"
                checked={useJavascript}
                onChange={(e) => setUseJavascript(e.target.checked)}
                disabled={submitting}
              />
              <span>JavaScript rendering</span>
            </label>
          </div>
        </div>

        {error && <div className="form-error">{error}</div>}

        <button 
          type="submit" 
          className="submit-btn"
          disabled={submitting || (!crawlMode && !url) || (crawlMode && !searchQuery)}
        >
          {submitting ? (
            <span className="spinner" />
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9"/>
              </svg>
              {crawlMode ? 'Start Crawling' : 'Start Scraping'}
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default JobForm
