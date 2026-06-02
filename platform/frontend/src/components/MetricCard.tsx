import type { ReactNode } from 'react'

type Props = {
  label: string
  value: ReactNode
  hint?: string
  tone?: 'neutral' | 'good' | 'warn'
  formula?: string[]
}

export default function MetricCard({ label, value, hint, tone = 'neutral', formula }: Props) {
  return (
    <article className={`metric-card tone-${tone}${formula ? ' has-formula' : ''}`}>
      <div className="metric-topline">
        <p className="metric-label">{label}</p>
        {formula && (
          <div className="metric-formula-wrap">
            <button type="button" className="metric-formula-chip" aria-label={`${label} formula`}>
              Formula
            </button>
            <div className="metric-formula-popover" role="note" aria-label={`${label} formula`}>
              <p className="metric-formula-title">How this is calculated</p>
              {formula.map((line) => (
                <p key={line} className="metric-formula-line">
                  {line}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
      <p className="metric-value">{value}</p>
      {hint && <p className="metric-hint">{hint}</p>}
    </article>
  )
}
