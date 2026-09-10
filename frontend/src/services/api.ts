import axios from 'axios';

// Instancia de axios apuntando a nuestro backend
export const api = axios.create({
    baseURL: 'http://localhost:8000/api',
});

// Interceptor para inyectar el token JWT en cada petición
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
