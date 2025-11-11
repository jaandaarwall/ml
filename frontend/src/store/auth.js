import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.role,
  },
  actions: {
    async login(email, password) {
      const response = await axios.post(`${API_URL}/login`, { email, password });
      this.token = response.data.token;
      this.role = response.data.role;
      localStorage.setItem('token', this.token);
      localStorage.setItem('role', this.role);
    },
    async register(fullName, email, password) {
      await axios.post(`${API_URL}/register`, { full_name: fullName, email, password });
    },
    logout() {
      this.token = null;
      this.role = null;
      localStorage.removeItem('token');
      localStorage.removeItem('role');
    },
  },
});
