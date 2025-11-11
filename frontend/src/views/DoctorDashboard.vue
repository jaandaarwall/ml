<template>
  <div>
    <h1>Doctor Dashboard</h1>
    <DoctorAvailability />
    <DoctorAppointments />
  </div>
</template>

<script setup>
import DoctorAvailability from '@/components/DoctorAvailability.vue';
import DoctorAppointments from '@/components/DoctorAppointments.vue';
</script>
