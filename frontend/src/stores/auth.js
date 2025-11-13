import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('authStore', () => {
  const auth_token = ref(localStorage.getItem('token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user')) || null)
  
  const isAuthenticated = computed(() => auth_token.value !== null)
  const userRoles = computed(() => user.value?.roles || [])
  const isAdmin = computed(() => userRoles.value.includes('admin'))
  const isDoctor = computed(() => userRoles.value.includes('doctor'))
  const isPatient = computed(() => userRoles.value.includes('user'))
  
  function setUserCred(token, userData) {
    localStorage.setItem('token', token)
    localStorage.setItem('user', JSON.stringify(userData))
    auth_token.value = token
    user.value = userData
  }
  
  function clearAuthToken() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    auth_token.value = null
    user.value = null
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
  
  function getAuthHeader() {
    return {
      'Authorization': `Bearer ${auth_token.value}`,
      'Content-Type': 'application/json'
    }
  }
  
  return {
    // Computed properties
    isAuthenticated,
    userRoles,
    isAdmin,
    isDoctor,
    isPatient,
    // Functions
    getAuthToken,
    getUserEmail,
    getUserRoles,
    getAuthHeader,
    setUserCred,
    clearAuthToken
  }
})