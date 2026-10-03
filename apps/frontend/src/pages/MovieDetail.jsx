import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { searchScreenings } from '../api.js'

function groupByCinema(screenings) {
  const cinemas = new Map()
  for (const s of screenings) {
    if (!cinemas.has(s.cinema_id)) {
      cinemas.set(s.cinema_id, { cinema_id: s.cinema_id, cinema_name: s.cinema_name, screenings: [] })
    }
    cinemas.get(s.cinema_id).screenings.push(s)
  }
  const groups = [...cinemas.values()]
  groups.forEach((g) => g.screenings.sort((a, b) => new Date(a.start_time) - new Date(b.start_time)))
  return groups.sort((a, b) => a.cinema_name.localeCompare(b.cinema_name))
}

function MovieDetail() {
  const { movieId } = useParams()
  const [screenings, setScreenings] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    searchScreenings({ movieId: Number(movieId) })
      .then((data) => {
        if (!cancelled) setScreenings(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [movieId])

  if (error) return <p className="error">{error}</p>
  if (screenings === null) return <p>Loading…</p>
  if (screenings.length === 0) return <p className="note">No showtimes for this movie right now.</p>

  const cinemas = groupByCinema(screenings)

  return (
    <div>
      <h2>{screenings[0].movie_title}</h2>
      {cinemas.map((c) => (
        <div className="panel" key={c.cinema_id}>
          <h3>{c.cinema_name}</h3>
          <div className="showtimes">
            {c.screenings.map((s) => (
              <Link key={s.screening_id} className="showtime-btn" to={`/screenings/${s.screening_id}`}>
                {new Date(s.start_time).toLocaleString()} — {Number(s.price).toFixed(2)}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

export default MovieDetail
