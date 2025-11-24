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
            <div v-else class="table-responsive">
              <table class="table table-sm table-hover">
                <thead>
                  <tr>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Diagnosis</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in appointments" :key="apt.id">
                    <td>{{ apt.doctor_name }}</td>
                    <td>{{ apt.date }}</td>
                    <td><span :class="['badge', getStatusClass(apt.status)]">{{ apt.status }}</span></td>
                    <td>
                      <button v-if="apt.diagnosis" class="btn btn-sm btn-info text-white" @click="showDiagnosis(apt)">
                        👁️ View Treatment
                      </button>
                      <span v-else class="text-muted">-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Treatment Detail Modal -->
    <div v-if="selectedTreatment" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title">Treatment Details</h5>
            <button type="button" class="btn-close" @click="selectedTreatment = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <h6 class="fw-bold text-primary">📋 Diagnosis:</h6>
              <p class="bg-light p-2 rounded border">{{ selectedTreatment.diagnosis || 'N/A' }}</p>
            </div>
            <div class="mb-3">
              <h6 class="fw-bold text-success">💊 Prescription:</h6>
              <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedTreatment.prescription || 'N/A' }}</p>
            </div>
            <div>
              <h6 class="fw-bold text-secondary">📝 Doctor's Notes:</h6>
              <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedTreatment.notes || 'N/A' }}</p>
            </div>
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
const selectedTreatment = ref(null)

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-info',
    'Completed': 'bg-success',
    'Cancelled': 'bg-danger'
  }
  return classes[status] || 'bg-secondary'
}

const showDiagnosis = (apt) => {
  selectedTreatment.value = {
    diagnosis: apt.diagnosis,
    prescription: apt.prescription,
    notes: apt.notes
  }
}

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