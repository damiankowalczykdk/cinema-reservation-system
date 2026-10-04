import { useI18n } from '../i18n/LanguageContext.jsx'

const STEPS = ['steps.seats', 'steps.payment', 'steps.tickets']

// Checkout progress indicator; `current` is the 0-based index of the active step.
function Steps({ current }) {
  const { t } = useI18n()
  return (
    <ol className="steps" aria-label={t('steps.label')} style={{ listStyle: 'none', padding: 0 }}>
      {STEPS.map((labelKey, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'todo'
        return (
          <li key={labelKey} className="steps__item-wrap" style={{ display: 'contents' }}>
            {i > 0 && <span className="steps__sep" aria-hidden="true" />}
            <span className={`steps__item steps__item--${state}`} aria-current={state === 'active' ? 'step' : undefined}>
              <span className="steps__num">{state === 'done' ? '✓' : i + 1}</span>
              {t(labelKey)}
            </span>
          </li>
        )
      })}
    </ol>
  )
}

export default Steps
