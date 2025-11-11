<template>
  <div>
    <h2>Doctors</h2>
    <table class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Email</th>
          <th>Department</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doctor in doctors" :key="doctor.id">
          <td>{{ doctor.id }}</td>
          <td>{{ doctor.full_name }}</td>
          <td>{{ doctor.email }}</td>
          <td>{{ doctor.department }}</td>
          <td>
            <button class="btn btn-sm btn-primary" @click="$emit('edit', doctor)">Edit</button>
            <button class="btn btn-sm btn-danger" @click="toggleStatus(doctor)">
              {{ doctor.is_active ? 'Deactivate' : 'Activate' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const doctors = ref([]);

const fetchDoctors = async () => {
  const response = await axios.get('http://localhost:5000/admin/doctor', {
    headers: { 'Authentication-Token': authStore.token },
  });
  doctors.value = response.data;
};

const toggleStatus = async (doctor) => {
  await axios.delete(`http://localhost:5000/admin/doctor/${doctor.id}`, {
    headers: { 'Authentication-Token': authStore.token },
  });
  fetchDoctors();
};

onMounted(fetchDoctors);
</script>
