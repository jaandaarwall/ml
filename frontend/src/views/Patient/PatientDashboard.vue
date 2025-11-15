<!-- <script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const authStore = useAuthStore()
const dashboard = ref(null)
const appointments = ref([])
const patients = ref([])
const selectedAppointment = ref(null)
const treatment = ref({
  diagnosis: '',
  prescription: '',
  notes: '',
  follow_up_required: false,
  follow_up_date: ''
})

onMounted(async () => {
  await fetchDashboard()
  await fetchAppointments()
  await fetchPatients()
})

async function fetchDashboard() {
  const response = await fetch('http://127.0.0.1:5000/api/doctor/dashboard', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    dashboard.value = await response.json()
  }
}

async function fetchAppointments() {
  const response = await fetch('http://127.0.0.1:5000/api/doctor/appointments', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    appointments.value = await response.json()
  }
}

async function fetchPatients() {
  const response = await fetch('http://127.0.0.1:5000/api/doctor/patients', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    patients.value = await response.json()
  }
}

async function completeAppointment(aptId) {
  const response = await fetch(`http://127.0.0.1:5000/api/doctor/appointment/${aptId}/complete`, {
    method: 'POST',
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    await fetchAppointments()
    await fetchDashboard()
  }
}

async function addTreatment() {
  if (!selectedAppointment.value) return
  
  const response = await fetch(`http://127.0.0.1:5000/api/doctor/appointment/${selectedAppointment.value}/treatment`, {
    method: 'POST',
    headers: authStore.getAuthHeader(),
    body: JSON.stringify(treatment.value)
  })
  
  if (response.ok) {
    alert('Treatment added successfully')
    treatment.value = {
      diagnosis: '',
      prescription: '',
      notes: '',
      follow_up_required: false,
      follow_up_date: ''
    }
    selectedAppointment.value = null
    await fetchAppointments()
  }
}

function openTreatmentModal(aptId) {
  selectedAppointment.value = aptId
}
</script>

<template>
  <div class="container-fluid mt-4">
    <h1 class="mb-4">Doctor Dashboard</h1>
    
    <div class="row mb-4" v-if="dashboard">
      <div class="col-md-4">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <h5 class="card-title">Today's Appointments</h5>
            <p class="card-text fs-3">{{ dashboard.today_appointments.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Upcoming (7 Days)</h5>
            <p class="card-text fs-3">{{ dashboard.upcoming_appointments.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Total Patients</h5>
            <p class="card-text fs-3">{{ dashboard.total_patients }}</p>
          </div>
        </div>
      </div>
    </div>

    <div class="row mb-4" v-if="dashboard && dashboard.today_appointments.length > 0">
      <div class="col-12">
        <h3>Today's Appointments</h3>
        <div class="list-group">
          <div v-for="apt in dashboard.today_appointments" :key="apt.id" class="list-group-item">
            <div class="d-flex justify-content-between">
              <div>
                <h5>{{ apt.patient_name }}</h5>
                <p class="mb-1">Time: {{ apt.time }} | Reason: {{ apt.reason }}</p>
                <span :class="{
                  'badge bg-primary': apt.status === 'Booked',
                  'badge bg-success': apt.status === 'Completed'
                }">{{ apt.status }}</span>
              </div>
              <div>
                <button v-if="apt.status === 'Booked'" class="btn btn-sm btn-success me-2" 
                        @click="openTreatmentModal(apt.id)" data-bs-toggle="modal" data-bs-target="#treatmentModal">
                  Add Treatment
                </button>
                <button v-if="apt.status === 'Booked'" class="btn btn-sm btn-primary" 
                        @click="completeAppointment(apt.id)">
                  Mark Complete
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ul class="nav nav-tabs" role="tablist">
      <li class="nav-item">
        <a class="nav-link active" data-bs-toggle="tab" href="#all-appointments">All Appointments</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#patients">My Patients</a>
      </li>
    </ul>

    <div class="tab-content mt-3">
      <div id="all-appointments" class="tab-pane fade show active">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
              <th>Reason</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="apt in appointments" :key="apt.id">
              <td>{{ apt.patient_name }}</td>
              <td>{{ apt.date }}</td>
              <td>{{ apt.time }}</td>
              <td>
                <span :class="{
                  'badge bg-primary': apt.status === 'Booked',
                  'badge bg-success': apt.status === 'Completed',
                  'badge bg-danger': apt.status === 'Cancelled'
                }">{{ apt.status }}</span>
              </td>
              <td>{{ apt.reason }}</td>
              <td>
                <button v-if="apt.status === 'Booked'" class="btn btn-sm btn-success" 
                        @click="openTreatmentModal(apt.id)" data-bs-toggle="modal" data-bs-target="#treatmentModal">
                  Add Treatment
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div id="patients" class="tab-pane fade">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Blood Group</th>
              <th>Appointments</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="patient in patients" :key="patient.id">
              <td>{{ patient.name }}</td>
              <td>{{ patient.email }}</td>
              <td>{{ patient.phone }}</td>
              <td>{{ patient.blood_group }}</td>
              <td>{{ patient.appointments_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="modal fade" id="treatmentModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add Treatment Details</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addTreatment">
            <div class="mb-3">
              <label class="form-label">Diagnosis</label>
              <textarea class="form-control" v-model="treatment.diagnosis" required></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Prescription</label>
              <textarea class="form-control" v-model="treatment.prescription"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea class="form-control" v-model="treatment.notes"></textarea>
            </div>
            <div class="mb-3 form-check">
              <input type="checkbox" class="form-check-input" v-model="treatment.follow_up_required">
              <label class="form-check-label">Follow-up Required</label>
            </div>
            <div class="mb-3" v-if="treatment.follow_up_required">
              <label class="form-label">Follow-up Date</label>
              <input type="date" class="form-control" v-model="treatment.follow_up_date">
            </div>
            <button type="submit" class="btn btn-primary" data-bs-dismiss="modal">Save Treatment</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template> -->



<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const authStore = useAuthStore()
const dashboard = ref(null)
const doctors = ref([])
const departments = ref([])
const selectedDepartment = ref('')
const selectedDoctor = ref(null)
const selectedDate = ref('')
const availableSlots = ref([])
const bookingData = ref({
  time: '',
  reason: ''
})

onMounted(async () => {
  await fetchDashboard()
  await fetchDepartments()
  await fetchDoctors()
})

async function fetchDashboard() {
  const response = await fetch('http://127.0.0.1:5000/api/patient/dashboard', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    dashboard.value = await response.json()
  }
}

async function fetchDepartments() {
  const response = await fetch('http://127.0.0.1:5000/api/departments')
  if (response.ok) {
    departments.value = await response.json()
  }
}

async function fetchDoctors() {
  let url = 'http://127.0.0.1:5000/api/patient/doctors'
  if (selectedDepartment.value) {
    url += `?department_id=${selectedDepartment.value}`
  }
  
  const response = await fetch(url, {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    doctors.value = await response.json()
  }
}

async function selectDoctor(doctor) {
  selectedDoctor.value = doctor
  availableSlots.value = []
  selectedDate.value = ''
}

async function checkAvailability() {
  if (!selectedDoctor.value || !selectedDate.value) return
  
  const response = await fetch(
    `http://127.0.0.1:5000/api/patient/doctor/${selectedDoctor.value.id}/availability?date=${selectedDate.value}`,
    { headers: authStore.getAuthHeader() }
  )
  if (response.ok) {
    availableSlots.value = await response.json()
  }
}

async function bookAppointment() {
  if (!bookingData.value.time || !bookingData.value.reason) {
    alert('Please select a time slot and provide a reason')
    return
  }
  
  const response = await fetch(
    `http://127.0.0.1:5000/api/patient/book/${selectedDoctor.value.id}`,
    {
      method: 'POST',
      headers: authStore.getAuthHeader(),
      body: JSON.stringify({
        date: selectedDate.value,
        time: bookingData.value.time,
        reason: bookingData.value.reason
      })
    }
  )
  
  const data = await response.json()
  alert(data.message)
  
  if (response.ok) {
    bookingData.value = { time: '', reason: '' }
    selectedDoctor.value = null
    await fetchDashboard()
  }
}

async function cancelAppointment(aptId) {
  if (!confirm('Are you sure you want to cancel this appointment?')) return
  
  const response = await fetch(
    `http://127.0.0.1:5000/api/patient/appointment/${aptId}/cancel`,
    {
      method: 'POST',
      headers: authStore.getAuthHeader()
    }
  )
  
  if (response.ok) {
    alert('Appointment cancelled successfully')
    await fetchDashboard()
  }
}
</script>

<template>
  <div class="container-fluid mt-4">
    <h1 class="mb-4">Patient Dashboard</h1>
    
    <div class="row mb-4" v-if="dashboard">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-primary text-white">
            <h5>Upcoming Appointments</h5>
          </div>
          <div class="card-body">
            <div v-if="dashboard.upcoming_appointments.length === 0">
              <p class="text-muted">No upcoming appointments</p>
            </div>
            <div v-else class="list-group">
              <div v-for="apt in dashboard.upcoming_appointments" :key="apt.id" class="list-group-item">
                <div class="d-flex justify-content-between align-items-center">
                  <div>
                    <h6>Dr. {{ apt.doctor_name }}</h6>
                    <p class="mb-1">{{ apt.department }}</p>
                    <small>{{ apt.date }} at {{ apt.time }}</small>
                  </div>
                  <button class="btn btn-sm btn-danger" @click="cancelAppointment(apt.id)">
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-success text-white">
            <h5>Past Appointments</h5>
          </div>
          <div class="card-body">
            <div v-if="dashboard.past_appointments.length === 0">
              <p class="text-muted">No past appointments</p>
            </div>
            <div v-else class="list-group">
              <div v-for="apt in dashboard.past_appointments" :key="apt.id" class="list-group-item">
                <h6>Dr. {{ apt.doctor_name }}</h6>
                <small>{{ apt.date }}</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <h5>Book New Appointment</h5>
      </div>
      <div class="card-body">
        <div class="row mb-3">
          <div class="col-md-4">
            <label class="form-label">Select Department</label>
            <select class="form-select" v-model="selectedDepartment" @change="fetchDoctors">
              <option value="">All Departments</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="row">
          <div class="col-12">
            <h6>Available Doctors</h6>
            <div class="row">
              <div v-for="doctor in doctors" :key="doctor.id" class="col-md-4 mb-3">
                <div class="card" :class="{'border-primary': selectedDoctor?.id === doctor.id}">
                  <div class="card-body">
                    <h6>{{ doctor.name }}</h6>
                    <p class="mb-1">{{ doctor.department }}</p>
                    <p class="mb-1"><small>{{ doctor.qualification }}</small></p>
                    <p class="mb-1"><small>Experience: {{ doctor.experience_years }} years</small></p>
                    <button class="btn btn-sm btn-primary mt-2" 
                            @click="selectDoctor(doctor)"
                            data-bs-toggle="modal" 
                            data-bs-target="#bookingModal">
                      Book Appointment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Booking Modal -->
  <div class="modal fade" id="bookingModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Book Appointment with Dr. {{ selectedDoctor?.name }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div class="mb-3">
            <label class="form-label">Select Date</label>
            <input type="date" class="form-control" v-model="selectedDate" 
                   :min="new Date().toISOString().split('T')[0]"
                   @change="checkAvailability">
          </div>

          <div v-if="availableSlots.length > 0" class="mb-3">
            <label class="form-label">Select Time Slot</label>
            <div class="d-flex flex-wrap gap-2">
              <button v-for="slot in availableSlots" :key="slot.time"
                      class="btn btn-sm"
                      :class="bookingData.time === slot.time ? 'btn-primary' : 'btn-outline-primary'"
                      @click="bookingData.time = slot.time">
                {{ slot.time }}
              </button>
            </div>
          </div>

          <div v-else-if="selectedDate" class="alert alert-info">
            No available slots for this date
          </div>

          <div class="mb-3">
            <label class="form-label">Reason for Visit</label>
            <textarea class="form-control" v-model="bookingData.reason" rows="3" required></textarea>
          </div>

          <button type="button" class="btn btn-primary" @click="bookAppointment" data-bs-dismiss="modal">
            Confirm Booking
          </button>
        </div>
      </div>
    </div>
  </div>
</template>