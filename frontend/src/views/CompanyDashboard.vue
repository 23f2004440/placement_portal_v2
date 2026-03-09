<template>
  <div>
    <h2 class="text-primary fw-bold mb-4">Company Dashboard <span v-if="dashboard.is_approved" class="badge bg-success fs-6">Approved</span><span v-else class="badge bg-warning text-dark fs-6">Pending Approval</span></h2>
    
    <div class="row mb-4">
      <div class="col-md-6">
        <div class="card card-3d p-4">
          <h4 class="text-secondary">Total Drives Created</h4>
          <h1 class="display-4 fw-bold text-primary">{{ dashboard.total_drives }}</h1>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card card-3d p-4">
          <h4 class="text-secondary">Total Applicants</h4>
          <h1 class="display-4 fw-bold text-success">{{ dashboard.total_applicants }}</h1>
        </div>
      </div>
    </div>
    
    <div v-if="error" class="alert alert-danger">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    
    <div class="card card-3d p-4 mb-5" v-if="dashboard.is_approved">
      <h4 class="mb-4">Create New Placement Drive</h4>
      <form @submit.prevent="createDrive">
        <div class="row">
          <div class="col-md-6 mb-3">
            <label class="form-label text-secondary fw-semibold">Job Title</label>
            <input type="text" class="form-control input-3d" v-model="newDrive.job_title" required>
          </div>
          <div class="col-md-6 mb-3">
            <label class="form-label text-secondary fw-semibold">Application Deadline</label>
            <input type="date" class="form-control input-3d" v-model="newDrive.application_deadline" required>
          </div>
          <div class="col-md-12 mb-3">
            <label class="form-label text-secondary fw-semibold">Job Description</label>
            <textarea class="form-control input-3d" rows="3" v-model="newDrive.job_description" required></textarea>
          </div>
          <div class="col-md-4 mb-3">
            <label class="form-label text-secondary fw-semibold">Eligible Branch</label>
            <input type="text" class="form-control input-3d" v-model="newDrive.eligibility_branch" placeholder="e.g. Computer Science">
          </div>
          <div class="col-md-4 mb-3">
            <label class="form-label text-secondary fw-semibold">Minimum CGPA</label>
            <input type="number" step="0.01" class="form-control input-3d" v-model="newDrive.eligibility_cgpa" required>
          </div>
          <div class="col-md-4 mb-3">
            <label class="form-label text-secondary fw-semibold">Graduation Year</label>
            <input type="number" class="form-control input-3d" v-model="newDrive.eligibility_year" required>
          </div>
        </div>
        <button type="submit" class="btn btn-3d-primary mt-3 px-4">Create Drive</button>
      </form>
    </div>
    
    <div class="card card-3d p-4">
      <h4 class="mb-4">My Placement Drives</h4>
      <div class="table-responsive">
        <table class="table table-hover align-middle">
          <thead>
            <tr>
              <th>ID</th>
              <th>Job Title</th>
              <th>Deadline</th>
              <th>Status</th>
              <th>Applicants</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td>{{ d.id }}</td>
              <td class="fw-bold">{{ d.job_title }}</td>
              <td>{{ d.application_deadline }}</td>
              <td>
                <span class="badge" :class="{'bg-warning text-dark': d.status === 'Pending', 'bg-success': d.status === 'Approved', 'bg-danger': d.status === 'Rejected', 'bg-secondary': d.status === 'Closed'}">{{ d.status }}</span>
              </td>
              <td>{{ d.applicant_count }}</td>
              <td>
                <button class="btn btn-sm btn-3d" @click="viewApplicants(d.id)" data-bs-toggle="modal" data-bs-target="#applicantsModal">View Applicants</button>
              </td>
            </tr>
            <tr v-if="drives.length === 0"><td colspan="6" class="text-center">No drives created yet</td></tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Applicants Modal -->
    <div class="modal fade" id="applicantsModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content glass-modal text-dark">
          <div class="modal-header border-0">
            <h5 class="modal-title fw-bold">Applicants</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="table-responsive">
              <table class="table table-hover align-middle">
                <thead>
                  <tr>
                    <th>Application ID</th>
                    <th>Student Name</th>
                    <th>Resume</th>
                    <th>Branch</th>
                    <th>CGPA</th>
                    <th>Year</th>
                    <th>Interview Details</th>
                    <th>Date</th>
                    <th>Status</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in applicants" :key="app.application_id">
                    <td>{{ app.application_id }}</td>
                    <td class="fw-bold">{{ app.student_name }}</td>
                    <td>
                      <a v-if="app.resume_path" :href="api.defaults.baseURL + '/company/resumes/' + app.resume_path" target="_blank" class="badge bg-primary text-decoration-none">View PDF</a>
                      <span v-else class="text-muted small">N/A</span>
                    </td>
                    <td>{{ app.branch }}</td>
                    <td>{{ app.cgpa }}</td>
                    <td>{{ app.year }}</td>
                    <td>
                      <div v-if="app.interview_datetime" class="small">
                        <strong>Time:</strong> {{ app.interview_datetime }}<br>
                        <strong>Link:</strong> <a :href="app.interview_link" target="_blank">Join</a>
                      </div>
                      <span v-else class="text-muted small">Not Scheduled</span>
                    </td>
                    <td>{{ app.application_date }}</td>
                    <td>
                      <span class="badge" :class="{'bg-secondary': app.status === 'Applied', 'bg-info text-dark': app.status === 'Shortlisted', 'bg-success': app.status === 'Selected', 'bg-danger': app.status === 'Rejected'}">{{ app.status }}</span>
                    </td>
                    <td>
                      <div class="d-flex flex-column gap-2">
                        <select class="form-select form-select-sm input-3d" :value="app.status" @change="updateApplicantStatus(app.application_id, $event.target.value)">
                          <option value="Applied">Applied</option>
                          <option value="Shortlisted">Shortlisted</option>
                          <option value="Selected">Selected</option>
                          <option value="Rejected">Rejected</option>
                        </select>
                        <button class="btn btn-sm btn-outline-info" @click="scheduleInterviewApp(app)">Schedule</button>
                        <button v-if="app.status === 'Selected'" class="btn btn-sm btn-outline-success" @click="downloadOfferLetter(app)" :disabled="downloadingOffer === app.application_id">
                          {{ downloadingOffer === app.application_id ? 'Generating...' : 'Offer Letter (PDF)' }}
                        </button>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="applicants.length === 0"><td colspan="11" class="text-center">No applicants yet</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../utils/axios';

const dashboard = ref({ company_name: '', is_approved: false, total_drives: 0, total_applicants: 0 });
const drives = ref([]);
const applicants = ref([]);
const newDrive = ref({ job_title: '', job_description: '', eligibility_branch: '', eligibility_cgpa: '', eligibility_year: '', application_deadline: '' });
const error = ref('');
const success = ref('');
const downloadingOffer = ref(null);

const fetchData = async () => {
  try {
    const dashRes = await api.get('/company/dashboard');
    dashboard.value = dashRes.data;
    
    const driveRes = await api.get('/company/drives');
    drives.value = driveRes.data;
  } catch (err) {
    error.value = 'Failed to load details';
  }
};

onMounted(() => {
  fetchData();
});

const createDrive = async () => {
  error.value = '';
  success.value = '';
  try {
    await api.post('/company/drives', newDrive.value);
    success.value = 'Placement drive created and pending admin approval!';
    newDrive.value = { job_title: '', job_description: '', eligibility_branch: '', eligibility_cgpa: '', eligibility_year: '', application_deadline: '' };
    fetchData();
  } catch (err) {
    error.value = err.response?.data?.msg || 'Failed to create drive';
  }
};

const viewApplicants = async (id) => {
  try {
    const res = await api.get(`/company/drives/${id}/applicants`);
    applicants.value = res.data;
  } catch (err) {
    alert("Could not load applicants");
  }
};

const updateApplicantStatus = async (appId, newStatus) => {
  try {
    await api.put(`/company/applications/${appId}/status`, { status: newStatus });
    const app = applicants.value.find(a => a.application_id === appId);
    if(app) app.status = newStatus;
  } catch (err) {
    alert("Failed to update status");
  }
};

const downloadOfferLetter = async (app) => {
  downloadingOffer.value = app.application_id;
  try {
    const res = await api.get(`/company/applications/${app.application_id}/offer-letter`, { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `Offer_${app.student_name.replace(/\s+/g, '_')}.pdf`);
    document.body.appendChild(link);
    link.click();
  } catch (err) {
    console.error("Error downloading offer letter", err);
    alert("Failed to download offer letter. Ensure the student is Selected.");
  } finally {
    downloadingOffer.value = null;
  }
};

const scheduleInterviewApp = async (app) => {
  const dateStr = prompt("Enter Interview Date & Time (YYYY-MM-DDTHH:MM):", app.interview_datetime ? app.interview_datetime.replace(' ', 'T') : "");
  if (!dateStr) return;
  const linkStr = prompt("Enter Interview Link (e.g. Google Meet URL):", app.interview_link || "");
  if (!linkStr) return;
  
  try {
    await api.post(`/company/applications/${app.application_id}/schedule`, {
      interview_datetime: dateStr,
      interview_link: linkStr
    });
    app.interview_datetime = dateStr.replace('T', ' ');
    app.interview_link = linkStr;
    app.status = 'Shortlisted';
    alert("Interview scheduled and email notification dispatched!");
  } catch (err) {
    alert("Failed to schedule interview");
  }
};
</script>
