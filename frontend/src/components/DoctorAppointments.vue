<template>
  <div>
    <h2>My Appointments</h2>
    <table class="table">
      <thead>
        <tr>
          <th>Date</th>
          <th>Time</th>
          <th>Patient</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in appointments" :key="app.id">
          <td>{{ app.appointment_date }}</td>
          <td>{{ app.appointment_time }}</td>
          <td>{{ app.patient_name }}</td>
          <td>{{ app.status }}</td>
          <td>
            <button
              class="btn btn-sm btn-primary"
              v-if="app.status === 'Booked'"
              @click="showTreatmentForm = app.id"
            >
              Add Treatment
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showTreatmentForm" class="mt-4">
      <h3>Add Treatment</h3>
      <form @submit.prevent="addTreatment">
        <div class="mb-3">
          <label for="diagnosis" class="form-label">Diagnosis</label>
          <textarea class="form-control" id="diagnosis" v-model="treatmentForm.diagnosis" required></textarea>
        </div>
        <div class="mb-3">
          <label for="prescription" class="form-label">Prescription</label>
          <textarea class="form-control" id="prescription" v-model="treatmentForm.prescription" required></textarea>
        </div>
        <div class="mb-3">
          <label for="notes" class="form-label">Notes</label>
          <textarea class="form-control" id="notes" v-model="treatmentForm.notes"></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Submit</button>
        <button type="button" class="btn btn-secondary" @click="showTreatmentForm = null">Cancel</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

const authStore = useAuthStore();
const appointments = ref([]);
const showTreatmentForm = ref(null);
const treatmentForm = ref({
  diagnosis: '',
  prescription: '',
  notes: '',
});

const fetchAppointments = async () => {
  const response = await axios.get('http://localhost:5000/doctor/appointment', {
    headers: { 'Authentication-Token': authStore.token },
  });
  appointments.value = response.data;
};

const addTreatment = async () => {
  await axios.post('http://localhost:5000/doctor/treatment', {
    appointment_id: showTreatmentForm.value,
    ...treatmentForm.value,
  }, {
    headers: { 'Authentication-Token': authStore.token },
  });
  showTreatmentForm.value = null;
  fetchAppointments();
};

onMounted(fetchAppointments);
</script>
