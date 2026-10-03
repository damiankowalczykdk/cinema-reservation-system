import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchScreenings } from '../api.js'

function groupByMovie(screenings) {
  const movies = new Map()
  for (const s of screenings) {
    if (!movies.has(s.movie_id)) {
      movies.set(s.movie_id, { movie_id: s.movie_id, movie_title: s.movie_title, showtimeCount: 0 })
    }
    movies.get(s.movie_id).showtimeCount += 1
  }
  return [...movies.values()].sort((a, b) => a.movie_title.localeCompare(b.movie_title))
}

function MoviesBrowse() {
  const [movies, setMovies] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    searchScreenings()
      .then((screenings) => {
        if (!cancelled) setMovies(groupByMovie(screenings))
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (error) return <p className="error">{error}</p>
  if (movies === null) return <p>Loading…</p>
  if (movies.length === 0) return <p className="note">No screenings scheduled right now.</p>

  return (
    <div>
      <h2>Now Showing</h2>
      <div className="grid">
        {movies.map((m) => (
          <Link className="panel" key={m.movie_id} to={`/movies/${m.movie_id}`}>
            <h3>{m.movie_title}</h3>
            <p className="note">
              {m.showtimeCount} showtime{m.showtimeCount === 1 ? '' : 's'}
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default MoviesBrowse
