<!-- views/doctor/Profile.vue -->
<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
      <div class="nav flex-column gap-2">
        <RouterLink to="/doctor/dashboard" class="nav-link text-white">
          <span class="me-2">📊</span>Dashboard
        </RouterLink>
        <RouterLink to="/doctor/appointments" class="nav-link text-white">
          <span class="me-2">📅</span>My Appointments
        </RouterLink>
        <RouterLink to="/doctor/patients" class="nav-link text-white">
          <span class="me-2">👥</span>My Patients
        </RouterLink>
        <RouterLink to="/doctor/availability" class="nav-link text-white">
          <span class="me-2">⏰</span>Set Availability
        </RouterLink>
        <RouterLink to="/doctor/profile" class="nav-link text-white active">
          <span class="me-2">👤</span>My Profile
        </RouterLink>
        <RouterLink to="/doctor/analytics" class="nav-link text-white">
          <span class="me-2">📈</span>Analytics
        </RouterLink>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4">
        <h2 class="mb-1">👤 My Profile</h2>
        <p class="text-muted mb-0">Update your personal and professional information.</p>
      </div>

      <div class="container-fluid px-4">
        <div class="row">
          <div class="col-lg-8">
            <div class="card">
              <div class="card-body">
                <form @submit.prevent="updateProfile">
                  <div class="row mb-3">
                    <div class="col-md-6">
                      <label class="form-label">Full Name</label>
                      <input v-model="profile.username" type="text" class="form-control">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label">Email Address</label>
                      <input v-model="profile.email" type="email" class="form-control" disabled>
                    </div>
                  </div>

                  <div class="row mb-3">
                    <div class="col-md-6">
                      <label class="form-label">Phone Number</label>
                      <input v-model="profile.phone" type="tel" class="form-control">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label">Department</label>
                      <input v-model="profile.department" type="text" class="form-control" disabled>
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Qualification</label>
                    <input v-model="profile.qualification" type="text" class="form-control">
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Years of Experience</label>
                    <input v-model.number="profile.experience_years" type="number" class="form-control">
                  </div>

                  <button type="submit" class="btn btn-primary">
                    💾 Save Changes
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const profile = ref({
  username: '',
  email: '',
  phone: '',
  department: '',
  qualification: '',
  experience_years: 0
})

const updateProfile = async () => {
  try {
    await doctorAPI.updateProfile(profile.value)
    alert('Profile updated successfully')
  } catch (err) {
    alert(err.message)
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

onMounted(async () => {
  try {
    const response = await doctorAPI.getProfile()
    profile.value = response
  } finally {
    loading.value = false
  }
})
</script>

<style>
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-left: 4px solid #ffc107;
  padding-left: calc(1rem - 4px) !important;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>