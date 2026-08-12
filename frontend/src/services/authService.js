import api from './api';

const authService = {
  register: async (userData) => {
    const { data } = await api.post('/auth/register', userData);
    return data;
  },

  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
    }
    return data;
  },

  logout: async () => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      await api.post('/auth/logout', null, { params: { token } });
      localStorage.removeItem('auth_token');
    }
  },

  isAuthenticated: () => {
    return !!localStorage.getItem('auth_token');
  },
};

export default authService;
