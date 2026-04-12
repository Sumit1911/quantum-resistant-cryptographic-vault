import { motion } from 'framer-motion'

type Step = {
  name: string
  duration_ms: number
  output_size?: number | null
}

export default function FlowVisualizer({ steps }: { steps: Step[] }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <h3>Pipeline Flow</h3>
        <p>Cryptographic processing stages</p>
      </div>
      <div className="flow-grid">
        {steps.map((step, i) => (
          <motion.article
            key={step.name}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className="flow-node"
          >
            <p className="flow-name">{step.name}</p>
            <p className="flow-time">{step.duration_ms.toFixed(3)} ms</p>
            <p className="flow-out">{step.output_size == null ? 'No payload output' : `${step.output_size} bytes`}</p>
          </motion.article>
        ))}
      </div>
    </section>
  )
}
