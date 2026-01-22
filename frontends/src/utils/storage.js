const PREFIX = 'science_ai_';
export default {
get(k){ try { return JSON.parse(localStorage.getItem(PREFIX + k)); } catch(e){ return localStorage.getItem(PREFIX + k); } },
set(k,v){ localStorage.setItem(PREFIX + k, typeof v === 'string' ? v : JSON.stringify(v)); },
remove(k){ localStorage.removeItem(PREFIX + k); }
}