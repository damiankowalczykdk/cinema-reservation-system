import { Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './AppShell.jsx'
import AdminRoute from './admin/AdminRoute.jsx'
import AdminLayout from './admin/AdminLayout.jsx'
import AdminReservations from './admin/AdminReservations.jsx'
import EntityCrud from './EntityCrud.jsx'
import SeatSelection from './pages/SeatSelection.jsx'
import BookingConfirmation from './pages/BookingConfirmation.jsx'
import MyReservations from './pages/MyReservations.jsx'
import MoviesBrowse from './pages/MoviesBrowse.jsx'
import MovieDetail from './pages/MovieDetail.jsx'
import entities from './entities.js'
import './App.css'

function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route path="/" element={<MoviesBrowse />} />
        <Route path="/movies/:movieId" element={<MovieDetail />} />
        <Route path="/screenings/:screeningId" element={<SeatSelection />} />
        <Route path="/booking/confirmation" element={<BookingConfirmation />} />
        <Route path="/my-reservations" element={<MyReservations />} />

        <Route path="/admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
          <Route index element={<Navigate to="cinemas" replace />} />
          <Route path="cinemas" element={<EntityCrud {...entities.cinema} />} />
          <Route path="halls" element={<EntityCrud {...entities.hall} />} />
          <Route path="movies" element={<EntityCrud {...entities.movie} />} />
          <Route path="screenings" element={<EntityCrud {...entities.screening} />} />
          <Route path="reservations" element={<AdminReservations />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
