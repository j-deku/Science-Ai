import { useState, useEffect } from 'react';
import jwtDecode from 'jwt-decode';
import { login as loginReq, me } from '../api/auth';
import storage from '../utils/storage';

export default function useAuth() {
const [user, setUser] = useState(storage.get('user') || null);


useEffect(() => {
const token = storage.get('token');
if (token && !user) {
try {
const decoded = jwtDecode(token);
Promise.resolve().then(() => setUser(decoded));
} catch (e) {
storage.remove('token');
}
}
}, []);


async function login(email, password) {
const { data } = await loginReq(email, password);
storage.set('token', data.access_token);
storage.set('user', data.user);
setUser(data.user);
return data;
}


function logout() {
storage.remove('token');
storage.remove('user');
setUser(null);
}


return { user, login, logout };
}