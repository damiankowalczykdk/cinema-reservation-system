import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { getMe, getLoginUrl, getLogoutUrl, logout as apiLogout } from '../api.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const refresh = useCallback(async () => {
    setLoading(true)
    try {
      setUser(await getMe())
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const login = useCallback(async () => {
    const { url } = await getLoginUrl()
    window.location.href = url
  }, [])

  const logout = useCallback(async () => {
    await apiLogout()
    const { url } = await getLogoutUrl()
    window.location.href = url
  }, [])

  const roles = user?.roles ?? []
  const isAdmin = roles.includes('admin')

  return (
    <AuthContext.Provider value={{ user, roles, isAdmin, loading, refresh, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
