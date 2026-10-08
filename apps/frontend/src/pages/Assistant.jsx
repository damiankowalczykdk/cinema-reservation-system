import { useEffect, useRef, useState } from 'react'
import { sendChatMessage } from '../api.js'
import { useI18n } from '../i18n/LanguageContext.jsx'

// the model answers in Markdown; bold is the only part worth rendering inside a bubble
function renderBold(text) {
  return text.split(/\*\*(.+?)\*\*/g).map((part, i) => (i % 2 ? <strong key={i}>{part}</strong> : part))
}

function Assistant() {
  const { t } = useI18n()
  const [messages, setMessages] = useState([]) // [{ role: 'user' | 'assistant', text }]
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  // id of the assistant's last answer; sending it back is what gives the chat its memory
  const [responseId, setResponseId] = useState(null)
  const logRef = useRef(null)

  useEffect(() => {
    const log = logRef.current
    if (log) log.scrollTop = log.scrollHeight
  }, [messages, sending])

  async function send(text) {
    const message = text.trim()
    if (!message || sending) return
    setMessages((prev) => [...prev, { role: 'user', text: message }])
    setInput('')
    setError(null)
    setSending(true)
    try {
      const data = await sendChatMessage(message, responseId)
      setMessages((prev) => [...prev, { role: 'assistant', text: data.answer }])
      if (data.response_id) setResponseId(data.response_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  function reset() {
    setMessages([])
    setResponseId(null)
    setError(null)
  }

  return (
    <div className="chat">
      <div className="page-header chat__header">
        <div>
          <h1>{t('assistant.title')}</h1>
          <p>{t('assistant.subtitle')}</p>
        </div>
        {messages.length > 0 && (
          <button type="button" className="btn-ghost" onClick={reset} disabled={sending}>
            {t('assistant.new')}
          </button>
        )}
      </div>

      <div className="chat__log" ref={logRef} role="log" aria-live="polite">
        {messages.length === 0 ? (
          <div className="chat__intro">
            <p>{t('assistant.greeting')}</p>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`chat__msg chat__msg--${m.role}`}>
              {m.role === 'assistant' ? renderBold(m.text) : m.text}
            </div>
          ))
        )}
        {sending && <div className="chat__msg chat__msg--assistant chat__msg--pending">{t('assistant.thinking')}</div>}
      </div>

      {error && <div className="alert alert--error">{error}</div>}

      <form
        className="chat__form"
        onSubmit={(e) => {
          e.preventDefault()
          send(input)
        }}
      >
        <input
          className="chat__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t('assistant.placeholder')}
          aria-label={t('assistant.placeholder')}
          autoFocus
        />
        <button type="submit" disabled={sending || !input.trim()}>
          {t('assistant.send')}
        </button>
      </form>
    </div>
  )
}

export default Assistant
