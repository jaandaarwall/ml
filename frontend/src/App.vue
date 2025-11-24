<template>
  <div id="app" class="d-flex flex-column vh-100">
    <div class="flex-shrink-0">
      <Navbar v-if="authStore.isAuthenticated" />
    </div>
    <main class="flex-grow-1 overflow-hidden">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import Navbar from './components/Navbar.vue'

const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  if (authStore.isAuthenticated && router.currentRoute.value.path === '/') {
    if (authStore.isAdmin) {
      router.push('/admin/dashboard')
    } else if (authStore.isDoctor) {
      router.push('/doctor/dashboard')
    } else {
      router.push('/patient/dashboard')
    }
  }
})
</script>

<style scoped>
main {
  background-color: #f8f9fa;
  position: relative;
}
</style>