import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'

function AdminRoute({ children }) {
  const { isAdmin, loading } = useAuth()

  if (loading) return <p>Loading…</p>

  if (!isAdmin) return <Navigate to="/" replace />

  return children
}

export default AdminRoute
