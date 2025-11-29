<template>
  <div class="d-flex" style="min-height: 100vh; background-color: #f8f9fa;">
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
                          <div v-if="!isPast(avail.date)" class="btn-group">
                            <button 
                              @click="openSlotsModal(avail)" 
                              class="btn btn-sm btn-outline-primary"
                            >
                              ✏️ Edit
                            </button>
                            <button 
                              @click="deleteAvailability(avail)" 
                              class="btn btn-sm btn-danger"
                            >
                              🗑️
                            </button>
                          </div>
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

    <!-- Slots Modal -->
    <div v-if="showSlotsModal" class="modal d-block" style="background: rgba(0,0,0,0.5);">
      <div class="modal-dialog modal-dialog-centered modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Manage Slots for {{ selectedAvail?.date }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="showSlotsModal = false"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingSlots" class="text-center py-3">
              <div class="spinner-border text-primary"></div>
            </div>
            <div v-else>
               <p class="text-muted mb-3">You can delete individual 30-minute slots below. If a slot has a booking, the patient will be notified.</p>
               <div class="list-group">
                  <div v-for="slot in generatedSlots" :key="slot.time" 
                       class="list-group-item d-flex justify-content-between align-items-center">
                     <div>
                        <strong>{{ slot.time }}</strong> - {{ slot.endTime }}
                        <span v-if="slot.hasBooking" class="badge bg-warning text-dark ms-2">
                           ⚠️ Booked
                        </span>
                     </div>
                     <button @click="deleteSlot(slot)" class="btn btn-sm btn-outline-danger">
                        Delete Slot
                     </button>
                  </div>
               </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showSlotsModal = false">Close</button>
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

// Slots Management State
const showSlotsModal = ref(false)
const selectedAvail = ref(null)
const generatedSlots = ref([])
const loadingSlots = ref(false)

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

// --- Slots Logic ---

const openSlotsModal = async (avail) => {
  selectedAvail.value = avail
  showSlotsModal.value = true
  loadingSlots.value = true
  generatedSlots.value = []

  try {
    // 1. Fetch appointments for this date to check bookings
    // Updated getAppointments API to support ?date= parameter
    const appointments = await doctorAPI.getAppointments(avail.date)
    
    // 2. Generate 30-min slots from start_time to end_time
    const slots = []
    let current = new Date(`2000-01-01T${avail.start_time}`)
    const end = new Date(`2000-01-01T${avail.end_time}`)

    while (current < end) {
      const timeStr = current.toTimeString().substring(0, 5) // "09:00"
      
      // Calculate next slot time
      current.setMinutes(current.getMinutes() + 30)
      const endTimeStr = current.toTimeString().substring(0, 5)

      // Check if booked
      const isBooked = appointments.some(apt => 
        apt.time === timeStr && apt.status === 'Booked'
      )

      slots.push({
        time: timeStr,
        endTime: endTimeStr,
        hasBooking: isBooked
      })
    }
    generatedSlots.value = slots

  } catch (err) {
    console.error("Error loading slots:", err)
    alert("Failed to load slot details.")
    showSlotsModal.value = false
  } finally {
    loadingSlots.value = false
  }
}

const deleteSlot = async (slot) => {
    let message = `Delete the slot ${slot.time} - ${slot.endTime}?`
    
    if (slot.hasBooking) {
        message = `⚠️ WARNING: This slot is currently BOOKED.\n\nDeleting it will cancel the appointment and send an email notification to the patient.\n\nAre you sure you want to delete this slot?`
    }
    
    if (confirm(message)) {
        try {
            await doctorAPI.deleteAvailabilitySlot(selectedAvail.value.id, slot.time)
            alert('Slot removed successfully.')
            showSlotsModal.value = false // Close to refresh state
            fetchAvailabilities() // Refresh main list
        } catch (err) {
            alert(err.message || "Failed to delete slot")
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

.modal.d-block {
  display: block !important;
}
</style>