<!-- views/admin/Search.vue -->
<template>
  <div class="d-flex" style="height: 100vh;">
    <!-- Sidebar Navigation -->
    <div class="bg-primary text-white p-4" style="width: 250px; overflow-y: auto;">
      <h4 class="text-center mb-4 fw-bold">🏥 HMS</h4>
      
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
        <RouterLink to="/admin/appointments" class="nav-link text-white mb-2">
          📅 All Appointments
        </RouterLink>
        <RouterLink to="/admin/analytics" class="nav-link text-white mb-2">
          📈 Reports
        </RouterLink>
      </nav>

      <div class="mt-5 pt-3 border-top border-light">
        <button @click="handleLogout" class="btn btn-outline-light w-100">
          🚪 Logout
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-grow-1 d-flex flex-column overflow-auto">
      <!-- Header -->
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">🔍 Search</h1>
        <p class="text-muted mb-0">Search for doctors and patients</p>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div class="card mb-4">
          <div class="card-body">
            <div class="row g-3 mb-3">
              <div class="col-md-8">
                <input 
                  v-model="searchQuery" 
                  type="text" 
                  class="form-control form-control-lg" 
                  placeholder="Search by name, email, or phone..."
                >
              </div>
              <div class="col-md-4">
                <select v-model="searchType" class="form-select form-select-lg">
                  <option value="all">All</option>
                  <option value="doctor">Doctors</option>
                  <option value="patient">Patients</option>
                </select>
              </div>
            </div>
            <button @click="performSearch" class="btn btn-primary btn-lg" :disabled="!searchQuery">
              🔍 Search
            </button>
          </div>
        </div>

        <div v-if="searched">
          <!-- Doctors Results -->
          <div v-if="results.doctors.length > 0" class="card mb-4">
            <div class="card-header bg-light">
              <h5 class="mb-0">👨‍⚕️ Doctors ({{ results.doctors.length }})</h5>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Department</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doc in results.doctors" :key="doc.id">
                    <td class="fw-bold">Dr. {{ doc.name }}</td>
                    <td>{{ doc.email }}</td>
                    <td><span class="badge bg-info">{{ doc.department }}</span></td>
                    <td>
                      <RouterLink :to="`/admin/doctor/${doc.id}`" class="btn btn-sm btn-info">
                        👁️ View
                      </RouterLink>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Patients Results -->
          <div v-if="results.patients.length > 0" class="card">
            <div class="card-header bg-light">
              <h5 class="mb-0">👥 Patients ({{ results.patients.length }})</h5>
            </div>
            <div class="table-responsive">
              <table class="table table-hover mb-0">
                <thead class="table-light">
                  <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="patient in results.patients" :key="patient.id">
                    <td class="fw-bold">{{ patient.name }}</td>
                    <td>{{ patient.email }}</td>
                    <td>{{ patient.phone }}</td>
                    <td>
                      <RouterLink :to="`/admin/patient/${patient.id}`" class="btn btn-sm btn-info">
                        👁️ View
                      </RouterLink>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="results.doctors.length === 0 && results.patients.length === 0" class="alert alert-warning text-center">
            No results found for "{{ searchQuery }}"
          </div>
        </div>

        <div v-else class="alert alert-info text-center py-5">
          Enter a search term to find doctors and patients
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const searchQuery = ref('')
const searchType = ref('all')
const searched = ref(false)

const results = ref({
  doctors: [],
  patients: []
})

const performSearch = async () => {
  if (!searchQuery.value.trim()) return

  try {
    const response = await adminAPI.search(searchQuery.value, searchType.value)
    results.value = response
    searched.value = true
  } catch (err) {
    console.error('Search error:', err)
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
