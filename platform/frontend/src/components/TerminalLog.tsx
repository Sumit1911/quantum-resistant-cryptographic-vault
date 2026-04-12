type Props = { lines: string[] }

export default function TerminalLog({ lines }: Props) {
  return (
    <section className="panel terminal">
      <div className="panel-head">
        <h3>Execution Log</h3>
        <p>Ordered instrumentation events</p>
      </div>
      <div className="terminal-scroll">
        {lines.map((line, idx) => (
          <div key={idx} className="terminal-line">
            <span className="terminal-index">{String(idx + 1).padStart(2, '0')}</span>
            <span>{line}</span>
          </div>
        ))}
      </div>
    </section>
  )
}
