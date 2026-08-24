import { useState, useEffect } from 'react'
import authService from '../services/authService'
import { AuthContext } from './context'

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('access_token'))

  useEffect(() => {
    // Check if user is logged in on mount
    const checkAuth = async () => {
      const storedToken = localStorage.getItem('access_token')
      if (storedToken) {
        try {
          const userData = await authService.getProfile()
          setUser(userData)
        } catch (error) {
          console.error('Auth check failed:', error)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          setToken(null)
        }
      }
      setLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (credentials) => {
    try {
      const response = await authService.login(credentials)
      setToken(response.access_token)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      const userData = await authService.getProfile()
      setUser(userData)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || { error: 'Login failed' } 
      }
    }
  }

  const register = async (userData) => {
    try {
      await authService.register({
        ...userData,
        email: userData.email.trim().toLowerCase(),
        phone_number: userData.phone_number.trim()
      })
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || { error: 'Registration failed' } 
      }
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      setUser(null)
      setToken(null)
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
