import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function AttackCurve({ data }: { data: Array<{ bits: number; classical: number; quantum: number }> }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-head">
        <h3>Complexity Curve</h3>
        <p>Classical vs quantum work factor trend</p>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="bits" stroke="var(--text-muted)" tickLine={false} />
          <YAxis stroke="var(--text-muted)" tickLine={false} />
          <Tooltip
            contentStyle={{
              background: '#0f1720',
              border: '1px solid #2f3d48',
              color: '#dce9f2',
              borderRadius: 10,
            }}
          />
          <Line type="monotone" dataKey="classical" stroke="var(--danger)" dot={false} strokeWidth={2} />
          <Line type="monotone" dataKey="quantum" stroke="var(--accent)" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}
