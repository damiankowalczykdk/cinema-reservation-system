import { useEffect, useState } from 'react'
import SeatMap, { seatKey } from './SeatMap.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { getOccupiedSeats } from '../api.js'

function bySeat(a, b) {
  return a.row - b.row || a.seat - b.seat
}

// Seat map shown under an assistant answer. It only collects a selection: the booking
// itself is made by the assistant, so confirming hands the seats back to the chat.
function ChatSeatPicker({ screeningId, disabled, onConfirm }) {
  const { t } = useI18n()
  const [hall, setHall] = useState(null) // { occupied: Set, rows, seatsPerRow }
  const [loadError, setLoadError] = useState(null)
  const [selected, setSelected] = useState([])
  const [confirmed, setConfirmed] = useState(false)

  useEffect(() => {
    let cancelled = false
    getOccupiedSeats(screeningId)
      .then((data) => {
        if (cancelled) return
        setHall({
          occupied: new Set(data.seats.map(([row, seat]) => seatKey(row, seat))),
          rows: data.row,
          seatsPerRow: data.seat_per_row,
        })
      })
      .catch((err) => {
        if (!cancelled) setLoadError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [screeningId])

  function toggleSeat(row, seat) {
    if (confirmed || disabled) return
    setSelected((prev) =>
      prev.some((s) => s.row === row && s.seat === seat)
        ? prev.filter((s) => !(s.row === row && s.seat === seat))
        : [...prev, { row, seat }]
    )
  }

  function confirm() {
    setConfirmed(true)
    onConfirm([...selected].sort(bySeat))
  }

  if (loadError) return <div className="alert alert--error">{loadError}</div>
  if (!hall) return <div className="chat__seats muted">{t('assistant.mapLoading')}</div>

  return (
    <div className="chat__seats">
      <SeatMap
        rows={hall.rows}
        seatsPerRow={hall.seatsPerRow}
        occupied={hall.occupied}
        selected={selected}
        onToggle={toggleSeat}
      />
      {!confirmed && (
        <button type="button" onClick={confirm} disabled={disabled || selected.length === 0}>
          {selected.length === 0 ? t('assistant.pickSeats') : t('assistant.confirmSeats', { count: selected.length })}
        </button>
      )}
    </div>
  )
}

export default ChatSeatPicker
