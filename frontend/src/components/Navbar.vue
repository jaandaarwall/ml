<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <RouterLink to="/" class="navbar-brand fw-bold d-flex align-items-center">
        <span class="me-2">🏥</span> HMS
        <span v-if="currentRoleLabel" class="badge bg-white text-primary ms-2 rounded-pill fs-6">
          {{ currentRoleLabel }}
        </span>
      </RouterLink>
      
      <button class="navbar-toggler" type="button" @click="toggleMobileMenu" aria-controls="navbarNav" :aria-expanded="isMobileMenuOpen" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" :class="{ show: isMobileMenuOpen }" id="navbarNav">
        <ul class="navbar-nav ms-auto align-items-center">
          
          <li v-if="hasMultipleRoles" class="nav-item dropdown me-2">
            <a class="btn btn-outline-light dropdown-toggle d-flex align-items-center" href="#" id="roleSwitcher" role="button" @click.prevent="toggleDropdown('roleSwitcher')" :class="{ show: activeDropdown === 'roleSwitcher' }" aria-expanded="false">
              🔄 Switch View
            </a>
            <ul class="dropdown-menu dropdown-menu-end shadow" :class="{ show: activeDropdown === 'roleSwitcher' }" aria-labelledby="roleSwitcher">
              <li v-if="authStore.isAdmin">
                <RouterLink to="/admin/dashboard" class="dropdown-item d-flex align-items-center" @click="closeDropdown">
                  <span class="me-2">⚙️</span> Admin Dashboard
                </RouterLink>
              </li>
              <li v-if="authStore.isDoctor">
                <RouterLink to="/doctor/dashboard" class="dropdown-item d-flex align-items-center" @click="closeDropdown">
                  <span class="me-2">👨‍⚕️</span> Doctor Dashboard
                </RouterLink>
              </li>
              <li v-if="authStore.isPatient">
                <RouterLink to="/patient/dashboard" class="dropdown-item d-flex align-items-center" @click="closeDropdown">
                  <span class="me-2">👤</span> Patient Dashboard
                </RouterLink>
              </li>
            </ul>
          </li>

          <div class="vr mx-2 d-none d-lg-block text-light opacity-50"></div>

          <li v-if="isAdminRoute" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle active" href="#" id="adminMenu" role="button" @click.prevent="toggleDropdown('adminMenu')" :class="{ show: activeDropdown === 'adminMenu' }">
              Manage
            </a>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: activeDropdown === 'adminMenu' }">
              <li><RouterLink to="/admin/dashboard" class="dropdown-item" @click="closeDropdown">Dashboard</RouterLink></li>
              <li><hr class="dropdown-divider"></li>
              <li><RouterLink to="/admin/doctors" class="dropdown-item" @click="closeDropdown">Manage Doctors</RouterLink></li>
              <li><RouterLink to="/admin/patients" class="dropdown-item" @click="closeDropdown">Manage Patients</RouterLink></li>
              <li><RouterLink to="/admin/appointments" class="dropdown-item" @click="closeDropdown">All Appointments</RouterLink></li>
              <li><RouterLink to="/admin/transactions" class="dropdown-item" @click="closeDropdown">Transactions</RouterLink></li>
              <li><RouterLink to="/admin/analytics" class="dropdown-item" @click="closeDropdown">Analytics</RouterLink></li>
            </ul>
          </li>

          <li v-if="isDoctorRoute" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle active" href="#" id="doctorMenu" role="button" @click.prevent="toggleDropdown('doctorMenu')" :class="{ show: activeDropdown === 'doctorMenu' }">
              Practice
            </a>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: activeDropdown === 'doctorMenu' }">
              <li><RouterLink to="/doctor/dashboard" class="dropdown-item" @click="closeDropdown">Dashboard</RouterLink></li>
              <li><hr class="dropdown-divider"></li>
              <li><RouterLink to="/doctor/appointments" class="dropdown-item" @click="closeDropdown">My Appointments</RouterLink></li>
              <li><RouterLink to="/doctor/patients" class="dropdown-item" @click="closeDropdown">My Patients</RouterLink></li>
              <li><RouterLink to="/doctor/availability" class="dropdown-item" @click="closeDropdown">My Availability</RouterLink></li>
              <li><RouterLink to="/doctor/analytics" class="dropdown-item" @click="closeDropdown">My Analytics</RouterLink></li>
              <li><RouterLink to="/doctor/profile" class="dropdown-item" @click="closeDropdown">My Profile</RouterLink></li>
            </ul>
          </li>

          <li v-if="isPatientRoute" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle active" href="#" id="patientMenu" role="button" @click.prevent="toggleDropdown('patientMenu')" :class="{ show: activeDropdown === 'patientMenu' }">
              My Health
            </a>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: activeDropdown === 'patientMenu' }">
              <li><RouterLink to="/patient/dashboard" class="dropdown-item" @click="closeDropdown">Dashboard</RouterLink></li>
              <li><hr class="dropdown-divider"></li>
              <li><RouterLink to="/patient/book-appointment" class="dropdown-item" @click="closeDropdown">Book Appointment</RouterLink></li>
              <li><RouterLink to="/patient/appointments" class="dropdown-item" @click="closeDropdown">My Appointments</RouterLink></li>
              <li><RouterLink to="/patient/history" class="dropdown-item" @click="closeDropdown">Medical History</RouterLink></li>
              <li><RouterLink to="/patient/analytics" class="dropdown-item" @click="closeDropdown">Analytics</RouterLink></li>
              <li><RouterLink to="/patient/profile" class="dropdown-item" @click="closeDropdown">Profile</RouterLink></li>
            </ul>
          </li>

          <li class="nav-item dropdown ms-lg-2">
            <a class="nav-link dropdown-toggle" href="#" id="userMenu" role="button" @click.prevent="toggleDropdown('userMenu')" :class="{ show: activeDropdown === 'userMenu' }">
              <span class="d-none d-lg-inline">{{ userEmail }}</span>
              <span class="d-lg-none">Account</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end" :class="{ show: activeDropdown === 'userMenu' }">
              <li class="px-3 py-1 text-muted small d-lg-none">{{ userEmail }}</li>
              <li v-if="hasMultipleRoles"><hr class="dropdown-divider d-lg-none"></li>
              <li>
                <button @click="handleLogout" class="dropdown-item text-danger d-flex align-items-center">
                  <span class="me-2">🚪</span> Logout
                </button>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter, useRoute } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const userEmail = computed(() => authStore.user?.email || 'User')

const hasMultipleRoles = computed(() => {
  let count = 0
  if (authStore.isAdmin) count++
  if (authStore.isDoctor) count++
  if (authStore.isPatient) count++
  return count > 1
})

const isAdminRoute = computed(() => route.path.startsWith('/admin'))
const isDoctorRoute = computed(() => route.path.startsWith('/doctor'))
const isPatientRoute = computed(() => route.path.startsWith('/patient'))

const currentRoleLabel = computed(() => {
  if (isAdminRoute.value) return 'Admin View'
  if (isDoctorRoute.value) return 'Doctor View'
  if (isPatientRoute.value) return 'Patient View'
  return ''
})

const activeDropdown = ref(null)
const isMobileMenuOpen = ref(false)

const toggleDropdown = (id) => {
  if (activeDropdown.value === id) {
    activeDropdown.value = null
  } else {
    activeDropdown.value = id
  }
}

const closeDropdown = () => {
  activeDropdown.value = null
  isMobileMenuOpen.value = false
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const handleClickOutside = (event) => {
  if (!event.target.closest('.dropdown') && !event.target.closest('.navbar-toggler')) {
    activeDropdown.value = null
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>
