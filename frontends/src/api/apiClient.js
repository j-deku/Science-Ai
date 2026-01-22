import axios from 'axios';
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';


const api = axios.create({
baseURL: API_BASE,
headers: { 'Content-Type': 'application/json' },
timeout: 30000,
});


export default api;