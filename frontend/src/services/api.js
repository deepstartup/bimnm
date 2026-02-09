import axios from 'axios';

// API base URL resolution:
// - If REACT_APP_API_URL is set (e.g. Vercel backend URL), always use it.
// - Otherwise, same-origin when deployed (e.g. Vercel) so no CORS.
// - Localhost for local dev.
const getBaseURL = () => {
  if (process.env.REACT_APP_API_URL && process.env.REACT_APP_API_URL.trim() !== '') {
    return process.env.REACT_APP_API_URL;
  }
  if (typeof window !== 'undefined') {
    const host = window.location.hostname;
    if (host !== 'localhost' && host !== '127.0.0.1') {
      return ''; // production: use /api on same origin
    }
  }
  return 'http://localhost:5011';
};
const API_URL = getBaseURL();

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Attach token from localStorage to every request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// On 401, clear token so auth context can redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      // Let the component or AuthContext handle redirect
    }
    return Promise.reject(error);
  }
);

export default api;
export { API_URL };
