<template>
  <div>
    <h1>Admin Dashboard</h1>
    <div v-if="!editingDoctor">
      <button class="btn btn-primary mb-3" @click="editingDoctor = {}">Add Doctor</button>
      <AdminDoctorList @edit="editDoctor" />
    </div>
    <div v-else>
      <AdminDoctorForm :doctor="editingDoctor" @success="onSuccess" @cancel="editingDoctor = null" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AdminDoctorList from '@/components/AdminDoctorList.vue';
import AdminDoctorForm from '@/components/AdminDoctorForm.vue';

const editingDoctor = ref(null);

const editDoctor = (doctor) => {
  editingDoctor.value = doctor;
};

const onSuccess = () => {
  editingDoctor.value = null;
};
</script>
