import { useState, useCallback } from 'react';
import api from '../services/api';

/**
 * Custom hook for making API calls with loading and error states.
 *
 * @returns {Object} { data, loading, error, execute }
 */
const useApi = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (method, url, body = null, config = {}) => {
    setLoading(true);
    setError(null);

    try {
      let response;
      switch (method.toLowerCase()) {
        case 'get':
          response = await api.get(url, config);
          break;
        case 'post':
          response = await api.post(url, body, config);
          break;
        case 'put':
          response = await api.put(url, body, config);
          break;
        case 'patch':
          response = await api.patch(url, body, config);
          break;
        case 'delete':
          response = await api.delete(url, config);
          break;
        default:
          throw new Error(`Unsupported HTTP method: ${method}`);
      }

      setData(response.data);
      return response.data;
    } catch (err) {
      const message = err.response?.data?.detail || err.message || 'Something went wrong';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, execute, reset };
};

export default useApi;
