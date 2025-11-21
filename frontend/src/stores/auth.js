import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const authToken = ref(localStorage.getItem('authToken'))
  const isAuthenticated = computed(() => !!authToken.value)

  const login = async (email, password) => {
    const response = await authAPI.login(email, password)
    authToken.value = response.user_details.auth_token
    user.value = {
      email: response.user_details.email,
      roles: response.user_details.roles
    }
    localStorage.setItem('authToken', authToken.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    return response
  }

  const register = async (username, email, password) => {
    const response = await authAPI.register(username, email, password)
    return response
  }

  const logout = async () => {
    await authAPI.logout()
    user.value = null
    authToken.value = null
    localStorage.removeItem('authToken')
    localStorage.removeItem('user')
  }

  const hasRole = (role) => {
    return user.value?.roles?.includes(role) || false
  }

  const isAdmin = computed(() => hasRole('admin'))
  const isDoctor = computed(() => hasRole('doctor'))
  const isPatient = computed(() => hasRole('user'))

  const checkEmail = async (email) => {
    return await authAPI.checkEmail(email)
  }

  // Initialize from localStorage
  if (localStorage.getItem('user')) {
    user.value = JSON.parse(localStorage.getItem('user'))
  }

  return {
    user,
    authToken,
    isAuthenticated,
    login,
    register,
    logout,
    hasRole,
    isAdmin,
    isDoctor,
    isPatient,
    checkEmail
  }
})