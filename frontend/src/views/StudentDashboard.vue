<template>
  <div>
    <h2 class="text-primary fw-bold mb-4">Student Dashboard</h2>
    
    <div class="row mb-5">
      <div class="col-md-6">
        <div class="card card-3d p-4 h-100">
          <h4 class="mb-4">My Profile</h4>
          <form @submit.prevent="updateProfile">
            <div v-if="profileSuccess" class="alert alert-success py-2">{{ profileSuccess }}</div>
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">Name</label>
              <input type="text" class="form-control input-3d" v-model="profile.name" required>
            </div>
            <div class="row">
              <div class="col-md-4 mb-3">
                <label class="form-label text-secondary fw-semibold">Branch</label>
                <input type="text" class="form-control input-3d" v-model="profile.branch" required>
              </div>
              <div class="col-md-4 mb-3">
                <label class="form-label text-secondary fw-semibold">CGPA</label>
                <input type="number" step="0.01" class="form-control input-3d" v-model="profile.cgpa" required>
              </div>
              <div class="col-md-4 mb-3">
                <label class="form-label text-secondary fw-semibold">Year</label>
                <input type="number" class="form-control input-3d" v-model="profile.year" required>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label text-secondary fw-semibold">Resume (PDF)</label>
              
              <div v-if="profile.resume_path" class="mb-2 p-2 border rounded bg-light d-flex justify-content-between align-items-center" style="box-shadow: inset 2px 2px 5px #d1d9e6, inset -2px -2px 5px #ffffff;">
                <div>
                  <i class="bi bi-file-earmark-pdf-fill text-danger fs-5 me-2"></i>
                  <span class="fw-bold text-dark small">Current Resume</span>
                </div>
                <a :href="`http://localhost:5000/api/student/view-resume/${profile.resume_path}`" target="_blank" class="btn btn-sm btn-outline-primary rounded-pill">
                  View
                </a>
              </div>
              
              <div class="d-flex align-items-center mt-2">
                <input type="file" ref="resumeInput" class="form-control input-3d me-2" accept=".pdf" @change="handleFileUpload">
                <button type="button" class="btn btn-3d-secondary" @click="uploadResume" :disabled="!selectedFile || uploading">
                  {{ uploading ? 'Uploading...' : (profile.resume_path ? 'Update' : 'Upload') }}
                </button>
              </div>
            </div>
            <button type="submit" class="btn btn-3d-primary mt-2">Update Profile</button>
          </form>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card card-3d p-4 h-100 d-flex flex-column justify-content-center align-items-center text-center">
          <h4 class="text-secondary">Total Applications</h4>
          <h1 class="display-1 fw-bold text-primary mb-4">{{ profile.total_applications || 0 }}</h1>
          <div>
            <button class="btn btn-3d-success me-2" @click="activeTab = 'drives'">Browse Drives</button>
            <button class="btn btn-3d" @click="activeTab = 'history'">My History</button>
          </div>
        </div>
      </div>
    </div>
    
    <ul class="nav nav-pills nav-fill mb-4 p-2 rounded-pill" style="background:#e0e5ec; box-shadow: inset 5px 5px 10px rgb(163,177,198,0.6), inset -5px -5px 10px rgba(255,255,255, 0.5);">
      <li class="nav-item">
        <a class="nav-link rounded-pill" :class="{'active btn-3d-primary': activeTab === 'drives', 'btn-3d text-muted fw-bold': activeTab !== 'drives'}" href="#" @click.prevent="activeTab = 'drives'">Available Drives</a>
      </li>
      <li class="nav-item">
        <a class="nav-link rounded-pill" :class="{'active btn-3d-primary': activeTab === 'history', 'btn-3d text-muted fw-bold': activeTab !== 'history'}" href="#" @click.prevent="activeTab = 'history'">Application History</a>
      </li>
      <li class="nav-item">
        <a class="nav-link rounded-pill" :class="{'active btn-3d-primary': activeTab === 'notifications', 'btn-3d text-muted fw-bold': activeTab !== 'notifications'}" href="#" @click.prevent="activeTab = 'notifications'">Notifications <span v-if="unreadCount > 0" class="badge bg-danger">{{unreadCount}}</span></a>
      </li>
    </ul>

    <!-- Available Drives -->
    <div v-if="activeTab === 'drives'" class="row">
      <div class="col-md-6 mb-4" v-for="d in availableDrives" :key="d.id">
        <div class="card card-3d p-4 h-100 d-flex flex-column">
          <div class="d-flex justify-content-between align-items-start mb-2">
            <h4 class="fw-bold text-primary mb-0">{{ d.job_title }}</h4>
            <span class="badge bg-secondary">{{ d.application_deadline }}</span>
          </div>
          <h5 class="text-muted mb-3">{{ d.company_name }}</h5>
          <p class="mb-3 flex-grow-1" style="white-space: pre-wrap;">{{ d.job_description }}</p>
          <div class="mb-4">
            <strong>Eligibility:</strong> {{ d.eligibility_branch || 'Any' }} | Min CGPA: {{ d.eligibility_cgpa }} | Year: {{ d.eligibility_year }}
            <br>
            <span v-if="!d.is_eligible" class="text-danger small fw-bold"><i class="bi bi-x-circle"></i> Not Eligible</span>
            <span v-else class="text-success small fw-bold">Eligible</span>
          </div>
          <div class="mt-auto">
            <button v-if="d.has_applied" class="btn btn-3d w-100" disabled>Already Applied</button>
            <button v-else-if="!d.is_eligible" class="btn btn-3d w-100" disabled>Not Eligible</button>
            <button v-else class="btn btn-3d-primary w-100" @click="applyForDrive(d.id)">Apply Now</button>
          </div>
        </div>
      </div>
      <div v-if="availableDrives.length === 0" class="col-12 text-center mt-4">
        <p class="text-muted">No approved placement drives available at the moment.</p>
      </div>
    </div>
    
    <!-- Application History -->
    <div v-if="activeTab === 'history'" class="card card-3d p-4">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h4 class="mb-0">My Applications</h4>
        <button class="btn btn-sm btn-3d-success" @click="triggerExport" :disabled="exporting">
          {{ exporting ? 'Exporting...' : 'Export as CSV' }}
        </button>
      </div>
      
      <div v-if="exportMsg" class="alert alert-info py-2">{{ exportMsg }}</div>
      
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company</th>
              <th>Job Title</th>
              <th>Date Applied</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="app in history" :key="app.id">
              <td>{{ app.id }}</td>
              <td class="fw-bold">{{ app.company_name }}</td>
              <td>{{ app.job_title }}</td>
              <td>{{ app.application_date }}</td>
              <td>
                <span class="badge" :class="{'bg-secondary': app.status === 'Applied', 'bg-info text-dark': app.status === 'Shortlisted', 'bg-success': app.status === 'Selected', 'bg-danger': app.status === 'Rejected'}">{{ app.status }}</span>
              </td>
            </tr>
            <tr v-if="history.length === 0"><td colspan="5" class="text-center">You haven't applied to any drives yet.</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Notifications -->
    <div v-if="activeTab === 'notifications'" class="card card-3d p-4">
      <h4 class="mb-4">Notifications & Reminders</h4>
      <div v-if="notifications.length === 0" class="text-center text-muted mt-3">You have no notifications.</div>
      <div v-else class="list-group">
        <div v-for="n in notifications" :key="n.id" class="list-group-item d-flex justify-content-between align-items-center mb-3 rounded" :class="{'bg-light': n.is_read}" style="border: none; box-shadow: 3px 3px 6px #d1d9e6, -3px -3px 6px #ffffff;">
          <div>
            <div class="mb-1" :class="{'fw-bold': !n.is_read}">{{ n.message }}</div>
            <small class="text-muted">{{ n.created_at }}</small>
          </div>
          <button v-if="!n.is_read" class="btn btn-sm btn-outline-primary rounded-pill mb-auto" @click="markAsRead(n.id)">Mark Read</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../utils/axios';

const profile = ref({ name: '', branch: '', cgpa: '', year: '', total_applications: 0 });
const availableDrives = ref([]);
const history = ref([]);
const activeTab = ref('drives');
const profileSuccess = ref('');
const exportMsg = ref('');
const exporting = ref(false);
const notifications = ref([]);
const unreadCount = ref(0);
let exportInterval = null;

const resumeInput = ref(null);
const selectedFile = ref(null);
const uploading = ref(false);

const fetchData = async () => {
  try {
    const dashRes = await api.get('/student/dashboard');
    profile.value = dashRes.data;
    
    const driveRes = await api.get('/student/drives');
    availableDrives.value = driveRes.data;
    
    const histRes = await api.get('/student/applications');
    history.value = histRes.data;

    const notifRes = await api.get('/student/notifications');
    notifications.value = notifRes.data;
    unreadCount.value = notifications.value.filter(n => !n.is_read).length;
  } catch (err) {
    console.error(err);
  }
};

onMounted(() => {
  fetchData();
});

const updateProfile = async () => {
  try {
    await api.put('/student/profile', profile.value);
    profileSuccess.value = 'Profile updated!';
    setTimeout(() => profileSuccess.value = '', 3000);
    fetchData(); // refresh drives to re-calc eligibility
  } catch (err) {
    alert("Failed to update profile");
  }
};

const markAsRead = async (id) => {
  try {
    await api.put(`/student/notifications/${id}/read`);
    fetchData();
  } catch(e) {
    console.error(e);
  }
};

const applyForDrive = async (id) => {
  if(!confirm("Are you sure you want to apply to this drive?")) return;
  try {
    await api.post('/student/applications', { drive_id: id });
    alert("Application submitted successfully! A confirmation email has been sent.");
    fetchData();
  } catch (err) {
    alert(err.response?.data?.msg || "Failed to apply");
  }
};

const handleFileUpload = (e) => {
  selectedFile.value = e.target.files[0];
};

const uploadResume = async () => {
  if (!selectedFile.value) return;
  uploading.value = true;
  const formData = new FormData();
  formData.append('file', selectedFile.value);
  
  try {
    const res = await api.post('/student/upload-resume', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    profileSuccess.value = res.data.msg;
    setTimeout(() => profileSuccess.value = '', 3000);
    fetchData();
    selectedFile.value = null;
    resumeInput.value.value = '';
  } catch (err) {
    alert(err.response?.data?.msg || "Failed to upload resume");
  } finally {
    uploading.value = false;
  }
};

const triggerExport = async () => {
  exporting.value = true;
  exportMsg.value = "Starting export...";
  try {
    const res = await api.post('/student/export');
    if (res.data.status === 'ACCEPTED') {
      exportMsg.value = res.data.msg;
      setTimeout(() => exportMsg.value = '', 5000);
    }
  } catch (err) {
    exportMsg.value = "Failed to start export job.";
  } finally {
    exporting.value = false;
  }
};

onUnmounted(() => {
  if (exportInterval) {
    clearInterval(exportInterval);
  }
});
</script>
