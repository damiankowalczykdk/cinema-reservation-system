import { useEffect, useState } from 'react'
import { getLoginUrl, getLogoutUrl, getMe, logout } from './api.js'
import { Section } from './ui.jsx'

function AuthPanel() {
  const [user, setUser] = useState(undefined) // undefined=loading, null=logged out, object=logged in
  const [error, setError] = useState(null)

  async function refreshUser() {
    try {
      setUser(await getMe())
    } catch (err) {
      setError(err.message)
      setUser(null)
    }
  }

  useEffect(() => {
    refreshUser()
  }, [])

  async function handleLogin() {
    try {
      const { url } = await getLoginUrl()
      window.location.href = url
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleLogout() {
    try {
      await logout()
      await refreshUser()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleFullLogout() {
    try {
      await logout()
      const { url } = await getLogoutUrl()
      window.location.href = url
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <Section title="Auth" method="SESSION">
      {error && <p className="error">{error}</p>}
      {user === undefined ? (
        <p>Loading…</p>
      ) : user ? (
        <div>
          <p>
            Logged in as <strong>{user.email ?? user.sub}</strong>
          </p>
          <pre>{JSON.stringify(user, null, 2)}</pre>
          <button onClick={handleLogout}>Log out (local)</button>
          <button onClick={handleFullLogout}>Log out (Auth0 session too)</button>
        </div>
      ) : (
        <button onClick={handleLogin}>Log in</button>
      )}
    </Section>
  )
}

export default AuthPanel
