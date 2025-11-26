import React from 'react'
import './ResultsView.css'

function ResultsView({ job, results, loading, onExport }) {
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#10b981'
      case 'running':
        return '#3b82f6'
      case 'failed':
        return '#ef4444'
      case 'pending':
        return '#f59e0b'
      default:
        return '#6b7280'
    }
  }

  if (loading) {
    return (
      <div className="results-view-card">
        <h2>Job Status</h2>
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Processing job...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="results-view-card">
      <div className="results-header">
        <h2>Job Details</h2>
        {job.status === 'completed' && results && (
          <div className="export-buttons">
            <button onClick={() => onExport('json')} className="export-btn">
              📥 JSON
            </button>
            <button onClick={() => onExport('csv')} className="export-btn">
              📥 CSV
            </button>
            <button onClick={() => onExport('excel')} className="export-btn">
              📥 Excel
            </button>
          </div>
        )}
      </div>

      <div className="job-info">
        <div className="info-row">
          <span className="info-label">Status:</span>
          <span
            className="info-value status-badge"
            style={{ backgroundColor: getStatusColor(job.status) }}
          >
            {job.status}
          </span>
        </div>
        <div className="info-row">
          <span className="info-label">URL:</span>
          <span className="info-value url-text">{job.url}</span>
        </div>
        <div className="info-row">
          <span className="info-label">Created:</span>
          <span className="info-value">{formatDate(job.created_at)}</span>
        </div>
        {job.completed_at && (
          <div className="info-row">
            <span className="info-label">Completed:</span>
            <span className="info-value">{formatDate(job.completed_at)}</span>
          </div>
        )}
        {job.ai_prompt && (
          <div className="info-row">
            <span className="info-label">AI Prompt:</span>
            <span className="info-value">{job.ai_prompt}</span>
          </div>
        )}
        {job.error && (
          <div className="error-box">
            <strong>Error:</strong> {job.error}
          </div>
        )}
      </div>

      {results && (
        <div className="results-section">
          <h3>Results ({results.total_items} items)</h3>
          <div className="results-content">
            {results.data && results.data.length > 0 ? (
              <pre className="results-json">
                {JSON.stringify(results.data, null, 2)}
              </pre>
            ) : (
              <p className="no-results">No results found</p>
            )}
          </div>
        </div>
      )}

      {job.status === 'pending' && (
        <div className="status-message">
          <p>⏳ Job is queued and will start processing shortly...</p>
        </div>
      )}

      {job.status === 'running' && (
        <div className="status-message">
          <p>🔄 Job is currently running...</p>
        </div>
      )}

      {job.status === 'failed' && (
        <div className="status-message error">
          <p>❌ Job failed. Check the error message above.</p>
        </div>
      )}
    </div>
  )
}

export default ResultsView

