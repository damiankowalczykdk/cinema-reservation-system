import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchScreenings, getMovieById } from '../api.js'
import Poster from '../components/Poster.jsx'
import { EmptyState, ErrorState, Skeleton } from '../components/Feedback.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { dayKey, dayLabel, formatTime, formatPrice, formatDuration, genreLabel } from '../format.js'

const DAYS_AHEAD = 7

// local midnights for today and the following days
function upcomingDays() {
  const start = new Date()
  start.setHours(0, 0, 0, 0)
  return Array.from({ length: DAYS_AHEAD }, (_, i) => {
    const d = new Date(start)
    d.setDate(start.getDate() + i)
    return d
  })
}

// screenings -> [{ movie_id, movie_title, cinemas: [{ cinema_id, cinema_name, screenings }] }] sorted by title
function groupByMovieAndCinema(screenings) {
  const movies = new Map()
  const sorted = [...screenings].sort((a, b) => new Date(a.start_time) - new Date(b.start_time))
  for (const s of sorted) {
    if (!movies.has(s.movie_id)) {
      movies.set(s.movie_id, { movie_id: s.movie_id, movie_title: s.movie_title, cinemas: new Map() })
    }
    const cinemas = movies.get(s.movie_id).cinemas
    if (!cinemas.has(s.cinema_id)) {
      cinemas.set(s.cinema_id, { cinema_id: s.cinema_id, cinema_name: s.cinema_name, screenings: [] })
    }
    cinemas.get(s.cinema_id).screenings.push(s)
  }
  return [...movies.values()]
    .map((m) => ({ ...m, cinemas: [...m.cinemas.values()].sort((a, b) => a.cinema_name.localeCompare(b.cinema_name)) }))
    .sort((a, b) => a.movie_title.localeCompare(b.movie_title))
}

function Schedule() {
  const { t } = useI18n()
  const [days] = useState(upcomingDays)
  const [screenings, setScreenings] = useState(null)
  const [details, setDetails] = useState({}) // movie_id -> MovieRead (genre, duration, poster)
  const [error, setError] = useState(null)
  const [activeDay, setActiveDay] = useState(null)
  const [cinema, setCinema] = useState('all')

  useEffect(() => {
    let cancelled = false
    const until = new Date(days[days.length - 1])
    until.setDate(until.getDate() + 1)
    // date_from = now, so showtimes that already started today never reach the page
    searchScreenings({ dateFrom: new Date().toISOString(), dateTo: until.toISOString() })
      .then(async (data) => {
        if (cancelled) return
        setScreenings(data)
        const movieIds = [...new Set(data.map((s) => s.movie_id))]
        // allSettled so one failing movie doesn't blank the whole schedule
        const results = await Promise.allSettled(movieIds.map((id) => getMovieById(id)))
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
  }, [days])

  if (error) return <ErrorState message={error} />

  if (screenings === null) {
    return (
      <>
        <Skeleton className="skeleton--line" />
        <Skeleton className="skeleton--line skeleton--short" />
      </>
    )
  }

  const cinemas = [...new Map(screenings.map((s) => [s.cinema_id, s.cinema_name])).entries()]
    .map(([id, name]) => ({ id, name }))
    .sort((a, b) => a.name.localeCompare(b.name))
  const inCinema = cinema === 'all' ? screenings : screenings.filter((s) => s.cinema_id === cinema)

  const busyDays = new Set(inCinema.map((s) => dayKey(s.start_time)))
  const dayKeys = days.map((d) => dayKey(d))
  // open on the first day that actually has showtimes
  const currentDay = activeDay ?? dayKeys.find((key) => busyDays.has(key)) ?? dayKeys[0]
  const movies = groupByMovieAndCinema(inCinema.filter((s) => dayKey(s.start_time) === currentDay))

  return (
    <>
      <div className="page-header">
        <h1>{t('schedule.title')}</h1>
        <p>{t('schedule.subtitle')}</p>
      </div>

      <div className="day-tabs" role="tablist" aria-label={t('movie.chooseDay')}>
        {days.map((d) => {
          const key = dayKey(d)
          return (
            <button
              key={key}
              role="tab"
              aria-selected={key === currentDay}
              className={`day-tab${key === currentDay ? ' day-tab--active' : ''}`}
              onClick={() => setActiveDay(key)}
            >
              {dayLabel(d)}
            </button>
          )
        })}
      </div>

      {cinemas.length > 1 && (
        <div className="day-tabs" role="tablist" aria-label={t('schedule.chooseCinema')}>
          {[{ id: 'all', name: t('schedule.allCinemas') }, ...cinemas].map((c) => (
            <button
              key={c.id}
              role="tab"
              aria-selected={cinema === c.id}
              className={`day-tab${cinema === c.id ? ' day-tab--active' : ''}`}
              onClick={() => setCinema(c.id)}
            >
              {c.name}
            </button>
          ))}
        </div>
      )}

      {movies.length === 0 ? (
        <EmptyState icon="🗓️" title={t('schedule.emptyTitle')}>
          <p>{t('schedule.emptyBody')}</p>
        </EmptyState>
      ) : (
        movies.map((m) => {
          const d = details[m.movie_id]
          return (
            <div className="schedule-row" key={m.movie_id}>
              <Link to={`/movies/${m.movie_id}`}>
                <Poster title={m.movie_title} genre={d?.genre} posterPath={d?.poster_path} size="sm" />
              </Link>
              <div>
                <h3 className="schedule-row__title">
                  <Link to={`/movies/${m.movie_id}`}>{m.movie_title}</Link>
                </h3>
                {d && (
                  <div className="meta">
                    <span className="chip">{genreLabel(d.genre)}</span>
                    <span>{formatDuration(d.duration_minutes)}</span>
                  </div>
                )}
                {m.cinemas.map((c) => (
                  <div className="schedule-cinema" key={c.cinema_id}>
                    <span className="muted">{c.cinema_name}</span>
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
              </div>
            </div>
          )
        })
      )}
    </>
  )
}

export default Schedule
