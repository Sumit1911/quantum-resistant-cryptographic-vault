import { useMemo, useState } from 'react'

import AttackCurve from '../components/AttackCurve'
import CryptoLoader from '../components/CryptoLoader'
import MetricCard from '../components/MetricCard'
import RiskTimeline from '../components/RiskTimeline'
import { useAttack } from '../hooks/useAttack'

export default function AttackLab() {
  const [mode, setMode] = useState<'shors' | 'grovers' | 'lattice' | 'harvest'>('shors')
  const [keySize, setKeySize] = useState(2048)
  const [algorithm, setAlgorithm] = useState('AES-128')
  const [dimension, setDimension] = useState(768)
  const [yearsToProtect, setYearsToProtect] = useState(15)
  const [dataValue, setDataValue] = useState('high')

  const { data, loading, error, runShors, runGrovers, runLattice, runHarvestRisk } = useAttack()

  const chart = useMemo(() => {
    if (!data?.classical_curve || !data?.quantum_curve) {
      return []
    }
    return (data.classical_curve || []).map((point: [number, number], i: number) => ({
      bits: point[0],
      classical: point[1],
      quantum: data?.quantum_curve?.[i]?.[1] ?? 0,
    }))
  }, [data])

  const runCurrent = () => {
    if (mode === 'shors') {
      runShors(keySize)
      return
    }
    if (mode === 'grovers') {
      runGrovers(algorithm)
      return
    }
    if (mode === 'harvest') {
      runHarvestRisk(yearsToProtect, dataValue)
      return
    }
    runLattice(dimension)
  }

  return (
    <section className="page-grid">
      <article className="panel">
        <div className="panel-head">
          <h2>Attack Lab</h2>
          <p>Simulate practical quantum pressure against deployed cryptosystems</p>
        </div>

        <div className="tab-row">
          <button className={mode === 'shors' ? 'tab-active' : 'tab'} onClick={() => setMode('shors')}>
            Shor
          </button>
          <button className={mode === 'grovers' ? 'tab-active' : 'tab'} onClick={() => setMode('grovers')}>
            Grover
          </button>
          <button className={mode === 'lattice' ? 'tab-active' : 'tab'} onClick={() => setMode('lattice')}>
            Lattice SVP
          </button>
          <button className={mode === 'harvest' ? 'tab-active' : 'tab'} onClick={() => setMode('harvest')}>
            HNDL
          </button>
        </div>

        {mode === 'shors' && (
          <label>
            RSA key size
            <input type="number" value={keySize} onChange={(e) => setKeySize(Number(e.target.value) || 2048)} />
          </label>
        )}

        {mode === 'grovers' && (
          <label>
            Symmetric/hash target
            <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
              <option value="AES-128">AES-128</option>
              <option value="AES-192">AES-192</option>
              <option value="AES-256">AES-256</option>
              <option value="SHA-256">SHA-256</option>
            </select>
          </label>
        )}

        {mode === 'lattice' && (
          <label>
            Lattice dimension
            <input type="number" value={dimension} onChange={(e) => setDimension(Number(e.target.value) || 768)} />
          </label>
        )}

        {mode === 'harvest' && (
          <div className="control-grid">
            <label>
              Years to protect
              <input
                type="number"
                min={1}
                max={50}
                value={yearsToProtect}
                onChange={(e) => setYearsToProtect(Number(e.target.value) || 15)}
              />
            </label>
            <label>
              Data value
              <select value={dataValue} onChange={(e) => setDataValue(e.target.value)}>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </label>
          </div>
        )}

        <button className="btn-primary" onClick={runCurrent}>
          {loading ? 'Simulating...' : 'Run Simulation'}
        </button>
        {error && <p className="error-text">{error}</p>}
        {loading && <CryptoLoader label="Modeling quantum attack progression..." />}
      </article>

      {data && (
        <>
          <div className="metric-grid">
            <MetricCard label="Mode" value={String(data.mode).toUpperCase()} hint="Current simulation family" />
            <MetricCard
              label="Verdict"
              value={String(data.verdict).toUpperCase()}
              hint={data.mode === 'grovers' ? data.recommendation : data.explanation || data.summary}
              tone={data.verdict === 'BROKEN' || data.verdict === 'WEAKENED' ? 'warn' : 'good'}
            />
            {data.mode === 'shors' && (
              <MetricCard
                label="Break Ratio"
                value={`${Number(data.break_ratio).toExponential(2)}`}
                hint={`${data.snapshot.classical_notation} vs ${data.snapshot.quantum_notation}`}
                tone="warn"
              />
            )}
            {data.mode === 'grovers' && (
              <MetricCard
                label="Bit Reduction"
                value={`${data.effective_reduction_percent}%`}
                hint={`Classical ${data.classical_bits} -> Quantum ${data.post_grover_bits}`}
              />
            )}
            {data.mode === 'lattice' && (
              <MetricCard
                label="Security Level"
                value={`${data.security_level} bits`}
                hint={`BKZ block size ${data.bkz_block_size}`}
                tone="good"
              />
            )}
            {data.mode === 'harvest' && (
              <MetricCard
                label="Risk Horizon"
                value={`${data.risk_horizon_percent}%`}
                hint={`Today ${data.risk_today_percent}%`}
                tone={data.risk_horizon_percent >= 70 ? 'warn' : 'good'}
              />
            )}
          </div>

          {data.classical_curve && data.quantum_curve && <AttackCurve data={chart} />}

          {data.mode === 'grovers' && (
            <article className="panel">
              <div className="panel-head">
                <h3>Security Bars</h3>
                <p>Post-Grover impact against 128-bit safety threshold</p>
              </div>
              <div className="bars-grid">
                {(data.bars || []).map((bar: { label: string; bits: number }) => (
                  <div className="bar-item" key={bar.label}>
                    <p>{bar.label}</p>
                    <strong>{bar.bits} bits</strong>
                  </div>
                ))}
              </div>
            </article>
          )}

          {data.mode === 'harvest' && (
            <>
              <RiskTimeline data={data.risk_curve || []} />
              <article className="panel">
                <div className="panel-head">
                  <h3>Harvest-Now Assessment</h3>
                  <p>Long-term confidentiality exposure estimate</p>
                </div>
                <div className="bars-grid">
                  <div className="bar-item">
                    <p>Compromise Estimate</p>
                    <strong>
                      {data.compromise_year_estimate ? `Year ${data.compromise_year_estimate}` : 'No trigger'}
                    </strong>
                  </div>
                  <div className="bar-item">
                    <p>Recommendation</p>
                    <strong>{data.recommendation}</strong>
                  </div>
                </div>
              </article>
            </>
          )}
        </>
      )}
    </section>
  )
}
