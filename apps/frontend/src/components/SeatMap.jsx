import { useI18n } from '../i18n/LanguageContext.jsx'

function seatKey(row, seat) {
  return `${row}-${seat}`
}

// Pure presentational seat grid: caller owns which seats are taken/selected and what
// happens on click. Used by SeatSelection today; the admin console doesn't need it.
function SeatMap({ rows, seatsPerRow, occupied, selected, onToggle }) {
  const { t } = useI18n()
  return (
    <div className="hall">
      <div className="screen" aria-hidden="true">
        <div className="screen__curve" />
        <span className="screen__label">{t('map.screen')}</span>
      </div>

      <div className="seat-map" role="grid" aria-label={t('map.label')}>
        {Array.from({ length: rows }, (_, i) => i + 1).map((row) => (
          <div className="seat-map__row" key={row} role="row">
            <span className="seat-map__row-label">{row}</span>
            {Array.from({ length: seatsPerRow }, (_, i) => i + 1).map((seat) => {
              const taken = occupied.has(seatKey(row, seat))
              const isSelected = selected.some((s) => s.row === row && s.seat === seat)
              const label = t(taken ? 'map.seatTaken' : 'map.seat', { row, seat })
              return (
                <button
                  type="button"
                  key={seat}
                  role="gridcell"
                  aria-pressed={isSelected}
                  aria-label={label}
                  className={`seat${taken ? ' seat--taken' : ''}${isSelected ? ' seat--selected' : ''}`}
                  disabled={taken}
                  onClick={() => onToggle(row, seat)}
                  title={label}
                >
                  {seat}
                </button>
              )
            })}
            <span className="seat-map__row-label">{row}</span>
          </div>
        ))}
      </div>

      <div className="seat-map__legend">
        <span>
          <i className="seat-map__swatch" /> {t('map.available')}
        </span>
        <span>
          <i className="seat-map__swatch seat-map__swatch--selected" /> {t('map.selected')}
        </span>
        <span>
          <i className="seat-map__swatch seat-map__swatch--taken" /> {t('map.taken')}
        </span>
      </div>
    </div>
  )
}

export { seatKey }
export default SeatMap
