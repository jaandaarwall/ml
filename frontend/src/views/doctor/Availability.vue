<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
    <!-- Sidebar -->
    <nav class="bg-primary text-white p-4" style="width: 240px; min-height: 100vh; overflow-y: auto;">
      <div class="nav flex-column gap-2">
        <RouterLink to="/doctor/dashboard" class="nav-link text-white">
          <span class="me-2">📊</span>Dashboard
        </RouterLink>
        <RouterLink to="/doctor/appointments" class="nav-link text-white">
          <span class="me-2">📅</span>My Appointments
        </RouterLink>
        <RouterLink to="/doctor/patients" class="nav-link text-white">
          <span class="me-2">👥</span>My Patients
        </RouterLink>
        <RouterLink to="/doctor/availability" class="nav-link text-white active">
          <span class="me-2">⏰</span>Set Availability
        </RouterLink>
        <RouterLink to="/doctor/profile" class="nav-link text-white">
          <span class="me-2">👤</span>My Profile
        </RouterLink>
        <RouterLink to="/doctor/analytics" class="nav-link text-white">
          <span class="me-2">📈</span>Analytics
        </RouterLink>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4">
        <h2 class="mb-1">⏰ Set Availability</h2>
        <p class="text-muted mb-0">Manage your available time slots for appointments.</p>
      </div>

      <div class="container-fluid px-4">
        <div class="row">
          <!-- Add New Availability Form -->
          <div class="col-lg-4 mb-4">
            <div class="card">
              <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">Add New Availability</h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="addAvailability">
                  <div class="mb-3">
                    <label class="form-label">Date</label>
                    <input v-model="newSlot.date" type="date" class="form-control" :min="todayDate" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Start Time</label>
                    <input v-model="newSlot.start_time" type="time" class="form-control" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">End Time</label>
                    <input v-model="newSlot.end_time" type="time" class="form-control" required>
                  </div>
                  <div class="mb-3">
                    <label class="form-label">Total Seats</label>
                    <input v-model.number="newSlot.total_seats" type="number" class="form-control" value="30">
                  </div>
                  
                  <!-- Repeat Option -->
                  <div class="mb-3 p-3 bg-light rounded border">
                    <label class="form-label fw-bold">🔁 Repeat Settings</label>
                    <div class="input-group">
                      <span class="input-group-text bg-white">For next</span>
                      <input 
                        v-model.number="newSlot.repeat_days" 
                        type="number" 
                        class="form-control" 
                        min="0" 
                        max="30"
                        placeholder="0"
                      >
                      <span class="input-group-text bg-white">days</span>
                    </div>
                    <small class="text-muted d-block mt-1">
                      Leave 0 to add only for the selected date. 
                      Enter e.g., 5 to create slots for 5 additional days.
                    </small>
                  </div>

                  <button type="submit" class="btn btn-primary w-100">
                    Add Availability
                  </button>
                </form>
              </div>
            </div>
          </div>

          <!-- Current Availability -->
          <div class="col-lg-8 mb-4">
            <div class="card">
              <div class="card-header bg-white border-bottom">
                <h5 class="mb-0">Your Current Availability</h5>
              </div>
              <div class="card-body">
                <div v-if="loading" class="text-center py-5">
                  <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>
                <div v-else-if="availabilities.length === 0" class="text-center py-5 text-muted">
                  <p>No availability slots added yet</p>
                </div>
                <div v-else class="table-responsive">
                  <table class="table table-hover mb-0">
                    <thead class="table-light">
                      <tr>
                        <th>Date</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Seats</th>
                        <th>Bookings</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="avail in availabilities" :key="avail.id">
                        <td>
                          <strong>{{ avail.date }}</strong>
                          <span v-if="isPast(avail.date)" class="badge bg-secondary ms-2">Past</span>
                        </td>
                        <td>{{ avail.start_time }}</td>
                        <td>{{ avail.end_time }}</td>
                        <td>{{ avail.total_seats }}</td>
                        <td>
                          <span :class="['badge', avail.booking_count > 0 ? 'bg-info' : 'bg-light text-dark border']">
                            {{ avail.booking_count }} Active
                          </span>
                        </td>
                        <td>
                          <!-- Only show delete if date is not in the past -->
                          <button 
                            v-if="!isPast(avail.date)" 
                            @click="deleteAvailability(avail)" 
                            class="btn btn-sm btn-danger"
                          >
                            🗑️
                          </button>
                          <span v-else class="text-muted small">Locked</span>
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
import { doctorAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(true)
const availabilities = ref([])
const newSlot = ref({
  date: '',
  start_time: '',
  end_time: '',
  total_seats: 30,
  repeat_days: 0
})

const todayDate = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const isPast = (dateStr) => {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const checkDate = new Date(dateStr)
  return checkDate < today
}

const fetchAvailabilities = async () => {
  try {
    const response = await doctorAPI.getAvailability()
    availabilities.value = response
  } finally {
    loading.value = false
  }
}

const addAvailability = async () => {
  if (isPast(newSlot.value.date)) {
    alert('Cannot add availability for past dates.')
    return
  }
  
  try {
    const res = await doctorAPI.addAvailability(newSlot.value)
    alert(res.message || 'Availability added successfully')
    // Reset form
    newSlot.value = { date: '', start_time: '', end_time: '', total_seats: 30, repeat_days: 0 }
    fetchAvailabilities()
  } catch (err) {
    alert(err.message)
  }
}

const deleteAvailability = async (avail) => {
  let message = 'Delete this availability slot?'
  
  // Warning if bookings exist
  if (avail.booking_count > 0) {
    message = `⚠️ WARNING: There are ${avail.booking_count} active booking(s) for this slot.\n\nDeleting this availability will CANCEL all these appointments and notify the patients via email.\n\nAre you sure you want to proceed?`
  }

  if (confirm(message)) {
    try {
      await doctorAPI.deleteAvailability(avail.id)
      alert('Availability deleted successfully.')
      fetchAvailabilities()
    } catch (err) {
      alert(err.message)
    }
  }
}

onMounted(fetchAvailabilities)
</script>

<style>
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2) !important;
  border-left: 4px solid #ffc107;
  padding-left: calc(1rem - 4px) !important;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>