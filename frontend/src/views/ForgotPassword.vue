<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-5">
          <div class="card shadow-lg border-0 rounded-4">
            <div class="card-body p-5">
              <div class="text-center mb-4">
                <div class="bg-primary bg-opacity-10 text-primary rounded-circle mx-auto d-flex align-items-center justify-content-center mb-3" style="width: 70px; height: 70px; font-size: 2rem;">
                  🔒
                </div>
                <h3 class="fw-bold text-dark">Forgot Password?</h3>
                <p class="text-muted">Enter your email address to receive a temporary password.</p>
              </div>

              <div v-if="successMessage" class="alert alert-success text-center py-3" role="alert">
                <div class="fs-1 mb-2">✉️</div>
                <strong>Check your email!</strong><br>
                {{ successMessage }}
                <div class="mt-3">
                  <RouterLink to="/login" class="btn btn-sm btn-success fw-bold px-4">Login Now</RouterLink>
                </div>
              </div>

              <div v-else>
                <form @submit.prevent="handleReset">
                  <div class="mb-4">
                    <label class="form-label fw-bold text-secondary small">EMAIL ADDRESS</label>
                    <input 
                      type="email" 
                      class="form-control form-control-lg" 
                      v-model="email"
                      placeholder="name@example.com"
                      required
                    >
                  </div>

                  <button 
                    type="submit" 
                    class="btn btn-primary w-100 btn-lg mb-4"
                    :disabled="isLoading"
                  >
                    <span v-if="!isLoading">Send Temporary Password</span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Sending...
                    </span>
                  </button>
                </form>
              </div>
              
              <div v-if="errorMessage" class="alert alert-danger text-center">
                {{ errorMessage }}
              </div>

              <div class="text-center border-top pt-3">
                <RouterLink to="/login" class="text-decoration-none d-flex align-items-center justify-content-center fw-bold text-secondary">
                  <span class="me-2">←</span> Back to Login
                </RouterLink>
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
import { authAPI } from '../services/api'

const email = ref('')
const isLoading = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const handleReset = async () => {
  if (!email.value) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authAPI.forgotPassword(email.value)
    successMessage.value = response.message
  } catch (err) {
    errorMessage.value = err.message || 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>