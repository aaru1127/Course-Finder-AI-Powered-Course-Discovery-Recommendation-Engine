import axios from 'axios';

const API_BASE = '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchCourses = async (searchPayload) => {
  const response = await apiClient.post('/search', searchPayload);
  return response.data;
};

export const getCourseDetails = async (courseId) => {
  const response = await apiClient.get(`/courses/${courseId}`);
  return response.data;
};

export const getSimilarCourses = async (courseId, params = {}) => {
  const response = await apiClient.get(`/courses/${courseId}/similar`, { params });
  return response.data;
};

export const getPersonalizedRecommendations = async (profilePayload) => {
  const response = await apiClient.post('/recommend', profilePayload);
  return response.data;
};

export const getFilterFacets = async () => {
  const response = await apiClient.get('/filters');
  return response.data;
};

export const getBenchmarkMetrics = async (forceRefresh = false) => {
  const response = await apiClient.get('/evaluation/benchmark', {
    params: { force_refresh: forceRefresh }
  });
  return response.data;
};

export const getSystemHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

export const clearCache = async () => {
  const response = await apiClient.post('/cache/clear');
  return response.data;
};
