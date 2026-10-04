import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { searchScreenings, getMovieById } from '../api.js'
import Poster from '../components/Poster.jsx'
import { EmptyState, ErrorState, Skeleton } from '../components/Feedback.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { dayKey, dayLabel, formatTime, formatPrice, formatDuration, genreLabel } from '../format.js'

// screenings -> [{ key, label, cinemas: [{ cinema_id, cinema_name, screenings }] }] sorted by day
function groupByDayAndCinema(screenings) {
  const days = new Map()
  const sorted = [...screenings].sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  for (const s of sorted) {
    const key = dayKey(s.start_time)
    if (!days.has(key)) days.set(key, { key, label: dayLabel(s.start_time), cinemas: new Map() })
    const cinemas = days.get(key).cinemas
    if (!cinemas.has(s.cinema_id)) {
      cinemas.set(s.cinema_id, { cinema_id: s.cinema_id, cinema_name: s.cinema_name, screenings: [] })
    }
    cinemas.get(s.cinema_id).screenings.push(s)
  }
  return [...days.values()].map((d) => ({
    ...d,
    cinemas: [...d.cinemas.values()].sort((a, b) => a.cinema_name.localeCompare(b.cinema_name)),
  }))
}

function MovieDetail() {
  const { t } = useI18n()
  const { movieId } = useParams()
  const [movie, setMovie] = useState(null)
  const [screenings, setScreenings] = useState(null)
  const [error, setError] = useState(null)
  const [activeDay, setActiveDay] = useState(null)

  useEffect(() => {
    let cancelled = false
    Promise.all([searchScreenings({ movieId: Number(movieId) }), getMovieById(movieId).catch(() => null)])
      .then(([screeningData, movieData]) => {
        if (cancelled) return
        setScreenings(screeningData)
        setMovie(movieData)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [movieId])

  if (error) return <ErrorState message={error} />

  if (screenings === null) {
    return (
      <div className="movie-hero">
        <Skeleton className="skeleton--poster" />
        <div>
          <Skeleton className="skeleton--line" />
          <Skeleton className="skeleton--line skeleton--short" />
        </div>
      </div>
    )
  }

  const title = movie?.title ?? screenings[0]?.movie_title ?? t('common.movie')
  const days = groupByDayAndCinema(screenings)
  const day = days.find((d) => d.key === activeDay) ?? days[0]

  return (
    <>
      <Link to="/" className="back-link">{t('movie.back')}</Link>

      <section className="movie-hero">
        <Poster title={title} genre={movie?.genre} posterPath={movie?.poster_path} size="lg" />
        <div>
          <h1>{title}</h1>
          {movie && (
            <div className="meta">
              <span className="chip">{genreLabel(movie.genre)}</span>
              <span>{formatDuration(movie.duration_minutes)}</span>
              <span className="meta__dot" />
              <span>{t('movie.released', { year: new Date(movie.release_date).getFullYear() })}</span>
            </div>
          )}
          {movie?.description && <p className="movie-hero__desc">{movie.description}</p>}
        </div>
      </section>

      <div className="section-head">
        <h2>{t('movie.showtimes')}</h2>
      </div>

      {days.length === 0 ? (
        <EmptyState icon="🗓️" title={t('movie.noShowtimesTitle')}>
          <p>{t('movie.noShowtimesBody')}</p>
          <Link className="btn btn-secondary" to="/">{t('movie.browseOther')}</Link>
        </EmptyState>
      ) : (
        <>
          <div className="day-tabs" role="tablist" aria-label={t('movie.chooseDay')}>
            {days.map((d) => (
              <button
                key={d.key}
                role="tab"
                aria-selected={d.key === day.key}
                className={`day-tab${d.key === day.key ? ' day-tab--active' : ''}`}
                onClick={() => setActiveDay(d.key)}
              >
                {d.label}
              </button>
            ))}
          </div>

          {day.cinemas.map((c) => (
            <div className="cinema-block" key={c.cinema_id}>
              <div>
                <h3>{c.cinema_name}</h3>
                <span className="muted">{t('common.showtimes', { count: c.screenings.length })}</span>
              </div>
              <div className="showtimes">
                {c.screenings.map((s) => (
                  <Link key={s.screening_id} className="showtime" to={`/screenings/${s.screening_id}`}>
                    <span className="showtime__time">{formatTime(s.start_time)}</span>
                    <span className="showtime__price">{formatPrice(s.price)}</span>
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </>
      )}
    </>
  )
}

export default MovieDetail
