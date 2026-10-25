import React from 'react'
import { Sparkles, Trash2, ArrowRight, Loader2, AlertTriangle, Layers } from 'lucide-react'

interface EmailInputProps {
  value: string
  onChange: (val: string) => void
  onVerify: () => void
  onClear: () => void
  isLoading: boolean
  maxBatchSize: number
  error: string | null
}

const SAMPLE_EMAILS = [
  'support@github.com',
  'admissions@stanford.edu',
  'invalid-email-missing-at.com',
  'john.doe@nonexistent-fake-domain-xyz987.org',
  'user@domain.invalid',
  'support@github.com', // Duplicate entry to test deduplication
]

export const EmailInput: React.FC<EmailInputProps> = ({
  value,
  onChange,
  onVerify,
  onClear,
  isLoading,
  maxBatchSize,
  error,
}) => {
  // Count non-empty lines
  const lines = value
    .split('\n')
    .map((l) => l.trim())
    .filter((l) => l.length > 0)
  const lineCount = lines.length

  // Check unique count for preview
  const uniqueCount = new Set(lines.map((l) => l.toLowerCase())).size
  const duplicateCount = lineCount - uniqueCount

  const isOverLimit = lineCount > maxBatchSize

  const handleLoadSample = () => {
    onChange(SAMPLE_EMAILS.join('\n'))
  }

  return (
    <div className="card input-card">
      <div className="input-header">
        <div>
          <h2 className="section-title">Paste Email Addresses</h2>
          <p className="section-desc">
            Enter one email address per line. Maximum {maxBatchSize} addresses per request.
          </p>
        </div>
        <button
          type="button"
          onClick={handleLoadSample}
          disabled={isLoading}
          className="btn-secondary btn-sm"
          title="Load demonstration emails with diverse test cases"
        >
          <Sparkles size={14} className="icon-blue" />
          <span>Load Test Sample</span>
        </button>
      </div>

      <div className="textarea-container">
        <textarea
          rows={7}
          className={`email-textarea ${isOverLimit ? 'textarea-error' : ''}`}
          placeholder={`e.g.\nstudent@university.edu\nteam@company.com\ninvalid-syntax-sample\nuser@nonexistent-domain.org`}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={isLoading}
          aria-label="Email addresses input area"
        />
      </div>

      <div className="input-meta-row">
        <div className="counts-group">
          <span className={`count-pill ${isOverLimit ? 'pill-danger' : 'pill-neutral'}`}>
            {lineCount} / {maxBatchSize} addresses
          </span>

          {duplicateCount > 0 && (
            <span className="count-pill pill-warning" title="Duplicate emails are automatically consolidated">
              <Layers size={13} />
              {duplicateCount} duplicate{duplicateCount > 1 ? 's' : ''} detected (will be merged)
            </span>
          )}
        </div>

        <div className="button-group">
          <button
            type="button"
            onClick={onClear}
            disabled={isLoading || (!value && lineCount === 0)}
            className="btn-neutral"
            title="Reset email input and verification results"
          >
            <Trash2 size={16} />
            <span>Clear</span>
          </button>

          <button
            type="button"
            onClick={onVerify}
            disabled={isLoading || lineCount === 0 || isOverLimit}
            className="btn-primary"
            title="Execute syntax and DNS/MX verification"
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="spin" />
                <span>Verifying Batch...</span>
              </>
            ) : (
              <>
                <span>Check Emails</span>
                <ArrowRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>

      {isOverLimit && (
        <div className="alert-box alert-error">
          <AlertTriangle size={18} className="alert-icon" />
          <div>
            <strong>Batch limit exceeded:</strong> You submitted {lineCount} emails. Please reduce your
            list to {maxBatchSize} or fewer addresses before checking.
          </div>
        </div>
      )}

      {error && !isOverLimit && (
        <div className="alert-box alert-error">
          <AlertTriangle size={18} className="alert-icon" />
          <div>{error}</div>
        </div>
      )}
    </div>
  )
}
