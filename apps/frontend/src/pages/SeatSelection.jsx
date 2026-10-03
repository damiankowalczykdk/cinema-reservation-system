import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import SeatMap, { seatKey } from '../components/SeatMap.jsx'
import { useAuth } from '../auth/AuthContext.jsx'
import {
  getOccupiedSeats,
  getScreeningById,
  getMovieById,
  createReservation,
  createPayment,
} from '../api.js'

function emptyGuestForm() {
  return { guest_email: '', guest_name: '' }
}

function SeatSelection() {
  const { screeningId } = useParams()
  const { user } = useAuth()

  const [screening, setScreening] = useState(null)
  const [movie, setMovie] = useState(null)
  const [occupied, setOccupied] = useState(null)
  const [rows, setRows] = useState(null)
  const [seatsPerRow, setSeatsPerRow] = useState(null)
  const [loadError, setLoadError] = useState(null)

  const [selectedSeats, setSelectedSeats] = useState([])
  const [guestForm, setGuestForm] = useState(emptyGuestForm())
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState(null)
  const [booking, setBooking] = useState(null) // seat rows of the just-created group
  const [paying, setPaying] = useState(false)

  async function refreshOccupied() {
    const seatsData = await getOccupiedSeats(screeningId)
    setOccupied(new Set(seatsData.seats.map(([row, seat]) => seatKey(row, seat))))
    return seatsData
  }

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoadError(null)
      try {
        const [seatsData, screeningData] = await Promise.all([
          getOccupiedSeats(screeningId),
          getScreeningById(screeningId),
        ])
        if (cancelled) return
        setOccupied(new Set(seatsData.seats.map(([row, seat]) => seatKey(row, seat))))
        setRows(seatsData.row)
        setSeatsPerRow(seatsData.seat_per_row)
        setScreening(screeningData)
        const movieData = await getMovieById(screeningData.movie_id)
        if (!cancelled) setMovie(movieData)
      } catch (err) {
        if (!cancelled) setLoadError(err.message)
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [screeningId])

  function toggleSeat(row, seat) {
    setSelectedSeats((prev) =>
      prev.some((s) => s.row === row && s.seat === seat)
        ? prev.filter((s) => !(s.row === row && s.seat === seat))
        : [...prev, { row, seat }]
    )
  }

  async function payFor(groupId) {
    setPaying(true)
    try {
      const { checkout_url } = await createPayment({
        group_id: groupId,
        guest_email: guestForm.guest_email || undefined,
      })
      // full browser navigation, not fetch — Stripe's checkout page is a different
      // origin and won't let a background request read/display it
      window.location.href = checkout_url
    } catch (err) {
      setCreateError(err.message)
      setPaying(false)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (selectedSeats.length === 0) return
    setCreating(true)
    setCreateError(null)

    // all selected seats go in one request: the backend books them atomically
    // (all or nothing) under a single group_id, which is then paid in one checkout
    let created
    try {
      created = await createReservation({
        screening_id: Number(screeningId),
        seats: selectedSeats,
        guest_email: guestForm.guest_email || undefined,
        guest_name: guestForm.guest_name || undefined,
      })
    } catch (err) {
      setCreateError(`${err.message} — nothing was booked. Pick different seats and try again.`)
      setCreating(false)
      // someone may have just taken a seat: reload so the map shows it as occupied
      refreshOccupied().catch(() => {})
      return
    }

    setOccupied((prev) => {
      const next = new Set(prev)
      created.forEach((r) => next.add(seatKey(r.row, r.seat)))
      return next
    })
    setSelectedSeats([])
    setBooking(created)
    setCreating(false)

    await payFor(created[0].group_id)
  }

  const bookingTotal = booking ? booking.reduce((sum, r) => sum + Number(r.price_paid), 0) : 0

  if (loadError) return <p className="error">{loadError}</p>
  if (!screening || occupied === null) return <p>Loading…</p>

  return (
    <div>
      <h2>{movie ? movie.title : `Screening #${screeningId}`}</h2>
      <p className="note">
        {new Date(screening.start_time).toLocaleString()} — {Number(screening.price).toFixed(2)} per seat
      </p>

      <SeatMap rows={rows} seatsPerRow={seatsPerRow} occupied={occupied} selected={selectedSeats} onToggle={toggleSeat} />

      <form onSubmit={handleSubmit}>
        <p className="note">
          {selectedSeats.length > 0
            ? `Selected (${selectedSeats.length}): ${selectedSeats.map((s) => `R${s.row}-S${s.seat}`).join(', ')}`
            : 'Pick one or more free seats above.'}
        </p>
        {!user && (
          <>
            <div className="field">
              <label>Email</label>
              <input
                type="text"
                value={guestForm.guest_email}
                onChange={(e) => setGuestForm({ ...guestForm, guest_email: e.target.value })}
                required
              />
            </div>
            <div className="field">
              <label>Name (optional)</label>
              <input
                type="text"
                value={guestForm.guest_name}
                onChange={(e) => setGuestForm({ ...guestForm, guest_name: e.target.value })}
              />
            </div>
          </>
        )}
        <button type="submit" disabled={creating || paying || selectedSeats.length === 0}>
          {creating ? 'Booking…' : `Book ${selectedSeats.length || ''} seat${selectedSeats.length === 1 ? '' : 's'}`}
        </button>
      </form>

      {createError && <p className="error">{createError}</p>}

      {booking && (
        <div className="panel">
          <p>
            Booking #{booking[0].group_id}: {booking.map((r) => `R${r.row}-S${r.seat}`).join(', ')}
          </p>
          <p className="note">Total: {bookingTotal.toFixed(2)}</p>
          <button onClick={() => payFor(booking[0].group_id)} disabled={paying}>
            {paying ? 'Redirecting…' : 'Pay now'}
          </button>
        </div>
      )}
    </div>
  )
}

export default SeatSelection
