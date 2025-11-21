<!-- views/doctor/PatientHistory.vue -->
<template>
  <div class="container-fluid">
    <div class="page-header">
      <h1>📋 Patient History</h1>
    </div>
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border"></div>
        </div>
        <div v-else-if="history.length === 0" class="no-data">
          <p>No history</p>
        </div>
        <div v-else>
          <div v-for="record in history" :key="record.date" class="card mb-3">
            <div class="card-body">
              <h6>{{ record.date }}</h6>
              <p><strong>Diagnosis:</strong> {{ record.diagnosis }}</p>
              <p><strong>Prescription:</strong> {{ record.prescription }}</p>
              <p><strong>Notes:</strong> {{ record.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { doctorAPI } from '../../services/api'
const route = useRoute()
const loading = ref(true)
const history = ref([])
onMounted(async () => {
  try {
    const response = await doctorAPI.getPatientHistory(route.params.id)
    history.value = response
  } finally {
    loading.value = false
  }
})
</script>
