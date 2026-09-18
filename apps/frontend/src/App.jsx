import { useState } from 'react'
import Overview from './Overview.jsx'
import EntityCrud from './EntityCrud.jsx'
import Reservation from './Reservation.jsx'
import Payment from './Payment.jsx'
import { Section } from './ui.jsx'
import entities from './entities.js'
import './App.css'

const NAV = [
  { key: 'overview', label: 'Overview' },
  { key: 'cinema', label: 'Cinemas' },
  { key: 'hall', label: 'Halls' },
  { key: 'movie', label: 'Movies' },
  { key: 'screening', label: 'Screenings' },
  { key: 'reservation', label: 'Reservations' },
  { key: 'payment', label: 'Payment' },
]

function App() {
  const [page, setPage] = useState('overview')
  const [sessionId] = useState(() => new URLSearchParams(window.location.search).get('session_id'))

  if (sessionId) {
    return (
      <div className="shell">
        <main className="content">
          <Section title="Payment received">
            <p>Thanks! We're confirming your payment with Stripe — this can take a few seconds.</p>
            <p>Session: {sessionId}</p>
          </Section>
        </main>
      </div>
    )
  }

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">Gateway Console</div>
        <nav>
          {NAV.map((item) => (
            <button
              key={item.key}
              className={`nav-item${page === item.key ? ' nav-item--active' : ''}`}
              onClick={() => setPage(item.key)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="content">
        {page === 'overview' ? (
          <Overview />
        ) : page === 'reservation' ? (
          <Reservation />
        ) : page === 'payment' ? (
          <Payment />
        ) : (
          <EntityCrud {...entities[page]} />
        )}
      </main>
    </div>
  )
}

export default App
