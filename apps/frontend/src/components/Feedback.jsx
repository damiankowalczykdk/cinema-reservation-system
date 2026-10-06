// Small shared states for customer pages: loading skeletons, empty/error blocks, status badge.
import { useI18n } from '../i18n/LanguageContext.jsx'

function Skeleton({ className = '', style }) {
  return <div className={`skeleton ${className}`} style={style} />
}

function PosterGridSkeleton({ count = 8 }) {
  return (
    <div className="movie-grid">
      {Array.from({ length: count }, (_, i) => (
        <div key={i}>
          <Skeleton className="skeleton--poster" />
          <Skeleton className="skeleton--line" />
          <Skeleton className="skeleton--line skeleton--short" />
        </div>
      ))}
    </div>
  )
}

function EmptyState({ icon = '🎬', title, children }) {
  return (
    <div className="empty-state">
      <div className="empty-state__icon" aria-hidden="true">{icon}</div>
      <h3>{title}</h3>
      {children && <div className="empty-state__body">{children}</div>}
    </div>
  )
}

function ErrorState({ message }) {
  const { t } = useI18n()
  return (
    <EmptyState icon="⚠️" title={t('common.error')}>
      <p>{message}</p>
    </EmptyState>
  )
}

const KNOWN_STATUSES = new Set(['pending', 'confirmed', 'cancelled'])

function StatusBadge({ status }) {
  const { t } = useI18n()
  return <span className={`badge badge--${status}`}>{KNOWN_STATUSES.has(status) ? t(`status.${status}`) : status}</span>
}

export { Skeleton, PosterGridSkeleton, EmptyState, ErrorState, StatusBadge }
