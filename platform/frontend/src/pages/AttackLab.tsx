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
          <h3>Threat Model Scope</h3>
          <p>These outputs are model-driven research views, not direct break-time forecasts.</p>
        </div>
        <ul className="notes-list">
          <li>Shor mode: modeled asymptotic exposure pressure for RSA/ECC-like systems.</li>
          <li>Grover mode: modeled search-space reduction for symmetric/hash targets.</li>
          <li>Lattice mode: modeled hardness trend for PQC-style lattice assumptions.</li>
          <li>HNDL mode: relative long-horizon exposure planning model.</li>
        </ul>
      </article>

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
              value={String(data.verdict).replaceAll('_', ' ').toUpperCase()}
              hint={data.mode === 'grovers' ? data.recommendation : data.explanation || data.summary}
              tone={String(data.verdict).includes('exposed') || String(data.verdict).includes('weakened') || String(data.verdict).includes('advised') ? 'warn' : 'good'}
            />
            {data.mode === 'shors' && (
              <MetricCard
                label="Break Ratio (model)"
                value={`${Number(data.break_ratio_model).toExponential(2)}`}
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
                label="Security Band (model)"
                value={`${data.security_band_model} bits`}
                hint={`BKZ proxy ${data.bkz_block_size_proxy}`}
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
                  <p>Relative long-term confidentiality exposure model</p>
                </div>
                <div className="bars-grid">
                  <div className="bar-item">
                    <p>Threshold Crossing Year (model)</p>
                    <strong>
                      {data.threshold_crossing_year_model ? `Year ${data.threshold_crossing_year_model}` : 'No trigger'}
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

          <article className="panel">
            <div className="panel-head">
              <h3>How This Is Computed</h3>
              <p>Formula transparency and model boundaries</p>
            </div>
            {data.formula_panel ? (
              <ul className="notes-list">
                {data.formula_panel.input && <li>Input: {data.formula_panel.input}</li>}
                {data.formula_panel.classical_formula_family && (
                  <li>Classical formula family: {data.formula_panel.classical_formula_family}</li>
                )}
                {data.formula_panel.quantum_formula_family && (
                  <li>Quantum formula family: {data.formula_panel.quantum_formula_family}</li>
                )}
                {data.formula_panel.formula_family && <li>Formula family: {data.formula_panel.formula_family}</li>}
                {data.formula_panel.output_meaning && <li>Output meaning: {data.formula_panel.output_meaning}</li>}
                {data.formula_panel.estimated_vs_measured && (
                  <li>Estimated vs measured: {data.formula_panel.estimated_vs_measured}</li>
                )}
                {data.formula_panel.curve_source && <li>Curve source: {data.formula_panel.curve_source}</li>}
              </ul>
            ) : (
              <p className="metric-hint">No formula panel available for this mode.</p>
            )}
          </article>
        </>
      )}
    </section>
  )
}
