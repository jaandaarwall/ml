<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router';
import { useMessageStore } from '@/stores/counter.js';
import { useAuthStore } from '@/stores/auth.js';
import { computed } from 'vue';

const router = useRouter();
const message_store = useMessageStore();
const auth_store = useAuthStore();

const ErrorMessages = computed(() => message_store.errorMessages);
const userEmail = computed(() => auth_store.getUserEmail());
const isAuthenticated = computed(() => auth_store.isAuthenticated);

// async function logout() {
//   try {
//     const response = await fetch('http://127.0.0.1:5000/api/logout', {
//       method: 'POST',
//       headers: auth_store.getAuthHeader()
//     });
    
//     if (response.ok) {
//       auth_store.clearAuthToken();
//       message_store.updateErrorMessages('You have been logged out successfully.');
//       router.push('/login');
//     }
//   } catch (error) {
//     auth_store.clearAuthToken();
//     message_store.updateErrorMessages('Logged out.');
//     router.push('/login');
//   }
// }

function logout() {
  // Sent a fetch request to the backend to log out the user

  auth_store.clearAuthToken();
  message_store.updateErrorMessages('You have been logged out successfully.');
}

</script>

<template>
<div class="container-fluid">
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">Hospital Management</RouterLink>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li class="nav-item" v-if="!isAuthenticated">
            <RouterLink class="nav-link" to="/login">Login</RouterLink>
          </li>
          <li class="nav-item" v-if="!isAuthenticated">
            <RouterLink class="nav-link" to="/register">Register</RouterLink>
          </li>

          <li class="nav-item" v-if="isAuthenticated">
            <span class="nav-link">Welcome, {{ userEmail }}</span>
          </li>
          <li class="nav-item" v-if="isAuthenticated">
            <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
          </li>
        </ul>
      </div>
    </div>
  </nav>

  <div class="container-fluid" v-if="ErrorMessages">
    <div class="alert alert-info alert-dismissible fade show mt-3" role="alert">
      {{ ErrorMessages }}
      <button type="button" class="btn-close" @click="message_store.updateErrorMessages(null)"></button>
    </div>
  </div>

  <RouterView />
</div>
</template>