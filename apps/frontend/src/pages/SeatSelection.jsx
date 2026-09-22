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
  const [createdReservations, setCreatedReservations] = useState([])
  const [payingId, setPayingId] = useState(null)

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

  async function payFor(reservation) {
    setPayingId(reservation.id)
    try {
      const { checkout_url } = await createPayment({
        reservation_id: reservation.id,
        guest_email: guestForm.guest_email || undefined,
      })
      // full browser navigation, not fetch — Stripe's checkout page is a different
      // origin and won't let a background request read/display it
      window.location.href = checkout_url
    } catch (err) {
      setCreateError(err.message)
      setPayingId(null)
    }
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (selectedSeats.length === 0) return
    setCreating(true)
    setCreateError(null)

    // backend only knows how to reserve one seat per call, so this fires one
    // request per selected seat and reports which succeeded/failed individually
    const created = []
    const failed = []
    for (const s of selectedSeats) {
      try {
        created.push(
          await createReservation({
            screening_id: Number(screeningId),
            row: s.row,
            seat: s.seat,
            guest_email: guestForm.guest_email || undefined,
            guest_name: guestForm.guest_name || undefined,
          })
        )
      } catch (err) {
        failed.push({ row: s.row, seat: s.seat, error: err.message })
      }
    }

    setOccupied((prev) => {
      const next = new Set(prev)
      created.forEach((r) => next.add(seatKey(r.row, r.seat)))
      return next
    })
    setSelectedSeats(failed.map((f) => ({ row: f.row, seat: f.seat })))
    setCreatedReservations(created)
    setCreateError(
      failed.length
        ? `${failed.length} of ${selectedSeats.length} seat(s) could not be booked — someone may have just taken them. Retry the highlighted seat(s) below.`
        : null
    )
    setCreating(false)

    // checkout is one-reservation-at-a-time on the backend, so the single-seat,
    // no-failures case can go straight to Stripe without an extra click
    if (created.length === 1 && failed.length === 0) {
      await payFor(created[0])
    }
  }

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
        <button type="submit" disabled={creating || selectedSeats.length === 0}>
          {creating ? 'Booking…' : `Book ${selectedSeats.length || ''} seat${selectedSeats.length === 1 ? '' : 's'}`}
        </button>
      </form>

      {createError && <p className="error">{createError}</p>}

      {createdReservations.length > 0 && (
        <div className="grid">
          {createdReservations.map((r) => (
            <div className="panel" key={r.id}>
              <p>
                Row {r.row}, Seat {r.seat}
              </p>
              <button onClick={() => payFor(r)} disabled={payingId !== null}>
                {payingId === r.id ? 'Redirecting…' : 'Pay for this seat'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SeatSelection
