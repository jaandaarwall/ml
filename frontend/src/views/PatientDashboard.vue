<template>
  <div>
    <h1>Patient Dashboard</h1>
    <div v-if="!bookingDoctor">
      <PatientDoctorSearch @book="bookDoctor" />
      <PatientAppointments />
    </div>
    <div v-else>
      <PatientBookingForm :doctor="bookingDoctor" @success="onSuccess" @cancel="bookingDoctor = null" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import PatientDoctorSearch from '@/components/PatientDoctorSearch.vue';
import PatientAppointments from '@/components/PatientAppointments.vue';
import PatientBookingForm from '@/components/PatientBookingForm.vue';

const bookingDoctor = ref(null);

const bookDoctor = (doctor) => {
  bookingDoctor.value = doctor;
};

const onSuccess = () => {
  bookingDoctor.value = null;
};
</script>
