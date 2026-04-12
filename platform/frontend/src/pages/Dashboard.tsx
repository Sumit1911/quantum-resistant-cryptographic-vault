import { Link } from 'react-router-dom'

import MetricCard from '../components/MetricCard'

export default function Dashboard() {
  return (
    <section className="page-grid">
      <article className="hero panel">
        <p className="hero-kicker">Research-first cryptography workspace</p>
        <h2>Quantify quantum risk, compare algorithmic tradeoffs, and visualize vault internals.</h2>
        <p>
          This platform combines benchmarking, attack simulation, and instrumentation traces so your final-year report
          can move from screenshots to defendable performance evidence.
        </p>
        <div className="hero-actions">
          <Link to="/arena" className="btn-primary">
            Run Algorithm Arena
          </Link>
          <Link to="/attack" className="btn-ghost">
            Open Attack Lab
          </Link>
          <Link to="/vault" className="btn-ghost">
            Analyze Vault Flow
          </Link>
        </div>
      </article>

      <div className="metric-grid">
        <MetricCard
          label="Research Dimensions"
          value="3 Labs"
          hint="Benchmarking, attack modeling, and cryptographic flow instrumentation"
        />
        <MetricCard
          label="Quantum Readiness"
          value="128-192 bits"
          hint="Configurable PQC profile from Kyber-512 to Kyber-768 and Dilithium variants"
          tone="good"
        />
        <MetricCard
          label="Telemetry Richness"
          value="Latency + Risk + Energy"
          hint="Beyond avg timing: p95, variance, throughput, memory and exposure markers"
        />
      </div>

      <article className="panel">
        <div className="panel-head">
          <h3>How To Use This For Research</h3>
          <p>Recommended experimental path</p>
        </div>
        <ol className="ordered-list">
          <li>Run Arena with multiple algorithm pairs and extract speedup + p95 + quantum risk deltas.</li>
          <li>Run Attack Lab across Shor, Grover, and lattice modes to justify threat assumptions.</li>
          <li>Use Vault Lens to analyze overhead behavior as payload size grows.</li>
        </ol>
      </article>
    </section>
  )
}
