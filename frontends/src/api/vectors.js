import api from './apiClient';


export const upsertVectors = (formData) => api.post('/vectors/upsert', formData, { headers: {'Content-Type': 'multipart/form-data'} });
export const searchVectors = (query) => api.post('/vectors/search', query);