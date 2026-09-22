import { NavLink, Outlet } from 'react-router-dom'

const TABS = [
  { path: 'cinemas', label: 'Cinemas' },
  { path: 'halls', label: 'Halls' },
  { path: 'movies', label: 'Movies' },
  { path: 'screenings', label: 'Screenings' },
]

const linkClass = ({ isActive }) => `nav-item${isActive ? ' nav-item--active' : ''}`

function AdminLayout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">Admin Console</div>
        <nav>
          {TABS.map((tab) => (
            <NavLink key={tab.path} to={tab.path} className={linkClass}>
              {tab.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}

export default AdminLayout
