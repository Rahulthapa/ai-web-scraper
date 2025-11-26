import React from 'react'
import './JobList.css'

function JobList({ jobs, selectedJob, onJobSelect }) {
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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  if (jobs.length === 0) {
    return (
      <div className="job-list-card">
        <h2>Jobs</h2>
        <div className="empty-state">
          <p>No jobs yet. Create your first scraping job!</p>
        </div>
      </div>
    )
  }

  return (
    <div className="job-list-card">
      <h2>Jobs ({jobs.length})</h2>
      <div className="job-list">
        {jobs.map((job) => (
          <div
            key={job.id}
            className={`job-item ${selectedJob?.id === job.id ? 'selected' : ''}`}
            onClick={() => onJobSelect(job)}
          >
            <div className="job-header">
              <div className="job-url">{job.url}</div>
              <span
                className="job-status"
                style={{ backgroundColor: getStatusColor(job.status) }}
              >
                {job.status}
              </span>
            </div>
            <div className="job-meta">
              <span className="job-date">{formatDate(job.created_at)}</span>
              {job.ai_prompt && (
                <span className="job-ai-badge">🤖 AI</span>
              )}
            </div>
            {job.error && (
              <div className="job-error">{job.error}</div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default JobList

