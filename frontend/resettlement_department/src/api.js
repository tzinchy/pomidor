// src/api.js
import axios from 'axios';

const api = axios.create({
  withCredentials: true,
});

api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      const loginUrl = `${import.meta.env.VITE_AUTH_URL}/?redirect_uri=${encodeURIComponent(window.location.href)}`;
      window.location.href = loginUrl;
    }
    return Promise.reject(err);
  }
);

export default api;