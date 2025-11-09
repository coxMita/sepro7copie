import { ref } from 'vue'
import { mockDataHelpers, type User } from '@/types/mockData'

export const loggedIn = ref(false)
export const userType = ref<'user' | 'admin' | null>(null)
export const currentUser = ref<User | null>(null)

export const authLogin = (type: 'user' | 'admin') => {
  loggedIn.value = true
  userType.value = type

  // Set current user based on login type
  if (type === 'user') {
    currentUser.value = mockDataHelpers.users.getCurrentUser() || null
  } else {
    // For admin, use the admin user from mock data
    const adminUser = mockDataHelpers.users.getByRole('admin')[0]
    currentUser.value = adminUser || null
  }
}

export const authLogOut = () => {
  loggedIn.value = false
  userType.value = null
  currentUser.value = null
}
