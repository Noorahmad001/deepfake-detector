import axios from 'axios'

// Use relative paths — Netlify proxies /api/* to the backend in production.
// Vite dev server proxies the same paths locally (see vite.config.js).
const API_BASE_URL = ''

const getSessionId = () => {
  let sessionId = sessionStorage.getItem('deepfake_session_id')
  if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
    sessionStorage.setItem('deepfake_session_id', sessionId)
  }
  return sessionId
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
})

export const detectImage = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post(
    `/api/detect-image?session_id=${getSessionId()}`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      }
    }
  )
  return response.data
}

export const detectVideo = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post(
    `/api/detect-video?session_id=${getSessionId()}`,
    formData,
    {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total) {
          onProgress(Math.round((e.loaded * 100) / e.total))
        }
      }
    }
  )
  return response.data
}

export const getHistory = async () => {
  const response = await api.get(
    `/api/history?session_id=${getSessionId()}`
  )
  return response.data
}

export const getHealth = async () => {
  const response = await api.get('/health')
  return response.data
}

export default api
