<template>
  <div class="row justify-content-center mt-5">
    <div class="col-md-5">
      <div class="card card-3d p-5">
        <h2 class="text-center mb-4 text-primary fw-bold">Login</h2>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        
        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="form-label text-secondary fw-semibold">Username</label>
            <input type="text" class="form-control input-3d" v-model="username" required>
          </div>
          <div class="mb-4">
            <label class="form-label text-secondary fw-semibold">Password</label>
            <input type="password" class="form-control input-3d" v-model="password" required>
          </div>
          <button type="submit" class="btn btn-3d-primary w-100 py-3 mt-3 shadow-none">Sign In</button>
        </form>
        
        <p class="text-center mt-4 text-muted">Don't have an account? <router-link to="/register" class="text-decoration-none fw-bold text-primary">Register here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../utils/axios';

const username = ref('');
const password = ref('');
const error = ref('');
const router = useRouter();

const handleLogin = async () => {
  try {
    const res = await api.post('/auth/login', {
      username: username.value,
      password: password.value
    });
    
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('role', res.data.role);
    localStorage.setItem('user_id', res.data.user_id);
    
    if (res.data.role === 'admin') router.push('/admin');
    else if (res.data.role === 'company') router.push('/company');
    else router.push('/student');
    
  } catch (err) {
    error.value = err.response?.data?.msg || 'Login failed';
  }
};
</script>
