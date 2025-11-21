<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6">
          <div class="card shadow-lg" style="border-radius: 12px;">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <h1 class="display-6 text-primary">🏥</h1>
                <h2 class="card-title mb-1">Create Account</h2>
                <p class="text-muted">Join our hospital management system</p>
              </div>

              <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show" role="alert">
                {{ errorMessage }}
                <button type="button" class="btn-close" @click="errorMessage = ''"></button>
              </div>

              <div v-if="successMessage" class="alert alert-success alert-dismissible fade show" role="alert">
                {{ successMessage }}
              </div>

              <form @submit.prevent="handleRegister">
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="username" 
                    v-model="formData.username"
                    placeholder="Choose a username"
                    required
                  >
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    id="email" 
                    v-model="formData.email"
                    placeholder="Enter your email"
                    @blur="checkEmail"
                    required
                  >
                  <small v-if="emailChecking" class="text-muted">Checking availability...</small>
                  <small v-else-if="emailAvailable !== null" :class="emailAvailable ? 'text-success' : 'text-danger'">
                    {{ emailAvailable ? '✓ Email available' : '✗ Email already in use' }}
                  </small>
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="password" 
                    v-model="formData.password"
                    placeholder="Enter a strong password"
                    minlength="6"
                    required
                  >
                  <small class="text-muted">Minimum 6 characters</small>
                </div>

                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input 
                    type="password" 
                    class="form-control" 
                    id="confirmPassword" 
                    v-model="formData.confirmPassword"
                    placeholder="Confirm your password"
                    required
                  >
                </div>

                <div class="form-check mb-3">
                  <input 
                    class="form-check-input" 
                    type="checkbox" 
                    id="agree" 
                    v-model="formData.agree"
                    required
                  >
                  <label class="form-check-label" for="agree">
                    I agree to the terms and conditions
                  </label>
                </div>

                <button 
                  type="submit" 
                  class="btn btn-primary w-100 py-2 fw-bold mb-3"
                  :disabled="isLoading || !emailAvailable"
                >
                  <span v-if="!isLoading">Create Account</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Creating account...
                  </span>
                </button>
              </form>

              <hr class="my-4">

              <p class="text-center text-muted">
                Already have an account?
                <RouterLink to="/login" class="text-primary fw-bold text-decoration-none">
                  Sign in here
                </RouterLink>
              </p>
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

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  agree: false
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const emailChecking = ref(false)
const emailAvailable = ref(null)

const checkEmail = async () => {
  if (!formData.value.email) return

  emailChecking.value = true
  try {
    const response = await authStore.checkEmail(formData.value.email)
    emailAvailable.value = response.available
  } catch (error) {
    console.error('Email check error:', error)
  } finally {
    emailChecking.value = false
  }
}

const handleRegister = async () => {
  // Validation
  if (!formData.value.username || !formData.value.email || !formData.value.password) {
    errorMessage.value = 'Please fill in all fields'
    return
  }

  if (formData.value.password !== formData.value.confirmPassword) {
    errorMessage.value = 'Passwords do not match'
    return
  }

  if (formData.value.password.length < 6) {
    errorMessage.value = 'Password must be at least 6 characters'
    return
  }

  if (!emailAvailable.value) {
    errorMessage.value = 'Email is not available'
    return
  }

  if (!formData.value.agree) {
    errorMessage.value = 'You must agree to the terms and conditions'
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    await authStore.register(formData.value.username, formData.value.email, formData.value.password)
    successMessage.value = 'Registration successful! Redirecting to login...'

    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (error) {
    errorMessage.value = error.message || 'Registration failed. Please try again.'
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