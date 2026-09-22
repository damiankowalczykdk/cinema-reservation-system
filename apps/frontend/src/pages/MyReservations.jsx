import { useCallback, useEffect, useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { useAuth } from '../auth/AuthContext.jsx'
import { getUserReservations, cancelReservation } from '../api.js'

const CANCELLABLE_STATUSES = new Set(['pending', 'confirmed'])

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

  async function handleCancel(id) {
    setCancellingId(id)
    try {
      const updated = await cancelReservation(id)
      setReservations((prev) => prev.map((r) => (r.id === id ? updated : r)))
    } catch (err) {
      setError(err.message)
    } finally {
      setCancellingId(null)
      setConfirmId(null)
    }
  }

  return (
    <div>
      <h2>My Reservations</h2>
      {error && <p className="error">{error}</p>}

      {reservations === null ? (
        <p>Loading…</p>
      ) : reservations.length === 0 ? (
        <p className="note">No reservations yet.</p>
      ) : (
        <div className="grid">
          {reservations.map((r) => (
            <div className="panel" key={r.id}>
              <p>
                Screening #{r.screening_id} — Row {r.row}, Seat {r.seat}
              </p>
              <p className="note">
                Status: {r.status} · Paid: {Number(r.price_paid).toFixed(2)}
              </p>
              {CANCELLABLE_STATUSES.has(r.status) && (
                <Dialog.Root open={confirmId === r.id} onOpenChange={(open) => setConfirmId(open ? r.id : null)}>
                  <Dialog.Trigger asChild>
                    <button className="btn-danger">Cancel</button>
                  </Dialog.Trigger>
                  <Dialog.Portal>
                    <Dialog.Overlay className="dialog-overlay" />
                    <Dialog.Content className="dialog-content">
                      <Dialog.Title>Cancel this reservation?</Dialog.Title>
                      <Dialog.Description>
                        Row {r.row}, Seat {r.seat} — this can't be undone.
                      </Dialog.Description>
                      <div className="dialog-actions">
                        <Dialog.Close asChild>
                          <button type="button">Keep it</button>
                        </Dialog.Close>
                        <button
                          className="btn-danger"
                          onClick={() => handleCancel(r.id)}
                          disabled={cancellingId === r.id}
                        >
                          {cancellingId === r.id ? 'Cancelling…' : 'Yes, cancel'}
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
