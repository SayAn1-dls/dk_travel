import api from './api';

const destinationService = {
  search: async (params = {}) => {
    const { data } = await api.get('/destinations', { params });
    return data;
  },

  getPopular: async (limit = 10) => {
    const { data } = await api.get('/destinations/popular', { params: { limit } });
    return data;
  },

  getById: async (id) => {
    const { data } = await api.get(`/destinations/${id}`);
    return data;
  },

  getCategories: async () => {
    const { data } = await api.get('/destinations/categories');
    return data.categories;
  },
};

export default destinationService;
