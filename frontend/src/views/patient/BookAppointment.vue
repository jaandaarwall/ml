<template>
  <div class="d-flex" style="min-height: 100vh;">
    <div class="flex-grow-1">
      <div class="bg-white border-bottom p-4 mb-4">
        <h1 class="mb-1">🔍 Find Doctors</h1>
        <p class="text-muted mb-0">Search doctors by specialization</p>
      </div>

      <div class="container-fluid px-4 pb-5">
        <div class="row mb-4">
          <div class="col-lg-8">
            <div class="card">
              <div class="card-body">
                <label class="form-label fw-bold mb-3">Select Specialization:</label>
                <div class="d-flex gap-2">
                  <select v-model="selectedDept" class="form-select" @change="fetchDoctors">
                    <option value="">All Specializations</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                      {{ dept.name }}
                    </option>
                  </select>
                  <button @click="fetchDoctors" class="btn btn-primary">
                    🔍 Filter
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="loadingDoctors" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>

        <div v-else class="row g-4">
          <div v-if="filteredDoctors.length === 0" class="col-12">
            <div class="alert alert-info">
              No doctors available for this specialization. Try selecting a different one.
            </div>
          </div>

          <div v-for="doctor in filteredDoctors" :key="doctor.id" class="col-md-6 col-lg-4">
            <div class="card h-100">
              <div class="card-body text-center">
                <div class="display-4 mb-2">👨‍⚕️</div>
                <h5 class="card-title">{{ doctor.name }}</h5>
                <p class="text-muted small mb-1">
                  <span class="badge bg-info">{{ doctor.department }}</span>
                </p>
                <p class="text-muted small mb-2">
                  🎓 {{ doctor.qualification || 'N/A' }}
                </p>
                <p class="text-muted small mb-3">
                  ⏰ {{ doctor.experience_years || 0 }} years experience
                </p>
                <p class="text-muted small mb-3">
                  ✉️ {{ doctor.email }}
                </p>
                <button 
                  @click="selectDoctor(doctor)" 
                  class="btn btn-primary w-100"
                >
                  📅 Book Appointment
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-if="showBookingModal" class="modal d-block" style="background: rgba(0,0,0,0.5); display: block !important;">
          <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
              <div class="modal-header bg-primary text-white">
                <h5 class="modal-title">📅 Book Appointment with {{ selectedDoctor?.name }}</h5>
                <button type="button" class="btn-close btn-close-white" @click="showBookingModal = false"></button>
              </div>
              <div class="modal-body">
                <div v-if="bookingError" class="alert alert-danger">{{ bookingError }}</div>

                <div class="mb-3">
                  <label class="form-label fw-bold">Select Date:</label>
                  <div v-if="loadingDates" class="text-center py-2">
                    <div class="spinner-border spinner-border-sm text-primary"></div> Loading dates...
                  </div>
                  <select 
                    v-else
                    v-model="bookingData.date" 
                    class="form-select"
                    @change="fetchAvailability"
                  >
                    <option value="" disabled>Select an Available Date</option>
                    <option v-for="date in availableDates" :key="date" :value="date">{{ date }}</option>
                  </select>
                  <small v-if="availableDates.length === 0 && !loadingDates" class="text-danger">
                    No available dates for this doctor in the next 30 days.
                  </small>
                </div>

                <div v-if="loadingSlots" class="text-center py-3">
                  <div class="spinner-border spinner-border-sm text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                </div>

                <div v-else-if="bookingData.date">
                  <label class="form-label fw-bold">Select Time Slot:</label>
                  <div v-if="availableSlots.length === 0" class="alert alert-warning">
                    No available slots for this date
                  </div>
                  <div v-else class="row g-2 mb-3">
                    <div v-for="slot in availableSlots" :key="slot.time" class="col-4">
                      <button 
                        @click="bookingData.time = slot.time"
                        :class="['btn', 'w-100', bookingData.time === slot.time ? 'btn-primary' : 'btn-outline-primary']"
                      >
                        {{ slot.time }}
                      </button>
                    </div>
                  </div>
                </div>

                <div class="mb-3">
                  <label class="form-label fw-bold">Reason for Visit:</label>
                  <textarea 
                    v-model="bookingData.reason" 
                    class="form-control" 
                    rows="3" 
                    placeholder="Describe your symptoms or reason for visit..."
                  ></textarea>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" @click="showBookingModal = false">Cancel</button>
                <button 
                  type="button" 
                  class="btn btn-success" 
                  @click="bookAppointment"
                  :disabled="!bookingData.date || !bookingData.time || bookingAppointment"
                >
                  {{ bookingAppointment ? 'Booking...' : '✅ Confirm Booking' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { patientAPI, departmentsAPI } from '../../services/api'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loadingDoctors = ref(false)
const loadingSlots = ref(false)
const loadingDates = ref(false)
const bookingAppointment = ref(false)
const error = ref('')
const bookingError = ref('')

const departments = ref([])
const doctors = ref([])
const availableDates = ref([])
const availableSlots = ref([])
const selectedDept = ref(route.query.department_id || '')
const selectedDoctor = ref(null)
const showBookingModal = ref(false)

const bookingData = ref({
  date: '',
  time: '',
  reason: ''
})

const filteredDoctors = computed(() => {
  if (!selectedDept.value) return doctors.value
  return doctors.value.filter(doc => {
    const dept = departments.value.find(d => d.name === doc.department)
    return dept && dept.id == selectedDept.value
  })
})

const fetchDepartments = async () => {
  try {
    const response = await departmentsAPI.getDepartments()
    departments.value = response
  } catch (err) {
    console.error('Failed to load departments', err)
  }
}

const fetchDoctors = async () => {
  loadingDoctors.value = true
  error.value = ''
  try {
    const response = await patientAPI.getDoctors(selectedDept.value || null)
    doctors.value = response
  } catch (err) {
    error.value = err.message || 'Failed to load doctors'
  } finally {
    loadingDoctors.value = false
  }
}

const selectDoctor = async (doctor) => {
  selectedDoctor.value = doctor
  showBookingModal.value = true
  bookingData.value = { date: '', time: '', reason: '' }
  bookingError.value = ''
  availableDates.value = []
  availableSlots.value = []
  
  loadingDates.value = true
  try {
    const dates = await patientAPI.getAvailableDates(doctor.id)
    availableDates.value = dates
  } catch (err) {
    bookingError.value = 'Failed to load available dates'
  } finally {
    loadingDates.value = false
  }
}

const fetchAvailability = async () => {
  if (!bookingData.value.date || !selectedDoctor.value) return

  loadingSlots.value = true
  availableSlots.value = []
  bookingData.value.time = ''
  
  try {
    const response = await patientAPI.getDoctorAvailability(selectedDoctor.value.id, bookingData.value.date)
    availableSlots.value = response
  } catch (err) {
    console.error('Failed to load slots', err)
  } finally {
    loadingSlots.value = false
  }
}

const bookAppointment = async () => {
  if (!bookingData.value.date || !bookingData.value.time) {
    bookingError.value = 'Please select date and time'
    return
  }

  bookingAppointment.value = true
  bookingError.value = ''

  try {
    const response = await patientAPI.bookAppointment(selectedDoctor.value.id, bookingData.value)
    showBookingModal.value = false
    router.push(`/payment/${response.payment_id}`)
  } catch (err) {
    bookingError.value = err.message || 'Failed to book appointment'
  } finally {
    bookingAppointment.value = false
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

onMounted(() => {
  fetchDepartments()
  fetchDoctors()
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

.modal {
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}
</style>