import api from "./axios";

// ── Auth ──────────────────────────────────────────────────────────
export const registerUser = (data) => api.post("/auth/register", data);
export const loginUser = (data) => api.post("/auth/login", data);
export const logoutUser = () => api.post("/auth/logout");
export const getProfile = () => api.get("/auth/profile");

// ── Resumes ───────────────────────────────────────────────────────
export const uploadResume = (formData) =>
  api.post("/resumes/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
export const getResumes = (params) => api.get("/resumes", { params });
export const getResume = (resumeId) => api.get(`/resumes/${resumeId}`);
export const deleteResume = (resumeId) => api.delete(`/resumes/${resumeId}`);

// ── Jobs ──────────────────────────────────────────────────────────
export const createJob = (data) => api.post("/jobs", data);
export const getJobs = (params) => api.get("/jobs", { params });
export const getJob = (jobId) => api.get(`/jobs/${jobId}`);
export const updateJob = (jobId, data) => api.put(`/jobs/${jobId}`, data);
export const deleteJob = (jobId) => api.delete(`/jobs/${jobId}`);

// ── Rankings ──────────────────────────────────────────────────────
// Changed from /rankings/run → /rankings/analyze
export const analyzeRankings = (data) => api.post("/rankings/analyze", data);
export const getRankings = (jobId) => api.get(`/rankings/${jobId}`);
export const getCandidateRanking = (jobId, candidateId) =>
  api.get(`/rankings/${jobId}/${candidateId}`);
export const getRankingHistory = () => api.get("/rankings/history/all");

// ── Skills ────────────────────────────────────────────────────────
export const getSkills = () => api.get("/skills");
export const extractSkills = (text) => api.post("/skills/extract", { text });
export const getMissingSkills = (candidateId, jobId) =>
  api.get(`/skills/missing/${candidateId}`, { params: { job_id: jobId } });

// ── Analytics ─────────────────────────────────────────────────────
export const getDashboardAnalytics = () => api.get("/analytics/dashboard");
export const getJobsAnalytics = () => api.get("/analytics/jobs");
export const getCandidatesAnalytics = () => api.get("/analytics/candidates");

// ── Reports ───────────────────────────────────────────────────────
export const generateReport = (data) => api.post("/reports/generate", data);
export const getReport = (reportId) => api.get(`/reports/${reportId}`);
export const downloadReport = (reportId) =>
  api.get(`/reports/download/${reportId}`, { responseType: "blob" });

// ── Interviews ────────────────────────────────────────────────────
export const generateInterviewQuestions = (data) =>
  api.post("/interviews/generate", data);
export const getInterviewQuestions = (candidateId, jobId) =>
  api.get(`/interviews/${candidateId}`, { params: jobId ? { job_id: jobId } : {} });
