import React from 'react'
import { ShieldAlert } from 'lucide-react'

export const Disclaimer: React.FC = () => {
  return (
    <div className="disclaimer-banner">
      <div className="disclaimer-icon-wrapper">
        <ShieldAlert size={20} className="disclaimer-icon" />
      </div>
      <div className="disclaimer-body">
        <h3 className="disclaimer-title">Verification Scope &amp; Delivery Disclaimer</h3>
        <p className="disclaimer-text">
          MailCheck performs syntax and domain-level checks. A valid domain does not guarantee that a
          mailbox exists or will accept messages. Some mail servers hide mailbox information, and
          results cannot guarantee delivery.
        </p>
      </div>
    </div>
  )
}
