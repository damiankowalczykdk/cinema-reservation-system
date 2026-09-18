import {
  createCinema, getCinemaById, searchCinemasByName, updateCinema, deleteCinema,
  createHall, getHallById, searchHallsByName, updateHall, deleteHall,
  createMovie, getMovieById, searchMoviesByTitle, updateMovie, deleteMovie, GENRES,
  createScreening, getScreeningById, updateScreening, deleteScreening,
} from './api.js'

const entities = {
  cinema: {
    resource: 'Cinema',
    note: "/cinemas isn't role-protected yet — these work whether you're logged in or not.",
    fields: [
      { name: 'name', label: 'Name', type: 'text' },
      { name: 'city', label: 'City', type: 'text' },
      { name: 'address', label: 'Address', type: 'text' },
    ],
    searchFields: [{ name: 'name', label: 'Name', type: 'text' }],
    api: { create: createCinema, getById: getCinemaById, search: searchCinemasByName, update: updateCinema, remove: deleteCinema },
  },
  hall: {
    resource: 'Hall',
    fields: [
      { name: 'cinema_id', label: 'Cinema ID', type: 'number' },
      { name: 'name', label: 'Name', type: 'text' },
      { name: 'rows', label: 'Rows', type: 'number' },
      { name: 'seats_per_row', label: 'Seats per row', type: 'number' },
    ],
    searchFields: [
      { name: 'cinema_id', label: 'Cinema ID', type: 'number' },
      { name: 'name', label: 'Name', type: 'text' },
    ],
    api: { create: createHall, getById: getHallById, search: searchHallsByName, update: updateHall, remove: deleteHall },
  },
  movie: {
    resource: 'Movie',
    fields: [
      { name: 'title', label: 'Title', type: 'text' },
      { name: 'description', label: 'Description', type: 'text' },
      { name: 'duration_minutes', label: 'Duration (min)', type: 'number' },
      { name: 'genre', label: 'Genre', type: 'select', options: GENRES },
      { name: 'release_date', label: 'Release date', type: 'date' },
    ],
    searchFields: [{ name: 'title', label: 'Title', type: 'text' }],
    api: { create: createMovie, getById: getMovieById, search: searchMoviesByTitle, update: updateMovie, remove: deleteMovie },
  },
  screening: {
    resource: 'Screening',
    note: 'No search-by-name endpoint on the gateway for screenings — use Get by ID.',
    fields: [
      { name: 'movie_id', label: 'Movie ID', type: 'number' },
      { name: 'hall_id', label: 'Hall ID', type: 'number' },
      { name: 'start_time', label: 'Start time', type: 'datetime-local' },
      { name: 'price', label: 'Price', type: 'decimal' },
    ],
    searchFields: [],
    api: { create: createScreening, getById: getScreeningById, update: updateScreening, remove: deleteScreening },
  },
}

export default entities
