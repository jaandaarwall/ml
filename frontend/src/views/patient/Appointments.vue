<template>
  <div class="d-flex" style="min-height: 100vh;">
    <!-- Main Content -->
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h1 class="mb-1">📅 My Appointments</h1>
          <p class="text-muted mb-0">View and manage your appointments</p>
        </div>
        <div class="d-flex gap-2">
          <!-- Sorting Dropdown -->
          <select v-model="sortOrder" class="form-select">
            <option value="desc">Newest First</option>
            <option value="asc">Oldest First</option>
          </select>
          <RouterLink to="/patient/book-appointment" class="btn btn-primary">
            ➕ Book New
          </RouterLink>
        </div>
      </div>

      <div class="container-fluid px-4 pb-5">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else-if="sortedAppointments.length === 0" class="alert alert-info">
          No appointments yet. <RouterLink to="/patient/book-appointment">Book one now!</RouterLink>
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Time</th>
                <th>Doctor</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in sortedAppointments" :key="apt.id">
                <td>#{{ apt.id }}</td>
                <td>{{ apt.date }}</td>
                <td>{{ apt.time }}</td>
                <td>{{ apt.doctor_name }}</td>
                <td>
                  <span :class="['badge', getStatusClass(apt.status)]">
                    {{ apt.status }}
                  </span>
                </td>
                <td>
                  <!-- Cancel Action: Allowed for 'Booked' AND 'Action Pending' -->
                  <button 
                    v-if="apt.status === 'Booked' || apt.status === 'Action Pending'"
                    @click="cancelAppointment(apt.id)"
                    class="btn btn-sm btn-danger me-2"
                  >
                    ❌ Cancel
                  </button>

                  <!-- Reschedule Action (Only Action Pending & >24h Booked) -->
                  <button 
                    v-if="canReschedule(apt)"
                    @click="openRescheduleModal(apt)"
                    class="btn btn-sm btn-warning me-2"
                  >
                    🔄 Reschedule
                  </button>
                  
                  <!-- Diagnosis Action -->
                  <button 
                    v-if="apt.status === 'Completed' && apt.diagnosis"
                    @click="showDiagnosis(apt)"
                    class="btn btn-sm btn-info text-white"
                  >
                    📋 View Treatment
                  </button>
                  
                  <span v-if="['Completed', 'Cancelled'].includes(apt.status) && !apt.diagnosis" class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Reschedule Modal -->
    <div v-if="showRescheduleModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-warning text-dark">
            <h5 class="modal-title">🔄 Reschedule Appointment #{{ selectedRescheduleApt?.id }}</h5>
            <button type="button" class="btn-close" @click="showRescheduleModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Rescheduling appointment with <strong>Dr. {{ selectedRescheduleApt?.doctor_name }}</strong></p>
            <div v-if="rescheduleError" class="alert alert-danger">{{ rescheduleError }}</div>

            <div class="mb-3">
              <label class="form-label fw-bold">Select New Date:</label>
              <div v-if="loadingDates" class="text-center py-2">
                <div class="spinner-border spinner-border-sm text-primary"></div> Loading dates...
              </div>
              <select 
                v-else
                v-model="rescheduleData.date" 
                class="form-select"
                @change="fetchAvailability"
              >
                <option value="" disabled>Select an Available Date</option>
                <option v-for="date in availableDates" :key="date" :value="date">{{ date }}</option>
              </select>
            </div>

            <div v-if="loadingSlots" class="text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
            </div>

            <div v-else-if="rescheduleData.date">
              <label class="form-label fw-bold">Select New Time Slot:</label>
              <div v-if="availableSlots.length === 0" class="alert alert-warning">
                No available slots for this date
              </div>
              <div v-else class="row g-2 mb-3">
                <div v-for="slot in availableSlots" :key="slot.time" class="col-4">
                  <button 
                    @click="rescheduleData.time = slot.time"
                    :class="['btn', 'w-100', rescheduleData.time === slot.time ? 'btn-primary' : 'btn-outline-primary']"
                  >
                    {{ slot.time }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showRescheduleModal = false">Cancel</button>
            <button 
              type="button" 
              class="btn btn-success" 
              @click="confirmReschedule"
              :disabled="!rescheduleData.date || !rescheduleData.time || processingReschedule"
            >
              {{ processingReschedule ? 'Updating...' : 'Confirm Reschedule' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Treatment Detail Modal -->
    <div v-if="selectedTreatment" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
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

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { patientAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const appointments = ref([])
const sortOrder = ref('desc')
const selectedTreatment = ref(null)

// Reschedule State
const showRescheduleModal = ref(false)
const selectedRescheduleApt = ref(null)
const rescheduleData = ref({ date: '', time: '' })
const availableDates = ref([])
const availableSlots = ref([])
const loadingDates = ref(false)
const loadingSlots = ref(false)
const processingReschedule = ref(false)
const rescheduleError = ref('')

const sortedAppointments = computed(() => {
  return [...appointments.value].sort((a, b) => {
    const dateA = new Date(`${a.date} ${a.time}`)
    const dateB = new Date(`${b.date} ${b.time}`)
    return sortOrder.value === 'asc' ? dateA - dateB : dateB - dateA
  })
})

const getStatusClass = (status) => {
  const classes = {
    'Booked': 'bg-info',
    'Completed': 'bg-success',
    'Cancelled': 'bg-danger',
    'Missed': 'bg-warning text-dark',
    'Action Pending': 'bg-warning text-dark'
  }
  return classes[status] || 'bg-secondary'
}

// Logic to enable reschedule button
const canReschedule = (apt) => {
  // Allow rescheduling for:
  // 1. 'Action Pending' (This is set by doctor cancellation or passing date)
  // 2. 'Booked' appointments more than 24 hours in the future
  
  if (apt.status === 'Action Pending') return true;
  
  // Disable rescheduling for patient-initiated cancellations
  if (apt.status === 'Cancelled') return false;

  // Standard rule for Booked
  if (apt.status === 'Booked') {
    const aptDate = new Date(apt.date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const diffTime = aptDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
    
    // Allow only if > 24h (1 day) ahead
    return diffDays > 1;
  }

  return false;
}

const fetchAppointments = async () => {
  try {
    const response = await patientAPI.getAppointments()
    appointments.value = response
  } catch (err) {
    error.value = err.message || 'Failed to load appointments'
  } finally {
    loading.value = false
  }
}

const cancelAppointment = async (appointmentId) => {
  if (!confirm('Are you sure you want to cancel this appointment?')) return

  try {
    await patientAPI.cancelAppointment(appointmentId)
    fetchAppointments()
  } catch (err) {
    error.value = err.message || 'Failed to cancel appointment'
  }
}

const showDiagnosis = (apt) => {
  selectedTreatment.value = {
    diagnosis: apt.diagnosis,
    prescription: apt.prescription,
    notes: apt.notes
  }
}

// --- Reschedule Logic ---

const openRescheduleModal = async (apt) => {
  selectedRescheduleApt.value = apt
  showRescheduleModal.value = true
  rescheduleData.value = { date: '', time: '' }
  rescheduleError.value = ''
  availableDates.value = []
  availableSlots.value = []
  
  if (!apt.doctor_id) {
      rescheduleError.value = "Error: Doctor information missing. Please contact support."
      return;
  }

  loadingDates.value = true;
  try {
    const dates = await patientAPI.getAvailableDates(apt.doctor_id)
    availableDates.value = dates
  } catch (err) {
    rescheduleError.value = 'Failed to load available dates'
  } finally {
    loadingDates.value = false
  }
}

const fetchAvailability = async () => {
  if (!rescheduleData.value.date || !selectedRescheduleApt.value) return

  loadingSlots.value = true
  availableSlots.value = []
  rescheduleData.value.time = ''
  
  try {
    const response = await patientAPI.getDoctorAvailability(selectedRescheduleApt.value.doctor_id, rescheduleData.value.date)
    availableSlots.value = response
  } catch (err) {
    console.error('Failed to load slots', err)
  } finally {
    loadingSlots.value = false
  }
}

const confirmReschedule = async () => {
    if (!rescheduleData.value.date || !rescheduleData.value.time) return
    
    processingReschedule.value = true
    rescheduleError.value = ''
    
    try {
        await patientAPI.rescheduleAppointment(selectedRescheduleApt.value.id, rescheduleData.value)
        showRescheduleModal.value = false
        alert('Appointment rescheduled successfully!')
        fetchAppointments()
    } catch (err) {
        rescheduleError.value = err.message || 'Failed to reschedule'
    } finally {
        processingReschedule.value = false
    }
}

onMounted(fetchAppointments)
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