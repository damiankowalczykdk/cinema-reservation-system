import { useState } from 'react'
import { posterStyle, posterUrl, genreLabel } from '../format.js'
import { useI18n } from '../i18n/LanguageContext.jsx'

// Real TMDB artwork when the movie has a poster_path; otherwise (or if the image fails
// to load) the generated poster: gradient keyed on the title + the title typeset on it,
// so a listing without real artwork still looks like a wall of posters.
function Poster({ title, genre, posterPath, size = 'md' }) {
  const { t } = useI18n()
  const [failedPath, setFailedPath] = useState(null)
  const url = posterPath !== failedPath ? posterUrl(posterPath, size) : null

  if (url) {
    return (
      <div className={`poster poster--${size} poster--image`}>
        <img
          className="poster__img"
          src={url}
          alt={t('poster.alt', { title })}
          loading="lazy"
          onError={() => setFailedPath(posterPath)}
        />
      </div>
    )
  }

  return (
    <div className={`poster poster--${size}`} style={posterStyle(title)} aria-hidden="true">
      <div className="poster__grain" />
      {genre && <span className="poster__genre">{genreLabel(genre)}</span>}
      <span className="poster__title">{title}</span>
    </div>
  )
}

export default Poster
