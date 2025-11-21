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
        <RouterLink to="/admin/patients" class="nav-link text-white mb-2 active-nav">
          👥 Manage Patients
        </RouterLink>
        <RouterLink to="/admin/appointments" class="nav-link text-white mb-2">
          📅 All Appointments
        </RouterLink>
        <RouterLink to="/admin/analytics" class="nav-link text-white mb-2">
          📈 Reports
        </RouterLink>
      </nav>
    </div>

    <!-- Main Content -->
    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <!-- Header -->
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">👥 Manage Patients</h1>
        <p class="text-muted mb-0">View and manage all patients</p>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div class="mb-3">
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control" 
            placeholder="Search patients by name or email..."
          >
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else-if="filteredPatients.length === 0" class="alert alert-info text-center">
          No patients found
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Blood Group</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in filteredPatients" :key="patient.id">
                <td class="fw-bold">{{ patient.name }}</td>
                <td>{{ patient.email }}</td>
                <td>{{ patient.phone }}</td>
                <td>
                  <span v-if="patient.blood_group" class="badge bg-warning text-dark">
                    {{ patient.blood_group }}
                  </span>
                  <span v-else class="text-muted">N/A</span>
                </td>
                <td>
                  <span v-if="patient.is_active" class="badge bg-success">Active</span>
                  <span v-else class="badge bg-danger">Inactive</span>
                </td>
                <td>
                  <RouterLink :to="`/admin/patient/${patient.id}`" class="btn btn-sm btn-info me-1">
                    👁️
                  </RouterLink>
                  <button @click="togglePatient(patient)" class="btn btn-sm" :class="patient.is_active ? 'btn-warning' : 'btn-success'">
                    {{ patient.is_active ? '❌' : '✅' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const patients = ref([])

const filteredPatients = computed(() => {
  if (!searchQuery.value) return patients.value
  const query = searchQuery.value.toLowerCase()
  return patients.value.filter(p => 
    p.name.toLowerCase().includes(query) ||
    p.email.toLowerCase().includes(query)
  )
})

const fetchPatients = async () => {
  try {
    const response = await adminAPI.getPatients()
    patients.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
}

const togglePatient = async (patient) => {
  try {
    await adminAPI.deactivatePatient(patient.id)
    patient.is_active = !patient.is_active
  } catch (err) {
    error.value = err.message
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

onMounted(fetchPatients)
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