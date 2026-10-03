import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from './auth/AuthContext.jsx'
import './App.css'

const linkClass = ({ isActive }) => `nav-item${isActive ? ' nav-item--active' : ''}`

function AppShell() {
  const { user, isAdmin, loading, login, logout } = useAuth()

  return (
    <div className="shell shell--top-nav">
      <header className="topbar">
        <div className="brand">CinemaApp</div>
        <nav className="topnav">
          <NavLink to="/" end className={linkClass}>Movies</NavLink>
          {user && <NavLink to="/my-reservations" className={linkClass}>My Reservations</NavLink>}
          {isAdmin && <NavLink to="/admin" className={linkClass}>Admin</NavLink>}
        </nav>
        <div className="authbox">
          {loading ? null : user ? (
            <>
              <span>{user.email ?? user.sub}</span>
              <button onClick={logout}>Log out</button>
            </>
          ) : (
            <button onClick={login}>Log in</button>
          )}
        </div>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}

export default AppShell
