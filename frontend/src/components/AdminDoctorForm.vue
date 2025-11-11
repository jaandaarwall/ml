<template>
  <div>
    <h2>{{ doctor ? 'Edit' : 'Add' }} Doctor</h2>
    <form @submit.prevent="handleSubmit">
      <div class="mb-3">
        <label for="fullName" class="form-label">Full Name</label>
        <input type="text" class="form-control" id="fullName" v-model="form.full_name" required>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Email address</label>
        <input type="email" class="form-control" id="email" v-model="form.email" required>
      </div>
      <div class="mb-3">
        <label for="password" class="form-label">Password</label>
        <input type="password" class="form-control" id="password" v-model="form.password" :required="!doctor">
      </div>
      <div class="mb-3">
        <label for="department" class="form-label">Department</label>
        <select class="form-control" id="department" v-model="form.department_id" required>
          <!-- In a real app, you would fetch departments from the API -->
          <option value="1">Cardiology</option>
          <option value="2">Neurology</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="qualification" class="form-label">Qualification</label>
        <input type="text" class="form-control" id="qualification" v-model="form.qualification" required>
      </div>
      <div class="mb-3">
        <label for="experience" class="form-label">Experience (Years)</label>
        <input type="number" class="form-control" id="experience" v-model="form.experience_years" required>
      </div>
      <button type="submit" class="btn btn-primary">{{ doctor ? 'Update' : 'Add' }}</button>
      <button type="button" class="btn btn-secondary" @click="$emit('cancel')">Cancel</button>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import axios from 'axios';
import { useAuthStore } from '@/store/auth';

const props = defineProps({
  doctor: Object,
});

const emit = defineEmits(['success', 'cancel']);

const authStore = useAuthStore();
const form = ref({
  full_name: '',
  email: '',
  password: '',
  department_id: '',
  qualification: '',
  experience_years: '',
});

watch(() => props.doctor, (newDoctor) => {
  if (newDoctor) {
    form.value = { ...newDoctor, password: '' };
  } else {
    form.value = {
      full_name: '',
      email: '',
      password: '',
      department_id: '',
      qualification: '',
      experience_years: '',
    };
  }
});

const handleSubmit = async () => {
  if (props.doctor) {
    await axios.put(`http://localhost:5000/admin/doctor/${props.doctor.id}`, form.value, {
      headers: { 'Authentication-Token': authStore.token },
    });
  } else {
    await axios.post('http://localhost:5000/admin/doctor', form.value, {
      headers: { 'Authentication-Token': authStore.token },
    });
  }
  emit('success');
};
</script>
