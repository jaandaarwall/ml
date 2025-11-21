<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-5">
          <div class="card shadow-lg" style="border-radius: 12px;">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <h1 class="display-6 text-primary">🏥</h1>
                <h2 class="card-title mb-1">Hospital Management System</h2>
                <p class="text-muted">Sign in to your account</p>
              </div>

              <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ errorMessage }}
                <button type="button" class="btn-close" @click="errorMessage = ''"></button>
              </div>

              <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                {{ successMessage }}
                <button type="button" class="btn-close" @click="successMessage = ''"></button>
              </div>

              <form @submit.prevent="handleLogin">
                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="credentials.email"
                    placeholder="Enter your email"
                    required
                  >
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    v-model="credentials.password"
                    placeholder="Enter your password"
                    required
                  >
                </div>

                <button 
                  type="submit" 
                  class="btn btn-primary w-100 py-2 fw-bold mb-3"
                  :disabled="isLoading"
                >
                  <span v-if="!isLoading">Sign In</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Signing in...
                  </span>
                </button>
              </form>

              <hr class="my-4">

              <p class="text-center text-muted">
                Don't have an account?
                <RouterLink to="/register" class="text-primary fw-bold text-decoration-none">
                  Sign up here
                </RouterLink>
              </p>

              <div class="mt-4 p-3" style="background-color: #f8f9fa; border-radius: 8px;">
                <p class="text-muted small mb-2"><strong>Demo Credentials:</strong></p>
                <p class="text-muted small mb-1">Admin: admin@hospital.com / admin123</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const credentials = ref({
  email: '',
  password: ''
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleLogin = async () => {
  if (!credentials.value.email || !credentials.value.password) {
    errorMessage.value = 'Please enter email and password'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await authStore.login(credentials.value.email, credentials.value.password)
    successMessage.value = 'Login successful! Redirecting...'

    // Redirect based on role
    setTimeout(() => {
      if (authStore.isAdmin) {
        router.push('/admin/dashboard')
      } else if (authStore.isDoctor) {
        router.push('/doctor/dashboard')
      } else {
        router.push('/patient/dashboard')
      }
    }, 500)
  } catch (error) {
    errorMessage.value = error.message || 'Login failed. Please check your credentials.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.min-vh-100 {
  min-height: 100vh;
}

.card {
  border: none;
}

.display-6 {
  font-size: 4rem;
}
</style>