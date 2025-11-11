<template>
  <div>
    <h2>Search Doctors</h2>
    <form @submit.prevent="searchDoctors" class="mb-3">
      <div class="input-group">
        <input type="text" class="form-control" placeholder="Search by name or department" v-model="query">
        <button class="btn btn-outline-secondary" type="submit">Search</button>
      </div>
    </form>
    <ul class="list-group">
      <li class="list-group-item" v-for="doctor in doctors" :key="doctor.id">
        {{ doctor.full_name }} ({{ doctor.department }})
        <button class="btn btn-sm btn-primary float-end" @click="$emit('book', doctor)">Book</button>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const query = ref('');
const doctors = ref([]);

const searchDoctors = async () => {
  const response = await axios.get(`http://localhost:5000/search?q=${query.value}`, {
    headers: { 'Authentication-Token': authStore.token },
  });
  doctors.value = response.data.doctors;
};
</script>
