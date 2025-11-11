<template>
  <div>
    <h2>Book Appointment with Dr. {{ doctor.full_name }}</h2>
    <form @submit.prevent="bookAppointment">
      <div class="mb-3">
        <label for="date" class="form-label">Date</label>
        <input type="date" class="form-control" id="date" v-model="form.appointment_date" required>
      </div>
      <div class="mb-3">
        <label for="time" class="form-label">Time</label>
        <input type="time" class="form-control" id="time" v-model="form.appointment_time" required>
      </div>
      <div class="mb-3">
        <label for="reason" class="form-label">Reason</label>
        <textarea class="form-control" id="reason" v-model="form.reason"></textarea>
      </div>
      <button type="submit" class="btn btn-primary">Book</button>
      <button type="button" class="btn btn-secondary" @click="$emit('cancel')">Cancel</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

const props = defineProps({
  doctor: Object,
});

const emit = defineEmits(['success', 'cancel']);

const authStore = useAuthStore();
const form = ref({
  doctor_id: props.doctor.id,
  appointment_date: '',
  appointment_time: '',
  reason: '',
});

const bookAppointment = async () => {
  await axios.post('http://localhost:5000/patient/appointment', form.value, {
    headers: { 'Authentication-Token': authStore.token },
  });
  emit('success');
};
</script>
