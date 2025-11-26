import React, { useState } from 'react'
import './JobForm.css'

function JobForm({ onJobCreated, apiUrl, setLoading }) {
  const [url, setUrl] = useState('')
  const [aiPrompt, setAiPrompt] = useState('')
  const [exportFormat, setExportFormat] = useState('json')
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
          url,
          ai_prompt: aiPrompt || null,
          export_format: exportFormat,
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
      setAiPrompt('')
      setExportFormat('json')
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

        {error && <div className="error-message">{error}</div>}

        <button type="submit" disabled={submitting || !url}>
          {submitting ? 'Creating...' : 'Start Scraping'}
        </button>
      </form>
    </div>
  )
}

export default JobForm

