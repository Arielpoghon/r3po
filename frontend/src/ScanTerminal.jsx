import { useEffect, useRef, useState } from 'react'

const logLines = [
  '$ git clone --depth 1 <repo>',
  'Cloning into temporary workspace...',
  'Checking repository size...',
  '$ trivy fs .',
  'Scanning dependencies for known CVEs...',
  '$ gitleaks detect',
  'Scanning files for leaked secrets...',
  '$ semgrep --config=auto',
  'Running static analysis rules...',
  'Aggregating findings...',
]

export default function ScanTerminal({ active }) {
  const [visibleLines, setVisibleLines] = useState([])
  const timers = useRef([])

  useEffect(() => {
    timers.current.forEach(clearTimeout)
    timers.current = []
    setVisibleLines([])
    if (!active) return undefined

    logLines.forEach((line, index) => {
      const timer = setTimeout(() => {
        setVisibleLines(lines => [...lines, line])
      }, index * 900)
      timers.current.push(timer)
    })
    return () => {
      timers.current.forEach(clearTimeout)
      timers.current = []
      setVisibleLines([])
    }
  }, [active])

  if (!active) return null
  return <section className="scan-terminal" role="status" aria-live="polite" aria-label="Repository scan in progress">
    <div className="terminal-bar"><span className="terminal-dots" aria-hidden="true"><i /><i /><i /></span><span>r3po — scanning</span></div>
    <div className="terminal-body">
      {visibleLines.map((line, index) => <div className="terminal-line" key={`${index}-${line}`}>{line}</div>)}
      <span className="terminal-cursor" aria-hidden="true">█</span>
    </div>
  </section>
}
