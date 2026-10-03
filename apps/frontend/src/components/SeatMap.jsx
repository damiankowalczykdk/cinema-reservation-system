function seatKey(row, seat) {
  return `${row}-${seat}`
}

// Pure presentational seat grid: caller owns which seats are taken/selected and what
// happens on click. Used by SeatSelection today; the admin console doesn't need it.
function SeatMap({ rows, seatsPerRow, occupied, selected, onToggle }) {
  return (
    <>
      <div className="seat-map">
        {Array.from({ length: rows }, (_, i) => i + 1).map((row) => (
          <div className="seat-map__row" key={row}>
            <span className="seat-map__row-label">{row}</span>
            {Array.from({ length: seatsPerRow }, (_, i) => i + 1).map((seat) => {
              const taken = occupied.has(seatKey(row, seat))
              const isSelected = selected.some((s) => s.row === row && s.seat === seat)
              return (
                <button
                  type="button"
                  key={seat}
                  className={`seat${taken ? ' seat--taken' : ''}${isSelected ? ' seat--selected' : ''}`}
                  disabled={taken}
                  onClick={() => onToggle(row, seat)}
                  title={`Row ${row}, Seat ${seat}${taken ? ' — taken' : ''}`}
                >
                  {seat}
                </button>
              )
            })}
          </div>
        ))}
      </div>
      <div className="seat-map__legend">
        <span>
          <i className="seat-map__swatch" /> free
        </span>
        <span>
          <i className="seat-map__swatch seat-map__swatch--taken" /> taken
        </span>
        <span>
          <i className="seat-map__swatch seat-map__swatch--selected" /> selected
        </span>
      </div>
    </>
  )
}

export { seatKey }
export default SeatMap
