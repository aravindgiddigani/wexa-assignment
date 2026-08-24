import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let refreshRequest = null

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const refreshToken = localStorage.getItem('refresh_token')

    if (error.response?.status !== 401 || originalRequest?._retry || !refreshToken) {
      return Promise.reject(error)
    }

    originalRequest._retry = true
    refreshRequest ||= axios.post(
      `${import.meta.env.VITE_API_BASE_URL || '/api'}/auth/refresh/`,
      { refresh_token: refreshToken },
      { headers: { 'Content-Type': 'application/json' } }
    ).then(({ data }) => {
      localStorage.setItem('access_token', data.access_token)
      return data.access_token
    }).finally(() => {
      refreshRequest = null
    })

    try {
      const accessToken = await refreshRequest
      originalRequest.headers.Authorization = `Bearer ${accessToken}`
      return api(originalRequest)
    } catch (refreshError) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      return Promise.reject(refreshError)
    }
  }
)

export default api