import React, { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp, Server, ShieldCheck, HelpCircle } from 'lucide-react'

export const ArchitectureInfo: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="card architecture-card">
      <button
        type="button"
        className="architecture-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
      >
        <div className="toggle-left">
          <BookOpen size={18} className="icon-blue" />
          <span className="toggle-title">System Architecture &amp; Verification Methodology</span>
          <span className="badge-pill badge-neutral">Assignment Reference</span>
        </div>
        <div className="toggle-right">
          <span className="toggle-hint">{isOpen ? 'Hide Details' : 'View Standards & Logic'}</span>
          {isOpen ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {isOpen && (
        <div className="architecture-content">
          <div className="methodology-grid">
            <div className="methodology-col">
              <div className="methodology-header">
                <ShieldCheck size={16} className="text-blue" />
                <h4>1. Syntax Validation</h4>
              </div>
              <p>
                Parsed using Python&apos;s <code>email-validator</code> against RFC 5321 and RFC 5322. Checks
                username and domain presence, maximum lengths (254 chars total, 64 chars local-part), valid
                characters, and rejects reserved test domains (RFC 2606).
              </p>
            </div>

            <div className="methodology-col">
              <div className="methodology-header">
                <Server size={16} className="text-green" />
                <h4>2. DNS &amp; Mail Exchange Routing</h4>
              </div>
              <p>
                Resolves real MX records via <code>dnspython</code>. Detects <strong>RFC 7505 Null MX</strong>{' '}
                records (domains explicitly rejecting email). If no MX records exist, checks for{' '}
                <strong>RFC 5321 §5.1 implicit mail routes</strong> using A/AAAA address records.
              </p>
            </div>

            <div className="methodology-col">
              <div className="methodology-header">
                <HelpCircle size={16} className="text-amber" />
                <h4>3. Deployment &amp; SMTP Limits</h4>
              </div>
              <p>
                Modern cloud platforms (Render, Vercel, Railway, AWS free tiers) intentionally block outbound
                TCP port 25 to prevent spam. MailCheck relies on safe, deterministic DNS-routing analysis and
                truthfully reports ambiguous states as <strong>Unknown</strong>.
              </p>
            </div>
          </div>

          <div className="status-definition-box">
            <h4>Status Classification Reference:</h4>
            <ul>
              <li>
                <strong>Likely to Be Delivered:</strong> Address syntax is valid and domain DNS provides an
                active mail exchange route (MX or A/AAAA fallback).
              </li>
              <li>
                <strong>Likely to Bounce:</strong> Syntax is demonstrably invalid, domain is nonexistent
                (NXDOMAIN), has an RFC 7505 Null MX, or lacks both MX and fallback address records.
              </li>
              <li>
                <strong>Unknown:</strong> DNS resolver timed out, temporary nameserver failure occurred, or
                the external mail infrastructure could not be reliably determined.
              </li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
