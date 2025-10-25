import axios from 'axios';

// Use environment variable for API URL, fallback to localhost for development
const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: apiUrl,
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
