// ========================================
// TYPES & INTERFACES
// ========================================

export type DeskStatus = 'available' | 'occupied' | 'reserved' | 'maintenance'
export type BookingStatus = 'active' | 'completed' | 'cancelled'

export interface DeskFeatures {
  nearWindow: boolean
  dualMonitor: boolean
  standingDesk?: boolean
}

export interface Desk {
  id: string
  status: DeskStatus
  features: string[] // ['near-window', 'dual-monitor']
  floor: number // 0 or 1
  bookedBy?: string
  isFavorite?: boolean
  height: number
}

export interface Booking {
  id: string
  deskId: string
  date: string // YYYY-MM-DD
  startTime: string // HH:mm
  endTime: string // HH:mm
  userId: string
  status: BookingStatus
  notes?: string
  createdAt: string // ISO date
}

export interface User {
  id: string
  username: string
  fullName: string
  email: string
  role: 'user' | 'admin'
  createdAt: string
  profilePicture?: string
}

// ========================================
// MOCK DATA
// ========================================
export const mockUsers: User[] = [
  {
    id: 'user-1',
    username: 'ana.popescu',
    fullName: 'Ana Popescu',
    email: 'ana.popescu@company.com',
    role: 'user',
    createdAt: '2024-01-15T08:00:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=1',
  },
  {
    id: 'user-2',
    username: 'ion.ionescu',
    fullName: 'Ion Ionescu',
    email: 'ion.ionescu@company.com',
    role: 'user',
    createdAt: '2024-01-20T09:30:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=2',
  },
  {
    id: 'user-3',
    username: 'maria.georgescu',
    fullName: 'Maria Georgescu',
    email: 'maria.georgescu@company.com',
    role: 'admin',
    createdAt: '2024-02-01T10:00:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=3',
  },
  {
    id: 'current-user',
    username: 'andrei.dumitrescu',
    fullName: 'Andrei Dumitrescu',
    email: 'andrei.dumitrescu@company.com',
    role: 'user',
    createdAt: '2024-02-10T11:15:00Z',
    profilePicture: 'https://i.pravatar.cc/150?img=4',
  },
]

export const mockDesks: Desk[] = [
  // FLOOR 0
  { id: 'D-001', status: 'available', features: ['near-window'], floor: 0, isFavorite: false },
  { id: 'D-002', status: 'available', features: ['dual-monitor'], floor: 0, isFavorite: true },
  { id: 'D-005', status: 'available', features: [], floor: 0, isFavorite: false },
  { id: 'D-004', status: 'available', features: ['near-window'], floor: 0, isFavorite: false },
  {
    id: 'D-00F',
    status: 'available',
    features: ['dual-monitor', 'near-window'],
    floor: 0,
    isFavorite: false,
  },
  {
    id: 'D-037',
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    bookedBy: 'user-1',
  },
  {
    id: 'D-027',
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    bookedBy: 'user-2',
  },
  {
    id: 'D-049',
    status: 'reserved',
    features: ['dual-monitor'],
    floor: 0,
    isFavorite: false,
    bookedBy: 'current-user',
  },
  { id: 'D-011', status: 'available', features: ['dual-monitor'], floor: 0, isFavorite: false },
  { id: 'D-014', status: 'maintenance', features: [], floor: 0, isFavorite: false },

  { id: 'D-007', status: 'available', features: ['near-window'], floor: 0, isFavorite: false },
  { id: 'D-008', status: 'available', features: [], floor: 0, isFavorite: false },
  { id: 'D-015', status: 'available', features: [], floor: 0, isFavorite: false },
  {
    id: 'D-019',
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    bookedBy: 'user-1',
  },
  {
    id: 'D-025',
    status: 'occupied',
    features: ['dual-monitor'],
    floor: 0,
    isFavorite: false,
    bookedBy: 'user-2',
  },
  { id: 'D-012', status: 'available', features: ['near-window'], floor: 0, isFavorite: false },
  {
    id: 'D-044',
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    bookedBy: 'user-3',
  },
  { id: 'D-021', status: 'available', features: [], floor: 0, isFavorite: false },
  {
    id: 'D-023',
    status: 'occupied',
    features: [],
    floor: 0,
    isFavorite: false,
    bookedBy: 'user-1',
  },
  { id: 'D-030', status: 'maintenance', features: [], floor: 0, isFavorite: false },

  // FLOOR 1
  {
    id: 'D-032',
    status: 'available',
    features: ['dual-monitor', 'near-window'],
    floor: 1,
    isFavorite: false,
  },
  { id: 'D-033', status: 'available', features: [], floor: 1, isFavorite: false },
  {
    id: 'D-034',
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    bookedBy: 'user-2',
  },
  { id: 'D-036', status: 'available', features: [], floor: 1, isFavorite: false },
  { id: 'D-038', status: 'available', features: [], floor: 1, isFavorite: false },
  { id: 'D-040', status: 'available', features: ['near-window'], floor: 1, isFavorite: false },
  { id: 'D-039', status: 'available', features: ['dual-monitor'], floor: 1, isFavorite: false },
  {
    id: 'D-031',
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    bookedBy: 'user-3',
  },
  { id: 'D-041', status: 'maintenance', features: [], floor: 1, isFavorite: false },
  { id: 'D-017', status: 'available', features: ['dual-monitor'], floor: 1, isFavorite: false },

  { id: 'D-042', status: 'available', features: [], floor: 1, isFavorite: false },
  { id: 'D-043', status: 'available', features: ['near-window'], floor: 1, isFavorite: false },
  { id: 'D-016', status: 'available', features: [], floor: 1, isFavorite: false },
  {
    id: 'D-045',
    status: 'occupied',
    features: [],
    floor: 1,
    isFavorite: false,
    bookedBy: 'user-1',
  },
  {
    id: 'D-022',
    status: 'available',
    features: ['dual-monitor', 'near-window'],
    floor: 1,
    isFavorite: false,
  },
  { id: 'D-024', status: 'available', features: [], floor: 1, isFavorite: false },
  { id: 'D-046', status: 'maintenance', features: [], floor: 1, isFavorite: false },
  { id: 'D-013', status: 'available', features: [], floor: 1, isFavorite: false },
  { id: 'D-109', status: 'maintenance', features: [], floor: 1, isFavorite: false },
]

export const mockBookings: Booking[] = [
  {
    id: 'booking-1',
    deskId: 'D-049',
    date: '2025-10-05',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'active',
    createdAt: '2025-10-03T14:30:00Z',
  },
  {
    id: 'booking-2',
    deskId: 'D-015',
    date: '2025-09-29',
    startTime: '09:00',
    endTime: '13:00',
    userId: 'current-user',
    status: 'active',
    notes: 'Half day work',
    createdAt: '2025-09-28T10:15:00Z',
  },
  {
    id: 'booking-3',
    deskId: 'D-002',
    date: '2025-09-26',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'completed',
    createdAt: '2025-09-25T16:45:00Z',
  },
  {
    id: 'booking-4',
    deskId: 'D-007',
    date: '2025-09-25',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'completed',
    createdAt: '2025-09-24T08:00:00Z',
  },
  {
    id: 'booking-5',
    deskId: 'D-002',
    date: '2025-09-24',
    startTime: '14:00',
    endTime: '18:00',
    userId: 'current-user',
    status: 'completed',
    createdAt: '2025-09-23T15:00:00Z',
  },
  {
    id: 'booking-6',
    deskId: 'D-001',
    date: '2025-09-23',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'current-user',
    status: 'completed',
    createdAt: '2025-09-22T09:00:00Z',
  },
  {
    id: 'booking-7',
    deskId: 'D-037',
    date: '2025-10-05',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'user-1',
    status: 'active',
    createdAt: '2025-10-03T08:00:00Z',
  },
  {
    id: 'booking-8',
    deskId: 'D-027',
    date: '2025-10-05',
    startTime: '10:00',
    endTime: '16:00',
    userId: 'user-2',
    status: 'active',
    notes: 'Important meeting day',
    createdAt: '2025-10-02T14:00:00Z',
  },
  // NEW BOOKINGS FOR OCCUPIED DESKS
  {
    id: 'booking-9',
    deskId: 'D-019',
    date: '2025-10-05',
    startTime: '08:00',
    endTime: '16:00',
    userId: 'user-1',
    status: 'active',
    createdAt: '2025-10-04T09:15:00Z',
  },
  {
    id: 'booking-10',
    deskId: 'D-025',
    date: '2025-10-05',
    startTime: '09:00',
    endTime: '18:00',
    userId: 'user-2',
    status: 'active',
    notes: 'Extended work session',
    createdAt: '2025-10-04T10:30:00Z',
  },
  {
    id: 'booking-11',
    deskId: 'D-034',
    date: '2025-10-05',
    startTime: '10:00',
    endTime: '15:00',
    userId: 'user-2',
    status: 'active',
    createdAt: '2025-10-04T11:00:00Z',
  },
  {
    id: 'booking-12',
    deskId: 'D-031',
    date: '2025-10-05',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'user-3',
    status: 'active',
    notes: 'Project deadline work',
    createdAt: '2025-10-03T16:20:00Z',
  },
  {
    id: 'booking-13',
    deskId: 'D-045',
    date: '2025-10-05',
    startTime: '08:30',
    endTime: '16:30',
    userId: 'user-1',
    status: 'active',
    createdAt: '2025-10-04T07:45:00Z',
  },
  {
    id: 'booking-14',
    deskId: 'D-023',
    date: '2025-10-05',
    startTime: '09:00',
    endTime: '13:00',
    userId: 'user-1',
    status: 'active',
    notes: 'Morning shift',
    createdAt: '2025-10-04T12:30:00Z',
  },
  {
    id: 'booking-15',
    deskId: 'D-044',
    date: '2025-10-05',
    startTime: '11:00',
    endTime: '19:00',
    userId: 'user-3',
    status: 'active',
    notes: 'Late shift for client calls',
    createdAt: '2025-10-03T15:10:00Z',
  },
  // FUTURE BOOKINGS FOR VARIETY
  {
    id: 'booking-16',
    deskId: 'D-019',
    date: '2025-10-06',
    startTime: '09:00',
    endTime: '17:00',
    userId: 'user-1',
    status: 'active',
    createdAt: '2025-10-04T14:00:00Z',
  },
  {
    id: 'booking-17',
    deskId: 'D-031',
    date: '2025-10-07',
    startTime: '09:00',
    endTime: '12:00',
    userId: 'user-2',
    status: 'active',
    notes: 'Team standup',
    createdAt: '2025-10-04T15:30:00Z',
  },
]

// ========================================
// HELPER FUNCTIONS
// ========================================

export const mockDataHelpers = {
  // Desk helpers
  desks: {
    getAll: () => mockDesks,
    getById: (id: string) => mockDesks.find((desk) => desk.id === id),
    getAvailable: () => mockDesks.filter((desk) => desk.status === 'available'),
    getOccupied: () => mockDesks.filter((desk) => desk.status === 'occupied'),
    getByStatus: (status: DeskStatus) => mockDesks.filter((desk) => desk.status === status),
    getByFloor: (floor: number) => mockDesks.filter((desk) => desk.floor === floor),
    getOccupiedByFloor: (floor: number) =>
      mockDesks.filter((desk) => desk.floor === floor && desk.status === 'occupied'),
    getFavorites: () => mockDesks.filter((desk) => desk.isFavorite),
    getByFeature: (feature: string) => mockDesks.filter((desk) => desk.features.includes(feature)),
    getByUser: (userId: string) => mockDesks.filter((desk) => desk.bookedBy === userId),
  },

  // Booking helpers
  bookings: {
    getAll: () => mockBookings,
    getById: (id: string) => mockBookings.find((booking) => booking.id === id),
    getByUserId: (userId: string) => mockBookings.filter((booking) => booking.userId === userId),
    getByDeskId: (deskId: string) => mockBookings.filter((booking) => booking.deskId === deskId),
    getByDate: (date: string) => mockBookings.filter((booking) => booking.date === date),
    getByHour: (time: string) => mockBookings.filter((booking) => booking.startTime === time),
    getActive: () => mockBookings.filter((booking) => booking.status === 'active'),
    getCompleted: () => mockBookings.filter((booking) => booking.status === 'completed'),
    getCancelled: () => mockBookings.filter((booking) => booking.status === 'cancelled'),
    getByStatus: (status: BookingStatus) =>
      mockBookings.filter((booking) => booking.status === status),
  },

  // User helpers
  users: {
    getAll: () => mockUsers,
    getById: (id: string) => mockUsers.find((user) => user.id === id),
    getByEmail: (email: string) => mockUsers.find((user) => user.email === email),
    getByRole: (role: 'user' | 'admin') => mockUsers.filter((user) => user.role === role),
    getCurrentUser: () => mockUsers.find((user) => user.id === 'current-user'),
  },
}
export const deskOccupancy = [
  { title: 'Used Desks', value: mockDataHelpers.desks.getOccupied().length },
  { title: 'Unused Desks', value: mockDataHelpers.desks.getAvailable().length },
]

export const plByTime = [
  { title: '07:00', value: mockDataHelpers.bookings.getByHour('07:00').length },
  { title: '08:00', value: mockDataHelpers.bookings.getByHour('08:00').length },
  { title: '09:00', value: mockDataHelpers.bookings.getByHour('09:00').length },
  { title: '10:00', value: mockDataHelpers.bookings.getByHour('10:00').length },
  { title: '11:00', value: mockDataHelpers.bookings.getByHour('11:00').length },
  { title: '12:00', value: mockDataHelpers.bookings.getByHour('12:00').length },
  { title: '13:00', value: mockDataHelpers.bookings.getByHour('13:00').length },
  { title: '14:00', value: mockDataHelpers.bookings.getByHour('14:00').length },
  { title: '15:00', value: mockDataHelpers.bookings.getByHour('15:00').length },
  { title: '16:00', value: mockDataHelpers.bookings.getByHour('16:00').length },
  { title: '17:00', value: mockDataHelpers.bookings.getByHour('17:00').length },
  { title: '18:00', value: mockDataHelpers.bookings.getByHour('18:00').length },
]

export const plByFloor = [
  { title: '1st Floor', value: mockDataHelpers.desks.getOccupiedByFloor(0).length },
  { title: '2nd Floor', value: mockDataHelpers.desks.getOccupiedByFloor(1).length },
]

// Export
export const mockData = {
  desks: mockDesks,
  bookings: mockBookings,
  users: mockUsers,
  helpers: mockDataHelpers,
}
