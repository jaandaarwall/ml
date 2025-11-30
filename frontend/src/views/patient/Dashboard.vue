<template>
  <div class="dashboard-content">
    <div class="row mb-4">
      <div class="col-12">
        <div class="card bg-white border-0 shadow-sm">
          <div class="card-body p-4 d-flex align-items-center justify-content-between">
            <div>
              <h2 class="fw-bold text-primary mb-1">Hello, {{ userName }}! 👋</h2>
              <p class="text-muted mb-0">Here's your health overview for today.</p>
            </div>
            <div class="d-none d-md-block display-4 text-primary opacity-25">🏥</div>
          </div>
        </div>
      </div>
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-4">
        <div class="card h-100 bg-primary text-white border-0 position-relative overflow-hidden">
          <div class="card-body position-relative z-1">
            <h6 class="text-uppercase opacity-75 mb-2">Upcoming</h6>
            <h2 class="display-4 fw-bold mb-0">{{ dashboard.upcoming_appointments.length }}</h2>
            <p class="mb-0 mt-2">Appointments</p>
          </div>
          <div class="position-absolute opacity-25" style="right: -20px; bottom: -20px; font-size: 8rem;">📅</div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card h-100 border-0">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div class="bg-success bg-opacity-10 p-3 rounded-circle me-3">
                <span class="fs-4">✅</span>
              </div>
              <div>
                <h6 class="text-muted text-uppercase mb-0">Completed Visits</h6>
                <h3 class="fw-bold mb-0">{{ dashboard.past_appointments.length }}</h3>
              </div>
            </div>
            <RouterLink to="/patient/history" class="btn btn-sm btn-outline-success w-100">View History</RouterLink>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card h-100 border-0">
          <div class="card-body">
            <h6 class="text-muted text-uppercase mb-3">Quick Actions</h6>
            <RouterLink to="/patient/book-appointment" class="btn btn-primary w-100 mb-2 py-2">
              + Book New Appointment
            </RouterLink>
            <RouterLink to="/patient/profile" class="btn btn-light w-100 text-muted">
              Update Profile
            </RouterLink>
          </div>
        </div>
      </div>
    </div>

    <div class="card border-0 mb-4">
      <div class="card-header bg-transparent d-flex justify-content-between align-items-center py-3">
        <h5 class="mb-0 fw-bold">📅 Upcoming Schedule</h5>
        <RouterLink to="/patient/appointments" class="btn btn-sm btn-light text-primary fw-bold">View All</RouterLink>
      </div>
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0">
          <thead class="bg-light text-secondary small text-uppercase">
            <tr>
              <th class="border-0 ps-4">Date & Time</th>
              <th class="border-0">Doctor</th>
              <th class="border-0">Department</th>
              <th class="border-0">Status</th>
            </tr>
          </thead>
          <tbody>
             <tr v-if="dashboard.upcoming_appointments.length === 0">
                <td colspan="4" class="text-center py-5 text-muted">
                  <div class="fs-1 mb-2">☕</div>
                  No upcoming appointments. Stay healthy!
                </td>
             </tr>
             <tr v-for="apt in dashboard.upcoming_appointments" :key="apt.id">
               <td class="ps-4">
                 <div class="fw-bold text-dark">{{ apt.date }}</div>
                 <small class="text-muted">{{ apt.time }}</small>
               </td>
               <td class="fw-medium text-primary">{{ apt.doctor_name }}</td>
               <td><span class="badge bg-light text-dark border">{{ apt.department }}</span></td>
               <td><span class="badge bg-info bg-opacity-10 text-info px-3 py-2">{{ apt.status }}</span></td>
             </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { patientAPI } from '../../services/api'

const authStore = useAuthStore()
const loading = ref(true)
const dashboard = ref({ upcoming_appointments: [], past_appointments: [] })
const userName = computed(() => authStore.user?.email?.split('@')[0] || 'Patient')

onMounted(async () => {
  try {
    dashboard.value = await patientAPI.getDashboard()
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})
</script>