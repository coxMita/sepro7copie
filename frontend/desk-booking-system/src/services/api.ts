import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',  // Changed from 8000 to 8080
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})
// Scheduler API functions
export const schedulerApi = {
  // Set all desks to a specific position
  setAllDesksPosition: async (positionMm: number) => {
    const response = await api.post('/scheduler/scheduler/api/v1/desks/position', {
      position_mm: positionMm,
    })
    return response.data
  },

  // Get all desks status
  getAllDesks: async () => {
    const response = await api.get('/scheduler/scheduler/api/v1/desks')
    return response.data
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/scheduler/scheduler/api/v1/health')
    return response.data
  },
}

export default api