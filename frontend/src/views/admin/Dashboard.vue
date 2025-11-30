<template>
  <div class="d-flex" style="height: 100vh;">
    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">⚙️ Admin Dashboard</h1>
        <p class="text-muted mb-0">Welcome back, System Administrator!</p>
      </div>

      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else>
          <div class="row g-4 mb-4">
            <div class="col-md-3">
              <div class="card border-start border-primary border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Total Doctors</h6>
                  <h2 class="mb-0">{{ dashboardData.total_doctors }}</h2>
                  <p class="text-muted small mt-2">Active doctors in system</p>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card border-start border-success border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Total Patients</h6>
                  <h2 class="mb-0">{{ dashboardData.total_patients }}</h2>
                  <p class="text-muted small mt-2">Registered patients</p>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card border-start border-warning border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Total Appointments</h6>
                  <h2 class="mb-0">{{ dashboardData.total_appointments }}</h2>
                  <p class="text-muted small mt-2">All appointments</p>
                </div>
              </div>
            </div>

            <div class="col-md-3">
              <div class="card border-start border-danger border-4 h-100">
                <div class="card-body">
                  <h6 class="text-muted text-uppercase small">Today's Appointments</h6>
                  <h2 class="mb-0">{{ dashboardData.today_appointments }}</h2>
                  <p class="text-muted small mt-2">Scheduled today</p>
                </div>
              </div>
            </div>
          </div>

          <div class="card mb-4">
            <div class="card-header bg-light">
              <h5 class="mb-0">⚡ Quick Actions</h5>
            </div>
            <div class="card-body">
              <div class="row g-2">
                <div class="col-md-3">
                  <RouterLink to="/admin/doctors" class="btn btn-primary w-100">
                    ➕ Add New Doctor
                  </RouterLink>
                </div>
                <div class="col-md-3">
                  <RouterLink to="/admin/departments" class="btn btn-secondary w-100">
                    🏥 Manage Depts
                  </RouterLink>
                </div>
                <div class="col-md-3">
                  <RouterLink to="/admin/analytics" class="btn btn-warning w-100">
                    📊 View Analytics
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>

          <!-- Recent Appointments -->
          <div class="card">
            <div class="card-header bg-light d-flex justify-content-between align-items-center">
              <h5 class="mb-0">⏰ Recent Appointments</h5>
              <RouterLink to="/admin/appointments" class="btn btn-sm btn-outline-primary">
                View All →
              </RouterLink>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Patient</th>
                    <th>Doctor</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="recentAppointments.length === 0">
                    <td colspan="7" class="text-center text-muted py-4">
                      No appointments found
                    </td>
                  </tr>
                  <tr v-for="(apt, index) in recentAppointments" :key="apt.id">
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
                    <td>
                      <button 
                        class="btn btn-sm btn-outline-secondary" 
                        @click="openDetailModal(apt)"
                      >
                        📋 View Details
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="showDetailModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Appointment Details (#{{ selectedAppointment?.id }})</h5>
            <button type="button" class="btn-close btn-close-white" @click="showDetailModal = false"></button>
          </div>
          <div class="modal-body" v-if="selectedAppointment">
            
            <div class="mb-3">
              <h6 class="fw-bold text-dark">👤 Patient:</h6>
              <p class="mb-1">{{ selectedAppointment.patient_name }}</p>
            </div>

            <div class="mb-3">
              <h6 class="fw-bold text-dark">👨‍⚕️ Doctor:</h6>
              <p class="mb-1">Dr. {{ selectedAppointment.doctor_name }}</p>
            </div>

            <hr>

            <div class="mb-3">
              <h6 class="fw-bold text-primary">❓ Reason for Visit:</h6>
              <p class="bg-light p-2 rounded border">{{ selectedAppointment.reason || 'No reason provided' }}</p>
            </div>

            <div v-if="selectedAppointment.diagnosis">
              <div class="mb-3">
                <h6 class="fw-bold text-success">📋 Diagnosis:</h6>
                <p class="bg-light p-2 rounded border">{{ selectedAppointment.diagnosis }}</p>
              </div>
              
              <div class="mb-3">
                <h6 class="fw-bold text-success">💊 Prescription:</h6>
                <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedAppointment.prescription || 'N/A' }}</p>
              </div>

              <div class="mb-3">
                <h6 class="fw-bold text-secondary">📝 Doctor Notes:</h6>
                <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedAppointment.notes || 'N/A' }}</p>
              </div>
            </div>
            <div v-else class="alert alert-info">
              No treatment details recorded yet.
            </div>

          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDetailModal = false">Close</button>
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
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const recentAppointments = ref([])

// Detail Modal State
const showDetailModal = ref(false)
const selectedAppointment = ref(null)

const dashboardData = ref({
  total_doctors: 0,
  total_patients: 0,
  total_appointments: 0,
  today_appointments: 0
})

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

const fetchDashboard = async () => {
  try {
    const response = await adminAPI.getDashboard()
    dashboardData.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message || 'Failed to load dashboard'
    loading.value = false
  }
}

const fetchAppointments = async () => {
  try {
    const response = await adminAPI.getAppointments()
    // Get recent 5
    recentAppointments.value = response.slice(0, 5)
  } catch (err) {
    console.error('Failed to load appointments', err)
  }
}

const openDetailModal = (apt) => {
  selectedAppointment.value = apt
  showDetailModal.value = true
}

onMounted(() => {
  fetchDashboard()
  fetchAppointments()
})
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

.modal.d-block {
  display: block !important;
}
</style>