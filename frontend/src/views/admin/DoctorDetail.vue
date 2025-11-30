<template>
  <div class="container-fluid">
    <div class="page-header d-flex justify-content-between align-items-center">
      <h1>👨‍⚕️ Doctor Details</h1>
      <div>
        <button @click="openEditModal" class="btn btn-primary me-2">✏️ Edit Details</button>
        <RouterLink to="/admin/doctors" class="btn btn-outline-light">Back to Doctors</RouterLink>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary"></div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>
    
    <div v-else>
      <div class="row g-4 mb-4">
        <div class="col-lg-4">
          <div class="card h-100">
            <div class="card-header bg-primary text-white">
              <h5 class="mb-0">Doctor Profile</h5>
            </div>
            <div class="card-body">
              <div class="text-center mb-3">
                <div class="display-4">👨‍⚕️</div>
                <h4 class="mt-2">{{ doctor.name }}</h4>
                <span :class="['badge', doctor.is_active ? 'bg-success' : 'bg-danger']">
                  {{ doctor.is_active ? 'Active' : 'Inactive' }}
                </span>
              </div>
              <hr>
              <p><strong>📧 Email:</strong> {{ doctor.email }}</p>
              <p><strong>📱 Phone:</strong> {{ doctor.phone }}</p>
              <p><strong>🏥 Dept:</strong> {{ doctor.department }}</p>
              <p><strong>🎓 Qual:</strong> {{ doctor.qualification }}</p>
              <p><strong>📅 Exp:</strong> {{ doctor.experience_years }} years</p>
              <div class="mt-3 p-3 bg-light rounded">
                <h6 class="mb-1">Total Appointments</h6>
                <h3>{{ doctor.appointments_count }}</h3>
              </div>
            </div>
          </div>
        </div>

        <div class="col-lg-8">
          <div class="card h-100">
            <div class="card-header bg-white">
              <h5 class="mb-0">📈 Performance Overview (Last 6 Months)</h5>
            </div>
            <div class="card-body">
              <div class="chart-container" style="height: 300px; width: 100%;">
                <canvas ref="chartCanvas"></canvas>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="card">
        <div class="card-header bg-white d-flex justify-content-between align-items-center">
          <h5 class="mb-0">📅 Appointment History</h5>
          <span class="badge bg-primary rounded-pill">{{ appointments.length }} Records</span>
        </div>
        <div class="card-body p-0">
          <div v-if="appointments.length === 0" class="text-center py-5 text-muted">
            <p>No appointments found for this doctor.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>Date & Time</th>
                  <th>Patient</th>
                  <th>Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="apt in appointments" :key="apt.id">
                  <td>
                    <div><strong>{{ apt.date }}</strong></div>
                    <small class="text-muted">{{ apt.time }}</small>
                  </td>
                  <td>{{ apt.patient_name }}</td>
                  <td><span :class="['badge', getStatusClass(apt.status)]">{{ apt.status }}</span></td>
                  <td class="text-end">
                    <div class="btn-group">
                      <button 
                        class="btn btn-sm btn-outline-primary" 
                        @click="fetchAndShowPatient(apt.patient_id)"
                      >
                        👤 Patient Detail
                      </button>
                      <button 
                        v-if="apt.diagnosis" 
                        class="btn btn-sm btn-outline-success" 
                        @click="showTreatment(apt)"
                      >
                        💊 Treatment Detail
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

    <div v-if="showEditModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Edit Doctor Details</h5>
            <button type="button" class="btn-close btn-close-white" @click="showEditModal = false"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateDoctor">
              <div class="mb-3">
                <label class="form-label">Name</label>
                <input v-model="editForm.username" type="text" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="editForm.email" type="email" class="form-control" required>
              </div>
              <div class="mb-3">
                <label class="form-label">Phone</label>
                <input v-model="editForm.phone" type="text" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Department</label>
                <select v-model="editForm.department_id" class="form-select" required>
                  <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                    {{ dept.name }}
                  </option>
                </select>
              </div>
              <div class="mb-3">
                <label class="form-label">Qualification</label>
                <input v-model="editForm.qualification" type="text" class="form-control">
              </div>
              <div class="mb-3">
                <label class="form-label">Experience (Years)</label>
                <input v-model.number="editForm.experience_years" type="number" class="form-control">
              </div>
              <div class="d-grid">
                <button type="submit" class="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedTreatment" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title">Treatment Details</h5>
            <button type="button" class="btn-close" @click="selectedTreatment = null"></button>
          </div>
          <div class="modal-body">
            <div class="mb-3">
              <h6 class="fw-bold text-primary">📋 Diagnosis:</h6>
              <p class="bg-light p-2 rounded border">{{ selectedTreatment.diagnosis || 'N/A' }}</p>
            </div>
            <div class="mb-3">
              <h6 class="fw-bold text-success">💊 Prescription:</h6>
              <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedTreatment.prescription || 'N/A' }}</p>
            </div>
            <div>
              <h6 class="fw-bold text-secondary">📝 Doctor's Notes:</h6>
              <p class="bg-light p-2 rounded border" style="white-space: pre-line;">{{ selectedTreatment.notes || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="selectedPatient" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Patient Information</h5>
            <button type="button" class="btn-close" @click="selectedPatient = null"></button>
          </div>
          <div class="modal-body" v-if="loadingPatient">
            <div class="text-center py-4"><div class="spinner-border text-primary"></div></div>
          </div>
          <div class="modal-body" v-else>
            <div class="text-center mb-3">
              <div class="display-6">👤</div>
              <h5 class="mt-2">{{ selectedPatient.name }}</h5>
            </div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item d-flex justify-content-between">
                <strong>Email:</strong> <span>{{ selectedPatient.email }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <strong>Phone:</strong> <span>{{ selectedPatient.phone || 'N/A' }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <strong>Gender:</strong> <span>{{ selectedPatient.gender || 'N/A' }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <strong>Blood Group:</strong> <span>{{ selectedPatient.blood_group || 'N/A' }}</span>
              </li>
              <li class="list-group-item d-flex justify-content-between">
                <strong>DOB:</strong> <span>{{ selectedPatient.dob || 'N/A' }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { adminAPI, departmentsAPI } from '../../services/api'
import { Chart } from 'chart.js/auto'

const route = useRoute()
const loading = ref(true)
const error = ref('')
const doctor = ref({})
const appointments = ref([])
const departments = ref([])

const selectedTreatment = ref(null)
const selectedPatient = ref(null)
const loadingPatient = ref(false)
const showEditModal = ref(false)
const editForm = ref({})

const chartCanvas = ref(null)
let chartInstance = null

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-info',
    'Completed': 'bg-success',
    'Cancelled': 'bg-danger'
  }
  return classes[status] || 'bg-secondary'
}

const showTreatment = (apt) => {
  selectedTreatment.value = {
    diagnosis: apt.diagnosis,
    prescription: apt.prescription,
    notes: apt.notes
  }
}

const fetchAndShowPatient = async (patientId) => {
  selectedPatient.value = {}
  loadingPatient.value = true
  try {
    const response = await adminAPI.getPatientDetail(patientId)
    selectedPatient.value = response.patient
  } catch (err) {
    alert('Failed to load patient details')
    selectedPatient.value = null
  } finally {
    loadingPatient.value = false
  }
}

const openEditModal = () => {
  editForm.value = {
    username: doctor.value.name,
    email: doctor.value.email,
    phone: doctor.value.phone,
    department_id: doctor.value.department_id,
    qualification: doctor.value.qualification,
    experience_years: doctor.value.experience_years
  }
  showEditModal.value = true
}

const updateDoctor = async () => {
  try {
    await adminAPI.updateDoctor(route.params.id, editForm.value)
    alert('Doctor updated successfully')
    showEditModal.value = false
    loadData()
  } catch (err) {
    alert(err.message || 'Failed to update doctor')
  }
}

const processChartData = (appointments) => {
  const monthlyCounts = {}
  const today = new Date()
  
  for (let i = 5; i >= 0; i--) {
    const d = new Date(today.getFullYear(), today.getMonth() - i, 1)
    const key = d.toLocaleString('default', { month: 'short', year: 'numeric' })
    monthlyCounts[key] = 0
  }

  appointments.forEach(apt => {
    const d = new Date(apt.date)
    const key = d.toLocaleString('default', { month: 'short', year: 'numeric' })
    if (monthlyCounts.hasOwnProperty(key)) {
      monthlyCounts[key]++
    }
  })

  return {
    labels: Object.keys(monthlyCounts),
    data: Object.values(monthlyCounts)
  }
}

const renderChart = (chartData) => {
  if (chartInstance) chartInstance.destroy()
  
  if (chartCanvas.value) {
    chartInstance = new Chart(chartCanvas.value, {
      type: 'line',
      data: {
        labels: chartData.labels,
        datasets: [{
          label: 'Appointments',
          data: chartData.data,
          borderColor: '#0d6efd',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          borderWidth: 2,
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    })
  }
}

const loadData = async () => {
  try {
    const response = await adminAPI.getDoctorDetail(route.params.id)
    doctor.value = { ...response.doctor, appointments_count: response.appointments_count }
    appointments.value = response.appointments
    
    const chartData = processChartData(response.appointments)
    
    if (departments.value.length === 0) {
        const deptResponse = await departmentsAPI.getDepartments()
        departments.value = deptResponse
    }

    loading.value = false
    await nextTick()
    renderChart(chartData)
    
  } catch (err) {
    error.value = err.message
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.modal {
  display: block !important;
  background: rgba(0,0,0,0.5);
}
.list-group-item {
  border-left: none;
  border-right: none;
}
</style>