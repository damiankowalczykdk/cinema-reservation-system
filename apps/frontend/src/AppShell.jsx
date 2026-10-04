import { Link, NavLink, Outlet } from 'react-router-dom'
import { useAuth } from './auth/AuthContext.jsx'
import { useI18n } from './i18n/LanguageContext.jsx'
import './App.css'

const linkClass = ({ isActive }) => `nav-item${isActive ? ' nav-item--active' : ''}`

function LogoMark() {
  return (
    <span className="logo__mark" aria-hidden="true">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="7" width="18" height="13" rx="2" />
        <path d="M3 7l3-4M9 7l3-4M15 7l3-4" />
      </svg>
    </span>
  )
}

function LanguageSwitch() {
  const { lang, setLang, languages, t } = useI18n()
  return (
    <div className="lang-switch" role="group" aria-label={t('lang.label')}>
      {languages.map((code) => (
        <button
          key={code}
          type="button"
          className={`lang-switch__btn${lang === code ? ' lang-switch__btn--active' : ''}`}
          aria-pressed={lang === code}
          onClick={() => setLang(code)}
        >
          {code.toUpperCase()}
        </button>
      ))}
    </div>
  )
}

function AppShell() {
  const { user, isAdmin, loading, login, logout } = useAuth()
  const { t } = useI18n()
  const displayName = user?.email ?? user?.sub ?? ''

  return (
    <div className="app">
      <header className="topbar">
        <div className="container topbar__inner">
          <Link to="/" className="logo">
            <LogoMark />
            <span>
              Cinema<em>App</em>
            </span>
          </Link>
          <nav className="topnav">
            <NavLink to="/" end className={linkClass}>{t('nav.movies')}</NavLink>
            <NavLink to="/schedule" className={linkClass}>{t('nav.schedule')}</NavLink>
            {user && <NavLink to="/my-reservations" className={linkClass}>{t('nav.tickets')}</NavLink>}
            {isAdmin && <NavLink to="/admin" className={linkClass}>{t('nav.admin')}</NavLink>}
          </nav>
          <LanguageSwitch />
          <div className="authbox">
            {loading ? null : user ? (
              <>
                <span className="avatar" title={displayName}>{displayName.charAt(0) || '?'}</span>
                <span className="authbox__email">{displayName}</span>
                <button className="btn-ghost" onClick={logout}>{t('auth.logOut')}</button>
              </>
            ) : (
              <button onClick={login}>{t('auth.signIn')}</button>
            )}
          </div>
        </div>
      </header>

      <main className="content">
        <div className="container">
          <Outlet />
        </div>
      </main>

      <footer className="footer">
        <div className="container footer__inner">
          <span>{t('footer.rights', { year: new Date().getFullYear() })}</span>
          <span>{t('footer.payments')}</span>
        </div>
      </footer>
    </div>
  )
}

export default AppShell
