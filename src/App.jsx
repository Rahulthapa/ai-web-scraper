import React, { useState, useEffect } from 'react'
import JobForm from './components/JobForm'
import JobList from './components/JobList'
import ResultsView from './components/ResultsView'
import './App.css'

function App() {
  const [jobs, setJobs] = useState([])
  const [selectedJob, setSelectedJob] = useState(null)
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)

  // In production, API is on the same origin, so use relative URLs
  // In development, use the VITE_API_URL or default to localhost
  const API_BASE_URL = import.meta.env.VITE_API_URL || 
    (import.meta.env.PROD ? '' : 'http://localhost:8000')

  const fetchJobs = async () => {
    // In a real app, you'd fetch jobs from an endpoint
    // For now, we'll manage jobs in local state
  }

  const handleJobCreated = (newJob) => {
    setJobs([newJob, ...jobs])
    setSelectedJob(newJob)
    // Poll for job status
    pollJobStatus(newJob.id)
  }

  const pollJobStatus = async (jobId) => {
    const maxAttempts = 60 // Poll for up to 5 minutes (5 second intervals)
    let attempts = 0

    const poll = async () => {
      if (attempts >= maxAttempts) return

      try {
        const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`)
        const job = await response.json()

        // Update job in list
        setJobs(prev => prev.map(j => j.id === jobId ? job : j))
        setSelectedJob(job)

        if (job.status === 'completed') {
          // Fetch results
          fetchResults(jobId)
        } else if (job.status === 'failed') {
          setLoading(false)
        } else {
          // Continue polling
          attempts++
          setTimeout(poll, 5000)
        }
      } catch (error) {
        console.error('Error polling job status:', error)
        setLoading(false)
      }
    }

    poll()
  }

  const fetchResults = async (jobId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/results`)
      if (response.ok) {
        const data = await response.json()
        setResults(data)
        setLoading(false)
      }
    } catch (error) {
      console.error('Error fetching results:', error)
      setLoading(false)
    }
  }

  const handleJobSelect = async (job) => {
    setSelectedJob(job)
    setResults(null)

    if (job.status === 'completed') {
      await fetchResults(job.id)
    } else if (job.status === 'pending' || job.status === 'running') {
      setLoading(true)
      pollJobStatus(job.id)
    }
  }

  const handleExport = async (format) => {
    if (!selectedJob) return

    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${selectedJob.id}/export?format=${format}`)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `scrape_results_${selectedJob.id}.${format === 'excel' ? 'xlsx' : format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Error exporting:', error)
      alert('Failed to export results')
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>🕷️ AI Web Scraper</h1>
        <p>Intelligent web scraping with AI-powered filtering</p>
      </header>

      <div className="app-content">
        <div className="left-panel">
          <JobForm 
            onJobCreated={handleJobCreated}
            apiUrl={API_BASE_URL}
            setLoading={setLoading}
          />
          
          <JobList
            jobs={jobs}
            selectedJob={selectedJob}
            onJobSelect={handleJobSelect}
          />
        </div>

        <div className="right-panel">
          {selectedJob && (
            <ResultsView
              job={selectedJob}
              results={results}
              loading={loading}
              onExport={handleExport}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default App

