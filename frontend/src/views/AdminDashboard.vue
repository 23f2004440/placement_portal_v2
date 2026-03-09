<template>
  <div>
    <h2 class="text-primary fw-bold mb-4">Admin Dashboard</h2>
    
    <!-- Stats Row -->
    <div class="row mb-5">
      <div class="col-md-4">
        <div class="card card-3d p-4 text-center">
          <h4 class="text-secondary">Total Students</h4>
          <h1 class="display-4 fw-bold text-primary">{{ stats.total_students }}</h1>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card card-3d p-4 text-center">
          <h4 class="text-secondary">Registered Companies</h4>
          <h1 class="display-4 fw-bold text-success">{{ stats.total_companies }}</h1>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card card-3d p-4 text-center">
          <h4 class="text-secondary">Placement Drives</h4>
          <h1 class="display-4 fw-bold text-warning">{{ stats.total_drives }}</h1>
        </div>
      </div>
    </div>
    
    <div class="row mb-5">
      <div class="col-md-6">
        <div class="card card-3d p-4 text-center">
          <h4 class="text-secondary">Total Applications</h4>
          <h1 class="display-4 fw-bold text-info">{{ stats.total_applications }}</h1>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card card-3d p-4 text-center">
          <h4 class="text-secondary">Selected Students</h4>
          <h1 class="display-4 fw-bold text-primary">{{ stats.total_selected }}</h1>
        </div>
      </div>
    </div>
    
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-white bg-warning mb-3">
          <div class="card-body">
            <h5 class="card-title">Pending Approvals</h5>
            <p class="card-text fs-4">{{ pendingApprovals }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div class="row mb-4 align-items-center">
      <div class="col-md-8 mb-3 mb-md-0 d-flex flex-wrap gap-3">
        <button class="btn btn-secondary" @click="triggerNotifications" :disabled="triggeringNotifications">
          {{ triggeringNotifications ? 'Triggering...' : 'Trigger Daily Notifications' }}
        </button>
        <button class="btn btn-info text-white fw-bold shadow-sm" @click="downloadReport" :disabled="downloadingReport">
          {{ downloadingReport ? 'Generating PDF...' : 'Download Monthly Report (PDF)' }}
        </button>
        <button class="btn btn-3d-primary shadow-sm" @click="showBroadcastModal = !showBroadcastModal">
          <i class="bi bi-envelope-fill me-1"></i> Broadcast Email
        </button>
        <button class="btn btn-warning shadow-sm fw-bold" @click="showStatsModal = !showStatsModal">
          <i class="bi bi-graph-up me-1"></i> Stats Graphs
        </button>
      </div>
      <div class="col-md-4">
        <div class="input-group shadow-sm">
          <span class="input-group-text bg-white border-end-0">🔍</span>
          <input type="text" class="form-control border-start-0 input-3d" placeholder="Search across current category..." v-model="searchQuery">
        </div>
      </div>
    </div>
    
    <div class="row mb-4" v-if="notificationMsg">
      <div class="col-12">
        <div class="alert alert-success alert-dismissible fade show shadow-sm" role="alert">
          {{ notificationMsg }}
          <button type="button" class="btn-close" @click="notificationMsg = ''"></button>
        </div>
      </div>
    </div>
    
    <!-- Broadcast Email Section -->
    <div class="row mb-4" v-if="showBroadcastModal">
      <div class="col-12">
        <div class="card card-3d p-4 border-primary">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="text-primary m-0"><i class="bi bi-broadcast me-2"></i>Send Broadcast Email to All Students</h5>
            <button type="button" class="btn-close" @click="showBroadcastModal = false"></button>
          </div>
          <form @submit.prevent="sendBroadcastEmail">
            <div class="mb-3">
              <label class="form-label fw-bold">Subject</label>
              <input type="text" class="form-control input-3d" v-model="broadcastSubject" required placeholder="Important Update from Placement Cell">
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">Message</label>
              <textarea class="form-control input-3d" v-model="broadcastBody" rows="4" required placeholder="Type your message here..."></textarea>
            </div>
            <button type="submit" class="btn btn-3d-primary w-100" :disabled="sendingBroadcast">
               {{ sendingBroadcast ? 'Sending out emails...' : 'Send Broadcast Email' }}
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- Stats Graphs Section -->
    <div class="row mb-4" v-if="showStatsModal">
      <div class="col-12">
        <div class="card card-3d p-4 border-warning">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h5 class="text-warning m-0"><i class="bi bi-graph-up me-2"></i>Placement Statistics Graphs</h5>
            <button type="button" class="btn-close" @click="showStatsModal = false"></button>
          </div>
          <div class="row">
            <div class="col-md-6 mb-4" style="height: 300px;">
              <h6 class="text-center text-secondary mb-3">Overall Platform Metrics</h6>
              <Bar :data="barChartData" :options="chartOptions" />
            </div>
            <div class="col-md-6 mb-4 d-flex flex-column align-items-center" style="height: 300px;">
              <h6 class="text-center text-secondary mb-3">Applications vs Selections</h6>
              <div style="height: 100%; width: 100%; position: relative;">
                <Pie :data="pieChartData" :options="pieChartOptions" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <ul class="nav nav-pills nav-fill mb-4 p-2 rounded-pill" style="background:#e0e5ec; box-shadow: inset 5px 5px 10px rgb(163,177,198,0.6), inset -5px -5px 10px rgba(255,255,255, 0.5);">
      <li class="nav-item">
        <a class="nav-link rounded-pill" :class="{'active btn-3d-primary': activeTab === 'companies', 'btn-3d text-muted fw-bold': activeTab !== 'companies'}" href="#" @click.prevent="activeTab = 'companies'">Companies</a>
      </li>
      <li class="nav-item">
        <a class="nav-link rounded-pill" :class="{'active btn-3d-primary': activeTab === 'drives', 'btn-3d text-muted fw-bold': activeTab !== 'drives'}" href="#" @click.prevent="activeTab = 'drives'">Placement Drives</a>
      </li>
      <li class="nav-item">
        <a class="nav-link rounded-pill" :class="{'active btn-3d-primary': activeTab === 'students', 'btn-3d text-muted fw-bold': activeTab !== 'students'}" href="#" @click.prevent="activeTab = 'students'">Students</a>
      </li>
    </ul>
    
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    
    <!-- Companies Tab -->
    <div v-if="activeTab === 'companies'" class="card card-3d p-4">
      <h4 class="mb-4">Manage Companies</h4>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company Name</th>
              <th>Contact</th>
              <th>Website</th>
              <th>Approval</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in filteredCompanies" :key="c.id">
              <td>{{ c.id }}</td>
              <td class="fw-bold">{{ c.company_name }}</td>
              <td>{{ c.hr_contact }}</td>
              <td><a :href="c.website" target="_blank">Link</a></td>
              <td>
                <span v-if="c.is_approved" class="badge bg-success">Approved</span>
                <span v-else-if="!c.is_active" class="badge bg-danger">Rejected</span>
                <div v-else class="d-flex gap-2">
                  <button class="btn btn-sm btn-3d-primary" @click="approveCompany(c.id)">Approve</button>
                  <button class="btn btn-sm btn-3d-danger" @click="rejectCompany(c.id)">Reject</button>
                </div>
              </td>
              <td>
                <span class="badge" :class="c.is_active ? 'bg-success' : 'bg-danger'">{{ c.is_active ? 'Active' : (c.is_approved ? 'Blacklisted' : 'Rejected') }}</span>
              </td>
              <td>
                <button class="btn btn-sm" :class="c.is_active ? 'btn-3d-danger' : 'btn-3d-success'" @click="toggleCompanyStatus(c.id)">
                  {{ c.is_active ? 'Blacklist' : 'Activate' }}
                </button>
              </td>
            </tr>
            <tr v-if="companies.length === 0"><td colspan="7" class="text-center">No companies found</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Drives Tab -->
    <div v-if="activeTab === 'drives'" class="card card-3d p-4">
      <h4 class="mb-4">Manage Placement Drives</h4>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Company</th>
              <th>Job Title</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in filteredDrives" :key="d.id">
              <td>{{ d.id }}</td>
              <td class="fw-bold">{{ d.company_name }}</td>
              <td>{{ d.job_title }}</td>
              <td>{{ d.application_deadline }}</td>
              <td>
                <span class="badge" :class="{'bg-warning text-dark': d.status === 'Pending', 'bg-success': d.status === 'Approved', 'bg-danger': d.status === 'Rejected', 'bg-secondary': d.status === 'Closed'}">{{ d.status }}</span>
              </td>
              <td>
                <div v-if="d.status === 'Pending'" class="d-flex gap-2">
                  <button class="btn btn-sm btn-3d-success" @click="updateDriveStatus(d.id, 'Approved')">Approve</button>
                  <button class="btn btn-sm btn-3d-danger" @click="updateDriveStatus(d.id, 'Rejected')">Reject</button>
                </div>
                <button v-if="d.status === 'Approved'" class="btn btn-sm btn-3d-danger" @click="updateDriveStatus(d.id, 'Closed')">Close Drive</button>
              </td>
            </tr>
            <tr v-if="drives.length === 0"><td colspan="6" class="text-center">No drives found</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Students Tab -->
    <div v-if="activeTab === 'students'" class="card card-3d p-4">
      <h4 class="mb-4">Manage Students</h4>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Branch</th>
              <th>CGPA</th>
              <th>Year</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in filteredStudents" :key="s.id">
              <td>{{ s.id }}</td>
              <td class="fw-bold">{{ s.name }}</td>
              <td>{{ s.branch }}</td>
              <td>{{ s.cgpa }}</td>
              <td>{{ s.year }}</td>
              <td>
                <span class="badge" :class="s.is_active ? 'bg-success' : 'bg-danger'">{{ s.is_active ? 'Active' : 'Blacklisted' }}</span>
              </td>
              <td>
                <button class="btn btn-sm" :class="s.is_active ? 'btn-3d-danger' : 'btn-3d-success'" @click="toggleStudentStatus(s)">
                  {{ s.is_active ? 'Blacklist' : 'Activate' }}
                </button>
              </td>
            </tr>
            <tr v-if="students.length === 0"><td colspan="7" class="text-center">No students found</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../utils/axios';
import { Bar, Pie } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const stats = ref({ total_students: 0, total_companies: 0, total_drives: 0, total_applications: 0, total_selected: 0 });
const companies = ref([]);
const drives = ref([]);
const students = ref([]);
const error = ref('');
const activeTab = ref('companies');
const pendingApprovals = ref(0); // Added for pending approvals stat

const triggeringNotifications = ref(false);
const notificationMsg = ref('');
const downloadingReport = ref(false);
const searchQuery = ref('');

const showBroadcastModal = ref(false);
const broadcastSubject = ref('');
const broadcastBody = ref('');
const sendingBroadcast = ref(false);

const showStatsModal = ref(false);

const barChartData = computed(() => ({
  labels: ['Students', 'Companies', 'Drives'],
  datasets: [{
    label: 'Total Count',
    backgroundColor: ['#0d6efd', '#198754', '#ffc107'],
    data: [stats.value.total_students, stats.value.total_companies, stats.value.total_drives]
  }]
}));

const pieChartData = computed(() => ({
  labels: ['Selected', 'Not Selected (Pending/Rejected)'],
  datasets: [{
    backgroundColor: ['#28a745', '#dc3545'],
    data: [stats.value.total_selected, stats.value.total_applications - stats.value.total_selected]
  }]
}));

const chartOptions = { responsive: true, maintainAspectRatio: false };
const pieChartOptions = { responsive: true, maintainAspectRatio: false };

const filteredCompanies = computed(() => {
  if (!searchQuery.value) return companies.value;
  const q = searchQuery.value.toLowerCase();
  return companies.value.filter(c => 
    c.company_name.toLowerCase().includes(q) || 
    (c.hr_contact && c.hr_contact.toLowerCase().includes(q))
  );
});

const filteredDrives = computed(() => {
  if (!searchQuery.value) return drives.value;
  const q = searchQuery.value.toLowerCase();
  return drives.value.filter(d => 
    d.company_name.toLowerCase().includes(q) || 
    d.job_title.toLowerCase().includes(q)
  );
});

const filteredStudents = computed(() => {
  if (!searchQuery.value) return students.value;
  const q = searchQuery.value.toLowerCase();
  return students.value.filter(s => 
    s.name.toLowerCase().includes(q) || 
    s.branch.toLowerCase().includes(q)
  );
});

const fetchDashboardStats = async () => {
  try {
    const [statsRes, compRes, driveRes, stuRes] = await Promise.all([
      api.get('/admin/dashboard'),
      api.get('/admin/companies'),
      api.get('/admin/drives'),
      api.get('/admin/students')
    ]);
    stats.value = statsRes.data;
    companies.value = compRes.data;
    drives.value = driveRes.data;
    students.value = stuRes.data;
    pendingApprovals.value = compRes.data.filter(c => !c.is_approved && c.is_active).length + driveRes.data.filter(d => d.status === 'Pending').length;
  } catch (err) {
    error.value = 'Failed to load data';
  }
};

onMounted(() => {
  fetchDashboardStats();
});

const approveCompany = async (id) => {
  try {
    await api.post(`/admin/companies/${id}/approve`);
    fetchDashboardStats();
  } catch (err) {
    error.value = err.response?.data?.msg || 'Error approving company';
  }
};

const rejectCompany = async (id) => {
  if (!confirm('Are you sure you want to reject and delete this company registration?')) return;
  try {
    await api.delete(`/admin/companies/${id}/reject`);
    fetchDashboardStats();
  } catch (err) {
    error.value = err.response?.data?.msg || 'Error rejecting company';
  }
};

const toggleCompanyStatus = async (id) => {
  try {
    await api.post(`/admin/companies/${id}/toggle-status`);
    fetchDashboardStats();
  } catch (err) {
    error.value = err.response?.data?.msg || 'Error toggling company status';
  }
};

const toggleStudentStatus = async (student) => {
  try {
    await api.put(`/admin/students/${student.id}/blacklist`);
    fetchDashboardStats();
  } catch (err) {
    console.error(err);
    error.value = err.response?.data?.msg || 'Error toggling student status';
  }
};

const updateDriveStatus = async (id, status) => {
  try {
    await api.put(`/admin/drives/${id}/status`, { status });
    fetchDashboardStats();
  } catch (err) {
    error.value = err.response?.data?.msg || 'Error updating drive status';
  }
};

const triggerNotifications = async () => {
  triggeringNotifications.value = true;
  notificationMsg.value = '';
  try {
    const res = await api.post('/admin/trigger-notifications');
    notificationMsg.value = res.data.msg;
  } catch (err) {
    error.value = err.response?.data?.msg || 'Failed to trigger notifications';
  } finally {
    triggeringNotifications.value = false;
  }
};

const downloadReport = async () => {
  downloadingReport.value = true;
  try {
    const res = await api.get('/admin/report/pdf', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    const date = new Date();
    link.setAttribute('download', `placement_report_${date.getFullYear()}_${date.getMonth() + 1}.pdf`);
    document.body.appendChild(link);
    link.click();
  } catch (err) {
    console.error("Error downloading report", err);
    error.value = 'Failed to download PDF report';
  } finally {
    downloadingReport.value = false;
  }
};

const sendBroadcastEmail = async () => {
  if (!confirm(`Are you sure you want to send this email to ALL ${stats.value.total_students} students?`)) return;
  sendingBroadcast.value = true;
  try {
    const res = await api.post('/admin/broadcast-email', {
      subject: broadcastSubject.value,
      body: broadcastBody.value
    });
    notificationMsg.value = res.data.msg;
    showBroadcastModal.value = false;
    broadcastSubject.value = '';
    broadcastBody.value = '';
  } catch (err) {
    error.value = err.response?.data?.msg || 'Failed to send broadcast email';
  } finally {
    sendingBroadcast.value = false;
  }
};
</script>
