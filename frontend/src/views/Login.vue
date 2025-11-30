<template>
  <div class="login-container">
    <div class="row g-0 h-100">
      <div class="col-lg-6 d-none d-lg-flex flex-column align-items-center justify-content-center bg-primary text-white p-5 position-relative overflow-hidden">
        <div class="bg-overlay"></div>
        <div class="position-relative z-1 text-center">
          <div class="mb-4 display-1">🏥</div>
          <h1 class="fw-bold mb-3">We Care About You</h1>
          <p class="lead mb-4">Streamline your hospital experience with our advanced management system.</p>
        </div>
        <div class="circle circle-1"></div>
        <div class="circle circle-2"></div>
      </div>

      <div class="col-lg-6 d-flex align-items-center justify-content-center bg-white">
        <div class="login-form-wrapper p-5 w-100">
          <div class="text-center mb-5 d-lg-none">
            <h1 class="text-primary">🏥 HMS</h1>
          </div>
          
          <div class="mb-4">
            <h2 class="fw-bold text-dark">Welcome Back!</h2>
            <p class="text-muted">Please enter your details to sign in.</p>
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
              <label class="form-label fw-bold text-secondary small">EMAIL ADDRESS</label>
              <input 
                type="email" 
                class="form-control form-control-lg" 
                v-model="credentials.email"
                placeholder="name@example.com"
                required
              >
            </div>

            <div class="mb-2">
              <label class="form-label fw-bold text-secondary small">PASSWORD</label>
              <input 
                type="password" 
                class="form-control form-control-lg" 
                v-model="credentials.password"
                placeholder="••••••••"
                required
              >
            </div>
            
            <div class="d-flex justify-content-end mb-4">
              <RouterLink to="/forgot-password" class="text-decoration-none small text-muted fw-bold">
                Forgot Password?
              </RouterLink>
            </div>

            <button 
              type="submit" 
              class="btn btn-primary w-100 btn-lg mb-4"
              :disabled="isLoading"
            >
              <span v-if="!isLoading">Sign In</span>
              <span v-else>
                <span class="spinner-border spinner-border-sm me-2"></span>
                Signing in...
              </span>
            </button>

            <p class="text-center text-muted">
              Don't have an account? 
              <RouterLink to="/register" class="text-primary fw-bold text-decoration-none">Sign up</RouterLink>
            </p>
            
            <p class="text-center mt-2">
              <RouterLink to="/" class="text-secondary small text-decoration-none">← Back to Home</RouterLink>
            </p>
          </form>
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

const credentials = ref({ email: '', password: '' })
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    await authStore.login(credentials.value.email, credentials.value.password)
    successMessage.value = 'Login successful! Redirecting...'
    setTimeout(() => {
      if (authStore.isAdmin) router.push('/admin/dashboard')
      else if (authStore.isDoctor) router.push('/doctor/dashboard')
      else router.push('/patient/dashboard')
    }, 500)
  } catch (error) {
    errorMessage.value = error.message || 'Invalid credentials'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  overflow: hidden;
}
.login-form-wrapper {
  max-width: 500px;
}
.bg-overlay {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(135deg, rgba(0,168,150,0.9) 0%, rgba(2,128,115,0.95) 100%);
  z-index: 0;
}
.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255,255,255,0.1);
}
.circle-1 { width: 300px; height: 300px; top: -50px; left: -50px; }
.circle-2 { width: 400px; height: 400px; bottom: -100px; right: -100px; }
</style>