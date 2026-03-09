<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-3d p-3">
      <div class="container">
        <router-link class="navbar-brand fw-bold mb-0 h1 text-primary" to="/" style="font-size: 1.5rem;">Placement Portal</router-link>
        
        <div class="collapse navbar-collapse justify-content-end">
          <ul class="navbar-nav align-items-center">
            <li class="nav-item" v-if="!isLoggedIn">
              <router-link class="nav-link nav-link-3d" to="/login">Login</router-link>
            </li>
            <li class="nav-item" v-if="!isLoggedIn">
              <router-link class="nav-link nav-link-3d" to="/register">Register</router-link>
            </li>
            
            <li class="nav-item" v-if="isLoggedIn && role === 'admin'">
              <router-link class="nav-link nav-link-3d" to="/admin">Admin Dashboard</router-link>
            </li>
            <li class="nav-item" v-if="isLoggedIn && role === 'company'">
              <router-link class="nav-link nav-link-3d" to="/company">Company Dashboard</router-link>
            </li>
            <li class="nav-item" v-if="isLoggedIn && role === 'student'">
              <router-link class="nav-link nav-link-3d" to="/student">Student Dashboard</router-link>
            </li>
            
            <li class="nav-item" v-if="isLoggedIn">
              <button class="btn btn-sm btn-3d-danger ms-3 mt-1" @click="logout">Logout</button>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <div class="container mt-4 pb-5">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const isLoggedIn = ref(false);
const role = ref('');

watchEffect(() => {
  // trigger reactivty
  route.name; 
  isLoggedIn.value = !!localStorage.getItem('token');
  role.value = localStorage.getItem('role') || '';
});

const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('role');
  localStorage.removeItem('user_id');
  isLoggedIn.value = false;
  router.push('/login');
};
</script>
