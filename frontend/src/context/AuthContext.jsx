import { createContext, useState, useEffect, useCallback } from 'react'
import api, { setAccessToken } from '../api/axios'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [accessToken, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  // Au démarrage : refresh silencieux via cookie httpOnly
  useEffect(() => {
    api.post('/auth/refresh')
      .then(res => {
        setAccessToken(res.data.access_token)  // module axios
        setToken(res.data.access_token)         // state React
      })
      .catch(() => setToken(null))
      .finally(() => setLoading(false))
  }, [])

  const login = useCallback((token) => {
    setAccessToken(token)  // module axios
    setToken(token)        // state React
  }, [])

  const logout = useCallback(async () => {
    try { await api.post('/auth/logout') } catch (_) {}
    setAccessToken(null)
    setToken(null)
  }, [])

  return (
    <AuthContext.Provider value={{ accessToken, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}