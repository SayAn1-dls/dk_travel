import api from './api';

const bookingService = {
  create: async (bookingData) => {
    const { data } = await api.post('/bookings', bookingData);
    return data;
  },

  getAll: async (status = null) => {
    const params = status ? { status } : {};
    const { data } = await api.get('/bookings', { params });
    return data;
  },

  getById: async (id) => {
    const { data } = await api.get(`/bookings/${id}`);
    return data;
  },

  cancel: async (id, reason = '') => {
    const { data } = await api.post(`/bookings/${id}/cancel`, { reason });
    return data;
  },

  confirm: async (id, paymentId) => {
    const { data } = await api.post(`/bookings/${id}/confirm`, null, {
      params: { payment_id: paymentId },
    });
    return data;
  },
};

export default bookingService;
