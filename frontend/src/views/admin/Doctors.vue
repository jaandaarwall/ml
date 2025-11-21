<template>
  <div class="d-flex" style="height: 100vh;">
    <!-- Sidebar Navigation -->
    <div class="bg-primary text-white p-4" style="width: 250px; overflow-y: auto;">      
      <nav class="nav flex-column">
        <RouterLink to="/admin/dashboard" class="nav-link text-white mb-2">
          📊 Dashboard
        </RouterLink>
        <RouterLink to="/admin/doctors" class="nav-link text-white mb-2 active-nav">
          👨‍⚕️ Manage Doctors
        </RouterLink>
        <RouterLink to="/admin/patients" class="nav-link text-white mb-2">
          👥 Manage Patients
        </RouterLink>
        <RouterLink to="/admin/appointments" class="nav-link text-white mb-2">
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
          <h1 class="mb-1">👨‍⚕️ Manage Doctors</h1>
          <p class="text-muted mb-0">Add, edit, or remove doctors from the system</p>
        </div>
        <button @click="showAddModal = true" class="btn btn-primary">
          ➕ Add New Doctor
        </button>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <!-- Search Bar -->
        <div class="mb-3">
          <input 
            v-model="searchQuery" 
            type="text" 
            class="form-control" 
            placeholder="Search doctors by name or email..."
          >
        </div>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else-if="filteredDoctors.length === 0" class="alert alert-info text-center">
          No doctors found
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Specialization</th>
                <th>Experience</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(doctor, index) in filteredDoctors" :key="doctor.id">
                <td><span class="badge bg-light text-dark">#{{ index + 1 }}</span></td>
                <td class="fw-bold">{{ doctor.name }}</td>
                <td>{{ doctor.email }}</td>
                <td>{{ doctor.phone }}</td>
                <td>
                  <span class="badge bg-info">{{ doctor.department }}</span>
                </td>
                <td>{{ doctor.experience_years }} years</td>
                <td>
                  <span v-if="doctor.is_active" class="badge bg-success">Active</span>
                  <span v-else class="badge bg-danger">Inactive</span>
                </td>
                <td>
                  <RouterLink :to="`/admin/doctor/${doctor.id}`" class="btn btn-sm btn-info me-1">
                    ✏️
                  </RouterLink>
                  <button 
                    @click="toggleDoctor(doctor)" 
                    :class="['btn', 'btn-sm', doctor.is_active ? 'btn-warning' : 'btn-success']"
                  >
                    {{ doctor.is_active ? '❌' : '✅' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add Doctor Modal -->
    <div v-if="showAddModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Add New Doctor</h5>
            <button type="button" class="btn-close btn-close-white" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <div v-if="addError" class="alert alert-danger">{{ addError }}</div>

            <form @submit.prevent="addDoctor">
              <div class="mb-3">
                <label class="form-label">Username *</label>
                <input v-model="newDoctor.username" type="text" class="form-control" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Email *</label>
                <input v-model="newDoctor.email" type="email" class="form-control" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Password *</label>
                <input v-model="newDoctor.password" type="password" class="form-control" required>
              </div>

              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="newDoctor.phone" type="tel" class="form-control">
              </div>

              <div class="mb-3">
                <label class="form-label">Department *</label>
                <select v-model="newDoctor.department_id" class="form-select" required>
                  <option value="">Select Department</option>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
              </div>

              <div class="mb-3">
                <label class="form-label">Qualification</label>
                <input v-model="newDoctor.qualification" type="text" class="form-control">
              </div>

              <div class="mb-3">
                <label class="form-label">Experience (Years)</label>
                <input v-model.number="newDoctor.experience_years" type="number" class="form-control">
              </div>

              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="addingDoctor">
                  {{ addingDoctor ? 'Adding...' : 'Add Doctor' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminAPI, departmentsAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const doctors = ref([])
const departments = ref([])
const showAddModal = ref(false)
const addingDoctor = ref(false)
const addError = ref('')

const newDoctor = ref({
  username: '',
  email: '',
  password: '',
  phone: '',
  department_id: '',
  qualification: '',
  experience_years: 0
})

const filteredDoctors = computed(() => {
  if (!searchQuery.value) return doctors.value
  const query = searchQuery.value.toLowerCase()
  return doctors.value.filter(doc => 
    doc.name.toLowerCase().includes(query) ||
    doc.email.toLowerCase().includes(query)
  )
})

const fetchDoctors = async () => {
  try {
    const response = await adminAPI.getDoctors()
    doctors.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
}

const fetchDepartments = async () => {
  try {
    const response = await departmentsAPI.getDepartments()
    departments.value = response
  } catch (err) {
    console.error('Failed to load departments', err)
  }
}

const addDoctor = async () => {
  if (!newDoctor.value.username || !newDoctor.value.email || !newDoctor.value.password || !newDoctor.value.department_id) {
    addError.value = 'Please fill in all required fields'
    return
  }

  addingDoctor.value = true
  addError.value = ''

  try {
    await adminAPI.addDoctor(newDoctor.value)
    showAddModal.value = false
    newDoctor.value = {
      username: '',
      email: '',
      password: '',
      phone: '',
      department_id: '',
      qualification: '',
      experience_years: 0
    }
    fetchDoctors()
  } catch (err) {
    addError.value = err.message
  } finally {
    addingDoctor.value = false
  }
}

const toggleDoctor = async (doctor) => {
  try {
    await adminAPI.deactivateDoctor(doctor.id)
    doctor.is_active = !doctor.is_active
  } catch (err) {
    error.value = err.message
  }
}

const closeModal = () => {
  showAddModal.value = false
  addError.value = ''
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
  }
}

onMounted(() => {
  fetchDoctors()
  fetchDepartments()
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

.nav-link.router-link-active,
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