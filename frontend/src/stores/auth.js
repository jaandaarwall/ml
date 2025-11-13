
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('authStore', () => {
  const router = useRouter()
  const auth_token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  const isAuthenticated = computed(() => auth_token.value !== null)

  function setUserCred(token, userCreds) {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userCreds))
    auth_token.value = token
    user.value = userCreds
    
    // Redirect based on role
    const roles = userCreds.roles || []
    if (roles.includes('admin')) {
      router.push('/admin/dashboard')
    } else if (roles.includes('doctor')) {
      router.push('/doctor/dashboard')
    } else {
      router.push('/patient/dashboard')
    }
  }

  function clearAuthToken() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    auth_token.value = null
    user.value = null
    router.push('/login')
  }

  function getAuthToken() {
    return auth_token.value
  }

  function getUserEmail() {
    return user.value ? user.value.email : null
  }

  function getUserRoles() {
    return user.value ? user.value.roles : []
  }

  return {
    isAuthenticated,
    getAuthToken,
    getUserEmail,
    getUserRoles,
    setUserCred,
    clearAuthToken
  }
})
