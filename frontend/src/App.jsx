import { useState } from 'react'
import { scanRepository } from './api'
import ScanTerminal from './ScanTerminal'
import MouseBackground from './MouseBackground'

const severityRank = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }
const logo = [' ____  _____ ____   ___', '|  _ \\|___ /|  _ \\ / _ \\', '| |_) | |_ \\| |_) | | | |', '|  _ < ___) |  __/| |_| |', '|_| \\_\\____/|_|    \\___/'].join('\n')
export default function App() {
  const [repoUrl, setRepoUrl] = useState('')
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  async function submit(event) {
    event.preventDefault(); setLoading(true); setError(''); setReport(null)
    try { setReport(await scanRepository(repoUrl)) } catch (err) { setError(err.message) } finally { setLoading(false) }
  }
  const findings = report ? [...report.findings].sort((a,b) => severityRank[a.severity] - severityRank[b.severity]) : []
  return <><MouseBackground /><main><header><pre className="ascii-logo" aria-label="r3po">{logo}</pre></header><p className="tagline">Scan public GitHub and GitLab repositories for CVEs, secrets, and SAST findings.</p>
    <form onSubmit={submit}><input required value={repoUrl} onChange={e => setRepoUrl(e.target.value)} placeholder="https://github.com/owner/repo" /><button disabled={loading}>{loading ? 'Scanning…' : 'Scan repository'}</button></form>
    <ScanTerminal active={loading} />
    {error && <p role="alert">{error}</p>}{report?.error && <p role="alert">{report.error}</p>}
    {report?.scan_timed_out && <p>Timed out — showing partial results.</p>}{report?.tool_errors.map(e => <p key={e}>Tool warning: {e}</p>)}
    {report && <table><thead><tr>{['Severity','Tool','File','Line','Title','Description','Remediation'].map(x => <th key={x}>{x}</th>)}</tr></thead><tbody>{findings.map((f,i) => <tr key={i}><td data-label="Severity">{f.severity}</td><td data-label="Tool">{f.tool}</td><td data-label="File">{f.source_url ? <a href={f.source_url} target="_blank" rel="noopener noreferrer">{f.file}</a> : f.file}</td><td data-label="Line">{f.line}</td><td data-label="Title">{f.title}</td><td data-label="Description">{f.description}</td><td data-label="Remediation">{f.remediation}</td></tr>)}</tbody></table>}
  </main></>
}
