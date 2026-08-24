import api from './api'

const API_BASE_URL = '/auth'

const authService = {
  // Register new user
  register: async (userData) => {
    const response = await api.post(`${API_BASE_URL}/register/`, userData)
    return response.data
  },

  // Login user
  login: async (credentials) => {
    const response = await api.post(`${API_BASE_URL}/login/`, credentials)
    return response.data
  },

  refresh: async (refreshToken) => {
    const response = await api.post(`${API_BASE_URL}/refresh/`, {
      refresh_token: refreshToken
    })
    return response.data
  },

  // Logout user
  logout: async () => {
    if (localStorage.getItem('access_token')) {
      await api.post(`${API_BASE_URL}/logout/`)
    }
  },

  // Get user profile
  getProfile: async () => {
    const response = await api.post(`${API_BASE_URL}/profile/`)
    return response.data
  }
}

export default authService