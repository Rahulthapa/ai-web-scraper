import React, { useState, useEffect } from 'react'
import './JobForm.css'

function JobForm({ onJobCreated, apiUrl, setLoading }) {
  const [mode, setMode] = useState('url') // 'url', 'crawl', 'html', 'yelp'
  const [url, setUrl] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [rawHtml, setRawHtml] = useState('')
  const [aiPrompt, setAiPrompt] = useState('')
  const [exportFormat, setExportFormat] = useState('json')
  const [useJavascript, setUseJavascript] = useState(false)
  const [maxPages, setMaxPages] = useState(10)
  const [maxDepth, setMaxDepth] = useState(2)
  const [sameDomain, setSameDomain] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  
  // Yelp specific
  const [yelpTerm, setYelpTerm] = useState('')
  const [yelpLocation, setYelpLocation] = useState('')
  const [yelpLimit, setYelpLimit] = useState(20)
  const [yelpSortBy, setYelpSortBy] = useState('rating')
  const [yelpApiReady, setYelpApiReady] = useState(null)

  // Check Yelp API status
  useEffect(() => {
    const checkYelpApi = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/yelp/status`)
        const data = await response.json()
        setYelpApiReady(data.configured)
      } catch {
        setYelpApiReady(false)
      }
    }
    checkYelpApi()
  }, [apiUrl])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSubmitting(true)
    setLoading(true)

    try {
      if (mode === 'yelp') {
        // Yelp API search
        const params = new URLSearchParams({
          term: yelpTerm,
          location: yelpLocation,
          limit: yelpLimit.toString(),
          sort_by: yelpSortBy,
        })
        
        const response = await fetch(`${apiUrl}/api/yelp/search?${params}`)
        
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || `Request failed (${response.status})`)
        }

        const result = await response.json()
        
        const fakeJob = {
          id: `yelp-${Date.now()}`,
          url: `Yelp: ${yelpTerm} in ${yelpLocation}`,
          status: 'completed',
          created_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
        }
        
        onJobCreated(fakeJob, {
          job_id: fakeJob.id,
          data: result.restaurants,
          total_items: result.total,
          filtered_items: result.total,
        })
        
        setLoading(false)
        return
      }

      if (mode === 'html') {
        // Parse HTML directly
        const response = await fetch(`${apiUrl}/parse-html`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            html: rawHtml,
            source_url: 'pasted-html',
            ai_prompt: aiPrompt || null,
          }),
        })

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}))
          throw new Error(errorData.detail || `Request failed (${response.status})`)
        }

        const result = await response.json()
        
        const fakeJob = {
          id: `html-${Date.now()}`,
          url: 'Pasted HTML',
          status: 'completed',
          created_at: new Date().toISOString(),
          completed_at: new Date().toISOString(),
          ai_prompt: aiPrompt,
        }
        
        onJobCreated(fakeJob, {
          job_id: fakeJob.id,
          data: result.results || [result.data],
          total_items: result.total_items || 1,
          filtered_items: result.total_items || 1,
        })
        
        setRawHtml('')
        setAiPrompt('')
        setLoading(false)
        return
      }

      // Regular URL or Crawl mode
      const response = await fetch(`${apiUrl}/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: mode === 'url' ? url : null,
          search_query: mode === 'crawl' ? searchQuery : null,
          crawl_mode: mode === 'crawl',
          max_pages: mode === 'crawl' ? maxPages : null,
          max_depth: mode === 'crawl' ? maxDepth : null,
          same_domain: mode === 'crawl' ? sameDomain : null,
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

  const canSubmit = () => {
    if (submitting) return false
    if (mode === 'url') return !!url
    if (mode === 'crawl') return !!searchQuery
    if (mode === 'html') return rawHtml.length > 100
    if (mode === 'yelp') return !!yelpTerm && !!yelpLocation
    return false
  }

  return (
    <div className="job-form">
      <h2>New Scraping Job</h2>
      
      <div className="mode-tabs">
        <button 
          type="button"
          className={`mode-tab ${mode === 'url' ? 'active' : ''}`}
          onClick={() => setMode('url')}
        >
          URL
        </button>
        <button 
          type="button"
          className={`mode-tab ${mode === 'crawl' ? 'active' : ''}`}
          onClick={() => setMode('crawl')}
        >
          Crawl
        </button>
        <button 
          type="button"
          className={`mode-tab ${mode === 'html' ? 'active' : ''}`}
          onClick={() => setMode('html')}
        >
          Paste HTML
        </button>
        <button 
          type="button"
          className={`mode-tab yelp ${mode === 'yelp' ? 'active' : ''}`}
          onClick={() => setMode('yelp')}
        >
          Yelp API
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        {mode === 'url' && (
          <div className="form-group">
            <label>Website URL</label>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
              disabled={submitting}
            />
          </div>
        )}

        {mode === 'crawl' && (
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

        {mode === 'html' && (
          <div className="form-group">
            <label>Paste HTML Content</label>
            <textarea
              value={rawHtml}
              onChange={(e) => setRawHtml(e.target.value)}
              placeholder="Open the page in your browser, right-click -> View Page Source, copy all the HTML and paste here..."
              disabled={submitting}
              className="html-input"
              rows={8}
            />
            <small>
              {rawHtml.length > 0 
                ? `${rawHtml.length.toLocaleString()} characters` 
                : 'Paste the complete HTML source code'}
            </small>
          </div>
        )}

        {mode === 'yelp' && (
          <>
            {yelpApiReady === false && (
              <div className="api-warning">
                Yelp API key not configured. Add YELP_API_KEY to environment variables.
                <a href="https://www.yelp.com/developers/v3/manage_app" target="_blank" rel="noopener noreferrer">
                  Get free API key
                </a>
              </div>
            )}
            
            <div className="form-group">
              <label>Search Term</label>
              <input
                type="text"
                value={yelpTerm}
                onChange={(e) => setYelpTerm(e.target.value)}
                placeholder="steakhouse, pizza, sushi..."
                required
                disabled={submitting}
              />
            </div>

            <div className="form-group">
              <label>Location</label>
              <input
                type="text"
                value={yelpLocation}
                onChange={(e) => setYelpLocation(e.target.value)}
                placeholder="Houston, TX"
                required
                disabled={submitting}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Results</label>
                <input
                  type="number"
                  value={yelpLimit}
                  onChange={(e) => setYelpLimit(parseInt(e.target.value) || 20)}
                  min="1"
                  max="50"
                  disabled={submitting}
                />
              </div>
              <div className="form-group">
                <label>Sort By</label>
                <select
                  value={yelpSortBy}
                  onChange={(e) => setYelpSortBy(e.target.value)}
                  disabled={submitting}
                >
                  <option value="rating">Rating</option>
                  <option value="review_count">Review Count</option>
                  <option value="best_match">Best Match</option>
                  <option value="distance">Distance</option>
                </select>
              </div>
            </div>
          </>
        )}

        {(mode === 'url' || mode === 'crawl' || mode === 'html') && (
          <div className="form-group">
            <label>AI Extraction Prompt (optional)</label>
            <textarea
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              placeholder="Extract restaurant names, addresses, ratings..."
              disabled={submitting}
            />
            <small>Describe what data you want to extract</small>
          </div>
        )}

        {(mode === 'url' || mode === 'crawl') && (
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
        )}

        {error && <div className="form-error">{error}</div>}

        <button 
          type="submit" 
          className="submit-btn"
          disabled={!canSubmit()}
        >
          {submitting ? (
            <span className="spinner" />
          ) : (
            <>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                {mode === 'html' ? (
                  <path d="M16 18l6-6-6-6M8 6l-6 6 6 6"/>
                ) : mode === 'yelp' ? (
                  <path d="M21 11.5a8.38 8.38 0 01-.9 3.8 8.5 8.5 0 01-7.6 4.7 8.38 8.38 0 01-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 01-.9-3.8 8.5 8.5 0 014.7-7.6 8.38 8.38 0 013.8-.9h.5a8.48 8.48 0 018 8v.5z"/>
                ) : (
                  <path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9"/>
                )}
              </svg>
              {mode === 'html' ? 'Parse HTML' : 
               mode === 'yelp' ? 'Search Yelp' :
               mode === 'crawl' ? 'Start Crawling' : 'Start Scraping'}
            </>
          )}
        </button>
      </form>
    </div>
  )
}

export default JobForm
