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
        <RouterLink to="/admin/departments" class="nav-link text-white mb-2 active-nav">
          🏥 Manage Departments
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
          <h1 class="mb-1">🏥 Departments</h1>
          <p class="text-muted mb-0">Manage hospital departments and pricing</p>
        </div>
        <button @click="openAddModal" class="btn btn-primary">
          ➕ Add Department
        </button>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Description</th>
                <th>Consultation Fee</th>
                <th>Active Doctors</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="dept in departments" :key="dept.id">
                <td>#{{ dept.id }}</td>
                <td class="fw-bold">{{ dept.name }}</td>
                <td>{{ dept.description }}</td>
                <td class="text-success fw-bold">₹{{ dept.price }}</td>
                <td>
                  <span :class="['badge', dept.active_doctors_count > 0 ? 'bg-info' : 'bg-secondary']">
                    {{ dept.active_doctors_count }} Doctors
                  </span>
                </td>
                <td>
                  <div class="btn-group">
                    <button @click="openEditModal(dept)" class="btn btn-sm btn-outline-primary">
                      ✏️
                    </button>
                    <button @click="deleteDepartment(dept)" class="btn btn-sm btn-outline-danger">
                      🗑️
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">{{ isEditing ? 'Edit Department' : 'Add New Department' }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="showModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="formError" class="alert alert-danger">{{ formError }}</div>
            <form @submit.prevent="handleSubmit">
              <div class="mb-3">
                <label class="form-label">Name *</label>
                <input v-model="formData.name" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea v-model="formData.description" class="form-control" rows="3"></textarea>
              </div>
              <div class="mb-3">
                <label class="form-label">Consultation Price (₹) *</label>
                <input v-model.number="formData.price" type="number" class="form-control" min="0" required>
              </div>
              <div class="modal-footer px-0 pb-0">
                <button type="button" class="btn btn-secondary" @click="showModal = false">Cancel</button>
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  {{ submitting ? 'Saving...' : 'Save Changes' }}
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
import { ref, onMounted } from 'vue'
import { adminAPI } from '../../services/api'

const loading = ref(true)
const error = ref('')
const departments = ref([])

// Modal State
const showModal = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const formError = ref('')
const formData = ref({ id: null, name: '', description: '', price: 300 })

const fetchDepartments = async () => {
  try {
    const response = await adminAPI.getDepartmentsManaged()
    departments.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message || 'Failed to load departments'
    loading.value = false
  }
}

const openAddModal = () => {
  isEditing.value = false
  formData.value = { name: '', description: '', price: 300 }
  formError.value = ''
  showModal.value = true
}

const openEditModal = (dept) => {
  isEditing.value = true
  formData.value = { ...dept }
  formError.value = ''
  showModal.value = true
}

const handleSubmit = async () => {
  submitting.value = true
  formError.value = ''
  try {
    if (isEditing.value) {
      await adminAPI.updateDepartment(formData.value.id, formData.value)
    } else {
      await adminAPI.addDepartment(formData.value)
    }
    showModal.value = false
    fetchDepartments()
  } catch (err) {
    formError.value = err.message
  } finally {
    submitting.value = false
  }
}

const deleteDepartment = async (dept) => {
  let message = `Are you sure you want to delete '${dept.name}'?`
  
  if (dept.active_doctors_count > 0) {
    message = `⚠️ WARNING: This department has ${dept.active_doctors_count} active doctor(s).\n\nDeleting it will:\n1. Make all associated doctors inactive.\n2. Send them an email.\n3. CANCEL all future appointments for these doctors.\n4. Notify all affected patients.\n\nThis action cannot be undone. Do you want to proceed?`
  }

  if (confirm(message)) {
    try {
      await adminAPI.deleteDepartment(dept.id)
      alert('Department deleted successfully.')
      fetchDepartments()
    } catch (err) {
      alert(err.message || 'Failed to delete department')
    }
  }
}

onMounted(fetchDepartments)
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