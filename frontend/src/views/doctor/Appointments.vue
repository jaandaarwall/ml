<!-- views/doctor/Appointments.vue -->
<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar (Keep existing sidebar code) -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
      <!-- ... existing sidebar links ... -->
      <div class="nav flex-column gap-2">
        <RouterLink to="/doctor/dashboard" class="nav-link text-white">
          <span class="me-2">📊</span>Dashboard
        </RouterLink>
        <RouterLink to="/doctor/appointments" class="nav-link text-white active">
          <span class="me-2">📅</span>My Appointments
        </RouterLink>
        <RouterLink to="/doctor/patients" class="nav-link text-white">
          <span class="me-2">👥</span>My Patients
        </RouterLink>
        <RouterLink to="/doctor/availability" class="nav-link text-white">
          <span class="me-2">⏰</span>Set Availability
        </RouterLink>
        <RouterLink to="/doctor/profile" class="nav-link text-white">
          <span class="me-2">👤</span>My Profile
        </RouterLink>
        <RouterLink to="/doctor/analytics" class="nav-link text-white">
          <span class="me-2">📈</span>Analytics
        </RouterLink>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h2 class="mb-1">📅 My Appointments</h2>
          <p class="text-muted mb-0">View and manage all your appointments.</p>
        </div>
        <div class="d-flex gap-2">
          <!-- Sorting Dropdown -->
          <select v-model="sortOrder" class="form-select" style="width: 150px;">
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
          <button class="btn btn-primary" @click="showExportModal = true">
            📥 Export CSV
          </button>
        </div>
      </div>

      <div class="container-fluid px-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else class="card">
          <div class="card-body">
            <div v-if="sortedAppointments.length === 0" class="text-center py-5 text-muted">
              <p>No appointments found</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in sortedAppointments" :key="apt.id">
                    <td><strong>{{ apt.date }}</strong></td>
                    <td>{{ apt.time }}</td>
                    <td>{{ apt.patient_name }}</td>
                    <td>
                      <span :class="['badge', getStatusClass(apt.status)]">{{ apt.status }}</span>
                    </td>
                    <td>
                      <div class="btn-group">
                        <!-- Treatment Button -->
                        <RouterLink v-if="apt.status === 'Booked'" 
                          :to="`/doctor/appointment/${apt.id}/treatment`"
                          class="btn btn-sm btn-success">
                          ✏️ Treatment
                        </RouterLink>
                        
                        <!-- Patient Detail Button -->
                        <button @click="openPatientDetails(apt.patient_id, apt.patient_name)" 
                                class="btn btn-sm btn-info text-white">
                          👤 Patient Detail
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient Details Modal -->
    <div v-if="showPatientModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-info text-white">
            <h5 class="modal-title">Patient History: {{ selectedPatientName }}</h5>
            <button type="button" class="btn-close" @click="showPatientModal = false"></button>
          </div>
          <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
            <div v-if="loadingHistory" class="text-center">
              <div class="spinner-border text-info"></div>
            </div>
            <div v-else-if="patientHistory.length === 0" class="alert alert-warning">
              No previous treatment history found for this patient.
            </div>
            <div v-else>
              <div v-for="(record, index) in patientHistory" :key="index" class="card mb-3 border">
                <div class="card-header bg-light d-flex justify-content-between align-items-center">
                  <strong>📅 {{ record.date }}</strong>
                  <button class="btn btn-sm btn-outline-primary" @click="toggleDiagnosis(index)">
                    {{ record.showDetails ? 'Hide' : 'Show' }} Diagnosis
                  </button>
                </div>
                <div v-if="record.showDetails" class="card-body">
                  <p><strong>📋 Diagnosis:</strong> {{ record.diagnosis }}</p>
                  <p><strong>💊 Prescription:</strong> {{ record.prescription }}</p>
                  <p class="mb-0"><strong>📝 Notes:</strong> {{ record.notes }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Export Modal (Keep existing) -->
    <div v-if="showExportModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Export My Appointments</h5>
            <button type="button" class="btn-close" @click="showExportModal = false"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <label class="form-label">Start Date</label>
              <input v-model="exportDates.start" type="date" class="form-control">
            </div>
            <div class="mb-3">
              <label class="form-label">End Date</label>
              <input v-model="exportDates.end" type="date" class="form-control">
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showExportModal = false">Cancel</button>
            <button type="button" class="btn btn-primary" @click="handleExport">Generate & Download</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const appointments = ref([])
const sortOrder = ref('desc')

// Patient Detail Modal State
const showPatientModal = ref(false)
const loadingHistory = ref(false)
const patientHistory = ref([])
const selectedPatientName = ref('')

// Export State
const exporting = ref(false)
const showExportModal = ref(false)
const exportDates = ref({ start: '', end: '' })

const sortedAppointments = computed(() => {
  return [...appointments.value].sort((a, b) => {
    const dateA = new Date(`${a.date} ${a.time}`)
    const dateB = new Date(`${b.date} ${b.time}`)
    return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
})

const getStatusClass = (status) => {
  const classes = { 'Booked': 'bg-info', 'Completed': 'bg-success', 'Cancelled': 'bg-danger' }
  return classes[status] || 'bg-secondary'
}

const openPatientDetails = async (patientId, patientName) => {
  selectedPatientName.value = patientName
  showPatientModal.value = true
  loadingHistory.value = true
  patientHistory.value = []
  
  try {
    const response = await doctorAPI.getPatientHistory(patientId)
    // Add local state for toggling diagnosis visibility
    patientHistory.value = response.map(record => ({ ...record, showDetails: false }))
  } catch (err) {
    console.error("Failed to load history", err)
  } finally {
    loadingHistory.value = false
  }
}

const toggleDiagnosis = (index) => {
  patientHistory.value[index].showDetails = !patientHistory.value[index].showDetails
}

const handleExport = async () => {
  exporting.value = true
  showExportModal.value = false
  try {
    const res = await doctorAPI.exportAppointments(exportDates.value.start, exportDates.value.end)
    const taskId = res.task_id
    const interval = setInterval(async () => {
      try {
        const statusRes = await doctorAPI.getTaskStatus(taskId)
        if (statusRes.state === 'SUCCESS') {
          clearInterval(interval)
          exporting.value = false
          const blob = new Blob([statusRes.result.csv_data], { type: 'text/csv' })
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = statusRes.result.filename
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
        } else if (statusRes.state === 'FAILURE') {
          clearInterval(interval)
          exporting.value = false
          alert('Export failed: ' + statusRes.status)
        }
      } catch (err) {
        clearInterval(interval)
        exporting.value = false
        alert('Error checking export status')
      }
    }, 1000) 
  } catch (err) {
    exporting.value = false
    alert(err.message || 'Export failed')
  }
}

onMounted(async () => {
  try {
    const response = await doctorAPI.getAppointments()
    appointments.value = response
  } finally {
    loading.value = false
  }
})
</script>