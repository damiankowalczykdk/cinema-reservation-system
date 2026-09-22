const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8000'

async function parseErrorMessage(res) {
  try {
    const body = await res.json()
    const detail = body?.detail ?? body?.message ?? body
    return typeof detail === 'string' ? detail : JSON.stringify(detail)
  } catch {
    return `HTTP ${res.status}`
  }
}

async function request(method, path, { params, body } = {}) {
  const url = new URL(`${GATEWAY_URL}${path}`)
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') url.searchParams.set(key, value)
    }
  }
  const res = await fetch(url, {
    method,
    credentials: 'include',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) throw new Error(await parseErrorMessage(res))
  if (res.status === 204) return null
  return res.json()
}

// --- auth ---

async function getLoginUrl() {
  const res = await fetch(`${GATEWAY_URL}/auth/login-url`, { credentials: 'include' })
  if (!res.ok) throw new Error('Failed to get login url')
  return res.json()
}

async function getLogoutUrl() {
  const res = await fetch(`${GATEWAY_URL}/auth/logout-url`, { credentials: 'include' })
  if (!res.ok) throw new Error('Failed to get logout url')
  return res.json()
}

async function getMe() {
  const res = await fetch(`${GATEWAY_URL}/auth/me`, { credentials: 'include' })
  if (res.status === 401) return null // expected "not logged in" state
  if (!res.ok) throw new Error(`Unexpected /auth/me status: ${res.status}`)
  return res.json()
}

async function logout() {
  return request('POST', '/auth/logout')
}

// --- health ---

async function getHealth() {
  const res = await fetch(`${GATEWAY_URL}/health`)
  if (!res.ok) throw new Error(await parseErrorMessage(res))
  return res.json()
}

// --- cinemas ---

const createCinema = (payload) => request('POST', '/cinemas/', { body: payload })
const getCinemaById = (id) => request('GET', `/cinemas/${id}`)
const searchCinemasByName = (name) => request('GET', '/cinemas/', { params: { name } })
const updateCinema = (id, patch) => request('PATCH', `/cinemas/${id}`, { body: patch })
const deleteCinema = (id) => request('DELETE', `/cinemas/${id}`)

// --- halls ---

const createHall = (payload) => request('POST', '/halls/', { body: payload })
const getHallById = (id) => request('GET', `/halls/${id}`)
const searchHallsByName = (cinemaId, name) => request('GET', '/halls/', { params: { cinema_id: cinemaId, name } })
const updateHall = (id, patch) => request('PATCH', `/halls/${id}`, { body: patch })
const deleteHall = (id) => request('DELETE', `/halls/${id}`)

// --- movies ---

const GENRES = [
  'action', 'comedy', 'drama', 'horror', 'thriller', 'romance', 'sci_fi',
  'fantasy', 'animation', 'documentary', 'crime', 'adventure', 'mystery', 'family', 'war',
]

const createMovie = (payload) => request('POST', '/movies/', { body: payload })
const getMovieById = (id) => request('GET', `/movies/${id}`)
const searchMoviesByTitle = (title) => request('GET', '/movies/', { params: { title } })
const updateMovie = (id, patch) => request('PATCH', `/movies/${id}`, { body: patch })
const deleteMovie = (id) => request('DELETE', `/movies/${id}`)

// --- screenings ---

const createScreening = (payload) => request('POST', '/screenings/', { body: payload })
const getScreeningById = (id) => request('GET', `/screenings/${id}`)
const updateScreening = (id, patch) => request('PATCH', `/screenings/${id}`, { body: patch })
const deleteScreening = (id) => request('DELETE', `/screenings/${id}`)
// public browse endpoint: denormalized rows (movie_title, cinema_name already joined in),
// so pages don't need to separately fetch /movies or /cinemas to display a listing
const searchScreenings = ({ movieId, cinemaId, dateFrom, dateTo } = {}) =>
  request('GET', '/screenings/search', {
    params: { movie_id: movieId, cinema_id: cinemaId, date_from: dateFrom, date_to: dateTo },
  })

// --- reservations ---
// Identity is inferred by the gateway from your session cookie, not sent explicitly:
// logged in -> reservation gets your user_id; not logged in -> pass guest_email instead.

const createReservation = (payload) => request('POST', '/reservations/', { body: payload })
const getReservationById = (id) => request('GET', `/reservations/${id}`) // admin only
const getUserReservations = () => request('GET', '/reservations/') // requires login
const cancelReservation = (id) => request('POST', `/reservations/${id}/cancel`) // requires login
const getOccupiedSeats = (screeningId) => request('GET', `/reservations/screening/${screeningId}/seats`) // { seats: [[row, seat], ...] }

// --- payment ---

const createPayment = (payload) => request('POST', '/payments', { body: payload }) // { checkout_url }

export {
  getLoginUrl,
  getLogoutUrl,
  getMe,
  logout,
  getHealth,
  createCinema,
  getCinemaById,
  searchCinemasByName,
  updateCinema,
  deleteCinema,
  createHall,
  getHallById,
  searchHallsByName,
  updateHall,
  deleteHall,
  GENRES,
  createMovie,
  getMovieById,
  searchMoviesByTitle,
  updateMovie,
  deleteMovie,
  createScreening,
  getScreeningById,
  updateScreening,
  deleteScreening,
  searchScreenings,
  createReservation,
  getReservationById,
  getUserReservations,
  cancelReservation,
  getOccupiedSeats,
  createPayment,
}
