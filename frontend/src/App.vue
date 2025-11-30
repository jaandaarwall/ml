<template>
  <div id="app">
    <div v-if="authStore.isAuthenticated && !isAuthPage" class="app-container">
      <div 
        class="sidebar-overlay d-lg-none" 
        :class="{ show: isSidebarOpen }" 
        @click="isSidebarOpen = false"
      ></div>

      <aside class="sidebar" :class="{ show: isSidebarOpen }">
        <div class="sidebar-header d-flex align-items-center justify-content-between px-4 py-3 d-lg-none">
          <h5 class="text-white m-0 fw-bold">Menu</h5>
          <button class="btn-close btn-close-white" @click="isSidebarOpen = false"></button>
        </div>

        <nav class="nav flex-column mt-2">
          <template v-if="isAdminRoute">
            <div class="px-4 py-2 text-white-50 small text-uppercase fw-bold">Admin Console</div>
            <RouterLink to="/admin/dashboard" class="nav-link" @click="closeSidebar"><span>📊</span> Dashboard</RouterLink>
            <RouterLink to="/admin/doctors" class="nav-link" @click="closeSidebar"><span>👨‍⚕️</span> Doctors</RouterLink>
            <RouterLink to="/admin/patients" class="nav-link" @click="closeSidebar"><span>👥</span> Patients</RouterLink>
            <RouterLink to="/admin/departments" class="nav-link" @click="closeSidebar"><span>🏥</span> Departments</RouterLink>
            <RouterLink to="/admin/appointments" class="nav-link" @click="closeSidebar"><span>📅</span> Appointments</RouterLink>
            <RouterLink to="/admin/transactions" class="nav-link" @click="closeSidebar"><span>💰</span> Transactions</RouterLink>
            <RouterLink to="/admin/analytics" class="nav-link" @click="closeSidebar"><span>📈</span> Analytics</RouterLink>
          </template>

          <template v-if="isDoctorRoute">
             <div class="px-4 py-2 text-white-50 small text-uppercase fw-bold">Medical Practice</div>
             <RouterLink to="/doctor/dashboard" class="nav-link" @click="closeSidebar"><span>📊</span> Dashboard</RouterLink>
             <RouterLink to="/doctor/appointments" class="nav-link" @click="closeSidebar"><span>📅</span> Appointments</RouterLink>
             <RouterLink to="/doctor/patients" class="nav-link" @click="closeSidebar"><span>👥</span> My Patients</RouterLink>
             <RouterLink to="/doctor/availability" class="nav-link" @click="closeSidebar"><span>⏰</span> Availability</RouterLink>
             <RouterLink to="/doctor/profile" class="nav-link" @click="closeSidebar"><span>👤</span> Profile</RouterLink>
          </template>

          <template v-if="isPatientRoute">
             <div class="px-4 py-2 text-white-50 small text-uppercase fw-bold">My Health</div>
             <RouterLink to="/patient/dashboard" class="nav-link" @click="closeSidebar"><span>📊</span> Dashboard</RouterLink>
             <RouterLink to="/patient/book-appointment" class="nav-link" @click="closeSidebar"><span>🔍</span> Find Doctor</RouterLink>
             <RouterLink to="/patient/appointments" class="nav-link" @click="closeSidebar"><span>📅</span> Appointments</RouterLink>
             <RouterLink to="/patient/history" class="nav-link" @click="closeSidebar"><span>📋</span> History</RouterLink>
             <RouterLink to="/patient/profile" class="nav-link" @click="closeSidebar"><span>👤</span> Profile</RouterLink>
             <RouterLink to="/patient/analytics" class="nav-link" @click="closeSidebar"><span>📈</span> Analytics</RouterLink>
          </template>
        </nav>
      </aside>

      <div class="main-content">
        <Navbar @toggle-sidebar="isSidebarOpen = !isSidebarOpen" />
        <div class="container-fluid py-4">
          <RouterView />
        </div>
      </div>
    </div>

    <div v-else>
      <RouterView />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter, useRoute } from 'vue-router'
import Navbar from './components/Navbar.vue'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isSidebarOpen = ref(false)

const isAuthPage = computed(() => ['Login', 'Register'].includes(route.name))
const isAdminRoute = computed(() => route.path.startsWith('/admin'))
const isDoctorRoute = computed(() => route.path.startsWith('/doctor'))
const isPatientRoute = computed(() => route.path.startsWith('/patient'))

const closeSidebar = () => {
  if (window.innerWidth < 992) {
    isSidebarOpen.value = false
  }
}

onMounted(() => {
  if (authStore.isAuthenticated && route.path === '/') {
    if (authStore.isAdmin) router.push('/admin/dashboard')
    else if (authStore.isDoctor) router.push('/doctor/dashboard')
    else router.push('/patient/dashboard')
  }
})
</script>

<style>
.sidebar-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  z-index: 999;
  opacity: 0;
  visibility: hidden;
  transition: all 0.3s;
}
.sidebar-overlay.show {
  opacity: 1;
  visibility: visible;
}
</style>