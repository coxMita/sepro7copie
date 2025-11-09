import LandingPageView from '@/views/LandingPageView.vue'
import { createRouter, createWebHistory } from 'vue-router'
import { loggedIn, userType } from '@/stores/auth'
import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'

const requireAuth = (requiredUserType: string) => {
  return (
    _to: RouteLocationNormalized,
    _from: RouteLocationNormalized,
    next: NavigationGuardNext,
  ) => {
    if (!loggedIn.value || userType.value !== requiredUserType) {
      next('/login')
    } else {
      next()
    }
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing-page',
      component: LandingPageView,
    },
    {
      path: '/book',
      name: 'book',
      component: () => import('../views/user/BookingView.vue'),
      beforeEnter: requireAuth('user'),
    },
    {
      path: '/my-bookings',
      name: 'my-bookings',
      component: () => import('../views/user/MyBookingsView.vue'),
      beforeEnter: requireAuth('user'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/user/ProfileView.vue'),
      beforeEnter: requireAuth('user'),
    },
    {
      path: '/admin/bookings',
      name: 'admin-manage-bookings',
      component: () => import('../views/admin/ManageBookingsView.vue'),
      beforeEnter: requireAuth('admin'),
    },
    {
      path: '/admin/desks',
      name: 'admin-manage-desks',
      component: () => import('../views/admin/ManageDesksView.vue'),
      beforeEnter: requireAuth('admin'),
    },
    {
      path: '/admin/availability',
      name: 'admin-desk-availability',
      component: () => import('../views/admin/DeskAvailabilityView.vue'),
      beforeEnter: requireAuth('admin'),
    },
    {
      path: '/admin/analytics',
      name: 'admin-analytics',
      component: () => import('../views/admin/AnalyticsView.vue'),
      beforeEnter: requireAuth('admin'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/MockLoginPage.vue'),
    },
  ],
})

export default router
