import { useMemo, useState } from 'react'

import AlgoRaceBar from '../components/AlgoRaceBar'
import CryptoLoader from '../components/CryptoLoader'
import LiveChart from '../components/LiveChart'
import MetricCard from '../components/MetricCard'
import { useBenchmark } from '../hooks/useBenchmark'
import type { BenchmarkConfig } from '../hooks/useBenchmark'

const classicalOptions = ['RSA-2048', 'RSA-4096', 'ECDSA', 'X25519']
const pqcOptions = ['Kyber-512', 'Kyber-768', 'Dilithium2', 'Dilithium3']
const operations = ['keygen', 'encrypt', 'sign', 'verify']

export default function Arena() {
  const [config, setConfig] = useState<BenchmarkConfig>({
    classical_algo: 'RSA-2048',
    pqc_algo: 'Kyber-512',
    operation: 'keygen',
    iterations: 80,
    file_size_mb: 1,
  })

  const { data, loading, error, run } = useBenchmark()

  const chart = useMemo(
    () =>
      (data?.classical?.timeseries || []).map((v: number, i: number) => ({
        i,
        classical: v,
        pqc: data?.pqc?.timeseries?.[i] ?? 0,
      })),
    [data],
  )

  return (
    <section className="page-grid">
      <article className="panel">
        <div className="panel-head">
          <h2>Algorithm Arena</h2>
          <p>Controlled benchmark race with expanded research telemetry</p>
        </div>
        <div className="control-grid">
          <label>
            Classical
            <select
              value={config.classical_algo}
              onChange={(e) => setConfig((p) => ({ ...p, classical_algo: e.target.value }))}
            >
              {classicalOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            PQC
            <select value={config.pqc_algo} onChange={(e) => setConfig((p) => ({ ...p, pqc_algo: e.target.value }))}>
              {pqcOptions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            Operation
            <select value={config.operation} onChange={(e) => setConfig((p) => ({ ...p, operation: e.target.value }))}>
              {operations.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            Iterations
            <input
              type="number"
              min={5}
              max={500}
              value={config.iterations}
              onChange={(e) => setConfig((p) => ({ ...p, iterations: Number(e.target.value) || 5 }))}
            />
          </label>
          <label>
            File Size (MB)
            <input
              type="number"
              min={1}
              max={100}
              value={config.file_size_mb}
              onChange={(e) => setConfig((p) => ({ ...p, file_size_mb: Number(e.target.value) || 1 }))}
            />
          </label>
        </div>
        <button className="btn-primary" onClick={() => run(config)}>
          {loading ? 'Running benchmark...' : 'Run Benchmark Race'}
        </button>
        {error && <p className="error-text">{error}</p>}
        {loading && <CryptoLoader label="Profiling classical and PQC branches..." />}
      </article>

      {data && (
        <>
          <div className="metric-grid">
            <MetricCard
              label="Winner"
              value={String(data.winner).toUpperCase()}
              hint={`Speedup ${data.speedup_factor}x`}
              tone={data.winner === 'pqc' ? 'good' : 'warn'}
            />
            <MetricCard
              label="Energy Reduction"
              value={`${data.energy_reduction_percent}%`}
              hint="Estimated operation energy delta"
              tone="good"
            />
            <MetricCard
              label="Latency Gap"
              value={`${data.comparative.latency_gap_ms} ms`}
              hint={`P95 gap ${data.comparative.p95_gap_ms} ms`}
            />
          </div>

          <AlgoRaceBar label="Average Latency" classical={data.classical.avg_ms} pqc={data.pqc.avg_ms} />

          <div className="metric-grid">
            <MetricCard
              label={`${data.classical.algo} Quantum Risk`}
              value={`${data.classical.quantum_risk_score}/100`}
              hint={`Memory ${data.classical.memory_kb} KB`}
              tone="warn"
            />
            <MetricCard
              label={`${data.pqc.algo} Quantum Risk`}
              value={`${data.pqc.quantum_risk_score}/100`}
              hint={`Memory ${data.pqc.memory_kb} KB`}
              tone="good"
            />
            <MetricCard
              label="Throughput Ratio"
              value={`${data.comparative.throughput_ratio}x`}
              hint="PQC throughput relative to classical"
            />
          </div>

          <LiveChart data={chart} />

          <article className="panel">
            <div className="panel-head">
              <h3>Research Notes</h3>
              <p>Auto-generated interpretation from run metadata</p>
            </div>
            <ul className="notes-list">
              {(data.research_insights || []).map((line: string) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </article>
        </>
      )}
    </section>
  )
}
