import { useEffect, useState } from 'react'
import { getLoginUrl, getLogoutUrl, getMe, logout } from './api.js'
import './App.css'

function App() {
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

  if (user === undefined) return <p>Loading...</p>

  return (
    <div className="container">
      <h1>Gateway Test Client</h1>
      {error && <p className="error">{error}</p>}
      {user ? (
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
    </div>
  )
}

export default App
