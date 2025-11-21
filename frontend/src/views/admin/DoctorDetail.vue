<!-- views/admin/DoctorDetail.vue -->
<template>
  <div class="container-fluid">
    <div class="page-header">
      <h1>👨‍⚕️ Doctor Details</h1>
    </div>
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-else class="row">
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header">Doctor Information</div>
          <div class="card-body">
            <p><strong>Name:</strong> {{ doctor.name }}</p>
            <p><strong>Email:</strong> {{ doctor.email }}</p>
            <p><strong>Phone:</strong> {{ doctor.phone }}</p>
            <p><strong>Department:</strong> {{ doctor.department }}</p>
            <p><strong>Qualification:</strong> {{ doctor.qualification }}</p>
            <p><strong>Experience:</strong> {{ doctor.experience_years }} years</p>
            <p><strong>Status:</strong> <span :class="doctor.is_active ? 'text-success' : 'text-danger'">{{ doctor.is_active ? 'Active' : 'Inactive' }}</span></p>
          </div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card">
          <div class="card-header">Statistics</div>
          <div class="card-body">
            <p><strong>Total Appointments:</strong> {{ doctor.appointments_count }}</p>
            <RouterLink to="/admin/doctors" class="btn btn-primary mt-3">Back to Doctors</RouterLink>
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
const doctor = ref({})
onMounted(async () => {
  try {
    const response = await adminAPI.getDoctorDetail(route.params.id)
    doctor.value = response.doctor
    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
})
</script>
