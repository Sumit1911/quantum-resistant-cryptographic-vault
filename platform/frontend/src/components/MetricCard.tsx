type Props = {
  label: string
  value: string
  hint?: string
  tone?: 'neutral' | 'good' | 'warn'
}

export default function MetricCard({ label, value, hint, tone = 'neutral' }: Props) {
  return (
    <article className={`metric-card tone-${tone}`}>
      <p className="metric-label">{label}</p>
      <p className="metric-value">{value}</p>
      {hint && <p className="metric-hint">{hint}</p>}
    </article>
  )
}
