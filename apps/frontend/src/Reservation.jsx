import { useState } from 'react'
import { Section, ResultBlock, useAction, Field } from './ui.jsx'
import {
  createReservation,
  getReservationById,
  getUserReservations,
  cancelReservation,
  getOccupiedSeats,
} from './api.js'

const GUEST_FIELDS = [
  { name: 'guest_email', label: 'Guest email (fill only if NOT logged in)', type: 'text' },
  { name: 'guest_name', label: 'Guest name (optional, guest only)', type: 'text' },
]

function seatKey(row, seat) {
  return `${row}-${seat}`
}

function emptyGuestForm() {
  return { guest_email: '', guest_name: '' }
}

// Create Reservation, built around a visual seat map instead of typing row/seat by hand:
// pick a Screening ID -> load the hall's dimensions + which seats are already taken for that
// screening -> click any number of free seats -> fill guest fields only if not logged in -> Create.
// Backend only knows how to reserve one seat per call, so Create fires one request per selected
// seat and reports which succeeded/failed individually (e.g. someone else grabbed one in the meantime).
function CreateReservationSection() {
  const [screeningId, setScreeningId] = useState('')
  const [hall, setHall] = useState(null) // { rows, seatsPerRow }
  const [occupied, setOccupied] = useState(null) // Set of "row-seat"
  const [selectedSeats, setSelectedSeats] = useState([]) // [{ row, seat }, ...]
  const [mapLoading, setMapLoading] = useState(false)
  const [mapError, setMapError] = useState(null)

  const [guestForm, setGuestForm] = useState(emptyGuestForm())
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState(null)
  const [createResult, setCreateResult] = useState(undefined)

  async function loadSeatMap(e) {
    e.preventDefault()
    setMapError(null)
    setHall(null)
    setOccupied(null)
    setSelectedSeats([])
    setCreateResult(undefined)
    setMapLoading(true)
    try {
      // one public call: gives both hall dimensions and which seats are already taken,
      // so this works for guests too (getHallById/getScreeningById are admin-only on the gateway)
      const data = await getOccupiedSeats(screeningId)
      setHall({ rows: data.row, seatsPerRow: data.seat_per_row })
      setOccupied(new Set(data.seats.map(([row, seat]) => seatKey(row, seat))))
    } catch (err) {
      setMapError(err.message)
    } finally {
      setMapLoading(false)
    }
  }

  function toggleSeat(row, seat) {
    setSelectedSeats((prev) =>
      prev.some((s) => s.row === row && s.seat === seat)
        ? prev.filter((s) => !(s.row === row && s.seat === seat))
        : [...prev, { row, seat }]
    )
  }

  async function handleCreate(e) {
    e.preventDefault()
    if (selectedSeats.length === 0) return
    setCreating(true)
    setCreateError(null)

    const created = []
    const failed = []
    for (const s of selectedSeats) {
      const payload = {
        screening_id: Number(screeningId),
        row: s.row,
        seat: s.seat,
        guest_email: guestForm.guest_email || undefined,
        guest_name: guestForm.guest_name || undefined,
      }
      try {
        created.push(await createReservation(payload))
      } catch (err) {
        failed.push({ row: s.row, seat: s.seat, error: err.message })
      }
    }

    setCreateResult({ created, failed })
    setCreateError(failed.length ? `${failed.length} of ${selectedSeats.length} seat(s) failed — see result below` : null)
    // reflect successfully created reservations on the map immediately, no need to reload
    setOccupied((prev) => {
      const next = new Set(prev)
      created.forEach((r) => next.add(seatKey(r.row, r.seat)))
      return next
    })
    // keep only the ones that failed selected, so they're easy to retry
    setSelectedSeats(failed.map((f) => ({ row: f.row, seat: f.seat })))
    if (!failed.length) setGuestForm(emptyGuestForm())
    setCreating(false)
  }

  return (
    <Section title="Create Reservation" method="POST">
      <p className="note">
        Logged in? Leave the guest fields empty — the reservation is tied to your account via your
        session cookie automatically. Not logged in? Fill in Guest email so the reservation is
        traceable as a guest booking.
      </p>

      <form onSubmit={loadSeatMap} className="seat-map-load">
        <div className="field">
          <label>Screening ID</label>
          <input value={screeningId} onChange={(e) => setScreeningId(e.target.value)} required />
        </div>
        <button type="submit" disabled={mapLoading || !screeningId}>
          {mapLoading ? 'Loading…' : 'Load seats'}
        </button>
      </form>
      {mapError && <p className="error">{mapError}</p>}

      {hall && occupied && (
        <>
          <div className="seat-map">
            {Array.from({ length: hall.rows }, (_, i) => i + 1).map((row) => (
              <div className="seat-map__row" key={row}>
                <span className="seat-map__row-label">{row}</span>
                {Array.from({ length: hall.seatsPerRow }, (_, i) => i + 1).map((seat) => {
                  const taken = occupied.has(seatKey(row, seat))
                  const isSelected = selectedSeats.some((s) => s.row === row && s.seat === seat)
                  return (
                    <button
                      type="button"
                      key={seat}
                      className={`seat${taken ? ' seat--taken' : ''}${isSelected ? ' seat--selected' : ''}`}
                      disabled={taken}
                      onClick={() => toggleSeat(row, seat)}
                      title={`Row ${row}, Seat ${seat}${taken ? ' — taken' : ''}`}
                    >
                      {seat}
                    </button>
                  )
                })}
              </div>
            ))}
          </div>
          <div className="seat-map__legend">
            <span>
              <i className="seat-map__swatch" /> free
            </span>
            <span>
              <i className="seat-map__swatch seat-map__swatch--taken" /> taken
            </span>
            <span>
              <i className="seat-map__swatch seat-map__swatch--selected" /> selected
            </span>
          </div>

          <form onSubmit={handleCreate}>
            <p className="note">
              {selectedSeats.length > 0
                ? `Selected (${selectedSeats.length}): ${selectedSeats.map((s) => `R${s.row}-S${s.seat}`).join(', ')}`
                : 'Pick one or more free seats above (click to toggle).'}
            </p>
            {GUEST_FIELDS.map((f) => (
              <Field key={f.name} field={f} value={guestForm[f.name]} onChange={(name, v) => setGuestForm({ ...guestForm, [name]: v })} />
            ))}
            <button type="submit" disabled={creating || selectedSeats.length === 0}>
              {creating ? 'Creating…' : `Create ${selectedSeats.length || ''} reservation${selectedSeats.length === 1 ? '' : 's'}`}
            </button>
          </form>
        </>
      )}

      <ResultBlock error={createError} result={createResult} />
    </Section>
  )
}

function GetReservationSection() {
  const [id, setId] = useState('')
  const { run, loading, error, result } = useAction(getReservationById)

  function handleSubmit(e) {
    e.preventDefault()
    run(id)
  }

  return (
    <Section title="Get Reservation by ID (admin only)" method="GET">
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input value={id} onChange={(e) => setId(e.target.value)} required />
        </div>
        <button type="submit" disabled={loading}>
          Get
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function MyReservationsSection() {
  const { run, loading, error, result } = useAction(getUserReservations)

  return (
    <Section title="My Reservations (requires login)" method="GET">
      <button onClick={() => run()} disabled={loading}>
        Load my reservations
      </button>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function CancelReservationSection() {
  const [id, setId] = useState('')
  const { run, loading, error, result } = useAction(cancelReservation)

  function handleSubmit(e) {
    e.preventDefault()
    run(id)
  }

  return (
    <Section title="Cancel Reservation (owner or admin, requires login)" method="POST" variant="danger">
      <form onSubmit={handleSubmit}>
        <div className="field">
          <label>ID</label>
          <input value={id} onChange={(e) => setId(e.target.value)} required />
        </div>
        <button type="submit" className="btn-danger" disabled={loading}>
          Cancel
        </button>
      </form>
      <ResultBlock error={error} result={result} />
    </Section>
  )
}

function Reservation() {
  return (
    <div>
      <h2>Reservations</h2>
      <p className="note">
        Create works both logged in and as a guest (see note below). Get by ID is admin-only. My
        Reservations and Cancel both require a login — check the Auth panel on Overview first.
      </p>
      <CreateReservationSection />
      <div className="grid">
        <GetReservationSection />
        <MyReservationsSection />
        <CancelReservationSection />
      </div>
    </div>
  )
}

export default Reservation
