import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

type RiskPoint = { year: number; risk: number }

export default function RiskTimeline({ data }: { data: RiskPoint[] }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-head">
        <h3>Harvest-Now Risk Timeline</h3>
        <p>Estimated probability growth of future compromise</p>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="year" stroke="var(--text-muted)" tickLine={false} />
          <YAxis stroke="var(--text-muted)" tickLine={false} domain={[0, 100]} />
          <Tooltip
            contentStyle={{
              background: '#0f1720',
              border: '1px solid #2f3d48',
              color: '#dce9f2',
              borderRadius: 10,
            }}
          />
          <Line type="monotone" dataKey="risk" stroke="var(--accent-2)" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}
