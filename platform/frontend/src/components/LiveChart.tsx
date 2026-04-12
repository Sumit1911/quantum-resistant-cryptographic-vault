import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

type Point = { i: number; classical: number; pqc: number }

export default function LiveChart({ data }: { data: Point[] }) {
  return (
    <section className="panel chart-panel">
      <div className="panel-head">
        <h3>Latency Evolution</h3>
        <p>Iteration-wise timing profile for both branches</p>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <XAxis dataKey="i" stroke="var(--text-muted)" tickLine={false} />
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
          <Line type="monotone" dataKey="pqc" stroke="var(--accent)" dot={false} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </section>
  )
}
