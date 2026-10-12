import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { searchScreenings, getMovieById } from '../api.js'
import { EmptyState, ErrorState, Skeleton } from '../components/Feedback.jsx'
import { useI18n } from '../i18n/LanguageContext.jsx'
import { formatDuration, genreLabel } from '../format.js'

const thumbnailUrl = (key) => `https://i.ytimg.com/vi/${encodeURIComponent(key)}/hqdefault.jpg`
// nocookie host: YouTube sets no cookies until the visitor actually presses play
const embedUrl = (key) => `https://www.youtube-nocookie.com/embed/${encodeURIComponent(key)}?autoplay=1&rel=0`

function Trailers() {
  const { t } = useI18n()
  const [movies, setMovies] = useState(null)
  const [error, setError] = useState(null)
  const [playingId, setPlayingId] = useState(null) // one player at a time; starting another replaces it

  useEffect(() => {
    let cancelled = false
    // same call as the home page, so both list exactly the same movies
    searchScreenings()
      .then(async (screenings) => {
        const movieIds = [...new Set(screenings.map((s) => s.movie_id))]
        // allSettled so one failing movie doesn't blank the whole page
        const results = await Promise.allSettled(movieIds.map((id) => getMovieById(id)))
        if (cancelled) return
        setMovies(
          results
            .filter((r) => r.status === 'fulfilled' && r.value.trailer_key)
            .map((r) => r.value)
            .sort((a, b) => a.title.localeCompare(b.title)),
        )
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
    return () => {
      cancelled = true
    }
  }, [])

  if (error) return <ErrorState message={error} />

  return (
    <>
      <div className="page-header">
        <h1>{t('trailers.title')}</h1>
        <p>{t('trailers.subtitle')}</p>
      </div>

      {movies === null ? (
        <div className="trailer-grid">
          {Array.from({ length: 4 }, (_, i) => (
            <Skeleton key={i} className="skeleton--block" />
          ))}
        </div>
      ) : movies.length === 0 ? (
        <EmptyState icon="🎞️" title={t('trailers.emptyTitle')}>
          <p>{t('trailers.emptyBody')}</p>
        </EmptyState>
      ) : (
        <div className="trailer-grid">
          {movies.map((m) => (
            <article className="trailer" key={m.id}>
              <div className="trailer__frame">
                {playingId === m.id ? (
                  <iframe
                    src={embedUrl(m.trailer_key)}
                    title={t('trailers.frameTitle', { title: m.title })}
                    allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
                    allowFullScreen
                  />
                ) : (
                  <button
                    type="button"
                    className="trailer__play"
                    aria-label={t('trailers.play', { title: m.title })}
                    onClick={() => setPlayingId(m.id)}
                  >
                    <img src={thumbnailUrl(m.trailer_key)} alt="" loading="lazy" />
                    <span className="trailer__icon" aria-hidden="true">
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M8 5v14l11-7z" />
                      </svg>
                    </span>
                  </button>
                )}
              </div>
              <h3 className="trailer__title">
                <Link to={`/movies/${m.id}`}>{m.title}</Link>
              </h3>
              <div className="meta">
                <span className="chip">{genreLabel(m.genre)}</span>
                <span>{formatDuration(m.duration_minutes)}</span>
                <span className="meta__dot" />
                <Link to={`/movies/${m.id}`}>{t('trailers.showtimes')}</Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </>
  )
}

export default Trailers
