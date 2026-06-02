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

  const verdictFormula =
    !data
      ? undefined
      : data.mode === 'shors'
        ? [
            'if break_ratio_model >= 1e12 -> highly_exposed',
            'else if break_ratio_model >= 1e6 -> degraded',
            'else -> not_broken_in_model',
            `current break_ratio_model = ${Number(data.break_ratio_model).toExponential(2)}`,
          ]
        : data.mode === 'grovers'
          ? [
              'if post_grover_bits < 128 -> weakened',
              'else -> resilient_in_model',
              `current post_grover_bits = ${data.post_grover_bits}`,
            ]
          : data.mode === 'lattice'
            ? [
                'if security_band_model >= 192 -> resilient_in_model',
                'else if security_band_model >= 128 -> degraded',
                'else -> highly_exposed',
                `current security_band_model = ${data.security_band_model}`,
              ]
            : [
                'if risk_horizon_percent >= 70 -> migration_advised',
                'else if risk_horizon_percent >= 45 -> weakened',
                'else -> resilient_in_model',
                `current risk_horizon_percent = ${data.risk_horizon_percent}%`,
              ]

  const primaryMetricFormula =
    !data
      ? undefined
      : data.mode === 'shors'
        ? [
            'classical_ops = 2^(key_bits / 18)',
            'quantum_ops = 2^((log2(key_bits)) * 2.5)',
            'break_ratio_model = classical_ops / quantum_ops',
            `${data.snapshot.classical_notation} / ${data.snapshot.quantum_notation} = ${Number(data.break_ratio_model).toExponential(2)}`,
          ]
        : data.mode === 'grovers'
          ? [
              'post_grover_bits = floor(classical_bits / 2)',
              'bit_reduction_percent = 100 * (1 - post_grover_bits / classical_bits)',
              `100 * (1 - ${data.post_grover_bits} / ${data.classical_bits}) = ${data.effective_reduction_percent}%`,
            ]
          : data.mode === 'lattice'
            ? [
                'bkz_proxy = max(180, floor(0.76 * dimension))',
                'security band = 128 if n <= 512, 192 if n <= 768, else 256',
                `dimension ${data.dimension} -> bkz_proxy ${data.bkz_block_size_proxy} -> security band ${data.security_band_model}`,
              ]
            : [
                'baseline = 100 / (1 + exp(-0.35 * (year - 9)))',
                'adjusted_risk = min(100, baseline * value_multiplier)',
                `horizon risk = ${data.risk_horizon_percent}% using value "${data.data_value}"`,
              ]

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
              formula={verdictFormula}
            />
            {data.mode === 'shors' && (
              <MetricCard
                label="Break Ratio (model)"
                value={`${Number(data.break_ratio_model).toExponential(2)}`}
                hint={`${data.snapshot.classical_notation} vs ${data.snapshot.quantum_notation}`}
                tone="warn"
                formula={primaryMetricFormula}
              />
            )}
            {data.mode === 'grovers' && (
              <MetricCard
                label="Bit Reduction"
                value={`${data.effective_reduction_percent}%`}
                hint={`Classical ${data.classical_bits} -> Quantum ${data.post_grover_bits}`}
                formula={primaryMetricFormula}
              />
            )}
            {data.mode === 'lattice' && (
              <MetricCard
                label="Security Band (model)"
                value={`${data.security_band_model} bits`}
                hint={`BKZ proxy ${data.bkz_block_size_proxy}`}
                tone="good"
                formula={primaryMetricFormula}
              />
            )}
            {data.mode === 'harvest' && (
              <MetricCard
                label="Risk Horizon"
                value={`${data.risk_horizon_percent}%`}
                hint={`Today ${data.risk_today_percent}%`}
                tone={data.risk_horizon_percent >= 70 ? 'warn' : 'good'}
                formula={primaryMetricFormula}
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
