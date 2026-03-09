<template>
  <div class="row justify-content-center mt-4 pb-5">
    <div class="col-md-6">
      <div class="card card-3d p-5">
        <h2 class="text-center mb-4 text-primary fw-bold">Register</h2>
        
        <ul class="nav nav-pills nav-fill mb-4 p-2 rounded-pill" style="background:#e0e5ec; box-shadow: inset 5px 5px 10px rgb(163,177,198,0.6), inset -5px -5px 10px rgba(255,255,255, 0.5);">
          <li class="nav-item">
            <a class="nav-link rounded-pill" :class="{ 'active': role === 'student', 'btn-3d-primary': role === 'student', 'text-muted fw-bold': role !== 'student' }" href="#" @click.prevent="role = 'student'">Student</a>
          </li>
          <li class="nav-item">
            <a class="nav-link rounded-pill" :class="{ 'active': role === 'company', 'btn-3d-primary': role === 'company', 'text-muted fw-bold': role !== 'company' }" href="#" @click.prevent="role = 'company'">Company</a>
          </li>
        </ul>
        
        <div v-if="error" class="alert alert-danger shadow-sm border-0">{{ error }}</div>
        <div v-if="success" class="alert alert-success shadow-sm border-0">{{ success }}</div>

        <form @submit.prevent="handleRegister">
          <!-- Common Fields -->
          <div class="mb-3">
            <label class="form-label text-secondary fw-semibold">Username</label>
            <input type="text" class="form-control input-3d" v-model="form.username" required>
          </div>
          <div class="mb-3">
            <label class="form-label text-secondary fw-semibold">Email</label>
            <input type="email" class="form-control input-3d" v-model="form.email" required>
          </div>
          <div class="mb-3">
            <label class="form-label text-secondary fw-semibold">Password</label>
            <input type="password" class="form-control input-3d" v-model="form.password" required>
          </div>
          
          <!-- Student Fields -->
          <div v-if="role === 'student'">
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">Full Name</label>
              <input type="text" class="form-control input-3d" v-model="form.name" required>
            </div>
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">Branch</label>
              <input type="text" class="form-control input-3d" v-model="form.branch" required placeholder="e.g. Computer Science">
            </div>
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label text-secondary fw-semibold">CGPA</label>
                <input type="number" step="0.01" class="form-control input-3d" v-model="form.cgpa" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label text-secondary fw-semibold">Graduation Year</label>
                <input type="number" class="form-control input-3d" v-model="form.year" required>
              </div>
            </div>
          </div>
          
          <!-- Company Fields -->
          <div v-if="role === 'company'">
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">Company Name</label>
              <input type="text" class="form-control input-3d" v-model="form.company_name" required>
            </div>
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">HR Contact (Email/Phone)</label>
              <input type="text" class="form-control input-3d" v-model="form.hr_contact" required>
            </div>
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">Website URL</label>
              <input type="url" class="form-control input-3d" v-model="form.website" required>
            </div>
          </div>
          
          <button type="submit" class="btn btn-3d-primary w-100 py-3 mt-4">Register as {{ role === 'student' ? 'Student' : 'Company' }}</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../utils/axios';

const role = ref('student');
const error = ref('');
const success = ref('');

const form = ref({
  username: '', email: '', password: '', name: '', branch: '', cgpa: '', year: '', 
  company_name: '', hr_contact: '', website: ''
});

const handleRegister = async () => {
  error.value = '';
  success.value = '';
  try {
    const endpoint = role.value === 'student' ? '/auth/register/student' : '/auth/register/company';
    await api.post(endpoint, form.value);
    success.value = `Successfully registered! ${role.value === 'company' ? 'Please wait for Admin approval to login.' : 'You can now login.'}`;
    form.value = {
      username: '', email: '', password: '', name: '', branch: '', cgpa: '', year: '', 
      company_name: '', hr_contact: '', website: ''
    };
  } catch (err) {
    error.value = err.response?.data?.msg || 'Registration failed';
  }
};
</script>
