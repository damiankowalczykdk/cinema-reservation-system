import { useSearchParams, Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'

function BookingConfirmation() {
  const [searchParams] = useSearchParams()
  const sessionId = searchParams.get('session_id')
  const { user } = useAuth()

  return (
    <div>
      <h2>Thanks for your booking!</h2>
      <p className="note">
        We're confirming your payment with Stripe — this can take a few seconds.
        {sessionId && <> Session: {sessionId}</>}
      </p>
      {user ? (
        <Link to="/my-reservations">
          <button type="button">Check My Reservations</button>
        </Link>
      ) : (
        <p className="note">Keep an eye on your email for confirmation.</p>
      )}
    </div>
  )
}

export default BookingConfirmation
