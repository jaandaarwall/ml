<!-- views/admin/Appointments.vue -->
<template>
  <div class="d-flex" style="height: 100vh;">
    <!-- Sidebar Navigation -->
    <div class="bg-primary text-white p-4" style="width: 250px; overflow-y: auto;">
      <nav class="nav flex-column">
        <RouterLink to="/admin/dashboard" class="nav-link text-white mb-2">
          📊 Dashboard
        </RouterLink>
        <RouterLink to="/admin/doctors" class="nav-link text-white mb-2">
          👨‍⚕️ Manage Doctors
        </RouterLink>
        <RouterLink to="/admin/patients" class="nav-link text-white mb-2">
          👥 Manage Patients
        </RouterLink>
        <RouterLink to="/admin/appointments" class="nav-link text-white mb-2 active-nav">
          📅 All Appointments
        </RouterLink>
        <RouterLink to="/admin/transactions" class="nav-link text-white mb-2">
          💰 Transactions
        </RouterLink>
        <RouterLink to="/admin/analytics" class="nav-link text-white mb-2">
          📈 Reports
        </RouterLink>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-1">📅 All Appointments</h1>
          <p class="text-muted mb-0">View and manage all appointments in the system</p>
        </div>
        <div class="d-flex gap-2">
          <select v-model="sortOrder" class="form-select" style="width: 150px;">
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
          <button class="btn btn-primary" @click="showExportModal = true" :disabled="exporting">
            <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
            <span v-if="exporting">Generating...</span>
            <span v-else>📥 Export CSV</span>
          </button>
        </div>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else-if="sortedAppointments.length === 0" class="alert alert-info text-center">
          No appointments found
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(apt, index) in sortedAppointments" :key="apt.id">
                <td><span class="badge bg-light text-dark">#{{ index + 1 }}</span></td>
                <td class="fw-bold">{{ apt.patient_name }}</td>
                <td>Dr. {{ apt.doctor_name }}</td>
                <td>{{ apt.date }}</td>
                <td>{{ apt.time }}</td>
                <td>
                  <span v-if="apt.status === 'Completed'" class="badge bg-success">
                    {{ apt.status }}
                  </span>
                  <span v-else-if="apt.status === 'Booked'" class="badge bg-info">
                    {{ apt.status }}
                  </span>
                  <span v-else class="badge bg-danger">
                    {{ apt.status }}
                  </span>
                </td>
                <td>{{ apt.reason }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Export Modal -->
    <div v-if="showExportModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Export Appointments</h5>
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
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const exporting = ref(false)
const error = ref('')
const appointments = ref([])
const showExportModal = ref(false)
const exportDates = ref({ start: '', end: '' })
const sortOrder = ref('desc')

const sortedAppointments = computed(() => {
  return [...appointments.value].sort((a, b) => {
    const dateA = new Date(`${a.date} ${a.time}`)
    const dateB = new Date(`${b.date} ${b.time}`)
    return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
})

const fetchAppointments = async () => {
  try {
    const response = await adminAPI.getAppointments()
    appointments.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
}

const handleExport = async () => {
  exporting.value = true
  showExportModal.value = false
  try {
    const res = await adminAPI.exportAppointments(exportDates.value.start, exportDates.value.end)
    const taskId = res.task_id
    
    const interval = setInterval(async () => {
      try {
        const statusRes = await adminAPI.getTaskStatus(taskId)
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

onMounted(fetchAppointments)
</script>

<style scoped>
.nav-link {
  transition: all 0.3s ease;
  padding: 0.75rem 0.5rem;
  border-radius: 0.375rem;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  padding-left: 1rem;
}

.nav-link.active-nav {
  background-color: rgba(255, 255, 255, 0.2);
  border-left: 4px solid #ffc107;
  padding-left: 1rem;
  font-weight: 600;
}
</style>