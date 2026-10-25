import React, { useState } from 'react'
import {
  Download,
  Copy,
  Check,
  Search,
  CheckCircle2,
  XCircle,
  HelpCircle,
  Filter,
} from 'lucide-react'
import type { VerificationResult, VerificationStatus } from '../types'

interface ResultsTableProps {
  results: VerificationResult[]
  activeFilter: VerificationStatus | 'all'
  onSelectFilter: (filter: VerificationStatus | 'all') => void
  onExportCsv: () => void
}

export const ResultsTable: React.FC<ResultsTableProps> = ({
  results,
  activeFilter,
  onSelectFilter,
  onExportCsv,
}) => {
  const [copiedEmail, setCopiedEmail] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  const handleCopy = (email: string) => {
    navigator.clipboard.writeText(email)
    setCopiedEmail(email)
    setTimeout(() => {
      setCopiedEmail(null)
    }, 2000)
  }

  // Filter results
  const filteredResults = results.filter((item) => {
    // Status filter
    if (activeFilter !== 'all' && item.status !== activeFilter) {
      return false
    }
    // Search query
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase()
      return (
        item.email.toLowerCase().includes(q) ||
        item.reason.toLowerCase().includes(q) ||
        item.checks_performed.some((c) => c.toLowerCase().includes(q))
      )
    }
    return true
  })

  const getStatusBadge = (status: VerificationStatus) => {
    switch (status) {
      case 'likely_delivered':
        return (
          <span className="badge badge-success">
            <CheckCircle2 size={14} />
            <span>Likely to Be Delivered</span>
          </span>
        )
      case 'likely_bounce':
        return (
          <span className="badge badge-danger">
            <XCircle size={14} />
            <span>Likely to Bounce</span>
          </span>
        )
      case 'unknown':
      default:
        return (
          <span className="badge badge-warning">
            <HelpCircle size={14} />
            <span>Unknown</span>
          </span>
        )
    }
  }

  const formatCheckLabel = (check: string) => {
    switch (check) {
      case 'syntax':
        return 'Syntax (RFC 5322)'
      case 'dns_mx':
        return 'MX Records'
      case 'dns_fallback_a':
        return 'A/AAAA Fallback'
      case 'dns_lookup':
        return 'DNS Query'
      default:
        return check
    }
  }

  return (
    <div className="card results-card">
      <div className="results-toolbar">
        <div className="toolbar-left">
          <h2 className="section-title">Verification Results</h2>
          <span className="result-count-badge">
            Showing {filteredResults.length} of {results.length} addresses
          </span>
        </div>

        <div className="toolbar-actions">
          <div className="search-box">
            <Search size={15} className="search-icon" />
            <input
              type="text"
              placeholder="Search email or reason..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
              aria-label="Search verification results"
            />
          </div>

          <button
            type="button"
            onClick={onExportCsv}
            disabled={results.length === 0}
            className="btn-secondary btn-export"
            title="Download structured CSV file with all verified emails"
          >
            <Download size={15} />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs Bar */}
      <div className="filter-tabs-row">
        <span className="filter-label">
          <Filter size={13} /> Filter:
        </span>
        <button
          type="button"
          className={`filter-pill ${activeFilter === 'all' ? 'active' : ''}`}
          onClick={() => onSelectFilter('all')}
        >
          All ({results.length})
        </button>
        <button
          type="button"
          className={`filter-pill ${activeFilter === 'likely_delivered' ? 'active' : ''}`}
          onClick={() => onSelectFilter('likely_delivered')}
        >
          Likely Delivered ({results.filter((r) => r.status === 'likely_delivered').length})
        </button>
        <button
          type="button"
          className={`filter-pill ${activeFilter === 'likely_bounce' ? 'active' : ''}`}
          onClick={() => onSelectFilter('likely_bounce')}
        >
          Likely Bounce ({results.filter((r) => r.status === 'likely_bounce').length})
        </button>
        <button
          type="button"
          className={`filter-pill ${activeFilter === 'unknown' ? 'active' : ''}`}
          onClick={() => onSelectFilter('unknown')}
        >
          Unknown ({results.filter((r) => r.status === 'unknown').length})
        </button>
      </div>

      {/* Table Container */}
      <div className="table-responsive">
        <table className="results-table">
          <thead>
            <tr>
              <th scope="col" style={{ width: '30%' }}>Email Address</th>
              <th scope="col" style={{ width: '22%' }}>Status</th>
              <th scope="col" style={{ width: '32%' }}>Reason &amp; Explanation</th>
              <th scope="col" style={{ width: '16%' }}>Checks Performed</th>
            </tr>
          </thead>
          <tbody>
            {filteredResults.map((item, idx) => (
              <tr key={`${item.email}-${idx}`}>
                <td className="cell-email">
                  <div className="email-display">
                    <span className="email-text" title={item.email}>
                      {item.email}
                    </span>
                    <button
                      type="button"
                      className="btn-copy"
                      onClick={() => handleCopy(item.email)}
                      title="Copy email address"
                      aria-label={`Copy email ${item.email}`}
                    >
                      {copiedEmail === item.email ? (
                        <Check size={13} className="copy-success" />
                      ) : (
                        <Copy size={13} />
                      )}
                    </button>
                  </div>
                </td>
                <td className="cell-status">{getStatusBadge(item.status)}</td>
                <td className="cell-reason">
                  <span className="reason-text">{item.reason}</span>
                </td>
                <td className="cell-checks">
                  <div className="checks-list">
                    {item.checks_performed.map((chk, cIdx) => (
                      <span key={cIdx} className="check-chip">
                        {formatCheckLabel(chk)}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
            {filteredResults.length === 0 && (
              <tr>
                <td colSpan={4} className="cell-empty">
                  No email addresses match your current filter or search criteria.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
