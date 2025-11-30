<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
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

                  <hr class="my-4">
                  <h5 class="mb-3">Change Password</h5>
                  <div class="row mb-3">
                    <div class="col-md-6">
                      <label class="form-label">New Password</label>
                      <input v-model="passwords.new" type="password" class="form-control" placeholder="Leave blank to keep current">
                    </div>
                    <div class="col-md-6">
                      <label class="form-label">Confirm Password</label>
                      <input v-model="passwords.confirm" type="password" class="form-control">
                    </div>
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
const passwords = ref({ new: '', confirm: '' })

const updateProfile = async () => {
  const payload = { ...profile.value }
  
  if (passwords.value.new) {
    if (passwords.value.new !== passwords.value.confirm) {
      alert('Passwords do not match')
      return
    }
    if (passwords.value.new.length < 6) {
        alert('Password must be at least 6 characters')
        return
    }
    payload.password = passwords.value.new
  }

  try {
    await doctorAPI.updateProfile(payload)
    alert('Profile updated successfully')
    passwords.value = { new: '', confirm: '' }
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