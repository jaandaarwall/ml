<!-- views/patient/Dashboard.vue -->
<template>
  <div class="d-flex" style="min-height: 100vh;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 250px; min-height: 100vh; overflow-y: auto;">
      <ul class="nav flex-column gap-2">
        <li class="nav-item">
          <RouterLink to="/patient/dashboard" class="nav-link text-white active">
            <span>📊 Dashboard</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/book-appointment" class="nav-link text-white">
            <span>🔍 Find Doctors</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/appointments" class="nav-link text-white">
            <span>📅 My Appointments</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/history" class="nav-link text-white">
            <span>📋 Medical History</span>
          </RouterLink>
        </li>
        <li class="nav-item">
          <RouterLink to="/patient/profile" class="nav-link text-white">
            <span>👤 My Profile</span>
          </RouterLink>
        </li>
      </ul>

        <li class="nav-item">
          <RouterLink to="/patient/analytics" class="nav-link text-white">
            <span>📈 Analytics</span>
          </RouterLink>
        </li>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <!-- Header -->
      <div class="bg-white border-bottom p-4 mb-4">
        <h1 class="mb-1">👤 Patient Dashboard</h1>
        <p class="text-muted mb-0">Welcome back, {{ userName }}!</p>
      </div>

      <!-- Content -->
      <div class="container-fluid px-4 pb-5">
        <!-- Profile Card -->
        <div class="row mb-4">
          <div class="col-md-4">
            <div class="card">
              <div class="card-body text-center">
                <div class="display-4 mb-3">👤</div>
                <h5 class="card-title">{{ userName }}</h5>
                <p class="text-muted small mb-1">
                  <span>✉️ {{ userEmail }}</span>
                </p>
                <p class="text-muted small mb-3">
                  <span>📱 {{ userPhone }}</span>
                </p>
                <p class="text-muted small mb-3">
                  <span>🩸 Blood Group: {{ userBloodGroup || 'N/A' }}</span>
                </p>
                <RouterLink to="/patient/profile" class="btn btn-outline-primary btn-sm">
                  ✏️ Edit Profile
                </RouterLink>
              </div>
            </div>
          </div>

          <!-- Stats Cards -->
          <div class="col-md-8">
            <div class="row g-3">
              <div class="col-md-6">
                <div class="card border-primary">
                  <div class="card-body">
                    <h6 class="card-title text-muted text-uppercase small fw-bold">📅 Upcoming Appointments</h6>
                    <h2 class="mb-0">{{ dashboard.upcoming_appointments.length }}</h2>
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card border-success">
                  <div class="card-body">
                    <h6 class="card-title text-muted text-uppercase small fw-bold">✅ Completed Visits</h6>
                    <h2 class="mb-0">{{ dashboard.past_appointments.length }}</h2>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-body">
                <h5 class="card-title mb-3">⚡ Quick Actions</h5>
                <div class="d-grid gap-2 d-sm-flex">
                  <RouterLink to="/patient/book-appointment" class="btn btn-primary btn-lg">
                    📅 Book New Appointment
                  </RouterLink>
                  <RouterLink to="/patient/book-appointment" class="btn btn-outline-primary btn-lg">
                    🔍 Search Doctors by Specialization
                  </RouterLink>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Available Specializations -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">🏥 Available Specializations</h5>
                <RouterLink to="/patient/book-appointment" class="btn btn-outline-primary btn-sm">
                  View All →
                </RouterLink>
              </div>
              <div class="card-body">
                <div v-if="loadingDepts" class="text-center py-5">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
                <div v-else-if="departments.length === 0" class="alert alert-info mb-0">
                  No specializations available
                </div>
                <div v-else class="row g-3">
                  <div v-for="dept in departments.slice(0, 3)" :key="dept.id" class="col-md-4">
                    <div class="card h-100 border-0 bg-light">
                      <div class="card-body">
                        <h6 class="card-title">👨‍⚕️ {{ dept.name }}</h6>
                        <p class="card-text text-muted small mb-2">{{ dept.description }}</p>
                        <p class="text-muted small mb-3">
                          👥 {{ getDoctorCountForDept(dept.id) }} doctor(s) available
                        </p>
                        <button 
                          @click="goToFindDoctors(dept.id)" 
                          class="btn btn-outline-primary btn-sm w-100"
                        >
                          View Doctors
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Upcoming Appointments -->
        <div class="row mb-4">
          <div class="col-12">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">📅 Upcoming Appointments</h5>
                <RouterLink to="/patient/appointments" class="btn btn-primary btn-sm">
                  View All
                </RouterLink>
              </div>
              <div class="card-body">
                <div v-if="dashboard.upcoming_appointments.length === 0" class="text-center py-5">
                  <div class="display-1 mb-3">📭</div>
                  <p class="text-muted mb-3">No upcoming appointments</p>
                  <RouterLink to="/patient/book-appointment" class="btn btn-primary">
                    Book Your First Appointment
                  </RouterLink>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover">
                    <thead class="table-light">
                      <tr>
                        <th>Date</th>
                        <th>Time</th>
                        <th>Doctor</th>
                        <th>Department</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="apt in dashboard.upcoming_appointments" :key="apt.id">
                        <td>{{ apt.date }}</td>
                        <td>{{ apt.time }}</td>
                        <td>{{ apt.doctor_name }}</td>
                        <td>{{ apt.department }}</td>
                        <td>
                          <span class="badge bg-info">{{ apt.status }}</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Medical History -->
        <div class="row">
          <div class="col-12">
            <div class="card">
              <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">📋 Medical History</h5>
                <RouterLink to="/patient/history" class="btn btn-primary btn-sm">
                  View Complete History
                </RouterLink>
              </div>
              <div class="card-body">
                <div v-if="dashboard.past_appointments.length === 0" class="alert alert-info mb-0">
                  No past consultations yet
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover">
                    <thead class="table-light">
                      <tr>
                        <th>Date</th>
                        <th>Doctor</th>
                        <th>Status</th>
                        <th>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="apt in dashboard.past_appointments" :key="apt.id">
                        <td>{{ apt.date }}</td>
                        <td>{{ apt.doctor_name }}</td>
                        <td>
                          <span class="badge bg-success">{{ apt.status }}</span>
                        </td>
                        <td>
                          <RouterLink to="/patient/history" class="btn btn-sm btn-outline-primary">
                            View
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
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { patientAPI, departmentsAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const loadingDepts = ref(true)
const error = ref('')
const departments = ref([])
const doctorsByDept = ref({})

const dashboard = ref({
  upcoming_appointments: [],
  past_appointments: []
})

// Get user info from auth store
const userName = computed(() => authStore.user?.email?.split('@')[0] || 'User')
const userEmail = computed(() => authStore.user?.email || '')
const userPhone = ref('')
const userBloodGroup = ref('')

const getDoctorCountForDept = (deptId) => {
  return doctorsByDept.value[deptId] || 0
}

const goToFindDoctors = (deptId) => {
  // Navigate to book appointment with department filter
  router.push({
    path: '/patient/book-appointment',
    query: { department_id: deptId }
  })
}

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
    const response = await patientAPI.getDashboard()
    dashboard.value = response
  } catch (err) {
    error.value = err.message || 'Failed to load dashboard'
  } finally {
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const response = await departmentsAPI.getDepartments()
    departments.value = response

    // Count doctors per department
    const doctors = await patientAPI.getDoctors()
    const counts = {}
    response.forEach(dept => {
      counts[dept.id] = doctors.filter(doc => doc.department === dept.name).length
    })
    doctorsByDept.value = counts
    console.log('Departments loaded:', response)
    console.log('Doctor counts:', counts)
  } catch (err) {
    console.error('Failed to load departments', err)
  } finally {
    loadingDepts.value = false
  }
}

const fetchUserProfile = async () => {
  try {
    const response = await patientAPI.getProfile()
    userPhone.value = response.phone || 'Not provided'
    userBloodGroup.value = response.blood_group || 'N/A'
  } catch (err) {
    console.error('Failed to load profile', err)
  }
}

onMounted(() => {
  fetchDashboard()
  fetchDepartments()
  fetchUserProfile()
})
</script>

<style scoped>
.nav-link {
  padding: 10px 15px;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
  font-weight: 600;
  border-left: 4px solid #fbbf24;
}
</style>
