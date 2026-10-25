import React from 'react'
import { CheckCircle2, XCircle, HelpCircle, Inbox } from 'lucide-react'
import type { VerificationSummary, VerificationStatus } from '../types'

interface SummaryCardsProps {
  summary: VerificationSummary | null
  activeFilter: VerificationStatus | 'all'
  onSelectFilter: (filter: VerificationStatus | 'all') => void
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({
  summary,
  activeFilter,
  onSelectFilter,
}) => {
  if (!summary) return null

  const cards = [
    {
      id: 'all' as const,
      label: 'Unique Processed',
      count: summary.unique_processed,
      subtitle: summary.duplicates_removed > 0 ? `${summary.duplicates_removed} duplicate(s) merged` : 'All valid lines',
      icon: Inbox,
      className: 'card-total',
      activeBorder: 'border-blue',
    },
    {
      id: 'likely_delivered' as const,
      label: 'Likely to Be Delivered',
      count: summary.likely_delivered,
      subtitle: 'Valid syntax & active mail route',
      icon: CheckCircle2,
      className: 'card-delivered',
      activeBorder: 'border-green',
    },
    {
      id: 'likely_bounce' as const,
      label: 'Likely to Bounce',
      count: summary.likely_bounce,
      subtitle: 'Invalid syntax or missing mail route',
      icon: XCircle,
      className: 'card-bounce',
      activeBorder: 'border-red',
    },
    {
      id: 'unknown' as const,
      label: 'Unknown',
      count: summary.unknown,
      subtitle: 'DNS timeout or resolver error',
      icon: HelpCircle,
      className: 'card-unknown',
      activeBorder: 'border-amber',
    },
  ]

  return (
    <div className="summary-grid">
      {cards.map((card) => {
        const IconComponent = card.icon
        const isSelected = activeFilter === card.id
        return (
          <button
            key={card.id}
            type="button"
            onClick={() => onSelectFilter(card.id)}
            className={`card summary-card ${card.className} ${isSelected ? 'is-selected' : ''}`}
            title={`Click to filter results by ${card.label}`}
          >
            <div className="summary-header">
              <span className="summary-label">{card.label}</span>
              <IconComponent size={20} className="summary-icon" />
            </div>
            <div className="summary-count">{card.count}</div>
            <div className="summary-subtitle">{card.subtitle}</div>
            {isSelected && <div className="selected-indicator">Filter Active</div>}
          </button>
        )
      })}
    </div>
  )
}
