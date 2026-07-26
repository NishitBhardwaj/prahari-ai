import axios from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Automatically attach auth token (Mocked for now since Auth is handled via Catalyst later)
apiClient.interceptors.request.use((config) => {
  // const token = getAuthToken()
  // if (token) {
  //   config.headers.Authorization = `Bearer ${token}`
  // }
  return config
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Handle global errors here
    console.error("API Error:", error.response?.data || error.message)
    return Promise.reject(error)
  }
)
