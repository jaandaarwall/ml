<template>
  <div>
    <h2>My Appointments</h2>
    <table class="table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Time</th>
          <th>Doctor</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in appointments" :key="app.id">
          <td>{{ app.appointment_date }}</td>
          <td>{{ app.appointment_time }}</td>
          <td>{{ app.doctor_name }}</td>
          <td>{{ app.status }}</td>
          <td>
            <button
              class="btn btn-sm btn-danger"
              v-if="app.status === 'Booked'"
              @click="cancelAppointment(app.id)"
            >
              Cancel
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
const appointments = ref([]);

const fetchAppointments = async () => {
  const response = await axios.get('http://localhost:5000/patient/appointment', {
    headers: { 'Authentication-Token': authStore.token },
  });
  appointments.value = response.data;
};

const cancelAppointment = async (appointmentId) => {
  await axios.put(`http://localhost:5000/patient/appointment/${appointmentId}`, {
    status: 'Cancelled'
  }, {
    headers: { 'Authentication-Token': authStore.token },
  });
  fetchAppointments();
};

onMounted(fetchAppointments);
</script>
