<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth.js'

const authStore = useAuthStore()
const stats = ref(null)
const doctors = ref([])
const patients = ref([])
const appointments = ref([])

onMounted(async () => {
  await fetchDashboardData()
  await fetchDoctors()
  await fetchPatients()
  await fetchAppointments()
})

async function fetchDashboardData() {
  const response = await fetch('http://127.0.0.1:5000/api/admin/dashboard', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    stats.value = await response.json()
  }
}

async function fetchDoctors() {
  const response = await fetch('http://127.0.0.1:5000/api/admin/doctors', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    doctors.value = await response.json()
  }
}

async function fetchPatients() {
  const response = await fetch('http://127.0.0.1:5000/api/admin/patients', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    patients.value = await response.json()
  }
}

async function fetchAppointments() {
  const response = await fetch('http://127.0.0.1:5000/api/admin/appointments', {
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    appointments.value = await response.json()
  }
}

async function toggleDoctor(doctorId) {
  const response = await fetch(`http://127.0.0.1:5000/api/admin/doctor/${doctorId}`, {
    method: 'DELETE',
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    await fetchDoctors()
  }
}

async function togglePatient(patientId) {
  const response = await fetch(`http://127.0.0.1:5000/api/admin/patient/${patientId}`, {
    method: 'DELETE',
    headers: authStore.getAuthHeader()
  })
  if (response.ok) {
    await fetchPatients()
  }
}
</script>

<template>
  <div class="container-fluid mt-4">
    <h1 class="mb-4">Admin Dashboard</h1>
    
    <div class="row mb-4" v-if="stats">
      <div class="col-md-3">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <h5 class="card-title">Total Doctors</h5>
            <p class="card-text fs-3">{{ stats.total_doctors }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Total Patients</h5>
            <p class="card-text fs-3">{{ stats.total_patients }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Total Appointments</h5>
            <p class="card-text fs-3">{{ stats.total_appointments }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <h5 class="card-title">Today's Appointments</h5>
            <p class="card-text fs-3">{{ stats.today_appointments }}</p>
          </div>
        </div>
      </div>
    </div>

    <ul class="nav nav-tabs" role="tablist">
      <li class="nav-item">
        <a class="nav-link active" data-bs-toggle="tab" href="#doctors">Doctors</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#patients">Patients</a>
      </li>
      <li class="nav-item">
        <a class="nav-link" data-bs-toggle="tab" href="#appointments">Appointments</a>
      </li>
    </ul>

    <div class="tab-content mt-3">
      <div id="doctors" class="tab-pane fade show active">
        <h3>Doctors</h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Department</th>
              <th>Experience</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doctor in doctors" :key="doctor.id">
              <td>{{ doctor.name }}</td>
              <td>{{ doctor.email }}</td>
              <td>{{ doctor.department }}</td>
              <td>{{ doctor.experience_years }} years</td>
              <td>
                <span :class="doctor.is_active ? 'badge bg-success' : 'badge bg-danger'">
                  {{ doctor.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-warning" @click="toggleDoctor(doctor.id)">
                  {{ doctor.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div id="patients" class="tab-pane fade">
        <h3>Patients</h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Blood Group</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="patient in patients" :key="patient.id">
              <td>{{ patient.name }}</td>
              <td>{{ patient.email }}</td>
              <td>{{ patient.phone }}</td>
              <td>{{ patient.blood_group }}</td>
              <td>
                <span :class="patient.is_active ? 'badge bg-success' : 'badge bg-danger'">
                  {{ patient.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td>
                <button class="btn btn-sm btn-warning" @click="togglePatient(patient.id)">
                  {{ patient.is_active ? 'Deactivate' : 'Activate' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div id="appointments" class="tab-pane fade">
        <h3>All Appointments</h3>
        <table class="table table-striped">
          <thead>
            <tr>
              <th>Patient</th>
              <th>Doctor</th>
              <th>Date</th>
              <th>Time</th>
              <th>Status</th>
              <th>Reason</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="apt in appointments" :key="apt.id">
              <td>{{ apt.patient_name }}</td>
              <td>{{ apt.doctor_name }}</td>
              <td>{{ apt.date }}</td>
              <td>{{ apt.time }}</td>
              <td>
                <span :class="{
                  'badge bg-primary': apt.status === 'Booked',
                  'badge bg-success': apt.status === 'Completed',
                  'badge bg-danger': apt.status === 'Cancelled'
                }">
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
</template>