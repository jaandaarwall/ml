<!-- views/doctor/Appointments.vue -->
<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
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
        <button class="btn btn-primary" @click="showExportModal = true" :disabled="exporting">
          <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
          <span v-if="exporting">Generating...</span>
          <span v-else>📥 Export CSV</span>
        </button>
      </div>

      <div class="container-fluid px-4">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else class="card">
          <div class="card-body">
            <div v-if="appointments.length === 0" class="text-center py-5 text-muted">
              <p>No appointments found</p>
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Patient</th>
                    <th>Reason</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="apt in appointments" :key="apt.id">
                    <td><strong>{{ apt.date }}</strong></td>
                    <td>{{ apt.time }}</td>
                    <td>{{ apt.patient_name }}</td>
                    <td>{{ apt.reason }}</td>
                    <td>
                      <span :class="['badge', getStatusClass(apt.status)]">
                        {{ apt.status }}
                      </span>
                    </td>
                    <td>
                      <RouterLink v-if="apt.status === 'Booked'" 
                        :to="`/doctor/appointment/${apt.id}/treatment`"
                        class="btn btn-sm btn-info">
                        ✏️ Treatment
                      </RouterLink>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Modal -->
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const exporting = ref(false)
const appointments = ref([])
const showExportModal = ref(false)
const exportDates = ref({ start: '', end: '' })

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-info',
    'Completed': 'bg-success',
    'Cancelled': 'bg-danger'
  }
  return classes[status] || 'bg-secondary'
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

<style>
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-left: 4px solid #ffc107;
  padding-left: calc(1rem - 4px) !important;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>