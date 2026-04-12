import { motion } from 'framer-motion'

export default function CryptoLoader({ label = 'Running cryptographic simulation...' }: { label?: string }) {
  return (
    <section className="loader-wrap">
      <div className="loader-core">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="loader-ring"
            animate={{ rotate: 360 }}
            transition={{ duration: 2.2 + i * 0.45, ease: 'linear', repeat: Infinity }}
            style={{ width: 42 + i * 18, height: 42 + i * 18 }}
          />
        ))}
        <motion.div
          className="loader-glyph"
          animate={{ opacity: [0.5, 1, 0.5], scale: [0.97, 1.04, 0.97] }}
          transition={{ duration: 1.2, repeat: Infinity }}
        >
          PQ
        </motion.div>
      </div>
      <p>{label}</p>
    </section>
  )
}
