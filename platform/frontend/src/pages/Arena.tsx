import { useMemo, useState } from 'react'

import AlgoRaceBar from '../components/AlgoRaceBar'
import CryptoLoader from '../components/CryptoLoader'
import LiveChart from '../components/LiveChart'
import MetricCard from '../components/MetricCard'
import { useBenchmark } from '../hooks/useBenchmark'
import type { BenchmarkConfig } from '../hooks/useBenchmark'

type Family = 'kem' | 'signature' | 'encryption'

const FAMILY_RULES: Record<
  Family,
  {
    label: string
    operation: string
    classical: string[]
    pqc: string[]
    note: string
  }
> = {
  kem: {
    label: 'Key Exchange / KEM Lab',
    operation: 'key_exchange',
    classical: ['X25519'],
    pqc: ['Kyber-512', 'Kyber-768'],
    note: 'Valid comparison: classical ECDH key exchange vs post-quantum KEM.',
  },
  signature: {
    label: 'Signature Lab',
    operation: 'sign_verify',
    classical: ['ECDSA'],
    pqc: ['Dilithium3', 'ML-DSA-65'],
    note: 'Valid comparison: classical signature vs post-quantum signature.',
  },
  encryption: {
    label: 'Encryption Hybrid Lab',
    operation: 'hybrid_encrypt',
    classical: ['RSA-OAEP-AES'],
    pqc: ['Kyber-AES-Hybrid'],
    note: 'Valid comparison: hybrid envelope encryption baselines only.',
  },
}

export default function Arena() {
  const [family, setFamily] = useState<Family>('kem')
  const [iterations, setIterations] = useState(80)
  const [fileSizeMb, setFileSizeMb] = useState(1)
  const [classicalAlgo, setClassicalAlgo] = useState(FAMILY_RULES.kem.classical[0])
  const [pqcAlgo, setPqcAlgo] = useState(FAMILY_RULES.kem.pqc[0])

  const { data, loading, error, run } = useBenchmark()

  const rules = FAMILY_RULES[family]

  const config: BenchmarkConfig = {
    experiment_family: family,
    classical_algo: classicalAlgo,
    pqc_algo: pqcAlgo,
    operation: rules.operation,
    iterations,
    file_size_mb: fileSizeMb,
  }

  const chart = useMemo(
    () =>
      (data?.classical?.timeseries || []).map((v: number, i: number) => ({
        i,
        classical: v,
        pqc: data?.pqc?.timeseries?.[i] ?? 0,
      })),
    [data],
  )

  const onFamilyChange = (nextFamily: Family) => {
    setFamily(nextFamily)
    setClassicalAlgo(FAMILY_RULES[nextFamily].classical[0])
    setPqcAlgo(FAMILY_RULES[nextFamily].pqc[0])
  }

  const downloadRunJson = () => {
    if (!data) return
    const exportPayload = {
      family,
      algorithms: [classicalAlgo, pqcAlgo],
      iterations,
      warmup_runs: data?.config?.warmup_runs ?? 5,
      file_size_mb: data?.config?.file_size_mb ?? null,
      results: data,
      methodology: data?.methodology ?? {},
    }
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], {
      type: 'application/json',
    })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `arena_${family}_${Date.now()}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <section className="page-grid">
      <article className="panel">
        <div className="panel-head">
          <h2>Algorithm Arena</h2>
          <p>Family-based benchmarking with strict valid-comparison controls</p>
        </div>

        <div className="control-grid">
          <label>
            Experiment family
            <select value={family} onChange={(e) => onFamilyChange(e.target.value as Family)}>
              <option value="kem">Key Exchange / KEM Lab</option>
              <option value="signature">Signature Lab</option>
              <option value="encryption">Encryption Hybrid Lab</option>
            </select>
          </label>
          <label>
            Classical baseline
            <select value={classicalAlgo} onChange={(e) => setClassicalAlgo(e.target.value)}>
              {rules.classical.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            PQC baseline
            <select value={pqcAlgo} onChange={(e) => setPqcAlgo(e.target.value)}>
              {rules.pqc.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
          <label>
            Operation class
            <input value={rules.operation} readOnly />
          </label>
          <label>
            Iterations
            <input
              type="number"
              min={5}
              max={500}
              value={iterations}
              onChange={(e) => setIterations(Number(e.target.value) || 5)}
            />
          </label>
          {family === 'encryption' ? (
            <label>
              Payload size (MB)
              <input
                type="number"
                min={1}
                max={100}
                value={fileSizeMb}
                onChange={(e) => setFileSizeMb(Number(e.target.value) || 1)}
              />
            </label>
          ) : (
            <label>
              Payload class
              <input value={family === 'kem' ? 'N/A for KEM benchmark' : 'Fixed 1KB message'} readOnly />
            </label>
          )}
        </div>

        <p className="metric-hint">{rules.note}</p>

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
              label="Median Latency Gap"
              value={`${data.comparative.latency_gap_ms} ms`}
              hint={`P95 gap ${data.comparative.p95_gap_ms} ms`}
            />
            <MetricCard
              label="Throughput Ratio"
              value={`${data.comparative.throughput_ratio}x`}
              hint={`Unit ${data.comparative.throughput_unit}`}
            />
          </div>

          <AlgoRaceBar label="Median Latency" classical={data.classical.median_ms} pqc={data.pqc.median_ms} />

          <div className="metric-grid">
            <MetricCard
              label={`${data.classical.algo} Throughput`}
              value={`${data.classical.throughput_value} ${data.classical.throughput_unit}`}
              hint={`${data.pqc.algo}: ${data.pqc.throughput_value} ${data.pqc.throughput_unit}`}
            />
          </div>

          <div className="metric-grid">
            <MetricCard
              label={`${data.classical.algo} Stats`}
              value={`med ${data.classical.median_ms} ms`}
              hint={`p95 ${data.classical.p95_ms} ms, stddev ${data.classical.stddev_ms} ms`}
            />
            <MetricCard
              label={`${data.pqc.algo} Stats`}
              value={`med ${data.pqc.median_ms} ms`}
              hint={`p95 ${data.pqc.p95_ms} ms, stddev ${data.pqc.stddev_ms} ms`}
            />
            <MetricCard
              label="Overhead"
              value={`CT +${data.classical.ciphertext_overhead_bytes}B`}
              hint={`PQC cap/sig +${data.pqc.capsule_signature_overhead_bytes}B`}
            />
          </div>

          <LiveChart data={chart} />

          <article className="panel">
            <div className="panel-head">
              <h3>Methodology</h3>
              <p>Run context and measurement basis for defensible comparisons</p>
            </div>
            <ul className="notes-list">
              <li>
                Machine: {data.methodology.machine_specs.system} {data.methodology.machine_specs.release},{' '}
                {data.methodology.machine_specs.machine}, CPU count {data.methodology.machine_specs.cpu_count}
              </li>
              <li>Python version: {data.methodology.python_version}</li>
              <li>Backend version: {data.methodology.backend_version}</li>
              <li>Iterations: {data.methodology.iterations}</li>
              <li>Warm-up runs: {data.methodology.warmup_runs}</li>
              <li>Payload size: {data.methodology.payload_size_mb == null ? 'N/A' : `${data.methodology.payload_size_mb} MB`}</li>
              <li>Primary metric: {data.methodology.measurement_basis.primary_metric}</li>
              <li>P95 metric: {data.methodology.measurement_basis.p95_metric}</li>
              <li>Timing boundary: {data.methodology.measurement_basis.timing_boundary}</li>
            </ul>
            <button className="btn-ghost" onClick={downloadRunJson}>
              Export Run JSON
            </button>
          </article>

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
