import React from 'react'
import { MailCheck, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react'

interface HeaderProps {
  apiStatus: 'online' | 'offline' | 'checking'
  onRefreshHealth: () => void
}

export const Header: React.FC<HeaderProps> = ({ apiStatus, onRefreshHealth }) => {
  return (
    <header className="header">
      <div className="header-container">
        <div className="brand-group">
          <div className="logo-wrapper">
            <MailCheck className="logo-icon" size={30} />
          </div>
          <div>
            <div className="title-row">
              <h1 className="brand-title">MailCheck</h1>
              <span className="badge-pill badge-project">College S.D. Project</span>
            </div>
            <p className="brand-subtitle">
              Bulk Email Verification Tool – Syntax Validation &amp; DNS/MX Mail Route Resolution
            </p>
          </div>
        </div>

        <div className="api-status-wrapper">
          <div
            className={`api-status-pill ${
              apiStatus === 'online'
                ? 'status-online'
                : apiStatus === 'offline'
                ? 'status-offline'
                : 'status-checking'
            }`}
            title="Backend Flask API connection state"
          >
            {apiStatus === 'online' && <CheckCircle2 size={15} />}
            {apiStatus === 'offline' && <AlertCircle size={15} />}
            {apiStatus === 'checking' && <RefreshCw size={15} className="spin" />}
            <span>
              {apiStatus === 'online'
                ? 'API Connected'
                : apiStatus === 'offline'
                ? 'API Disconnected'
                : 'Checking API...'}
            </span>
          </div>
          <button
            onClick={onRefreshHealth}
            className="btn-icon"
            title="Recheck API health"
            aria-label="Refresh API status"
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </div>
    </header>
  )
}
