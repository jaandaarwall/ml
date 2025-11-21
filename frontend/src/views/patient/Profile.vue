<!-- views/patient/Profile.vue -->
<template>
  <div class="d-flex" style="min-height: 100vh;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 250px; min-height: 100vh; overflow-y: auto;">
      <ul class="nav flex-column gap-2">
        <li class="nav-item">
          <RouterLink to="/patient/dashboard" class="nav-link text-white">
            <span>📊 Dashboard</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/book-appointment" class="nav-link text-white">
            <span>🔍 Find Doctors</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/appointments" class="nav-link text-white">
            <span>📅 My Appointments</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/history" class="nav-link text-white">
            <span>📋 Medical History</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/profile" class="nav-link text-white active">
            <span>👤 My Profile</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/analytics" class="nav-link text-white">
            <span>📈 Analytics</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4">
        <h1 class="mb-1">👤 My Profile</h1>
        <p class="text-muted mb-0">Update your personal information</p>
      </div>

      <!-- Content -->
      <div class="container-fluid px-4 pb-5">
        <div class="row">
          <div class="col-lg-6">
            <div class="card">
              <div class="card-body">
                <div v-if="loading" class="text-center py-5">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>

                <form v-else @submit.prevent="updateProfile">
                  <div v-if="successMessage" class="alert alert-success">
                    {{ successMessage }}
                  </div>
                  <div v-if="errorMessage" class="alert alert-danger">
                    {{ errorMessage }}
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Username</label>
                    <input v-model="profile.username" type="text" class="form-control">
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Email</label>
                    <input v-model="profile.email" type="email" class="form-control" disabled>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Phone</label>
                    <input v-model="profile.phone" type="tel" class="form-control">
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Date of Birth</label>
                    <input v-model="profile.date_of_birth" type="date" class="form-control">
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Gender</label>
                    <select v-model="profile.gender" class="form-select">
                      <option value="">Select Gender</option>
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Other">Other</option>
                    </select>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Blood Group</label>
                    <select v-model="profile.blood_group" class="form-select">
                      <option value="">Select Blood Group</option>
                      <option value="A+">A+</option>
                      <option value="A-">A-</option>
                      <option value="B+">B+</option>
                      <option value="B-">B-</option>
                      <option value="O+">O+</option>
                      <option value="O-">O-</option>
                      <option value="AB+">AB+</option>
                      <option value="AB-">AB-</option>
                    </select>
                  </div>

                  <div class="mb-3">
                    <label class="form-label fw-bold">Address</label>
                    <textarea v-model="profile.address" class="form-control" rows="3"></textarea>
                  </div>

                  <button type="submit" class="btn btn-primary w-100" :disabled="updating">
                    {{ updating ? 'Updating...' : '💾 Save Changes' }}
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
import { patientAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const updating = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const profile = ref({
  username: '',
  email: '',
  phone: '',
  date_of_birth: '',
  gender: '',
  blood_group: '',
  address: ''
})

const fetchProfile = async () => {
  try {
    const response = await patientAPI.getProfile()
    profile.value = response
  } catch (err) {
    errorMessage.value = err.message || 'Failed to load profile'
  } finally {
    loading.value = false
  }
}

const updateProfile = async () => {
  updating.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    await patientAPI.updateProfile(profile.value)
    successMessage.value = 'Profile updated successfully!'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)
  } catch (err) {
    errorMessage.value = err.message || 'Failed to update profile'
  } finally {
    updating.value = false
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

onMounted(fetchProfile)
</script>

<style scoped>
.nav-link {
  padding: 10px 15px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
  border-left: 4px solid #fbbf24;
}
</style>