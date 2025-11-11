import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/store/auth';

import Login from '@/views/Login.vue';
import Register from '@/views/Register.vue';
import Home from '@/views/Home.vue'; // Will create this component later

// Placeholders for role-based dashboards
import AdminDashboard from '@/views/AdminDashboard.vue';
import DoctorDashboard from '@/views/DoctorDashboard.vue';
import PatientDashboard from '@/views/PatientDashboard.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  {
    path: '/admin/dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/doctor/dashboard',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' },
  },
  {
    path: '/patient/dashboard',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiredRole = to.meta.role;

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login');
  } else if (requiresAuth && requiredRole && authStore.userRole !== requiredRole) {
    next('/'); // Redirect to home if role doesn't match
  } else {
    next();
  }
});

export default router;
