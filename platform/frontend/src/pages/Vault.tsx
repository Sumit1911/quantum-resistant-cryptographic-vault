import { useState } from 'react'

import CryptoLoader from '../components/CryptoLoader'
import FlowVisualizer from '../components/FlowVisualizer'
import MetricCard from '../components/MetricCard'
import TerminalLog from '../components/TerminalLog'
import { useVault } from '../hooks/useVault'

export default function Vault() {
  const [plaintext, setPlaintext] = useState(
    'Post-quantum secure payload for instrumentation and research analysis.',
  )
  const [algorithm, setAlgorithm] = useState('Kyber-512')
  const [signing, setSigning] = useState('Dilithium3')

  const { data, loading, error, encrypt } = useVault()

  return (
    <section className="page-grid">
      <article className="panel">
        <div className="panel-head">
          <h2>Vault Lens</h2>
          <p>Inspect encryption pipeline internals and overhead tradeoffs</p>
        </div>

        <div className="control-grid">
          <label>
            KEM Algorithm
            <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
              <option value="Kyber-512">Kyber-512</option>
              <option value="Kyber-768">Kyber-768</option>
            </select>
          </label>
          <label>
            Signature Scheme
            <select value={signing} onChange={(e) => setSigning(e.target.value)}>
              <option value="Dilithium2">Dilithium2</option>
              <option value="Dilithium3">Dilithium3</option>
              <option value="ML-DSA-65">ML-DSA-65</option>
            </select>
          </label>
        </div>

        <label>
          Plaintext payload
          <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} rows={6} />
        </label>
        <button className="btn-primary" onClick={() => encrypt(plaintext, algorithm, signing)}>
          {loading ? 'Running instrumentation...' : 'Encrypt & Inspect Pipeline'}
        </button>
        {error && <p className="error-text">{error}</p>}
        {loading && <CryptoLoader label="Executing KEM, AEAD and signature pipeline..." />}
      </article>

      {data && (
        <>
          <div className="metric-grid">
            <MetricCard label="Total Time" value={`${data.total_ms} ms`} hint={`${data.algorithm} + ${data.signing}`} />
            <MetricCard
              label="Quantum Readiness"
              value={`${data.metrics.quantum_readiness_score}/100`}
              hint={`Tamper gate ${data.metrics.tamper_detection_window_ms} ms`}
              tone="good"
            />
            <MetricCard
              label="Throughput"
              value={`${data.metrics.throughput_mbps} MB/s`}
              hint={`Payload ${data.metrics.plaintext_size} bytes`}
            />
          </div>

          <div className="metric-grid">
            <MetricCard
              label="Ciphertext Size"
              value={`${data.metrics.ciphertext_size} bytes`}
              hint={`AES tag included`}
            />
            <MetricCard
              label="Signature Overhead"
              value={`${data.metrics.signature_size} bytes`}
              hint={`Capsule ${data.metrics.capsule_size} bytes`}
            />
            <MetricCard
              label="Total Overhead"
              value={`${data.metrics.overhead_percent}%`}
              hint={`${data.metrics.overhead_bytes} bytes extra`}
            />
          </div>

          <FlowVisualizer steps={data.steps || []} />
          <TerminalLog
            lines={(data.steps || []).map(
              (step: any, idx: number) =>
                `${idx + 1}. ${step.name} :: ${step.duration_ms} ms :: ${step.output_size ?? '-'} bytes`,
            )}
          />

          <article className="panel">
            <div className="panel-head">
              <h3>Research Notes</h3>
              <p>Contextual interpretation from the instrumentation model</p>
            </div>
            <ul className="notes-list">
              {(data.research_notes || []).map((line: string) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </article>
        </>
      )}
    </section>
  )
}
