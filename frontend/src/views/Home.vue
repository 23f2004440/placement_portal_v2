<template>
  <div class="row min-vh-100 align-items-center justify-content-center pb-5" style="margin-top:-80px">
    <div class="col-md-8 text-center pt-5">
      <h1 class="display-4 fw-bold text-primary mb-4" style="text-shadow: 2px 2px 5px rgba(0,0,0,0.1)">Welcome to Placement Portal</h1>
      <p class="lead text-secondary mb-5">A unified 3D-styled platform for Institutes, Companies, and Students to manage recruitment activities seamlessly.</p>
      
      <div class="row mt-4">
        <div class="col-md-4 mb-4">
          <div class="card card-3d p-4 h-100">
            <h3 class="mb-3">Institute Admin</h3>
            <p class="text-muted">Manage drives, approve companies, and oversee all student recruitment activities.</p>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card card-3d p-4 h-100">
            <h3 class="mb-3">Companies</h3>
            <p class="text-muted">Create placement drives, shortlist candidates, and hire top talent from the institute.</p>
          </div>
        </div>
        <div class="col-md-4 mb-4">
          <div class="card card-3d p-4 h-100">
            <h3 class="mb-3">Students</h3>
            <p class="text-muted">Apply for jobs, track applications, and download your entire activity history instantly.</p>
          </div>
        </div>
      </div>
      
      <div class="mt-5">
        <router-link to="/register" class="btn btn-3d-primary btn-lg px-5 py-3 rounded-pill me-3">Get Started</router-link>
        <router-link to="/login" class="btn btn-3d btn-lg px-5 py-3 rounded-pill">Login</router-link>
      </div>
    </div>
  </div>
</template>
