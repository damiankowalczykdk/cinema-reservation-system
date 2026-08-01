const GATEWAY_URL = import.meta.env.VITE_GATEWAY_URL || 'http://localhost:8000'

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
  const res = await fetch(`${GATEWAY_URL}/auth/logout`, {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Failed to log out')
  return res.json()
}

export { getLoginUrl, getLogoutUrl, getMe, logout }
