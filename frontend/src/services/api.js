import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Changed from 8001 to 8000
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getMe: () => api.get('/api/auth/me'),
};

export const analysisAPI = {
  analyze: (formData) => api.post('/api/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
  getAnalyses: () => api.get('/api/analyses'),
};

export default api;
