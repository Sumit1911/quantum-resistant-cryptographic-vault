import { useState } from 'react'

import CryptoLoader from '../components/CryptoLoader'
import FlowVisualizer from '../components/FlowVisualizer'
import MetricCard from '../components/MetricCard'
import TerminalLog from '../components/TerminalLog'
import { useVault } from '../hooks/useVault'
import type { VaultEncryptRequest } from '../hooks/useVault'

async function toBase64(file: File): Promise<string> {
  return await new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const value = String(reader.result || '')
      const comma = value.indexOf(',')
      resolve(comma >= 0 ? value.slice(comma + 1) : value)
    }
    reader.onerror = () => reject(new Error('Failed to read file'))
    reader.readAsDataURL(file)
  })
}

export default function Vault() {
  const [inputKind, setInputKind] = useState<'text' | 'file'>('text')
  const [plaintext, setPlaintext] = useState(
    'Post-quantum secure payload for instrumentation and research analysis.',
  )
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [algorithm, setAlgorithm] = useState('Kyber-512')
  const [signing, setSigning] = useState('Dilithium3')

  const { data, loading, error, encrypt } = useVault()

  const runFlow = async () => {
    const payload: VaultEncryptRequest = {
      input_kind: inputKind,
      algorithm,
      signing,
    }

    if (inputKind === 'text') {
      payload.plaintext = plaintext
      payload.item_name = 'text_payload.txt'
      payload.mime_type = 'text/plain'
    } else {
      if (!selectedFile) {
        return
      }
      payload.content_base64 = await toBase64(selectedFile)
      payload.item_name = selectedFile.name
      payload.mime_type = selectedFile.type || 'application/octet-stream'
    }

    await encrypt(payload)
  }

  return (
    <section className="page-grid">
      <article className="panel">
        <div className="panel-head">
          <h2>Vault Lens</h2>
          <p>Real backend crypto flow: encrypt, sign, store, verify, decrypt</p>
        </div>

        <div className="tab-row">
          <button className={inputKind === 'text' ? 'tab-active' : 'tab'} onClick={() => setInputKind('text')}>
            Text
          </button>
          <button className={inputKind === 'file' ? 'tab-active' : 'tab'} onClick={() => setInputKind('file')}>
            File
          </button>
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
              <option value="Dilithium3">Dilithium3</option>
              <option value="ML-DSA-65">ML-DSA-65</option>
            </select>
          </label>
        </div>

        {inputKind === 'text' ? (
          <label>
            Plaintext payload
            <textarea value={plaintext} onChange={(e) => setPlaintext(e.target.value)} rows={6} />
          </label>
        ) : (
          <label>
            Upload file payload
            <input
              type="file"
              onChange={(e) => setSelectedFile(e.target.files && e.target.files[0] ? e.target.files[0] : null)}
            />
          </label>
        )}

        <button className="btn-primary" onClick={runFlow}>
          {loading ? 'Running live crypto flow...' : 'Encrypt & Inspect Live Flow'}
        </button>
        {error && <p className="error-text">{error}</p>}
        {loading && <CryptoLoader label="Executing KEM, AEAD, signature, DB and verification pipeline..." />}
      </article>

      {data && (
        <>
          <div className="metric-grid">
            <MetricCard
              label="Total Time"
              value={`${data.total_ms} ms`}
              hint={`${data.algorithm} + ${data.signing} (${data.input_kind})`}
            />
            <MetricCard
              label="Quantum Readiness"
              value={`${data.metrics.quantum_readiness_score}/100`}
              hint={`Tamper gate ${data.metrics.tamper_detection_window_ms} ms`}
              tone="good"
            />
            <MetricCard
              label="Flow Check"
              value={data.metrics.recovered_matches_input ? 'ROUNDTRIP OK' : 'MISMATCH'}
              hint={`item_id ${data.item_id}`}
              tone={data.metrics.recovered_matches_input ? 'good' : 'warn'}
            />
          </div>

          <div className="metric-grid">
            <MetricCard
              label="Payload Size"
              value={`${data.metrics.plaintext_size} bytes`}
              hint={`Ciphertext ${data.metrics.ciphertext_size} bytes`}
            />
            <MetricCard
              label="PQC Overhead"
              value={`${data.metrics.overhead_percent}%`}
              hint={`Capsule ${data.metrics.capsule_size}B · Signature ${data.metrics.signature_size}B`}
            />
            <MetricCard
              label="Throughput"
              value={`${data.metrics.throughput_mbps} MB/s`}
              hint={`Total overhead ${data.metrics.overhead_bytes} bytes`}
            />
          </div>

          <FlowVisualizer steps={data.steps || []} />
          <TerminalLog
            lines={(data.steps || []).map(
              (step: any, idx: number) =>
                `${idx + 1}. ${step.name} :: ${step.duration_ms} ms :: ${step.output_size ?? '-'} bytes :: ${step.detail || ''}`,
            )}
          />

          <article className="panel">
            <div className="panel-head">
              <h3>Research Notes</h3>
              <p>Live backend flow interpretation</p>
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
