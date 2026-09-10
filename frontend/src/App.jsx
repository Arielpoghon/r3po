import { useState } from 'react'
import { scanRepository } from './api'

const severityRank = { critical: 0, high: 1, medium: 2, low: 3, info: 4 }
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
  return <main><h1>r3po</h1><p>Scan public GitHub and GitLab repositories for CVEs, secrets, and SAST findings.</p>
    <form onSubmit={submit}><input required value={repoUrl} onChange={e => setRepoUrl(e.target.value)} placeholder="https://github.com/owner/repo" /><button disabled={loading}>{loading ? 'Scanning…' : 'Scan repository'}</button></form>
    {error && <p role="alert">{error}</p>}{report?.error && <p role="alert">{report.error}</p>}
    {report?.scan_timed_out && <p>Timed out — showing partial results.</p>}{report?.tool_errors.map(e => <p key={e}>Tool warning: {e}</p>)}
    {report && <table><thead><tr>{['Severity','Tool','File','Line','Title','Description','Remediation'].map(x => <th key={x}>{x}</th>)}</tr></thead><tbody>{findings.map((f,i) => <tr key={i}><td>{f.severity}</td><td>{f.tool}</td><td>{f.file}</td><td>{f.line}</td><td>{f.title}</td><td>{f.description}</td><td>{f.remediation}</td></tr>)}</tbody></table>}
  </main>
}
