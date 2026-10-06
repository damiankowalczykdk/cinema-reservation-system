import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchScreenings, getMovieById } from '../api.js'
import Poster from '../components/Poster.jsx'
import { PosterGridSkeleton, EmptyState, ErrorState } from '../components/Feedback.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { dayLabel, formatTime, formatDuration, genreLabel, posterStyle } from '../format.js'

function groupByMovie(screenings) {
  const movies = new Map()
  for (const s of screenings) {
    if (!movies.has(s.movie_id)) {
      movies.set(s.movie_id, { movie_id: s.movie_id, movie_title: s.movie_title, showtimeCount: 0, next: s.start_time })
    }
    const m = movies.get(s.movie_id)
    m.showtimeCount += 1
    if (new Date(s.start_time) < new Date(m.next)) m.next = s.start_time
  }
  return [...movies.values()].sort((a, b) => a.movie_title.localeCompare(b.movie_title))
}

function MoviesBrowse() {
  const { t } = useI18n()
  const [movies, setMovies] = useState(null)
  const [details, setDetails] = useState({}) // movie_id -> MovieRead (genre, duration, description)
  const [error, setError] = useState(null)
  const [genre, setGenre] = useState('all')

  useEffect(() => {
    let cancelled = false
    searchScreenings()
      .then(async (screenings) => {
        if (cancelled) return
        const grouped = groupByMovie(screenings)
        setMovies(grouped)
        // the search endpoint only carries titles; pull genre/duration/description per movie.
        // allSettled so one failing movie doesn't blank the whole listing
        const results = await Promise.allSettled(grouped.map((m) => getMovieById(m.movie_id)))
        if (cancelled) return
        const byId = {}
        results.forEach((r) => {
          if (r.status === 'fulfilled') byId[r.value.id] = r.value
        })
        setDetails(byId)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const genres = useMemo(() => {
    const set = new Set(Object.values(details).map((d) => d.genre))
    return [...set].sort()
  }, [details])

  if (error) return <ErrorState message={error} />

  if (movies === null) {
    return (
      <>
        <div className="skeleton skeleton--block" style={{ marginBottom: 56, height: 320 }} />
        <PosterGridSkeleton />
      </>
    )
  }

  if (movies.length === 0) {
    return (
      <EmptyState title={t('browse.emptyTitle')}>
        <p>{t('browse.emptyBody')}</p>
      </EmptyState>
    )
  }

  const featured = [...movies].sort((a, b) => b.showtimeCount - a.showtimeCount)[0]
  const featuredDetail = details[featured.movie_id]
  const visible = genre === 'all' ? movies : movies.filter((m) => details[m.movie_id]?.genre === genre)

  return (
    <>
      <section className="hero">
        <div className="hero__backdrop" style={posterStyle(featured.movie_title)} />
        <div>
          <span className="hero__eyebrow">{t('browse.featured')}</span>
          <h1>{featured.movie_title}</h1>
          {featuredDetail && (
            <div className="meta">
              <span className="chip">{genreLabel(featuredDetail.genre)}</span>
              <span>{formatDuration(featuredDetail.duration_minutes)}</span>
              <span className="meta__dot" />
              <span>{new Date(featuredDetail.release_date).getFullYear()}</span>
            </div>
          )}
          <p className="hero__desc">
            {featuredDetail?.description ?? t('browse.showtimesAvailable', { count: featured.showtimeCount })}
          </p>
          <div className="hero__actions">
            <Link className="btn btn--lg" to={`/movies/${featured.movie_id}`}>{t('browse.getTickets')}</Link>
            <span className="meta">{t('browse.next', { day: dayLabel(featured.next), time: formatTime(featured.next) })}</span>
          </div>
        </div>
        <Poster title={featured.movie_title} genre={featuredDetail?.genre} posterPath={featuredDetail?.poster_path} size="lg" />
      </section>

      <div className="section-head">
        <h2>{t('browse.nowShowing')}</h2>
        <span className="muted">{t('common.movies', { count: movies.length })}</span>
      </div>

      {genres.length > 1 && (
        <div className="day-tabs" role="tablist" aria-label={t('browse.filterLabel')}>
          {['all', ...genres].map((g) => (
            <button
              key={g}
              role="tab"
              aria-selected={genre === g}
              className={`day-tab${genre === g ? ' day-tab--active' : ''}`}
              onClick={() => setGenre(g)}
            >
              {g === 'all' ? t('browse.all') : genreLabel(g)}
            </button>
          ))}
        </div>
      )}

      <div className="movie-grid">
        {visible.map((m) => {
          const d = details[m.movie_id]
          return (
            <Link className="movie-card" key={m.movie_id} to={`/movies/${m.movie_id}`}>
              <Poster title={m.movie_title} genre={d?.genre} posterPath={d?.poster_path} />
              <h3 className="movie-card__title">{m.movie_title}</h3>
              <div className="movie-card__meta">
                {d ? `${formatDuration(d.duration_minutes)} · ` : ''}
                {t('common.showtimes', { count: m.showtimeCount })}
              </div>
            </Link>
          )
        })}
      </div>
    </>
  )
}

export default MoviesBrowse
