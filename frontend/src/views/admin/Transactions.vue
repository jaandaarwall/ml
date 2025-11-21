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
        <RouterLink to="/admin/appointments" class="nav-link text-white mb-2">
          📅 All Appointments
        </RouterLink>
        <RouterLink to="/admin/transactions" class="nav-link text-white mb-2 active-nav">
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
      <div class="bg-white border-bottom p-4">
        <h1 class="mb-1">💰 Transaction History</h1>
        <p class="text-muted mb-0">View details of all payment transactions</p>
      </div>

      <!-- Content -->
      <div class="flex-grow-1 p-4 overflow-auto">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <div v-else-if="transactions.length === 0" class="alert alert-info text-center">
          No transactions found
        </div>

        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Date</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Appt ID</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="txn in transactions" :key="txn.id">
                <td><span class="badge bg-light text-dark">#{{ txn.id }}</span></td>
                <td>{{ txn.date }}</td>
                <td class="fw-bold">{{ txn.patient }}</td>
                <td>Dr. {{ txn.doctor }}</td>
                <td class="text-success fw-bold">₹{{ txn.amount }}</td>
                <td>
                  <span v-if="txn.status === 'Success'" class="badge bg-success">
                    {{ txn.status }}
                  </span>
                  <span v-else-if="txn.status === 'Pending'" class="badge bg-warning text-dark">
                    {{ txn.status }}
                  </span>
                  <span v-else class="badge bg-danger">
                    {{ txn.status }}
                  </span>
                </td>
                <td>#{{ txn.appointment_id }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { adminAPI } from '../../services/api'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')
const transactions = ref([])

const fetchTransactions = async () => {
  try {
    const response = await adminAPI.getTransactions()
    transactions.value = response
    loading.value = false
  } catch (err) {
    error.value = err.message
    loading.value = false
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

onMounted(fetchTransactions)
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