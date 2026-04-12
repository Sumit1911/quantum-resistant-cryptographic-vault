export default function AlgoRaceBar({ label, classical, pqc }: { label: string; classical: number; pqc: number }) {
  const max = Math.max(classical, pqc, 1)

  return (
    <section className="panel">
      <div className="panel-head">
        <h3>{label}</h3>
        <p>Relative normalized performance</p>
      </div>

      <div className="race-line">
        <div className="race-label">Classical</div>
        <div className="race-track">
          <div className="race-fill classical" style={{ width: `${(classical / max) * 100}%` }} />
        </div>
        <div className="race-number">{classical.toFixed(3)} ms</div>
      </div>

      <div className="race-line">
        <div className="race-label">PQC</div>
        <div className="race-track">
          <div className="race-fill pqc" style={{ width: `${(pqc / max) * 100}%` }} />
        </div>
        <div className="race-number">{pqc.toFixed(3)} ms</div>
      </div>
    </section>
  )
}
