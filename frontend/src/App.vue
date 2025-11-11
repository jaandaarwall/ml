<template>
  <Navbar />
  <div class="container mt-4">
    <router-view />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
</script>

<style>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
