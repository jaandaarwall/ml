<template>
  <div id="app">
    <Navbar v-if="authStore.isAuthenticated" />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'

const authStore = useAuthStore()
const router = useRouter()

// Redirect to appropriate dashboard on app load
if (authStore.isAuthenticated && router.currentRoute.value.path === '/') {
  if (authStore.isAdmin) {
    router.push('/admin/dashboard')
  } else if (authStore.isDoctor) {
    router.push('/doctor/dashboard')
  } else {
    router.push('/patient/dashboard')
  }
}
</script>

<style scoped>
main {
  min-height: 100vh;
  background-color: #f8f9fa;
}
</style>