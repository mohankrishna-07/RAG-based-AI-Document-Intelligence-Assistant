import { useEffect, useRef, useState } from 'react'
import './App.css'

const API = `${(import.meta.env.VITE_API_URL || '').replace(/\/$/, '')}/api`.replace(/^\/api$/, '/api')

function Icon({ name, size = 20 }) {
  const icons = {
    grid: '▦', upload: '↑', chat: '◎', book: '▤', history: '↺', logout: '↪',
    plus: '+', send: '➤', search: '⌕', file: '▧', sparkle: '✦', trash: '⌫',
  }
  return <span className="icon" style={{ fontSize: size }} aria-hidden="true">{icons[name]}</span>
}

function App() {
  const [token, setToken] = useState(() => localStorage.getItem('docai_token') || '')
  const [user, setUser] = useState(() => JSON.parse(localStorage.getItem('docai_user') || 'null'))
  const [mode, setMode] = useState('login')
  const [view, setView] = useState('chat')
  const [documents, setDocuments] = useState([])
  const [history, setHistory] = useState([])
  const [selected, setSelected] = useState([])
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const fileRef = useRef(null)

  const parseJsonResponse = async (response) => {
    const text = await response.text()
    if (!text) return {}
    try {
      return JSON.parse(text)
    } catch {
      return { detail: text.startsWith('<') ? 'The API returned an HTML page instead of JSON. Check the backend URL.' : text }
    }
  }

  const request = async (path, options = {}) => {
    const response = await fetch(API + path, {
      ...options,
      headers: { ...(options.headers || {}), ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    })
    const data = await parseJsonResponse(response)
    if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'Request failed')
    return data
  }

  const loadData = async () => {
    if (!token) return
    try {
      const [docs, chatHistory] = await Promise.all([request('/documents'), request('/chat/history')])
      setDocuments(docs)
      setHistory(chatHistory)
    } catch (err) {
      const message = err.message.toLowerCase()
      if (message.includes('token') || message.includes('authentication')) logout()
    }
  }

  useEffect(() => { loadData() }, [token])

  const authenticate = async (event) => {
    event.preventDefault()
    setBusy(true)
    setError('')
    const form = new FormData(event.currentTarget)
    const body = Object.fromEntries(form.entries())
    try {
      const endpoint = mode === 'login' ? '/auth/login' : '/auth/register'
      const data = await fetch(API + endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
      }).then(async (response) => {
        const result = await parseJsonResponse(response)
        if (!response.ok) {
          if (typeof result.detail === 'string') throw new Error(result.detail)
          if (Array.isArray(result.detail)) {
            const messages = result.detail.map((item) => {
              const field = Array.isArray(item.loc) ? item.loc[item.loc.length - 1] : 'Field'
              return `${field}: ${item.msg}`
            })
            throw new Error(messages.join(' • '))
          }
          throw new Error('Authentication failed')
        }
        return result
      })
      localStorage.setItem('docai_token', data.access_token)
      localStorage.setItem('docai_user', JSON.stringify(data.user))
      setToken(data.access_token)
      setUser(data.user)
    } catch (err) { setError(err.message) }
    finally { setBusy(false) }
  }

  const logout = () => {
    localStorage.removeItem('docai_token')
    localStorage.removeItem('docai_user')
    setToken(''); setUser(null); setDocuments([]); setMessages([]); setHistory([])
  }

  const upload = async (event) => {
    const file = event.target.files?.[0]
    if (!file) return
    setBusy(true); setError('')
    const form = new FormData(); form.append('file', file)
    try {
      await request('/documents/upload', { method: 'POST', body: form })
      await loadData()
    } catch (err) { setError(err.message) }
    finally { setBusy(false); event.target.value = '' }
  }

  const removeDocument = async (id) => {
    try { await request(`/documents/${id}`, { method: 'DELETE' }); await loadData()
      setSelected((current) => current.filter((item) => item !== id))
    } catch (err) { setError(err.message) }
  }

  const ask = async (event) => {
    event.preventDefault()
    if (!question.trim() || busy) return
    const text = question.trim()
    setMessages((current) => [...current, { role: 'user', content: text }])
    setQuestion(''); setBusy(true); setError('')
    try {
      const data = await request('/chat/ask', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, document_ids: selected.length ? selected : null }),
      })
      setMessages((current) => [...current, { role: 'assistant', content: data.answer, sources: data.sources }])
      await loadData()
    } catch (err) {
      setMessages((current) => [...current, { role: 'assistant', content: `I couldn't answer: ${err.message}` }])
    } finally { setBusy(false) }
  }

  if (!token) {
    return (
      <main className="auth-page">
        <section className="auth-brand">
          <div className="brand-mark"><Icon name="book" size={28} /></div>
          <h1>AI Document<br /><span>Intelligence</span></h1>
          <p>Turn PDFs into answers, insights, and citations.</p>
          <div className="auth-art"><span /><span /><span /></div>
        </section>
        <section className="auth-card-wrap">
          <form className="auth-card" onSubmit={authenticate}>
            <div className="auth-tabs">
              <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>Sign in</button>
              <button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>Create account</button>
            </div>
            {mode === 'register' && <label>Full name<input name="name" required placeholder="Alex Morgan" /></label>}
            <label>Email address<input name="email" type="email" required placeholder="you@example.com" /></label>
            <label>Password<input name="password" type="password" required minLength={6} placeholder="••••••••" /></label>
            {error && <div className="error-banner">{error}</div>}
            <button className="primary-button" disabled={busy}>{busy ? 'Please wait...' : mode === 'login' ? 'Sign in' : 'Create account'}</button>
          </form>
        </section>
      </main>
    )
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand-row"><div className="brand-mark small"><Icon name="book" size={19} /></div><strong>DocIntel</strong></div>
        <nav>
          <button className={view === 'chat' ? 'active' : ''} onClick={() => setView('chat')}><Icon name="chat" /> Chat</button>
          <button className={view === 'documents' ? 'active' : ''} onClick={() => setView('documents')}><Icon name="book" /> Documents <b>{documents.length}</b></button>
          <button className={view === 'history' ? 'active' : ''} onClick={() => setView('history')}><Icon name="history" /> History</button>
        </nav>
        <div className="sidebar-bottom">
          <div className="storage"><div><span>Storage</span><b>{documents.reduce((sum, d) => sum + d.size, 0) / 1024 / 1024 < 1 ? 'Local' : 'Files'}</b></div><div className="storage-bar"><span /></div></div>
          <button className="profile" onClick={logout}><div className="avatar">{user?.name?.[0] || 'U'}</div><div><b>{user?.name}</b><span>{user?.email}</span></div><Icon name="logout" /></button>
        </div>
      </aside>

      <section className="workspace">
        {view === 'chat' && (
          <>
            <header className="topbar"><div><span className="eyebrow">WORKSPACE</span><h2>AI Chat</h2></div><button className="upload-button" onClick={() => fileRef.current?.click()}><Icon name="upload" /> Upload PDF</button></header>
            <div className="chat-layout">
              <section className="conversation">
                {messages.length === 0 ? (
                  <div className="welcome">
                    <div className="welcome-icon"><Icon name="sparkle" size={24} /></div>
                    <h1>What would you like to know?</h1>
                    <p>Ask questions across your uploaded documents.</p>
                    <div className="suggestions">
                      {['Summarize the key findings', 'What are the main conclusions?', 'Compare the most important sections'].map((text) => <button key={text} onClick={() => setQuestion(text)}>{text}</button>)}
                    </div>
                  </div>
                ) : (
                  <div className="messages">
                    {messages.map((message, index) => (
                      <article className={`message ${message.role}`} key={index}>
                        {message.role === 'assistant' && <div className="assistant-avatar"><Icon name="sparkle" /></div>}
                        <div className="message-body"><p>{message.content}</p>{message.sources?.length > 0 && <div className="sources">{message.sources.slice(0, 4).map((source, i) => <button key={i} title={source.content}><Icon name="file" /> {source.filename} · Page {source.page_number}</button>)}</div>}</div>
                      </article>
                    ))}
                    {busy && <div className="typing"><span /><span /><span /></div>}
                  </div>
                )}
                <form className="chat-input" onSubmit={ask}><input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask a question about your documents..." /><button disabled={busy || !question.trim()}><Icon name="send" /></button></form>
              </section>
              <aside className="context-panel">
                <div className="panel-title"><h3>Documents</h3><button onClick={() => fileRef.current?.click()}><Icon name="plus" /></button></div>
                <div className="document-list">
                  {documents.map((document) => (
                    <label className="document-row" key={document.id}><input type="checkbox" checked={selected.includes(document.id)} onChange={(e) => setSelected((current) => e.target.checked ? [...current, document.id] : current.filter((id) => id !== document.id))} /><div className="pdf-icon">PDF</div><div><b>{document.filename}</b><span>{document.page_count} pages · {document.chunk_count} chunks</span></div></label>
                  ))}
                  {!documents.length && <div className="empty-docs"><Icon name="file" size={28} /><p>No documents yet</p><button onClick={() => fileRef.current?.click()}>Upload a PDF</button></div>}
                </div>
              </aside>
            </div>
          </>
        )}

        {view === 'documents' && (
          <><header className="topbar"><div><span className="eyebrow">LIBRARY</span><h2>Documents</h2></div><button className="upload-button" onClick={() => fileRef.current?.click()}><Icon name="upload" /> Upload PDF</button></header><section className="page-content"><div className="document-grid">{documents.map((document) => <article className="document-card" key={document.id}><div className="document-card-head"><div className="pdf-icon large">PDF</div><span className="status-dot">Ready</span></div><h3>{document.filename}</h3><p>{document.page_count} pages · {(document.size / 1024).toFixed(0)} KB</p><button className="delete-button" onClick={() => removeDocument(document.id)}><Icon name="trash" /> Delete</button></article>)}</div>{!documents.length && <div className="large-empty"><Icon name="file" size={38} /><h3>Your library is empty</h3><p>Upload a PDF to begin building its searchable knowledge base.</p><button className="primary-button" onClick={() => fileRef.current?.click()}>Upload document</button></div>}</section></>
        )}

        {view === 'history' && (
          <><header className="topbar"><div><span className="eyebrow">ARCHIVE</span><h2>Conversation history</h2></div></header><section className="page-content"><div className="history-list">{history.map((item) => <button className="history-item" key={item.id} onClick={() => { setView('chat'); setMessages([{ role: 'user', content: item.question }, { role: 'assistant', content: item.answer, sources: item.sources }]) }}><div className="history-icon"><Icon name="chat" /></div><div><b>{item.question}</b><p>{item.answer}</p></div></button>)}</div>{!history.length && <div className="large-empty"><Icon name="history" size={38} /><h3>No conversations yet</h3><p>Your questions and answers will appear here.</p></div>}</section></>
        )}
      </section>
      <input ref={fileRef} type="file" accept="application/pdf,.pdf" hidden onChange={upload} />
      {error && view !== 'chat' && <div className="toast">{error}</div>}
    </main>
  )
}

export default App
