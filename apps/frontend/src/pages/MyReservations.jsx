import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import * as Dialog from '@radix-ui/react-dialog'
import { useAuth } from '../auth/AuthContext.jsx'
import { getUserReservations, cancelReservation, getScreeningById, getMovieById } from '../api.js'
import Poster from '../components/Poster.jsx'
import { EmptyState, ErrorState, Skeleton, StatusBadge } from '../components/Feedback.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { formatDateTime, formatPrice } from '../format.js'

const CANCELLABLE_STATUSES = new Set(['pending', 'confirmed'])

// backend returns flat seat rows; one booking = all rows sharing a group_id
function groupByBooking(rows) {
  const groups = new Map()
  for (const r of rows) {
    if (!groups.has(r.group_id)) groups.set(r.group_id, [])
    groups.get(r.group_id).push(r)
  }
  return [...groups.entries()]
    .map(([groupId, seats]) => ({
      groupId,
      screeningId: seats[0].screening_id,
      status: seats[0].status,
      seats: [...seats].sort((a, b) => a.row - b.row || a.seat - b.seat),
      total: seats.reduce((sum, s) => sum + Number(s.price_paid), 0),
    }))
    .sort((a, b) => b.groupId - a.groupId) // newest first
}

// screening_id -> { start_time, title } — reservations only carry the screening id,
// so look each distinct screening (and its movie) up once for display
async function loadScreeningInfo(screeningIds) {
  const info = {}
  await Promise.allSettled(
    screeningIds.map(async (id) => {
      const screening = await getScreeningById(id)
      const movie = await getMovieById(screening.movie_id).catch(() => null)
      info[id] = {
        start_time: screening.start_time,
        title: movie?.title ?? null,
        poster_path: movie?.poster_path ?? null,
      }
    })
  )
  return info
}

function MyReservations() {
  const { user, loading: authLoading, login } = useAuth()
  const [reservations, setReservations] = useState(null)
  const [screeningInfo, setScreeningInfo] = useState({})
  const [error, setError] = useState(null)
  const [confirmId, setConfirmId] = useState(null)
  const [cancellingId, setCancellingId] = useState(null)
  const { t } = useI18n()

  const load = useCallback(async () => {
    try {
      const rows = await getUserReservations()
      setReservations(rows)
      setScreeningInfo(await loadScreeningInfo([...new Set(rows.map((r) => r.screening_id))]))
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => {
    if (user) load()
  }, [user, load])

  if (authLoading) return <Skeleton className="skeleton--block" />

  if (!user) {
    return (
      <EmptyState icon="🎟️" title={t('tickets.signInTitle')}>
        <p>{t('tickets.signInBody')}</p>
        <button onClick={login}>{t('auth.signIn')}</button>
      </EmptyState>
    )
  }

  async function handleCancel(groupId) {
    setCancellingId(groupId)
    try {
      const updated = await cancelReservation(groupId)
      const updatedById = new Map(updated.map((r) => [r.id, r]))
      setReservations((prev) => prev.map((r) => updatedById.get(r.id) ?? r))
    } catch (err) {
      setError(err.message)
    } finally {
      setCancellingId(null)
      setConfirmId(null)
    }
  }

  const bookings = reservations ? groupByBooking(reservations) : null

  return (
    <>
      <div className="page-header">
        <h1>{t('tickets.title')}</h1>
        <p>{t('tickets.subtitle')}</p>
      </div>

      {error && <ErrorState message={error} />}

      {bookings === null ? (
        !error && (
          <div className="tickets">
            <Skeleton className="skeleton--block" style={{ height: 120 }} />
            <Skeleton className="skeleton--block" style={{ height: 120 }} />
          </div>
        )
      ) : bookings.length === 0 ? (
        <EmptyState icon="🎟️" title={t('tickets.emptyTitle')}>
          <p>{t('tickets.emptyBody')}</p>
          <Link className="btn" to="/">{t('tickets.findMovie')}</Link>
        </EmptyState>
      ) : (
        <div className="tickets">
          {bookings.map((b) => {
            const info = screeningInfo[b.screeningId]
            const title = info?.title ?? t('common.screening', { id: b.screeningId })
            const seatList = b.seats.map((s) => t('seats.chip', { row: s.row, seat: s.seat })).join(', ')
            return (
              <article className={`ticket${b.status === 'cancelled' ? ' ticket--cancelled' : ''}`} key={b.groupId}>
                <Poster title={title} posterPath={info?.poster_path} size="sm" />

                <div className="ticket__body">
                  <h3>{title}</h3>
                  <div className="meta">
                    {info && <span>{formatDateTime(info.start_time)}</span>}
                    <StatusBadge status={b.status} />
                  </div>
                  <div className="ticket__seats">
                    {b.seats.map((s) => (
                      <span className="chip" key={s.id}>{t('seats.chipLong', { row: s.row, seat: s.seat })}</span>
                    ))}
                  </div>
                </div>

                <div className="ticket__side">
                  <span className="ticket__total">{formatPrice(b.total)}</span>
                  <span className="ticket__ref">{t('common.booking', { id: b.groupId })}</span>
                  {CANCELLABLE_STATUSES.has(b.status) && (
                    <Dialog.Root open={confirmId === b.groupId} onOpenChange={(open) => setConfirmId(open ? b.groupId : null)}>
                      <Dialog.Trigger asChild>
                        <button className="btn-danger-ghost">{t('tickets.cancel')}</button>
                      </Dialog.Trigger>
                      <Dialog.Portal>
                        <Dialog.Overlay className="dialog-overlay" />
                        <Dialog.Content className="dialog-content">
                          <Dialog.Title>{t('tickets.cancelTitle')}</Dialog.Title>
                          <Dialog.Description>
                            {t('tickets.cancelBody', { title, seats: seatList })}
                            {b.status === 'confirmed' && ` ${t('tickets.cancelRefund')}`} {t('tickets.cancelUndo')}
                          </Dialog.Description>
                          <div className="dialog-actions">
                            <Dialog.Close asChild>
                              <button type="button" className="btn-secondary">{t('tickets.keep')}</button>
                            </Dialog.Close>
                            <button
                              className="btn-danger"
                              onClick={() => handleCancel(b.groupId)}
                              disabled={cancellingId === b.groupId}
                            >
                              {cancellingId === b.groupId ? t('tickets.cancelling') : t('tickets.confirmCancel')}
                            </button>
                          </div>
                        </Dialog.Content>
                      </Dialog.Portal>
                    </Dialog.Root>
                  )}
                </div>
              </article>
            )
          })}
        </div>
      )}
    </>
  )
}

export default MyReservations
