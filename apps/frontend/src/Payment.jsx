import { useState } from 'react'
import { Section, Field } from './ui.jsx'
import { createPayment } from './api.js'

const FIELDS = [
  { name: 'reservation_id', label: 'Reservation ID', type: 'number' },
  { name: 'guest_email', label: 'Guest email (fill only if the reservation is NOT yours via login)', type: 'text' },
]

function emptyForm() {
  return { reservation_id: '', guest_email: '' }
}

function Payment() {
  const [form, setForm] = useState(emptyForm())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const { checkout_url } = await createPayment({
        reservation_id: Number(form.reservation_id),
        guest_email: form.guest_email || undefined,
      })
      // full browser navigation, not fetch — Stripe's checkout page is a different
      // origin and won't let a background request read/display it
      window.location.href = checkout_url
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <div>
      <h2>Payment</h2>
      <Section title="Pay for Reservation" method="POST">
        <form onSubmit={handleSubmit}>
          {FIELDS.map((f) => (
            <Field
              key={f.name}
              field={f}
              value={form[f.name]}
              onChange={(name, v) => setForm({ ...form, [name]: v })}
              required={f.name === 'reservation_id'}
            />
          ))}
          <button type="submit" disabled={loading}>
            {loading ? 'Redirecting…' : 'Pay with Stripe'}
          </button>
        </form>
        {error && <p className="error">{error}</p>}
      </Section>
    </div>
  )
}

export default Payment
