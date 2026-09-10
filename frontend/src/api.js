export async function scanRepository(repo_url) {
  const response = await fetch('/scan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ repo_url }) })
  const data = await response.json()
  if (!response.ok) throw new Error(data.detail || data.error || 'Scan failed')
  return data
}
