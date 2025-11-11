import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8080',  // Gateway port
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

  // Schedule management
  createSchedule: async (schedule: {
    name: string
    action: 'raise' | 'lower'
    position_mm: number
    cron: {
      hour: number
      minute: number
      day_of_week: string
    }
    id?: string
  }) => {
    const response = await api.post('/scheduler/scheduler/api/v1/schedules', schedule)
    return response.data
  },

  getSchedules: async () => {
    const response = await api.get('/scheduler/scheduler/api/v1/schedules')
    return response.data
  },

  deleteSchedule: async (jobId: string) => {
    const response = await api.delete(`/scheduler/scheduler/api/v1/schedules/${jobId}`)
    return response.data
  },
}

export default api