<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Main Content -->
    <div class="flex-grow-1">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h2 class="mb-1">📋 Patient History</h2>
          <p v-if="patient.name" class="text-muted mb-0">Medical records for {{ patient.name }}</p>
        </div>
        <RouterLink to="/doctor/patients" class="btn btn-outline-secondary">
          ← Back to Patients
        </RouterLink>
      </div>

      <div class="container-fluid px-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else>
          <!-- Patient Info Card -->
          <div class="card mb-4 border-info">
            <div class="card-header bg-light text-info fw-bold">
              👤 Patient Details
            </div>
            <div class="card-body">
              <div class="row">
                <div class="col-md-6">
                  <p class="mb-2"><strong>Name:</strong> {{ patient.name }}</p>
                  <p class="mb-2"><strong>Age:</strong> {{ patient.age || 'N/A' }} ({{ patient.gender || 'N/A' }})</p>
                </div>
                <div class="col-md-6">
                   <p class="mb-2"><strong>Blood Group:</strong> <span class="badge bg-danger">{{ patient.blood_group || 'N/A' }}</span></p>
                   <p class="mb-2"><strong>Phone:</strong> {{ patient.phone || 'N/A' }}</p>
                   <p class="mb-0"><strong>Email:</strong> {{ patient.email }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- History Records -->
          <div v-if="history.length === 0" class="alert alert-info text-center py-4">
            No medical history records found for this patient.
          </div>
          
          <div v-else>
            <div v-for="(record, index) in history" :key="index" class="card mb-3 shadow-sm border-0">
              <div class="card-header bg-white border-bottom d-flex justify-content-between align-items-center">
                <div>
                  <h6 class="mb-0 fw-bold">📅 {{ record.date }}</h6>
                </div>
                <span class="badge bg-light text-dark border">Dr. {{ record.doctor_name }}</span>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label class="text-muted small text-uppercase fw-bold mb-1">Diagnosis</label>
                    <p class="fw-medium bg-light p-2 rounded">{{ record.diagnosis }}</p>
                  </div>
                  <div class="col-md-6 mb-3">
                     <label class="text-muted small text-uppercase fw-bold mb-1">Prescription</label>
                     <p class="bg-light p-2 rounded" style="white-space: pre-line;">{{ record.prescription }}</p>
                  </div>
                  <div class="col-12" v-if="record.notes">
                     <label class="text-muted small text-uppercase fw-bold mb-1">Doctor's Notes</label>
                     <p class="text-muted fst-italic mb-0 border-start border-3 border-secondary ps-3">{{ record.notes }}</p>
                  </div>
                </div>
              </div>
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
import { doctorAPI } from '../../services/api'

const route = useRoute()
const loading = ref(true)
const history = ref([])
const patient = ref({})

onMounted(async () => {
  try {
    const response = await doctorAPI.getPatientHistory(route.params.id)
    // The API returns an object containing { patient: {}, history: [] }
    patient.value = response.patient || {}
    history.value = response.history || []
  } catch (err) {
    console.error("Failed to load history", err)
  } finally {
    loading.value = false
  }
})
</script>