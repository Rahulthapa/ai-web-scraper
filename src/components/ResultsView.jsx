import React from 'react'
import './ResultsView.css'

function ResultsView({ job, results, loading, onExport }) {
  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString()
  }

  const getDisplayUrl = (job) => {
    if (job.crawl_mode && job.search_query) {
      return job.search_query
    }
    return job.url || '-'
  }

  if (loading) {
    return (
      <div className="results-view">
        <div className="results-header">
          <h2>Processing</h2>
        </div>
        <div className="loading-state">
          <div className="loading-spinner" />
          <p>Scraping in progress...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="results-view">
      <div className="results-header">
        <h2>Job Results</h2>
        {job.status === 'completed' && results && results.data && results.data.length > 0 && (
          <div className="export-buttons">
            <button className="export-btn" onClick={() => onExport('json')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              JSON
            </button>
            <button className="export-btn" onClick={() => onExport('csv')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              CSV
            </button>
            <button className="export-btn" onClick={() => onExport('excel')}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/>
              </svg>
              Excel
            </button>
          </div>
        )}
      </div>

      <div className="results-info">
        <div className="info-item">
          <span className="info-label">Status</span>
          <span className="info-value status">
            <span className={`status-dot ${job.status}`} />
            {job.status}
          </span>
        </div>
        <div className="info-item">
          <span className="info-label">Target</span>
          <span className="info-value">{getDisplayUrl(job)}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Created</span>
          <span className="info-value">{formatDate(job.created_at)}</span>
        </div>
        {job.completed_at && (
          <div className="info-item">
            <span className="info-label">Completed</span>
            <span className="info-value">{formatDate(job.completed_at)}</span>
          </div>
        )}
        {job.ai_prompt && (
          <div className="info-item">
            <span className="info-label">AI Prompt</span>
            <span className="info-value">{job.ai_prompt}</span>
          </div>
        )}
      </div>

      {job.error && (
        <div className="error-banner">
          <strong>Error:</strong> {job.error}
        </div>
      )}

      <div className="results-content">
        {job.status === 'completed' && results ? (
          results.data && results.data.length > 0 ? (
            <div className="results-data">
              <pre className="results-json">
                {JSON.stringify(results.data, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="no-results">No data found</div>
          )
        ) : job.status === 'pending' ? (
          <div className="status-message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <p>Job is queued and will start shortly</p>
          </div>
        ) : job.status === 'running' ? (
          <div className="status-message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            <p>Scraping in progress...</p>
          </div>
        ) : job.status === 'failed' ? (
          <div className="status-message">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <circle cx="12" cy="12" r="10"/>
              <path d="M15 9l-6 6M9 9l6 6"/>
            </svg>
            <p>Job failed - check error message above</p>
          </div>
        ) : null}
      </div>
    </div>
  )
}

export default ResultsView
