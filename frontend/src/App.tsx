import { useState, useEffect, useCallback } from 'react'
import { Header } from './components/Header'
import { EmailInput } from './components/EmailInput'
import { SummaryCards } from './components/SummaryCards'
import { ResultsTable } from './components/ResultsTable'
import { Disclaimer } from './components/Disclaimer'
import { ArchitectureInfo } from './components/ArchitectureInfo'
import type {
  VerificationResult,
  VerificationSummary,
  VerificationStatus,
  VerificationResponse,
  HealthResponse,
} from './types'

// Use configured API base URL or empty string for proxy / same-origin
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const MAX_BATCH_SIZE = 100

export function App() {
  const [emailsText, setEmailsText] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [results, setResults] = useState<VerificationResult[]>([])
  const [summary, setSummary] = useState<VerificationSummary | null>(null)
  const [activeFilter, setActiveFilter] = useState<VerificationStatus | 'all'>('all')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking')

  // Check backend health
  const checkHealth = useCallback(async () => {
    setApiStatus('checking')
    try {
      const res = await fetch(`${API_BASE_URL}/api/health`, {
        method: 'GET',
        headers: { Accept: 'application/json' },
      })
      if (res.ok) {
        const data: HealthResponse = await res.json()
        if (data.status === 'healthy') {
          setApiStatus('online')
          return
        }
      }
      setApiStatus('offline')
    } catch {
      setApiStatus('offline')
    }
  }, [])

  useEffect(() => {
    checkHealth()
  }, [checkHealth])

  // Handle email verification
  const handleVerify = async () => {
    setErrorMessage(null)

    // Extract non-empty lines
    const emailLines = emailsText
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0)

    if (emailLines.length === 0) {
      setErrorMessage('Please enter at least one email address before submitting.')
      return
    }

    if (emailLines.length > MAX_BATCH_SIZE) {
      setErrorMessage(
        `Batch size limit exceeded. You entered ${emailLines.length} emails, but the maximum batch size is ${MAX_BATCH_SIZE}.`
      )
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch(`${API_BASE_URL}/api/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({ emails: emailLines }),
      })

      const data: VerificationResponse = await response.json()

      if (!response.ok) {
        setErrorMessage(data.error || 'Failed to verify emails. Please check your submission.')
        setIsLoading(false)
        return
      }

      setResults(data.results)
      setSummary(data.summary)
      setActiveFilter('all')
      setApiStatus('online')
    } catch (err: unknown) {
      const message =
        err instanceof Error
          ? err.message
          : 'Unable to connect to the MailCheck backend server. Please verify the API is running.'
      setErrorMessage(`Network or Server Error: ${message}`)
      setApiStatus('offline')
    } finally {
      setIsLoading(false)
    }
  }

  // Clear inputs and results
  const handleClear = () => {
    setEmailsText('')
    setResults([])
    setSummary(null)
    setActiveFilter('all')
    setErrorMessage(null)
  }

  // Export results as CSV
  const handleExportCsv = () => {
    if (results.length === 0) return

    const escapeCsvField = (text: string) => {
      const sanitized = text.replace(/"/g, '""')
      return `"${sanitized}"`
    }

    const headers = ['Email Address', 'Verification Status', 'Reason / Explanation', 'Checks Performed']
    const rows = results.map((r) => [
      escapeCsvField(r.email),
      escapeCsvField(r.status),
      escapeCsvField(r.reason),
      escapeCsvField(r.checks_performed.join(', ')),
    ])

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const downloadLink = document.createElement('a')
    downloadLink.href = url
    downloadLink.setAttribute('download', `mailcheck_results_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app-layout">
      <Header apiStatus={apiStatus} onRefreshHealth={checkHealth} />

      <main className="main-content">
        <div className="content-container">
          {/* Email Input Section */}
          <EmailInput
            value={emailsText}
            onChange={setEmailsText}
            onVerify={handleVerify}
            onClear={handleClear}
            isLoading={isLoading}
            maxBatchSize={MAX_BATCH_SIZE}
            error={errorMessage}
          />

          {/* Results & Summary Section */}
          {results.length > 0 && summary && (
            <div className="results-wrapper">
              <SummaryCards
                summary={summary}
                activeFilter={activeFilter}
                onSelectFilter={setActiveFilter}
              />

              <ResultsTable
                results={results}
                activeFilter={activeFilter}
                onSelectFilter={setActiveFilter}
                onExportCsv={handleExportCsv}
              />

              <Disclaimer />
            </div>
          )}

          {/* Educational Architecture Reference */}
          <ArchitectureInfo />
        </div>
      </main>

      <footer className="footer">
        <div className="footer-container">
          <p>
            <strong>MailCheck</strong> &bull; College Software Development Assignment &bull; Real RFC
            Syntax &amp; DNS/MX Verification Engine
          </p>
          <p className="footer-meta">
            Developed with React 19, TypeScript, Vite, Python Flask, and dnspython.
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
