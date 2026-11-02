import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const dashboardService = {
  getSummary: () => api.get('/dashboard/summary'),
};

export const participantService = {
  getAll: (params) => api.get('/participants', { params }),
  getById: (id) => api.get(`/participants/${id}`),
  create: (data) => api.post('/participants', data),
  update: (id, data) => api.put(`/participants/${id}`, data),
  delete: (id) => api.delete(`/participants/${id}`),
};

export const sessionService = {
  getAll: (params) => api.get('/sessions', { params }),
  getById: (id) => api.get(`/sessions/${id}`),
  create: (data) => api.post('/sessions', data),
  update: (id, data) => api.put(`/sessions/${id}`, data),
  delete: (id) => api.delete(`/sessions/${id}`),
  
  uploadMedia: (id, formData) => api.post(`/sessions/${id}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  triggerProcess: (id) => api.post(`/sessions/${id}/process`),
  getStatus: (id) => api.get(`/sessions/${id}/status`),
  
  getAttendance: (id) => api.get(`/sessions/${id}/attendance`),
  updateAttendanceRecord: (sessionId, recordId, data) =>
    api.patch(`/sessions/${sessionId}/attendance/${recordId}`, data),
    
  getEngagement: (id) => api.get(`/sessions/${id}/engagement`),
  getRecommendations: (id) => api.get(`/sessions/${id}/recommendations`),
  getReport: (id) => api.get(`/sessions/${id}/report`),
  
  getExportCsvUrl: (id) => `/api/sessions/${id}/export/csv`,
  getExportJsonUrl: (id) => `/api/sessions/${id}/export/json`,
};

export default api;
