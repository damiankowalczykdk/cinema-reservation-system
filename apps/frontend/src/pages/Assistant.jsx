import { useEffect, useRef, useState } from 'react'
import { sendChatMessage, createPayment } from '../api.js'
import { useI18n } from '../i18n/LanguageContext.jsx'
import ChatSeatPicker from '../components/ChatSeatPicker.jsx'

// the model answers in Markdown; bold is the only part worth rendering inside a bubble
function renderBold(text) {
  return text.split(/\*\*(.+?)\*\*/g).map((part, i) => (i % 2 ? <strong key={i}>{part}</strong> : part))
}

function SparkIcon() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor" aria-hidden="true">
      <path d="M12 2l1.9 5.6a4 4 0 0 0 2.5 2.5L22 12l-5.6 1.9a4 4 0 0 0-2.5 2.5L12 22l-1.9-5.6a4 4 0 0 0-2.5-2.5L2 12l5.6-1.9a4 4 0 0 0 2.5-2.5L12 2z" />
    </svg>
  )
}

// what the assistant can do, shown only while the chat is empty; informational, not clickable
const HOW_IT_WORKS = ['find', 'seats', 'pay']

function Assistant() {
  const { t } = useI18n()
  // [{ role: 'user' | 'assistant', text, reservation?, seatMapScreeningId? }]
  // reservation is set on the answer that created a booking and is what the pay button
  // under it works on; seatMapScreeningId is set when the assistant looked up a hall and
  // makes the seat map appear under that answer
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [paying, setPaying] = useState(false)
  const [error, setError] = useState(null)
  // id of the conversation; sending it back is what gives the chat its memory
  const [conversationId, setConversationId] = useState(null)
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
      const data = await sendChatMessage(message, conversationId)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: data.answer,
          reservation: data.reservation ?? null,
          seatMapScreeningId: data.seats_map_screening_id ?? null,
        },
      ])
      if (data.conversation_id) setConversationId(data.conversation_id)
    } catch (err) {
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  async function payFor(reservation) {
    setPaying(true)
    setError(null)
    try {
      const { checkout_url } = await createPayment({
        group_id: reservation.group_id,
        guest_email: reservation.guest_email || undefined,
      })
      // full browser navigation, not fetch — Stripe's checkout page is a different origin
      window.location.href = checkout_url
    } catch (err) {
      setError(err.message)
      setPaying(false)
    }
  }

  // seats picked on the map go back to the assistant as an ordinary chat message
  function sendSeats(seats) {
    const list = seats.map((s) => t('assistant.seatPhrase', { row: s.row, seat: s.seat })).join(', ')
    send(t('assistant.pickMessage', { seats: list }))
  }

  function reset() {
    setMessages([])
    setConversationId(null)
    setError(null)
  }

  return (
    <div className="chat">
      <div className="page-header chat__header">
        <div className="chat__title">
          <span className="chat__badge">
            <SparkIcon />
          </span>
          <div>
            <h1>{t('assistant.title')}</h1>
            <p>{t('assistant.subtitle')}</p>
          </div>
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
            <span className="chat__badge chat__badge--lg">
              <SparkIcon />
            </span>
            <p className="chat__greeting">{t('assistant.greeting')}</p>
            <ol className="chat__how">
              {HOW_IT_WORKS.map((step, i) => (
                <li key={step} className="chat__how-step">
                  <span className="chat__how-num">{i + 1}</span>
                  <strong>{t(`assistant.how.${step}.title`)}</strong>
                  <span>{t(`assistant.how.${step}.text`)}</span>
                </li>
              ))}
            </ol>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`chat__msg chat__msg--${m.role}`}>
              {m.role === 'assistant' ? renderBold(m.text) : m.text}
              {m.seatMapScreeningId && (
                <ChatSeatPicker screeningId={m.seatMapScreeningId} disabled={sending} onConfirm={sendSeats} />
              )}
              {m.reservation && (
                <button type="button" className="chat__pay" onClick={() => payFor(m.reservation)} disabled={paying}>
                  {paying ? t('assistant.redirecting') : t('assistant.pay')}
                </button>
              )}
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
