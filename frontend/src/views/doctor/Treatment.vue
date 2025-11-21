<!-- views/doctor/Treatment.vue -->
<template>
  <div class="container-fluid">
    <div class="page-header">
      <h1>💊 Treatment Record</h1>
    </div>
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border"></div>
        </div>
        <div v-else>
          <form @submit.prevent="saveTreatment">
            <div class="mb-3">
              <label class="form-label">Diagnosis</label>
              <textarea v-model="treatment.diagnosis" class="form-control" rows="3" required></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Prescription</label>
              <textarea v-model="treatment.prescription" class="form-control" rows="3"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Notes</label>
              <textarea v-model="treatment.notes" class="form-control" rows="3"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-check-label">
                <input v-model="treatment.follow_up_required" type="checkbox" class="form-check-input">
                Follow-up Required
              </label>
            </div>
            <div v-if="treatment.follow_up_required" class="mb-3">
              <label class="form-label">Follow-up Date</label>
              <input v-model="treatment.follow_up_date" type="date" class="form-control">
            </div>
            <button type="submit" class="btn btn-success">💾 Save Treatment</button>
          </form>
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
const treatment = ref({
  diagnosis: '',
  prescription: '',
  notes: '',
  follow_up_required: false,
  follow_up_date: ''
})
const saveTreatment = async () => {
  try {
    await doctorAPI.saveTreatment(route.params.id, treatment.value)
    alert('Treatment saved successfully')
  } catch (err) {
    alert(err.message)
  }
}
onMounted(async () => {
  try {
    const response = await doctorAPI.getTreatment(route.params.id)
    if (Object.keys(response).length > 0) {
      treatment.value = response
    }
  } finally {
    loading.value = false
  }
})
</script>
