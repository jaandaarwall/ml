<!-- views/admin/PatientDetail.vue -->
<template>
  <div class="container-fluid">
    <div class="page-header">
      <h1>👤 Patient Details</h1>
    </div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else class="row">
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header">Patient Information</div>
          <div class="card-body">
            <p><strong>Name:</strong> {{ patient.name }}</p>
            <p><strong>Email:</strong> {{ patient.email }}</p>
            <p><strong>Phone:</strong> {{ patient.phone }}</p>
            <p><strong>Blood Group:</strong> {{ patient.blood_group }}</p>
            <p><strong>Gender:</strong> {{ patient.gender }}</p>
            <p><strong>DOB:</strong> {{ patient.dob }}</p>
          </div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header">Appointments</div>
          <div class="card-body">
            <div v-if="appointments.length === 0" class="text-muted">No appointments</div>
            <table v-else class="table table-sm">
              <thead>
                <tr>
                  <th>Doctor</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="apt in appointments" :key="apt.id">
                  <td>{{ apt.doctor_name }}</td>
                  <td>{{ apt.date }}</td>
                  <td>{{ apt.time }}</td>
                  <td><span class="badge bg-info">{{ apt.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { adminAPI } from '../../services/api'
const route = useRoute()
const loading = ref(true)
const error = ref('')
const patient = ref({})
const appointments = ref([])
onMounted(async () => {
  try {
    const response = await adminAPI.getPatientDetail(route.params.id)
    patient.value = response.patient
    appointments.value = response.appointments
    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
})
</script>
