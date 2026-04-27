import axios, { AxiosError } from 'axios'

// En dev : on passe par le proxy Vite (/api → http://localhost:8000)
// En prod : on tape l'URL définie via VITE_API_URL (build-time)
const baseURL = import.meta.env.DEV
  ? '/api'
  : (import.meta.env.VITE_API_URL as string | undefined) ?? '/api'

export const api = axios.create({
  baseURL,
  timeout: 10_000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
})

// Interception des erreurs pour normaliser les messages
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string }>) => {
    const message =
      error.response?.data?.detail ??
      error.message ??
      'Une erreur inattendue est survenue'

    return Promise.reject(new ApiError(message, error.response?.status))
  },
)

export class ApiError extends Error {
  status?: number
  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}
