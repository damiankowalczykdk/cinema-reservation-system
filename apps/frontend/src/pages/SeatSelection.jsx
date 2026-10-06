import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import SeatMap, { seatKey } from '../components/SeatMap.jsx'
import Poster from '../components/Poster.jsx'
import Steps from '../components/Steps.jsx'
import { ErrorState, Skeleton } from '../components/Feedback.jsx'
import { useAuth } from '../auth/AuthContext.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { formatDateLong, formatTime, formatPrice, formatDuration } from '../format.js'
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

function bySeat(a, b) {
  return a.row - b.row || a.seat - b.seat
}

function SeatSelection() {
  const { screeningId } = useParams()
  const { user } = useAuth()
  const { t } = useI18n()

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
      setCreateError(t('seats.createFailed', { message: err.message }))
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

  if (loadError) return <ErrorState message={loadError} />

  if (!screening || occupied === null) {
    return (
      <div className="booking-layout">
        <Skeleton className="skeleton--block" />
        <Skeleton className="skeleton--block" />
      </div>
    )
  }

  const title = movie ? movie.title : t('common.screening', { id: screeningId })
  const seatPrice = Number(screening.price)
  // once the booking exists the selection is cleared, so the summary switches to the booked seats
  const summarySeats = booking
    ? booking.map((r) => ({ row: r.row, seat: r.seat }))
    : [...selectedSeats].sort(bySeat)
  const total = booking
    ? booking.reduce((sum, r) => sum + Number(r.price_paid), 0)
    : selectedSeats.length * seatPrice

  return (
    <>
      <Link to={movie ? `/movies/${movie.id}` : '/'} className="back-link">{t('seats.back')}</Link>
      <Steps current={booking ? 1 : 0} />

      <div className="booking-layout">
        <div>
          <div className="page-header">
            <h2>{t('seats.title')}</h2>
            <p>{t('seats.help')}</p>
          </div>
          <SeatMap rows={rows} seatsPerRow={seatsPerRow} occupied={occupied} selected={selectedSeats} onToggle={toggleSeat} />
        </div>

        <aside className="summary">
          <div className="summary__movie">
            <Poster title={title} posterPath={movie?.poster_path} size="sm" />
            <div>
              <h3>{title}</h3>
              <div className="muted" style={{ fontSize: 13 }}>
                {movie && `${formatDuration(movie.duration_minutes)} · `}
                {formatTime(screening.start_time)}
              </div>
            </div>
          </div>

          <div className="summary__row">
            <span className="muted">{t('seats.date')}</span>
            <span>{formatDateLong(screening.start_time)}</span>
          </div>
          <div className="summary__row">
            <span className="muted">{t('seats.ticket')}</span>
            <span>{formatPrice(seatPrice)}</span>
          </div>

          <div className="summary__row" style={{ marginBottom: 4 }}>
            <span className="muted">{t('seats.seats')}</span>
            <span>{summarySeats.length || '—'}</span>
          </div>
          <div className="summary__seats">
            {summarySeats.length === 0 ? (
              <span className="muted" style={{ fontSize: 13 }}>{t('seats.none')}</span>
            ) : (
              summarySeats.map((s) => (
                <span className="chip" key={seatKey(s.row, s.seat)}>
                  {t('seats.chip', { row: s.row, seat: s.seat })}
                </span>
              ))
            )}
          </div>

          {booking ? (
            <>
              <div className="summary__total">
                <span>{t('common.total')}</span>
                <strong>{formatPrice(total)}</strong>
              </div>
              <button className="btn--lg btn--block" onClick={() => payFor(booking[0].group_id)} disabled={paying}>
                {paying ? t('seats.redirecting') : t('seats.payNow')}
              </button>
              <p className="summary__hint">{t('seats.held', { id: booking[0].group_id })}</p>
            </>
          ) : (
            <form onSubmit={handleSubmit}>
              {!user && (
                <>
                  <div className="field">
                    <label htmlFor="guest-email">{t('seats.email')}</label>
                    <input
                      id="guest-email"
                      type="email"
                      placeholder={t('seats.emailPlaceholder')}
                      value={guestForm.guest_email}
                      onChange={(e) => setGuestForm({ ...guestForm, guest_email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="field">
                    <label htmlFor="guest-name">{t('seats.name')}</label>
                    <input
                      id="guest-name"
                      type="text"
                      value={guestForm.guest_name}
                      onChange={(e) => setGuestForm({ ...guestForm, guest_name: e.target.value })}
                    />
                  </div>
                </>
              )}

              <div className="summary__total">
                <span>{t('common.total')}</span>
                <strong>{formatPrice(total)}</strong>
              </div>

              <button
                type="submit"
                className="btn--lg btn--block"
                disabled={creating || paying || selectedSeats.length === 0}
              >
                {creating
                  ? t('seats.reserving')
                  : paying
                    ? t('seats.redirecting')
                    : selectedSeats.length === 0
                      ? t('seats.selectToContinue')
                      : t('seats.continue')}
              </button>
              <p className="summary__hint">{t('seats.secure')}</p>
            </form>
          )}

          {createError && <div className="alert alert--error">{createError}</div>}
        </aside>
      </div>
    </>
  )
}

export default SeatSelection
