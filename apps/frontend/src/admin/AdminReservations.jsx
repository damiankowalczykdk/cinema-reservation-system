import { useState } from 'react'
import * as Dialog from '@radix-ui/react-dialog'
import { getReservationGroup, cancelReservation, deleteReservationGroup } from '../api.js'

const CANCELLABLE_STATUSES = new Set(['pending', 'confirmed'])

function seatList(seats) {
  return seats.map((s) => `R${s.row}-S${s.seat}`).join(', ')
}

// gateway has no "list all reservations" endpoint, so admin looks a booking up by its group_id
function AdminReservations() {
  const [groupIdInput, setGroupIdInput] = useState('')
  const [seats, setSeats] = useState(null)
  const [error, setError] = useState(null)
  const [message, setMessage] = useState(null)
  const [busy, setBusy] = useState(false)
  const [confirm, setConfirm] = useState(null) // 'cancel' | 'delete' | null

  async function handleLookup(e) {
    e.preventDefault()
    setError(null)
    setMessage(null)
    setSeats(null)
    setBusy(true)
    try {
      setSeats(await getReservationGroup(groupIdInput))
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  async function handleCancel(groupId) {
    setBusy(true)
    setError(null)
    try {
      setSeats(await cancelReservation(groupId))
      setMessage(`Booking #${groupId} cancelled.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
      setConfirm(null)
    }
  }

  async function handleDelete(groupId) {
    setBusy(true)
    setError(null)
    try {
      await deleteReservationGroup(groupId)
      setSeats(null)
      setMessage(`Booking #${groupId} deleted.`)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
      setConfirm(null)
    }
  }

  const booking = seats && seats.length > 0 ? seats : null
  const first = booking?.[0]
  const total = booking ? booking.reduce((sum, s) => sum + Number(s.price_paid), 0) : 0

  return (
    <div>
      <h2>Reservations</h2>

      <form className="panel" onSubmit={handleLookup}>
        <div className="field">
          <label>Booking # (group id)</label>
          <input
            type="number"
            min="1"
            value={groupIdInput}
            onChange={(e) => setGroupIdInput(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={busy}>
          {busy && !booking ? 'Looking up…' : 'Look up'}
        </button>
      </form>

      {error && <p className="error">{error}</p>}
      {message && <p className="note">{message}</p>}

      {booking && (
        <div className="panel">
          <p>
            Booking #{first.group_id} · Screening #{first.screening_id}
          </p>
          <p>
            {booking.length} seat{booking.length === 1 ? '' : 's'}: {seatList(booking)}
          </p>
          <p className="note">
            Status: {first.status} · Total: {total.toFixed(2)}
          </p>
          <p className="note">
            {first.user_id ? `User: ${first.user_id}` : `Guest: ${first.guest_email ?? '—'}${first.guest_name ? ` (${first.guest_name})` : ''}`}
          </p>

          <Dialog.Root open={confirm !== null} onOpenChange={(open) => !open && setConfirm(null)}>
            <div className="dialog-actions">
              {CANCELLABLE_STATUSES.has(first.status) && (
                <button className="btn-danger" onClick={() => setConfirm('cancel')} disabled={busy}>
                  Cancel booking
                </button>
              )}
              <button className="btn-danger" onClick={() => setConfirm('delete')} disabled={busy}>
                Delete booking
              </button>
            </div>
            <Dialog.Portal>
              <Dialog.Overlay className="dialog-overlay" />
              <Dialog.Content className="dialog-content">
                <Dialog.Title>
                  {confirm === 'delete' ? 'Delete' : 'Cancel'} booking #{first.group_id}?
                </Dialog.Title>
                <Dialog.Description>
                  {confirm === 'delete'
                    ? `All seat rows (${seatList(booking)}) will be permanently removed from the database.`
                    : `All seats (${seatList(booking)}) will be released.`}
                </Dialog.Description>
                <div className="dialog-actions">
                  <Dialog.Close asChild>
                    <button type="button">Back</button>
                  </Dialog.Close>
                  <button
                    className="btn-danger"
                    disabled={busy}
                    onClick={() =>
                      confirm === 'delete' ? handleDelete(first.group_id) : handleCancel(first.group_id)
                    }
                  >
                    {busy ? 'Working…' : `Yes, ${confirm}`}
                  </button>
                </div>
              </Dialog.Content>
            </Dialog.Portal>
          </Dialog.Root>
        </div>
      )}
    </div>
  )
}

export default AdminReservations
