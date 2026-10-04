import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import Steps from '../components/Steps.jsx'

function BookingConfirmation() {
  const { user } = useAuth()
  const { t } = useI18n()

  return (
    <>
      <Steps current={2} />
      <div className="confirmation">
        <div className="confirmation__icon" aria-hidden="true">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 6L9 17l-5-5" />
          </svg>
        </div>
        <h2>{t('confirm.title')}</h2>
        <p>
          {t('confirm.body')} {user ? t('confirm.bodyUser') : t('confirm.bodyGuest')}
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          {user && (
            <Link className="btn btn--lg" to="/my-reservations">{t('confirm.viewTickets')}</Link>
          )}
          <Link className={`btn btn--lg${user ? ' btn-secondary' : ''}`} to="/">{t('confirm.browseMore')}</Link>
        </div>
      </div>
    </>
  )
}

export default BookingConfirmation
