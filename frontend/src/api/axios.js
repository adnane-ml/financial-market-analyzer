import axios from 'axios'

const api = axios.create({
  baseURL: '',
  withCredentials: true,
})

let accessToken = null

export function setAccessToken(token) {
  accessToken = token
}

api.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const res = await api.post('/auth/refresh')
        accessToken = res.data.access_token
        original.headers.Authorization = `Bearer ${accessToken}`
        return api(original)
      } catch {
        accessToken = null
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api