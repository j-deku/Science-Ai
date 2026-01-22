import api from './apiClient';


export const askAI = (payload) => api.post('/ai/ask_sync', payload);