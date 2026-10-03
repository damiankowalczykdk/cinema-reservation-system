import { useCallback, useEffect, useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { useAuth } from '../auth/AuthContext.jsx'
import { getUserReservations, cancelReservation } from '../api.js'

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
      seats,
      total: seats.reduce((sum, s) => sum + Number(s.price_paid), 0),
    }))
    .sort((a, b) => b.groupId - a.groupId) // newest first
}

function seatList(seats) {
  return seats.map((s) => `R${s.row}-S${s.seat}`).join(', ')
}

function MyReservations() {
  const { user, loading: authLoading, login } = useAuth()
  const [reservations, setReservations] = useState(null)
  const [error, setError] = useState(null)
  const [confirmId, setConfirmId] = useState(null)
  const [cancellingId, setCancellingId] = useState(null)

  const load = useCallback(async () => {
    try {
      setReservations(await getUserReservations())
    } catch (err) {
      setError(err.message)
    }
  }, [])

  useEffect(() => {
    if (user) load()
  }, [user, load])

  if (authLoading) return <p>Loading…</p>

  if (!user) {
    return (
      <div>
        <h2>My Reservations</h2>
        <p className="note">You need to be logged in to see your reservations.</p>
        <button onClick={login}>Log in</button>
      </div>
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
    <div>
      <h2>My Reservations</h2>
      {error && <p className="error">{error}</p>}

      {bookings === null ? (
        <p>Loading…</p>
      ) : bookings.length === 0 ? (
        <p className="note">No reservations yet.</p>
      ) : (
        <div className="grid">
          {bookings.map((b) => (
            <div className="panel" key={b.groupId}>
              <p>
                Booking #{b.groupId} · Screening #{b.screeningId}
              </p>
              <p>
                {b.seats.length} seat{b.seats.length === 1 ? '' : 's'}: {seatList(b.seats)}
              </p>
              <p className="note">
                Status: {b.status} · Total: {b.total.toFixed(2)}
              </p>
              {CANCELLABLE_STATUSES.has(b.status) && (
                <Dialog.Root open={confirmId === b.groupId} onOpenChange={(open) => setConfirmId(open ? b.groupId : null)}>
                  <Dialog.Trigger asChild>
                    <button className="btn-danger">Cancel booking</button>
                  </Dialog.Trigger>
                  <Dialog.Portal>
                    <Dialog.Overlay className="dialog-overlay" />
                    <Dialog.Content className="dialog-content">
                      <Dialog.Title>Cancel this booking?</Dialog.Title>
                      <Dialog.Description>
                        All seats ({seatList(b.seats)}) will be released — this can't be undone.
                      </Dialog.Description>
                      <div className="dialog-actions">
                        <Dialog.Close asChild>
                          <button type="button">Keep it</button>
                        </Dialog.Close>
                        <button
                          className="btn-danger"
                          onClick={() => handleCancel(b.groupId)}
                          disabled={cancellingId === b.groupId}
                        >
                          {cancellingId === b.groupId ? 'Cancelling…' : 'Yes, cancel'}
                        </button>
                      </div>
                    </Dialog.Content>
                  </Dialog.Portal>
                </Dialog.Root>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyReservations
