// Display helpers shared by the customer pages: money, dates and the generated poster art.
// The backend has no poster images, so each movie gets a deterministic gradient derived
// from its title — the same movie always renders with the same colours.

import { DEFAULT_LANGUAGE, translate } from './i18n/translations.js'

const LOCALES = { en: 'en-GB', pl: 'pl-PL' }
const CURRENCY = 'USD' // matches payment-service default_currency

// Current UI language. LanguageProvider sets it before each re-render, so these helpers
// stay plain functions instead of every caller threading a locale through.
let language = DEFAULT_LANGUAGE

function setFormatLanguage(next) {
  language = next
}

function locale() {
  return LOCALES[language] ?? LOCALES[DEFAULT_LANGUAGE]
}

const priceFormatters = {}

function formatPrice(value) {
  priceFormatters[language] ??= new Intl.NumberFormat(locale(), { style: 'currency', currency: CURRENCY })
  return priceFormatters[language].format(Number(value))
}

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString(locale(), { hour: '2-digit', minute: '2-digit' })
}

function formatDateLong(iso) {
  return new Date(iso).toLocaleDateString(locale(), { weekday: 'long', day: 'numeric', month: 'long' })
}

function formatDateTime(iso) {
  return `${formatDateLong(iso)} · ${formatTime(iso)}`
}

function dayKey(iso) {
  const d = new Date(iso)
  return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`
}

// "Today" / "Tomorrow" / "Fri 3 Oct"
function dayLabel(iso) {
  const d = new Date(iso)
  const today = new Date()
  const tomorrow = new Date()
  tomorrow.setDate(today.getDate() + 1)
  if (dayKey(d) === dayKey(today)) return translate(language, 'date.today')
  if (dayKey(d) === dayKey(tomorrow)) return translate(language, 'date.tomorrow')
  return d.toLocaleDateString(locale(), { weekday: 'short', day: 'numeric', month: 'short' })
}

function formatDuration(minutes) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return h
    ? translate(language, 'duration.hm', { h, m: String(m).padStart(2, '0') })
    : translate(language, 'duration.m', { m })
}

function genreLabel(genre) {
  if (!genre) return ''
  const key = `genre.${genre}`
  const label = translate(language, key)
  // unknown genre from the backend: fall back to a capitalised raw value
  return label === key ? genre.charAt(0).toUpperCase() + genre.slice(1) : label
}

function hashString(str) {
  let h = 0
  for (let i = 0; i < str.length; i++) h = (h * 31 + str.charCodeAt(i)) | 0
  return Math.abs(h)
}

function posterStyle(title) {
  const h = hashString(title || '?')
  const hue1 = h % 360
  const hue2 = (hue1 + 40 + (h % 80)) % 360
  return {
    background: `
      radial-gradient(120% 80% at 20% 10%, hsla(${hue2}, 85%, 60%, 0.55), transparent 60%),
      linear-gradient(160deg, hsl(${hue1}, 70%, 32%), hsl(${hue2}, 65%, 14%) 70%, #07070b)`,
  }
}

// TMDB serves artwork from its image CDN: base + width bucket + the poster_path stored on the movie
const POSTER_WIDTHS = { sm: 'w185', md: 'w342', lg: 'w500' }

function posterUrl(posterPath, size = 'md') {
  if (!posterPath) return null
  return `https://image.tmdb.org/t/p/${POSTER_WIDTHS[size] ?? POSTER_WIDTHS.md}${posterPath}`
}

export {
  setFormatLanguage,
  posterUrl,
  formatPrice,
  formatTime,
  formatDateLong,
  formatDateTime,
  dayKey,
  dayLabel,
  formatDuration,
  genreLabel,
  posterStyle,
}
