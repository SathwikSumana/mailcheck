export type VerificationStatus = 'likely_delivered' | 'likely_bounce' | 'unknown'

export interface VerificationResult {
  email: string
  status: VerificationStatus
  reason: string
  checks_performed: string[]
}

export interface VerificationSummary {
  total_submitted: number
  unique_processed: number
  duplicates_removed: number
  likely_delivered: number
  likely_bounce: number
  unknown: number
}

export interface VerificationResponse {
  results: VerificationResult[]
  summary: VerificationSummary
  error?: string
}

export interface HealthResponse {
  status: string
  service: string
  max_batch_size: number
  version: string
}
