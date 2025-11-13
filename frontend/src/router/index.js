import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.js'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
    },
    {
      path: '/admin/dashboard',
      name: 'admin-dashboard',
      component: () => import('../views/Admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/doctor/dashboard',
      name: 'doctor-dashboard',
      component: () => import('../views/Doctor/DoctorDashboard.vue'),
      meta: { requiresAuth: true, role: 'doctor' }
    },
    {
      path: '/patient/dashboard',
      name: 'patient-dashboard',
      component: () => import('../views/Patient/PatientDashboard.vue'),
      meta: { requiresAuth: true, role: 'user' }
    }
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.role && !authStore.userRoles.includes(to.meta.role)) {
    next('/')
  } else {
    next()
  }
})

export default router