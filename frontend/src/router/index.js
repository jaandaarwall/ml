import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Auth Views
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Payment from '../views/Payment.vue'

// Admin Views
import AdminDashboard from '../views/admin/Dashboard.vue'
import AdminDoctors from '../views/admin/Doctors.vue'
import AdminDoctorDetail from '../views/admin/DoctorDetail.vue'
import AdminPatients from '../views/admin/Patients.vue'
import AdminPatientDetail from '../views/admin/PatientDetail.vue'
import AdminAppointments from '../views/admin/Appointments.vue'
import AdminAnalytics from '../views/admin/Analytics.vue'

// Doctor Views
import DoctorDashboard from '../views/doctor/Dashboard.vue'
import DoctorAppointments from '../views/doctor/Appointments.vue'
import DoctorPatients from '../views/doctor/Patients.vue'
import DoctorPatientHistory from '../views/doctor/PatientHistory.vue'
import DoctorAvailability from '../views/doctor/Availability.vue'
import DoctorTreatment from '../views/doctor/Treatment.vue'
import DoctorProfile from '../views/doctor/Profile.vue'
import DoctorAnalytics from '../views/doctor/Analytics.vue'

// Patient Views
import PatientDashboard from '../views/patient/Dashboard.vue'
import PatientBookAppointment from '../views/patient/BookAppointment.vue'
import PatientAppointments from '../views/patient/Appointments.vue'
import PatientHistory from '../views/patient/History.vue'
import PatientProfile from '../views/patient/Profile.vue'
import PatientAnalytics from '../views/patient/Analytics.vue'

const routes = [
  { path: '/login', name: 'Login', component: Login, meta: { requiresAuth: false } },
  { path: '/register', name: 'Register', component: Register, meta: { requiresAuth: false } },
  { path: '/payment/:paymentId', name: 'Payment', component: Payment, meta: { requiresAuth: true } },

  {
    path: '/admin',
    meta: { requiresAuth: true, requiresRole: 'admin' },
    children: [
      { path: 'dashboard', name: 'AdminDashboard', component: AdminDashboard },
      { path: 'doctors', name: 'AdminDoctors', component: AdminDoctors },
      { path: 'doctor/:id', name: 'AdminDoctorDetail', component: AdminDoctorDetail },
      { path: 'patients', name: 'AdminPatients', component: AdminPatients },
      { path: 'patient/:id', name: 'AdminPatientDetail', component: AdminPatientDetail },
      { path: 'appointments', name: 'AdminAppointments', component: AdminAppointments },
      { path: 'analytics', name: 'AdminAnalytics', component: AdminAnalytics }
    ]
  },

  {
    path: '/doctor',
    meta: { requiresAuth: true, requiresRole: 'doctor' },
    children: [
      { path: 'dashboard', name: 'DoctorDashboard', component: DoctorDashboard },
      { path: 'appointments', name: 'DoctorAppointments', component: DoctorAppointments },
      { path: 'patients', name: 'DoctorPatients', component: DoctorPatients },
      { path: 'patient/:id/history', name: 'DoctorPatientHistory', component: DoctorPatientHistory },
      { path: 'availability', name: 'DoctorAvailability', component: DoctorAvailability },
      { path: 'appointment/:id/treatment', name: 'DoctorTreatment', component: DoctorTreatment },
      { path: 'profile', name: 'DoctorProfile', component: DoctorProfile },
      { path: 'analytics', name: 'DoctorAnalytics', component: DoctorAnalytics }
    ]
  },

  {
    path: '/patient',
    meta: { requiresAuth: true, requiresRole: 'user' },
    children: [
      { path: 'dashboard', name: 'PatientDashboard', component: PatientDashboard },
      { path: 'book-appointment', name: 'PatientBookAppointment', component: PatientBookAppointment },
      { path: 'book/:doctorId', name: 'PatientBookWithDoctor', component: PatientBookAppointment },
      { path: 'appointments', name: 'PatientAppointments', component: PatientAppointments },
      { path: 'history', name: 'PatientHistory', component: PatientHistory },
      { path: 'profile', name: 'PatientProfile', component: PatientProfile },
      { path: 'analytics', name: 'PatientAnalytics', component: PatientAnalytics }
    ]
  },

  { path: '/', redirect: '/login' },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  if (to.meta.requiresRole) {
    if (authStore.hasRole(to.meta.requiresRole)) {
      next()
    } else {
      next('/login')
    }
  } else if (to.meta.requiresAuth === false && authStore.isAuthenticated) {
    // Redirect authenticated users away from login/register
    if (to.name === 'Login' || to.name === 'Register') {
      if (authStore.isAdmin) next('/admin/dashboard')
      else if (authStore.isDoctor) next('/doctor/dashboard')
      else next('/patient/dashboard')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router