<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container-fluid">
      <RouterLink to="/" class="navbar-brand fw-bold">🏥 HMS</RouterLink>
      
      <button 
        class="navbar-toggler" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#navbarNav"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <!-- Admin Menu -->
          <li v-if="authStore.isAdmin" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="adminMenu" role="button" data-bs-toggle="dropdown">
              Admin
            </a>
            <ul class="dropdown-menu" aria-labelledby="adminMenu">
              <li><RouterLink to="/admin/dashboard" class="dropdown-item">Dashboard</RouterLink></li>
              <li><RouterLink to="/admin/doctors" class="dropdown-item">Doctors</RouterLink></li>
              <li><RouterLink to="/admin/patients" class="dropdown-item">Patients</RouterLink></li>
              <li><RouterLink to="/admin/appointments" class="dropdown-item">Appointments</RouterLink></li>
              <li><RouterLink to="/admin/transactions" class="dropdown-item">Transactions</RouterLink></li>
              <li><RouterLink to="/admin/analytics" class="dropdown-item">Analytics</RouterLink></li>
            </ul>
          </li>

          <!-- Doctor Menu -->
          <li v-if="authStore.isDoctor" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="doctorMenu" role="button" data-bs-toggle="dropdown">
              Doctor
            </a>
            <ul class="dropdown-menu" aria-labelledby="doctorMenu">
              <li><RouterLink to="/doctor/dashboard" class="dropdown-item">Dashboard</RouterLink></li>
              <li><RouterLink to="/doctor/appointments" class="dropdown-item">Appointments</RouterLink></li>
              <li><RouterLink to="/doctor/patients" class="dropdown-item">Patients</RouterLink></li>
              <li><RouterLink to="/doctor/availability" class="dropdown-item">Availability</RouterLink></li>
              <li><RouterLink to="/doctor/analytics" class="dropdown-item">Analytics</RouterLink></li>
              <li><RouterLink to="/doctor/profile" class="dropdown-item">Profile</RouterLink></li>
            </ul>
          </li>

          <!-- Patient Menu -->
          <li v-if="authStore.isPatient" class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="patientMenu" role="button" data-bs-toggle="dropdown">
              Patient
            </a>
            <ul class="dropdown-menu" aria-labelledby="patientMenu">
              <li><RouterLink to="/patient/dashboard" class="dropdown-item">Dashboard</RouterLink></li>
              <li><RouterLink to="/patient/book-appointment" class="dropdown-item">Book Appointment</RouterLink></li>
              <li><RouterLink to="/patient/appointments" class="dropdown-item">My Appointments</RouterLink></li>
              <li><RouterLink to="/patient/history" class="dropdown-item">History</RouterLink></li>
              <li><RouterLink to="/patient/analytics" class="dropdown-item">Analytics</RouterLink></li>
              <li><RouterLink to="/patient/profile" class="dropdown-item">Profile</RouterLink></li>
            </ul>
          </li>

          <!-- Logout -->
          <li class="nav-item">
            <button @click="handleLogout" class="btn btn-outline-light ms-2">
              Logout
            </button>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}
</script>

<style scoped>
.navbar-brand {
  font-size: 1.5rem;
}

.nav-link {
  transition: color 0.3s ease;
}

.nav-link:hover {
  color: #fff !important;
}

.dropdown-menu {
  background-color: #0d47a1;
  border: none;
}

.dropdown-item {
  color: #fff;
  transition: background-color 0.3s ease;
}

.dropdown-item:hover {
  background-color: #1565c0;
  color: #fff;
}

.dropdown-item.router-link-active {
  background-color: #1565c0;
}
</style>