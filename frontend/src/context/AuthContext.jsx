import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => localStorage.getItem('idp_token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('idp_user')
    if (stored && token) {
      try {
        setUser(JSON.parse(stored))
      } catch {
        logout()
      }
    }
    setLoading(false)
  }, [])

  const login = (tokenValue, userValue) => {
    localStorage.setItem('idp_token', tokenValue)
    localStorage.setItem('idp_user', JSON.stringify(userValue))
    setToken(tokenValue)
    setUser(userValue)
  }

  const logout = () => {
    localStorage.removeItem('idp_token')
    localStorage.removeItem('idp_user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
