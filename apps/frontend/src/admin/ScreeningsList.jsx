import { useEffect, useState } from 'react'
import { searchScreenings, getHallById } from '../api.js'
import { formatPrice } from '../format.js'

function formatWhen(iso) {
  return new Date(iso).toLocaleString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Readable overview for the admin: the CRUD forms below work on raw ids, so this table
// maps each upcoming screening id to its movie, cinema and hall. Uses the public search
// endpoint, which already joins movie_title / cinema_name; hall names are fetched once per hall.
function ScreeningsList() {
  const [rows, setRows] = useState(null)
  const [halls, setHalls] = useState({}) // hall_id -> hall name
  const [error, setError] = useState(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    setError(null)
    searchScreenings()
      .then(async (data) => {
        if (cancelled) return
        setRows(data)
        const hallIds = [...new Set(data.map((s) => s.hall_id))]
        const results = await Promise.allSettled(hallIds.map((id) => getHallById(id)))
        if (cancelled) return
        const names = {}
        results.forEach((r, i) => {
          if (r.status === 'fulfilled') names[hallIds[i]] = r.value.name
        })
        setHalls(names)
      })
      .catch((err) => !cancelled && setError(err.message))
    return () => {
      cancelled = true
    }
  }, [reloadKey])

  return (
    <section className="panel">
      <h3>
        Upcoming screenings
        <button type="button" className="admin-list__reload" onClick={() => setReloadKey((k) => k + 1)}>
          Refresh
        </button>
      </h3>
      {error && <p className="error">{error}</p>}
      {!error && rows === null && <p className="note">Loading…</p>}
      {rows && rows.length === 0 && <p className="note">No upcoming screenings.</p>}
      {rows && rows.length > 0 && (
        <div className="admin-list">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Movie</th>
                <th>Cinema</th>
                <th>Hall</th>
                <th>Start</th>
                <th>Price</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((s) => (
                <tr key={s.screening_id}>
                  <td>{s.screening_id}</td>
                  <td>
                    {s.movie_title} <span className="note">#{s.movie_id}</span>
                  </td>
                  <td>
                    {s.cinema_name} <span className="note">· {s.city}</span>
                  </td>
                  <td>
                    {halls[s.hall_id] ?? '—'} <span className="note">#{s.hall_id}</span>
                  </td>
                  <td>{formatWhen(s.start_time)}</td>
                  <td>{formatPrice(s.price, s.currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default ScreeningsList
