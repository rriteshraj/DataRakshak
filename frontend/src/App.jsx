import { useEffect, useState } from 'react'
import axios from 'axios'

import {
  ShieldCheck,
  LayoutDashboard,
  ScanSearch,
  FileText,
  MessageSquare,
  ChartNoAxesCombined,
  Database,
  Settings,
  ArrowUpRight,
  Activity,
  LockKeyhole,
  Upload,
  Send,
  CheckCircle2,
  AlertCircle,
  Menu,
  X,
  RefreshCw,
  ShieldAlert
} from 'lucide-react'

const API = 'http://127.0.0.1:8000'

const navigation = [
  { name: 'Dashboard', icon: LayoutDashboard },
  { name: 'Privacy Scanner', icon: ScanSearch },
  { name: 'Document Protection', icon: FileText },
  { name: 'RAG Playground', icon: MessageSquare },
  { name: 'LeakTest', icon: ChartNoAxesCombined },
  { name: 'Attack Simulation', icon: ShieldAlert },
  { name: 'Advanced Attack Simulation', icon: ShieldAlert },
  { name: 'Prompt Injection Simulation', icon: ShieldAlert },
  { name: 'Token Vault', icon: Database },
]
function App() {
  const [token, setToken] = useState('')
  const [currentUser, setCurrentUser] = useState(null)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authLoading, setAuthLoading] = useState(false)
  const [page, setPage] = useState('Dashboard')
  const [apiOnline, setApiOnline] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [busy, setBusy] = useState(false)

  const [scanText, setScanText] = useState('')
  const [scanAction, setScanAction] = useState('redact')
  const [scanResult, setScanResult] = useState(null)

  const [document, setDocument] = useState(null)
  const [documentId, setDocumentId] = useState('')

  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(3)
  const [ragResult, setRagResult] = useState(null)
  const [leakResult, setLeakResult] = useState(null)
  const [attackResult, setAttackResult] = useState(null)
  const [advancedAttackResult, setAdvancedAttackResult] = useState(null)
  const [promptInjectionResult, setPromptInjectionResult] = useState(null)

  const [error, setError] = useState('')

  useEffect(() => {
    const check = async () => {
      try {
        await axios.get(`${API}/`)
        setApiOnline(true)
      } catch {
        setApiOnline(false)
      }
    }
    check()
    const timer = setInterval(check, 10000)
    return () => clearInterval(timer)
  }, [])
  const login = async () => {
  if (!username.trim() || !password) {
    return setError('Enter username and password.')
  }

  setAuthLoading(true)
  setError('')

  try {
    const response = await axios.post(`${API}/api/v1/auth/login`, {
      username,
      password,
    })

    const accessToken = response.data.access_token

    setToken(accessToken)
    setCurrentUser(response.data.user)

    axios.defaults.headers.common.Authorization =
      `Bearer ${accessToken}`

    setPassword('')
  } catch (err) {
    setError(err.response?.data?.detail || 'Login failed.')
  } finally {
    setAuthLoading(false)
  }
}

  const runScan = async () => {
    if (!scanText.trim()) return setError('Enter some text first.')
    setBusy(true)
    setError('')
    setScanResult(null)

    try {
      const response = await axios.post(`${API}/api/v1/process`, {
        text: scanText,
        action: scanAction,
      })
      setScanResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not connect to the API.')
    } finally {
      setBusy(false)
    }
  }
  const logout = () => {
  delete axios.defaults.headers.common.Authorization
  setToken('')
  setCurrentUser(null)
  setPage('Dashboard')
  setRagResult(null)
  setError('')
}

  const ingestDocument = async () => {
    if (!document) return setError('Choose a TXT document first.')

    setBusy(true)
    setError('')

    try {
      const text = await document.text()
      if (!text.trim()) throw new Error('The document is empty.')

      const id = `${document.name.replace(/[^a-zA-Z0-9_-]/g, '_')}_${Date.now()}`
      const response = await axios.post(`${API}/api/v1/rag/ingest`, {
        text,
        document_id: id,
      })
      setDocumentId(id)
      setRagResult(null)
      setError('')
      alert(`Document protected and stored. ${response.data.chunks_stored} chunk(s) created.`)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Document ingestion failed.')
    } finally {
      setBusy(false)
    }
  }

  
const searchDocuments = async () => {
  if (!query.trim()) return setError('Enter a question first.')

  setBusy(true)
  setError('')
  setRagResult(null)

  try {
    const response = await axios.post(`${API}/api/v1/rag/ask`, {
      query,
      top_k: topK,
    })
    setRagResult(response.data)
  } catch (err) {
    setError(err.response?.data?.detail || 'AI answer generation failed.')
  } finally {
    setBusy(false)
  }
}

  const runLeakTest = async () => {
  setBusy(true)
  setError('')
  setLeakResult(null)

  try {
    const response = await axios.post(`${API}/api/v1/leaktest/run`)
    setLeakResult(response.data)
  } catch (err) {
    setError(
      err.response?.data?.detail || 'LeakTest execution failed.'
    )
  } finally {
    setBusy(false)
  }
}

  const runAttackSimulation = async () => {
    setBusy(true)
    setError('')
    setAttackResult(null)

    try {
      const response = await axios.post(`${API}/api/v1/leaktest/attacks`)
      setAttackResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Attack simulation failed.')
    } finally {
      setBusy(false)
    }
  }

  const runAdvancedAttackSimulation = async () => {
    setBusy(true)
    setError('')
    setAdvancedAttackResult(null)

    try {
      const response = await axios.post(`${API}/api/v1/leaktest/advanced`)
      setAdvancedAttackResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Advanced attack simulation failed.')
    } finally {
      setBusy(false)
    }
  }

  const runPromptInjectionEvaluation = async () => {
    setBusy(true)
    setError('')
    setPromptInjectionResult(null)

    try {
      const response = await axios.post(`${API}/api/v1/leaktest/prompt-injection`)
      setPromptInjectionResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Prompt injection evaluation failed.')
    } finally {
      setBusy(false)
    }
  }

  const StatCard = ({ title, value, subtitle, icon: Icon, color }) => (
    <div className="stat-card">
      <div className="stat-top">
        <span>{title}</span>
        <div className={`stat-icon ${color}`}><Icon size={19} /></div>
      </div>
      <h2>{value}</h2>
      <p>{subtitle}</p>
    </div>
  )

  const Header = ({ title, subtitle }) => (
    <div className="page-heading">
      <div>
        <div className="eyebrow">DATARAKSHAK / {title.toUpperCase()}</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="header-actions">
        <div className={`api-pill ${apiOnline ? 'online' : 'offline'}`}>
          <span className="status-dot" />
          API {apiOnline ? 'Connected' : 'Disconnected'}
        </div>
        <button className="icon-button" title="Refresh API status" onClick={() => {
          axios.get(`${API}/`).then(() => setApiOnline(true)).catch(() => setApiOnline(false))
        }}>
          <RefreshCw size={17} />
        </button>
      </div>
    </div>
  )
  if (!token) {
  return (
    <div className="app-shell" style={{
      minHeight: '100vh',
      display: 'grid',
      placeItems: 'center'
    }}>
      <div className="workspace-card" style={{
        width: 'min(420px, 90%)',
        padding: '32px'
      }}>
        <div className="card-heading">
          <div>
            <h2>DataRakshak</h2>
            <p>Privacy Firewall Authentication</p>
          </div>
          <ShieldCheck size={30} />
        </div>

        {error && <div className="error-banner">{error}</div>}

        <label>USERNAME</label>
        <input
          value={username}
          onChange={e => setUsername(e.target.value)}
          placeholder="Enter username"
        />

        <label>PASSWORD</label>
        <input
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          placeholder="Enter password"
          onKeyDown={e => {
            if (e.key === 'Enter') login()
          }}
        />

        <button
          className="primary-button full-button"
          disabled={authLoading}
          onClick={login}
        >
          {authLoading ? 'Signing in...' : 'Sign In'}
          <ShieldCheck size={17} />
        </button>
      </div>
    </div>
  )
}

  return (
    <div className="app-shell">
      <aside className={`sidebar ${sidebarOpen ? '' : 'collapsed'}`}>
        <div className="brand">
          <div className="brand-mark"><ShieldCheck size={25} /></div>
          {sidebarOpen && <div><strong>DataRakshak</strong><small>PRIVACY FIREWALL</small></div>}
          <button className="collapse-button" onClick={() => setSidebarOpen(!sidebarOpen)}>
            {sidebarOpen ? <X size={16} /> : <Menu size={18} />}
          </button>
        </div>

        {sidebarOpen && <div className="nav-label">WORKSPACE</div>}
        <nav className="navigation">
          {navigation.map(({ name, icon: Icon }) => (
            <button key={name}
              className={`nav-item ${page === name ? 'active' : ''}`}
              onClick={() => { setPage(name); setError('') }}
              title={name}>
              <Icon size={19} />
              {sidebarOpen && <span>{name}</span>}
              {sidebarOpen && page === name && <span className="active-mark" />}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <button className={`nav-item ${page === 'Settings' ? 'active' : ''}`}
            onClick={() => setPage('Settings')}>
            <Settings size={19} />
            {sidebarOpen && <span>Settings</span>}
          </button>
          {sidebarOpen && (
            <div className="sidebar-security">
              <LockKeyhole size={17} />
              <div><strong>Privacy protected</strong><small>Local development mode</small></div>
            </div>
          )}
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumb">Workspace <span>/</span> {page}</div>
          <div className="topbar-right">
            <span className="environment">
              {currentUser?.username} · {currentUser?.role?.toUpperCase()}
            </span>
            <button className="icon-button" onClick={logout} title="Sign out">
              Logout
            </button>
          </div>
        </header>

        <div className="content">
          {error && (
            <div className="error-banner">
              <AlertCircle size={18} /> {error}
              <button onClick={() => setError('')}><X size={16} /></button>
            </div>
          )}

          {page === 'Dashboard' && (
            <>
              <Header title="Security Overview" subtitle="Monitor your privacy firewall and protected data pipeline." />
              <div className="welcome-banner">
                <div>
                  <div className="welcome-tag"><ShieldCheck size={15} /> PRIVACY FIREWALL ACTIVE</div>
                  <h2>Your data deserves<br />a safer journey.</h2>
                  <p>Detect sensitive Indian identifiers. Protect information before it reaches AI systems.</p>
                  <button className="primary-button" onClick={() => setPage('Privacy Scanner')}>
                    Open Privacy Scanner <ArrowUpRight size={17} />
                  </button>
                </div>
                <div className="shield-art"><ShieldCheck size={112} strokeWidth={1.1} /></div>
              </div>

              <div className="section-title"><div><h3>System Overview</h3><p>Live system status and available modules</p></div></div>
              <div className="stats-grid">
                <StatCard title="API Status" value={apiOnline ? 'Online' : 'Offline'} subtitle="FastAPI connection" icon={Activity} color="green" />
                <StatCard title="Privacy Actions" value="04" subtitle="Redact · Block · Tokenize · Allow" icon={ShieldCheck} color="blue" />
                <StatCard title="Vector Database" value="ChromaDB" subtitle="Persistent local storage" icon={Database} color="purple" />
                <StatCard title="RAG Pipeline" value="Active" subtitle="Ingestion and retrieval available" icon={FileText} color="teal" />
              </div>

              <div className="section-title"><div><h3>Security Modules</h3><p>Choose a module to get started</p></div></div>
              <div className="module-grid">
                {navigation.slice(1).map(({ name, icon: Icon }, index) => (
                  <button className="module-card" key={name} onClick={() => setPage(name)}>
                    <div className="module-icon"><Icon size={22} /></div>
                    <h4>{name}</h4>
                    <p>{[
                      'Detect and protect Indian PII in text.',
                      'Scan and protect TXT documents.',
                      'Retrieve relevant protected document context.',
                      'Evaluate privacy leakage across pipeline stages.',
                      'Run controlled PII leakage attacks and evaluate defenses.',
                      'Test encoded and obfuscated PII attack patterns.',
                      'Evaluate heuristic detection of prompt injection attempts.',
                      'Encrypted token storage and restoration controls.'
                    ][index]}</p>
                    <ArrowUpRight size={17} className="module-arrow" />
                  </button>
                ))}
              </div>
            </>
          )}

          {page === 'Privacy Scanner' && (
            <>
              <Header title="Privacy Scanner" subtitle="Inspect text for sensitive Indian identifiers and apply privacy controls." />
              <div className="workspace-card">
                <div className="card-heading"><div><h3>Text Analysis</h3><p>Use synthetic test data. Avoid real identity numbers.</p></div><ScanSearch size={22} /></div>
                <label>INPUT TEXT</label>
                <textarea value={scanText} onChange={e => setScanText(e.target.value)}
                  placeholder="Example: My PAN is ABCDE1234F. Please protect my information." rows={7} />
                <div className="form-row">
                  <div className="field">
                    <label>PRIVACY ACTION</label>
                    <select value={scanAction} onChange={e => setScanAction(e.target.value)}>
                      <option value="redact">Redact – Replace sensitive values</option>
                      <option value="block">Block – Reject detected PII</option>
                      <option value="tokenize">Tokenize – Create reversible tokens</option>
                      {currentUser?.role === 'admin' && (
                        <option value="allow">Allow – Pass original text (Admin)</option>
                      )}
                    </select>
                  </div>
                  <button className="primary-button scan-button" disabled={busy} onClick={runScan}>
                    {busy ? 'Processing...' : 'Scan and Protect'} <ShieldCheck size={17} />
                  </button>
                </div>
              </div>

              {scanResult && (
                <div className="workspace-card result-card">
                  <div className="card-heading"><div><h3>Protection Result</h3><p>Response from DataRakshak Privacy Engine</p></div><CheckCircle2 color="#32d6a0" /></div>
                  <div className="result-status">{scanResult.status.toUpperCase()}</div>
                  <label>PROTECTED OUTPUT</label>
                  <pre>{scanResult.protected_text ?? 'Request blocked. No protected output returned.'}</pre>
                  <div className="stats-grid compact">
                    <StatCard title="PII Detections" value={scanResult.detection_count} subtitle="Detected entities" icon={ScanSearch} color="blue" />
                    <StatCard title="Tokens Created" value={scanResult.token_count} subtitle="Vault tokens" icon={Database} color="purple" />
                  </div>
                  {scanResult.detections?.length > 0 && (
                    <div className="detection-list">
                      <h4>Detection Details</h4>
                      {scanResult.detections.map((item, i) => (
                        <div className="detection-row" key={i}>
                          <span>{item.entity_type}</span>
                          <span>Confidence: {(item.score * 100).toFixed(0)}%</span>
                          <span>Position: {item.start}–{item.end}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}

          {page === 'Document Protection' && (
            <>
              <Header title="Document Protection" subtitle="Protect document content before it enters your AI workflow." />
              <div className="workspace-card">
                <div className="card-heading"><div><h3>Upload a document</h3><p>Currently supports UTF-8 TXT files.</p></div><FileText size={22} /></div>
                <label className="upload-zone">
                  <Upload size={30} />
                  <strong>{document ? document.name : 'Choose a TXT document'}</strong>
                  <span>Click to browse · UTF-8 text only</span>
                  <input type="file" accept=".txt,text/plain" onChange={e => setDocument(e.target.files?.[0] || null)} hidden />
                </label>
                <div className="form-row">
                  <div className="field"><label>PROTECTION MODE</label><span className="static-value">Redaction before storage</span></div>
                  <button className="primary-button" disabled={busy || !document} onClick={async () => {
                    setBusy(true); setError('')
                    try {
                      const text = await document.text()
                      const id = `${document.name.replace(/[^a-zA-Z0-9_-]/g, '_')}_${Date.now()}`
                      const response = await axios.post(`${API}/api/v1/rag/ingest`, { text, document_id: id })
                      setDocumentId(id)
                      alert(`Protected and stored ${response.data.chunks_stored} chunk(s).`)
                    } catch (err) { setError(err.response?.data?.detail || err.message) }
                    finally { setBusy(false) }
                  }}>
                    Protect Document <ShieldCheck size={17} />
                  </button>
                </div>
                {documentId && <p className="success-line"><CheckCircle2 size={16} /> Latest document ID: {documentId}</p>}
              </div>
            </>
          )}

          
{page === 'RAG Playground' && (
  <>
    <Header
      title="RAG Playground"
      subtitle="Ask questions using your privacy-protected knowledge base and local AI."
    />

    <div className="rag-layout">
      {/* Document Upload */}
      <div className="workspace-card">
        <div className="card-heading">
          <div>
            <h3>Knowledge Base</h3>
            <p>Ingest documents after PII redaction.</p>
          </div>
          <Database size={22} />
        </div>

        <label className="upload-zone">
          <Upload size={28} />
          <strong>
            {document ? document.name : 'Upload a TXT document'}
          </strong>
          <span>PII is redacted before ChromaDB storage</span>

          <input
            type="file"
            accept=".txt,text/plain"
            onChange={e => setDocument(e.target.files?.[0] || null)}
            hidden
          />
        </label>

        <button
          className="primary-button full-button"
          disabled={busy || !document}
          onClick={ingestDocument}
        >
          {busy ? 'Protecting document...' : 'Protect and Store'}
          <ShieldCheck size={17} />
        </button>

        {documentId && (
          <p className="success-line">
            <CheckCircle2 size={16} />
            Document stored: {documentId}
          </p>
        )}
      </div>

      {/* AI Question */}
      <div className="workspace-card">
        <div className="card-heading">
          <div>
            <h3>Ask your documents</h3>
            <p>Get AI-generated answers from protected documents.</p>
          </div>
          <MessageSquare size={22} />
        </div>

        <label>YOUR QUESTION</label>

        <textarea
          rows={3}
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask something about your uploaded documents..."
        />

        <div className="form-row">
          <div className="field">
            <label>RESULT COUNT</label>
            <select
              value={topK}
              onChange={e => setTopK(Number(e.target.value))}
            >
              {[1, 2, 3, 5, 10].map(n => (
                <option key={n} value={n}>{n} chunks</option>
              ))}
            </select>
          </div>

          <button
            className="primary-button scan-button"
            disabled={busy || !query.trim()}
            onClick={searchDocuments}
          >
            {busy ? 'Generating...' : 'Ask AI'}
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>

    {/* AI Answer and Retrieval Results */}
    {ragResult && (
      <>
        <div className="workspace-card">
          <div className="card-heading">
            <div>
              <h3>AI Generated Answer</h3>
              <p>
                Powered by {ragResult.model || 'DataRakshak RAG'}
              </p>
            </div>
            <MessageSquare color="#32d6a0" size={22} />
          </div>

          <div className="success-line">
            Status: {ragResult.status}
          </div>

          <div className="retrieved-card">
            <p>{ragResult.answer}</p>
          </div>

          {ragResult.sources?.length > 0 && (
            <div>
              <h4>Source Documents</h4>
              {ragResult.sources.map((source, index) => (
                <div className="retrieved-card" key={index}>
                  <strong>{source.document_id}</strong>
                  <p>
                    Chunk: {source.chunk_index}
                    {' · '}
                    Protection: {source.protection_status}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Privacy and Security Details */}
        {ragResult.retrieval && (
          <div className="workspace-card">
            <div className="card-heading">
              <div>
                <h3>Privacy & Security Report</h3>
                <p>Protection checks performed during retrieval.</p>
              </div>
              <ShieldCheck color="#32d6a0" size={22} />
            </div>

            <div className="query-summary">
              Protected query: {ragResult.retrieval.query_protected}
            </div>

            <p>
              PII detected: {ragResult.retrieval.query_pii_detected ? 'Yes' : 'No'}
            </p>

            <p>
              Prompt injection detected: {
                ragResult.retrieval.query_prompt_injection_detected ? 'Yes' : 'No'
              }
            </p>

            <p>
              Protected chunks: {ragResult.retrieval.protected_chunks}
            </p>

            <p>
              Blocked chunks: {ragResult.retrieval.blocked_chunks}
            </p>

            <p className="success-line">
              <CheckCircle2 size={16} />
              {ragResult.retrieval.message}
            </p>
          </div>
        )}

        {/* Retrieved Context */}
        <div className="workspace-card">
          <div className="card-heading">
            <div>
              <h3>Retrieved Context</h3>
              <p>Protected chunks retrieved from ChromaDB.</p>
            </div>
            <Database size={22} />
          </div>

          {ragResult.retrieval?.results?.length ? (
            ragResult.retrieval.results.map((item, index) => (
              <div className="retrieved-card" key={index}>
                <div className="retrieved-heading">
                  <strong>Result {index + 1}</strong>
                  <span>{item.document_id}</span>
                </div>

                <p>{item.text}</p>

                <small>
                  Chunk {item.chunk_index}
                  {' · '}
                  Vector distance {Number(item.distance).toFixed(4)}
                  {' · '}
                  {item.protection_status}
                </small>
              </div>
            ))
          ) : (
            <p>No relevant document context found.</p>
          )}
        </div>
      </>
    )}
  </>
)}

          
{page === 'LeakTest' && (
  <>
    <Header
      title="LeakTest"
      subtitle="Stage-wise privacy leakage detection and benchmarking."
    />

    <div className="workspace-card">
      <div className="card-heading">
        <div>
          <h3>Leakage Evaluation Pipeline</h3>
          <p>Evaluate privacy protection across five pipeline boundaries.</p>
        </div>
        <ChartNoAxesCombined size={22} />
      </div>

      <button className="primary-button" disabled={busy || currentUser?.role !== 'admin'} onClick={runLeakTest}>
        {busy ? 'Running Benchmark...' : 'Run Benchmark'}
        <RefreshCw size={17} />
      </button>

      {!leakResult && (
        <p className="muted-note">
          Run the benchmark to retrieve results from the LeakTest API.
        </p>
      )}
    </div>

    {leakResult && (
      <>
        {leakResult.comparative_metrics && (
          <div className="workspace-card">
            <div className="card-heading">
              <div>
                <h3>Baseline vs Protected Pipeline</h3>
                <p>Exact-value leakage comparison across all five stages.</p>
              </div>
              <ShieldCheck color="#32d6a0" size={24} />
            </div>

            <div className="stats-grid">
              <StatCard
                title="Baseline Leaks"
                value={leakResult.comparative_metrics.baseline_leaks}
                subtitle="Simulated unprotected pass-through"
                icon={ShieldAlert}
                color="purple"
              />
              <StatCard
                title="Protected Leaks"
                value={leakResult.comparative_metrics.protected_leaks}
                subtitle="Actual protected pipeline outputs"
                icon={LockKeyhole}
                color="green"
              />
              <StatCard
                title="Leaks Prevented"
                value={leakResult.comparative_metrics.leaks_prevented}
                subtitle="Baseline minus protected leaks"
                icon={ShieldCheck}
                color="teal"
              />
              <StatCard
                title="Leakage Reduction"
                value={`${leakResult.comparative_metrics.leakage_reduction_rate}%`}
                subtitle="On this controlled benchmark"
                icon={ChartNoAxesCombined}
                color="blue"
              />
            </div>

            <div className="comparison-chart">
              <h4>Stage-wise leakage comparison</h4>
              <p className="muted-note">
                Each bar is scaled against the largest baseline stage count.
              </p>
              {Object.entries(leakResult.comparative_metrics.stage_comparison || {}).map(([stage, values]) => {
                const maxLeaks = Math.max(
                  1,
                  ...Object.values(leakResult.comparative_metrics.stage_comparison || {}).map(item => item.baseline_leaks || 0)
                )
                return (
                  <div className="comparison-stage" key={stage}>
                    <strong>{stage}</strong>
                    <div className="comparison-bars">
                      <div className="comparison-bar-line">
                        <span>Baseline</span>
                        <div className="comparison-track">
                          <div
                            className="comparison-fill baseline-fill"
                            style={{ width: `${(values.baseline_leaks / maxLeaks) * 100}%` }}
                          />
                        </div>
                        <b>{values.baseline_leaks}</b>
                      </div>
                      <div className="comparison-bar-line">
                        <span>Protected</span>
                        <div className="comparison-track">
                          <div
                            className="comparison-fill protected-fill"
                            style={{ width: `${(values.protected_leaks / maxLeaks) * 100}%` }}
                          />
                        </div>
                        <b>{values.protected_leaks}</b>
                      </div>
                    </div>
                    <span className="pending-tag">
                      {values.leakage_reduction_rate}% reduction
                    </span>
                  </div>
                )
              })}
            </div>

            <div className="warning-line">
              <ShieldAlert size={17} />
              Baseline type: {leakResult.comparative_metrics.baseline_type}.
              This is a simulated unprotected pass-through reference, not a separately executed unprotected RAG pipeline.
            </div>
          </div>
        )}

        <div className="workspace-card">
          <div className="card-heading">
            <div>
              <h3>Benchmark Results</h3>
              <p>
                {leakResult.total_test_cases} test cases ·
                {' '}{leakResult.stages_tested} pipeline stages
              </p>
            </div>
            <CheckCircle2 color="#32d6a0" size={24} />
          </div>

          <div className="stats-grid">
            <StatCard
              title="Detection Rate"
              value={`${leakResult.metrics.detection_rate}%`}
              subtitle="Expected PII entities detected"
              icon={ScanSearch}
              color="blue"
            />
            <StatCard
              title="Leakage Rate"
              value={`${leakResult.metrics.leakage_rate}%`}
              subtitle="Measured exact-value leakage"
              icon={ShieldAlert}
              color="green"
            />
            <StatCard
              title="Protection Rate"
              value={`${leakResult.metrics.protection_rate}%`}
              subtitle="Values not exposed in tested outputs"
              icon={ShieldCheck}
              color="teal"
            />
            <StatCard
              title="False Positive Rate"
              value={`${leakResult.metrics.false_positive_rate}%`}
              subtitle="Non-PII entity classifications"
              icon={AlertCircle}
              color="purple"
            />
            <StatCard
              title="Average Latency"
              value={`${leakResult.metrics.average_latency_ms} ms`}
              subtitle="Per test case"
              icon={Activity}
              color="blue"
            />
            <StatCard
              title="Stage Evaluations"
              value={leakResult.stage_results.length}
              subtitle="Total pipeline evaluations"
              icon={ChartNoAxesCombined}
              color="green"
            />
          </div>
        </div>

        <div className="workspace-card">
          <div className="card-heading">
            <div>
              <h3>Five-Stage Pipeline Results</h3>
              <p>Evaluation summary for each pipeline boundary.</p>
            </div>
            <Activity size={22} />
          </div>

          {[
            'User Prompt',
            'Document Ingestion',
            'Vector Retrieval',
            'LLM Input',
            'LLM Output'
          ].map((stage, index) => {
            const results = leakResult.stage_results.filter(item => item.stage === stage)
            const leaks = results.reduce((total, item) => total + item.leaked_count, 0)
            const mode = leakResult.stage_modes?.[stage] || 'TESTED'

            return (
              <div className="stage-row" key={stage}>
                <span className="stage-number">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <div>
                  <strong>{stage}</strong>
                  <p className="muted-note">
                    {results.length} evaluations · {leaks} leaked values
                  </p>
                </div>
                <span className="pending-tag">{mode.replaceAll('_', ' ')}</span>
              </div>
            )
          })}
        </div>

        <div className="workspace-card">
          <h3>Detection Summary</h3>
          <div className="setting-row">
            <span>True Positives</span>
            <strong>{leakResult.metrics.counts.true_positives}</strong>
          </div>
          <div className="setting-row">
            <span>False Negatives</span>
            <strong>{leakResult.metrics.counts.false_negatives}</strong>
          </div>
          <div className="setting-row">
            <span>False Positives</span>
            <strong>{leakResult.metrics.counts.false_positives}</strong>
          </div>
          <div className="setting-row">
            <span>True Negatives</span>
            <strong>{leakResult.metrics.counts.true_negatives}</strong>
          </div>
          <div className="setting-row">
            <span>Total expected PII entities</span>
            <strong>{leakResult.metrics.counts.total_pii_entities}</strong>
          </div>
        </div>

        <div className="workspace-card">
          <div className="warning-line">
            <ShieldAlert size={17} />
            {leakResult.simulation_note}
          </div>
          <p className="muted-note">
            Leakage checks currently use exact-value matching against synthetic ground-truth values.
            Encoded, obfuscated, or semantically inferred disclosures are not covered by this metric.
            Results are preliminary and are not a real-world security guarantee.
          </p>
        </div>
      </>
    )}
  </>
)}


{page === 'Attack Simulation' && (
            <>
              <Header
                title="Attack Simulation"
                subtitle="Test whether DataRakshak detects and prevents controlled PII leakage attacks."
              />

              <div className="workspace-card">
                <div className="card-heading">
                  <div>
                    <h3>Controlled Privacy Attacks</h3>
                    <p>Test PAN, Aadhaar, phone, email and GSTIN protection.</p>
                  </div>
                  <ShieldAlert size={22} />
                </div>

                <button
                  className="primary-button"
                  disabled={busy || currentUser?.role !== 'admin'}
                  onClick={runAttackSimulation}
                >
                  {busy ? 'Running Attack Simulation...' : 'Run Attack Simulation'}
                  <ShieldCheck size={17} />
                </button>

                {!attackResult && (
                  <p className="muted-note">
                    Run the simulation to retrieve results from the Attack Evaluation API.
                  </p>
                )}
              </div>

              {attackResult && (
                <>
                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Attack Simulation Results</h3>
                        <p>Evaluation status: {attackResult.status}</p>
                      </div>
                      <CheckCircle2 color="#32d6a0" size={24} />
                    </div>

                    <div className="stats-grid">
                      <StatCard
                        title="Total Attack Cases"
                        value={attackResult.total_attack_cases}
                        subtitle="Individual PII attacks"
                        icon={ShieldAlert}
                        color="blue"
                      />
                      <StatCard
                        title="Attacks Detected"
                        value={`${attackResult.attacks_detected}/${attackResult.total_attack_cases}`}
                        subtitle="Controlled attacks identified"
                        icon={ScanSearch}
                        color="green"
                      />
                      <StatCard
                        title="Leaks Prevented"
                        value={`${attackResult.individual_leaks_prevented}/${attackResult.total_attack_cases}`}
                        subtitle="Individual attack cases protected"
                        icon={ShieldCheck}
                        color="teal"
                      />
                      <StatCard
                        title="Combined Protected Leaks"
                        value={attackResult.combined_attack.protected_leaks}
                        subtitle="Remaining exact-value leaks"
                        icon={LockKeyhole}
                        color="purple"
                      />
                    </div>
                  </div>

                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Individual Attack Analysis</h3>
                        <p>PII detection and redaction results.</p>
                      </div>
                      <Activity size={22} />
                    </div>

                    {attackResult.attack_results.map((item) => (
                      <div className="stage-row" key={item.entity_type}>
                        <div>
                          <strong>{item.entity_type}</strong>
                          <p className="muted-note">
                            Raw leaks: {item.raw_leak_count} · Protected leaks: {item.protected_leak_count}
                          </p>
                        </div>
                        <span className="pending-tag">
                          {item.leak_prevented ? 'PROTECTED' : 'LEAK DETECTED'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Combined Attack Result</h3>
                        <p>Multiple Indian PII identifiers in one input.</p>
                      </div>
                      <ShieldCheck color="#32d6a0" size={22} />
                    </div>

                    <div className="setting-row">
                      <span>Raw leaks detected</span>
                      <strong>{attackResult.combined_attack.raw_leaks_detected}</strong>
                    </div>
                    <div className="setting-row">
                      <span>Protected leaks</span>
                      <strong>{attackResult.combined_attack.protected_leaks}</strong>
                    </div>
                    <div className="setting-row">
                      <span>All leaks prevented</span>
                      <strong>{attackResult.combined_attack.all_leaks_prevented ? 'Yes' : 'No'}</strong>
                    </div>

                    <label>PROTECTED OUTPUT</label>
                    <pre>{attackResult.combined_attack.protected_text}</pre>
                  </div>

                  <div className="workspace-card">
                    <div className="warning-line">
                      <ShieldAlert size={17} />
                      These are controlled synthetic tests using exact-value leakage checks. They do not establish protection against every real-world or adversarial attack.
                    </div>
                  </div>
                </>
              )}
            </>
          )}


          {page === 'Advanced Attack Simulation' && (
            <>
              <Header
                title="Advanced Attack Simulation"
                subtitle="Evaluate protection against encoded and obfuscated Indian PII."
              />

              <div className="workspace-card">
                <div className="card-heading">
                  <div>
                    <h3>Encoded and Obfuscated PII Attacks</h3>
                    <p>Test Base64, URL encoding, separator and whitespace evasion patterns.</p>
                  </div>
                  <ShieldAlert size={22} />
                </div>

                <button
                  className="primary-button"
                  disabled={busy || currentUser?.role !== 'admin'}
                  onClick={runAdvancedAttackSimulation}
                >
                  {busy ? 'Running Advanced Tests...' : 'Run Advanced Attack Tests'}
                  <ShieldCheck size={17} />
                </button>

                {!advancedAttackResult && (
                  <p className="muted-note">
                    Run the advanced evaluator to retrieve results from the Advanced Attack API.
                  </p>
                )}
              </div>

              {advancedAttackResult && (
                <>
                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Advanced Evaluation Results</h3>
                        <p>{advancedAttackResult.evaluation_type?.replaceAll('_', ' ')}</p>
                      </div>
                      <CheckCircle2 color="#32d6a0" size={24} />
                    </div>

                    <div className="stats-grid">
                      <StatCard
                        title="Total Attack Cases"
                        value={advancedAttackResult.total_attack_cases}
                        subtitle="Encoded and obfuscated cases"
                        icon={ShieldAlert}
                        color="blue"
                      />
                      <StatCard
                        title="Attacks Detected"
                        value={`${advancedAttackResult.attacks_detected}/${advancedAttackResult.total_attack_cases}`}
                        subtitle={`${advancedAttackResult.detection_rate}% detection rate`}
                        icon={ScanSearch}
                        color="green"
                      />
                      <StatCard
                        title="Leaks Prevented"
                        value={`${advancedAttackResult.leaks_prevented}/${advancedAttackResult.total_attack_cases}`}
                        subtitle={`${advancedAttackResult.protection_rate}% protection rate`}
                        icon={ShieldCheck}
                        color="teal"
                      />
                      <StatCard
                        title="Remaining Leaks"
                        value={advancedAttackResult.remaining_leaks}
                        subtitle="Exact-value checks"
                        icon={LockKeyhole}
                        color="purple"
                      />
                      <StatCard
                        title="False Positives"
                        value={advancedAttackResult.false_positives}
                        subtitle={`${advancedAttackResult.false_positive_rate}% of benign cases`}
                        icon={AlertCircle}
                        color="blue"
                      />
                      <StatCard
                        title="Benign Test Cases"
                        value={advancedAttackResult.total_benign_cases}
                        subtitle="Ordinary text checks"
                        icon={CheckCircle2}
                        color="green"
                      />
                    </div>
                  </div>

                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Attack Category Breakdown</h3>
                        <p>Detection and protection results for each tested technique.</p>
                      </div>
                      <ChartNoAxesCombined size={22} />
                    </div>

                    {Object.entries(advancedAttackResult.category_summary || {}).map(([category, values]) => (
                      <div className="stage-row" key={category}>
                        <div>
                          <strong>{category}</strong>
                          <p className="muted-note">
                            {values.detected}/{values.total} detected · {values.prevented}/{values.total} prevented · {values.leaks} remaining
                          </p>
                        </div>
                        <span className="pending-tag">
                          {values.protection_rate}% PROTECTED
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Individual Attack Analysis</h3>
                        <p>Detailed result for each synthetic attack case.</p>
                      </div>
                      <Activity size={22} />
                    </div>

                    {(advancedAttackResult.attack_results || []).map((item) => (
                      <div className="stage-row" key={item.test_id}>
                        <div>
                          <strong>{item.test_id} · {item.category}</strong>
                          <p className="muted-note">
                            {item.expected_entity} · Status: {item.protection_status} · Detections: {item.detection_count}
                          </p>
                          {item.protected_output !== null && (
                            <pre>{item.protected_output}</pre>
                          )}
                        </div>
                        <span className="pending-tag">
                          {item.leak_prevented ? 'PROTECTED' : 'CHECK REQUIRED'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="workspace-card">
                    <h3>Evaluation Limitations</h3>
                    {(advancedAttackResult.limitations || []).map((item, index) => (
                      <p className="muted-note" key={index}>• {item}</p>
                    ))}
                    <div className="warning-line">
                      <ShieldAlert size={17} />
                      These results apply only to the listed controlled synthetic cases. They do not establish protection against every encoding, evasion, prompt-injection, or retrieval attack.
                    </div>
                  </div>
                </>
              )}
            </>
          )}

          {page === 'Prompt Injection Simulation' && (
            <>
              <Header
                title="Prompt Injection Simulation"
                subtitle="Evaluate heuristic detection of instruction overrides, prompt extraction, role manipulation and privacy bypass attempts."
              />

              <div className="workspace-card">
                <div className="card-heading">
                  <div>
                    <h3>Prompt Injection Evaluation</h3>
                    <p>Run controlled synthetic attack prompts and benign examples against the heuristic detector.</p>
                  </div>
                  <ShieldAlert size={22} />
                </div>

                <button
                  className="primary-button"
                  disabled={busy || currentUser?.role !== 'admin'}
                  onClick={runPromptInjectionEvaluation}
                >
                  {busy ? 'Running Evaluation...' : 'Run Prompt Injection Evaluation'}
                  <ShieldCheck size={17} />
                </button>

                {!promptInjectionResult && (
                  <p className="muted-note">
                    Run the evaluator to test the Prompt Injection API. Results are based on predefined heuristic patterns.
                  </p>
                )}
              </div>

              {promptInjectionResult && (
                <>
                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Evaluation Results</h3>
                        <p>Evaluation type: {promptInjectionResult.evaluation_type?.replaceAll('_', ' ')}</p>
                      </div>
                      <CheckCircle2 color="#32d6a0" size={24} />
                    </div>

                    <div className="stats-grid">
                      <StatCard
                        title="Total Attacks"
                        value={promptInjectionResult.total_attacks}
                        subtitle="Synthetic prompt-injection cases"
                        icon={ShieldAlert}
                        color="blue"
                      />
                      <StatCard
                        title="Attacks Detected"
                        value={`${promptInjectionResult.attacks_detected}/${promptInjectionResult.total_attacks}`}
                        subtitle={`${promptInjectionResult.detection_rate}% detection rate`}
                        icon={ScanSearch}
                        color="green"
                      />
                      <StatCard
                        title="Attacks Blocked"
                        value={`${promptInjectionResult.attacks_prevented}/${promptInjectionResult.total_attacks}`}
                        subtitle={`${promptInjectionResult.prevention_rate}% simulated blocking rate`}
                        icon={ShieldCheck}
                        color="teal"
                      />
                      <StatCard
                        title="False Positives"
                        value={promptInjectionResult.false_positives}
                        subtitle={`${promptInjectionResult.false_positive_rate}% of benign cases`}
                        icon={AlertCircle}
                        color="purple"
                      />
                      <StatCard
                        title="Benign Cases"
                        value={promptInjectionResult.benign_cases}
                        subtitle="Ordinary prompts evaluated"
                        icon={CheckCircle2}
                        color="blue"
                      />
                    </div>
                  </div>

                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Attack Analysis</h3>
                        <p>Detection results by synthetic attack category.</p>
                      </div>
                      <Activity size={22} />
                    </div>

                    {(promptInjectionResult.attack_results || []).map((item) => (
                      <div className="stage-row" key={item.id}>
                        <div>
                          <strong>{item.id} · {item.category}</strong>
                          <p className="muted-note">
                            Detected patterns: {item.detected_patterns?.length
                              ? item.detected_patterns.join(', ').replaceAll('_', ' ')
                              : 'None'}
                          </p>
                        </div>
                        <span className="pending-tag">
                          {item.prevented ? 'BLOCKED' : item.detected ? 'DETECTED' : 'NOT DETECTED'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="workspace-card">
                    <div className="card-heading">
                      <div>
                        <h3>Benign Prompt Validation</h3>
                        <p>Normal prompts should be allowed by the detector.</p>
                      </div>
                      <CheckCircle2 color="#32d6a0" size={22} />
                    </div>

                    {(promptInjectionResult.benign_results || []).map((item, index) => (
                      <div className="stage-row" key={index}>
                        <div>
                          <strong>{item.text}</strong>
                          <p className="muted-note">
                            {item.detected_patterns?.length
                              ? `Detected patterns: ${item.detected_patterns.join(', ')}`
                              : 'No known injection pattern detected'}
                          </p>
                        </div>
                        <span className="pending-tag">
                          {item.allowed ? 'ALLOWED' : 'FALSE POSITIVE'}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="workspace-card">
                    <div className="warning-line">
                      <ShieldAlert size={17} />
                      {promptInjectionResult.note}
                    </div>
                    <p className="muted-note">
                      This benchmark evaluates predefined pattern matching only. It does not test a connected LLM,
                      semantic prompt injection, indirect injection in retrieved documents, or model compliance.
                      Blocking is simulated by the evaluator and is not yet enforced in the live RAG or LLM request pipeline.
                    </p>
                  </div>
                </>
              )}
            </>
          )}

          {page === 'Token Vault' && (
            <>
              <Header title="Token Vault" subtitle="Encrypted storage for reversible privacy tokens." />
              <div className="workspace-card">
                <div className="card-heading"><div><h3>Vault Security</h3><p>Local encrypted vault prototype.</p></div><LockKeyhole size={22} /></div>
                <div className="warning-line"><ShieldAlert size={17} /> Token restoration is restricted to authenticated administrators. Token listing and audit-log interfaces are not yet implemented.</div>
                <div className="vault-note"><Database size={25} /><div><strong>Encrypted SQLite vault</strong><p>Original values are encrypted at rest using Fernet.</p></div></div>
                <p className="muted-note">Restoration is available through the admin-protected API. Token listing and audit logs remain future enhancements.</p>
              </div>
            </>
          )}

          {page === 'Settings' && (
            <>
              <Header title="Settings" subtitle="Application configuration and system information." />
              <div className="workspace-card">
                <h3>System Configuration</h3>
                <div className="setting-row"><span>Backend URL</span><strong>{API}</strong></div>
                <div className="setting-row"><span>Frontend</span><strong>React + Vite</strong></div>
                <div className="setting-row"><span>Vector database</span><strong>ChromaDB</strong></div>
                <div className="setting-row"><span>API status</span><strong>{apiOnline ? 'Connected' : 'Disconnected'}</strong></div>
              </div>
            </>
          )}

          <footer className="footer">
            <span>© 2026 DataRakshak</span>
            <span>Your Data. Your Privacy. Our Protection.</span>
            <span>Development Build 1.0.0</span>
          </footer>
        </div>
      </main>
    </div>
  )
}

export default App