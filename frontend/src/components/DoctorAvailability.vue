<template>
  <div>
    <h2>My Availability</h2>
    <form @submit.prevent="addAvailability" class="mb-3">
      <div class="row">
        <div class="col">
          <input type="date" class="form-control" v-model="form.date" required>
        </div>
        <div class="col">
          <input type="time" class="form-control" v-model="form.start_time" required>
        </div>
        <div class="col">
          <input type="time" class="form-control" v-model="form.end_time" required>
        </div>
        <div class="col">
          <input type="number" class="form-control" placeholder="Total Seats" v-model.number="form.total_seats" required>
        </div>
        <div class="col">
          <button type="submit" class="btn btn-primary">Add</button>
        </div>
      </div>
    </form>

    <table class="table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Start Time</th>
          <th>End Time</th>
          <th>Seats</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="avail in availabilities" :key="avail.id">
          <td>{{ avail.date }}</td>
          <td>{{ avail.start_time }}</td>
          <td>{{ avail.end_time }}</td>
          <td>{{ avail.total_seats }}</td>
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
const availabilities = ref([]);
const form = ref({
  date: '',
  start_time: '',
  end_time: '',
  total_seats: 1,
});

const fetchAvailability = async () => {
  const response = await axios.get('http://localhost:5000/doctor/availability', {
    headers: { 'Authentication-Token': authStore.token },
  });
  availabilities.value = response.data;
};

const addAvailability = async () => {
  await axios.post('http://localhost:5000/doctor/availability', form.value, {
    headers: { 'Authentication-Token': authStore.token },
  });
  fetchAvailability();
};

onMounted(fetchAvailability);
</script>
