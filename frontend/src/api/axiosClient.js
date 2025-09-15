import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const axiosClient = axios.create({
    baseURL: 'http://127.0.0.1:8000/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

axiosClient.interceptors.request.use(
    config => {
        const accessToken = localStorage.getItem('accessToken');
        if (accessToken) {
            config.headers['Authorization'] = `Bearer ${accessToken}`;
        }
        return config;
    },
    error => Promise.reject(error)
);


axiosClient.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;
        if (error.response.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refreshToken');

            if (refreshToken) {
                const tokenParts = jwtDecode(refreshToken);
                // check if refresh token is expired
                const now = Math.ceil(Date.now() / 1000);
                if (tokenParts.exp > now) {
                    try {
                        const { data } = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
                            refresh: refreshToken
                        });
                        localStorage.setItem('accessToken', data.access);
                        axiosClient.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
                        originalRequest.headers['Authorization'] = `Bearer ${data.access}`;
                        return axiosClient(originalRequest);
                    } catch (refreshError) {
                        console.error("Token refresh failed", refreshError);
                        localStorage.removeItem('accessToken');
                        localStorage.removeItem('refreshToken');
                        window.location.href = '/login'; // Force logout
                        return Promise.reject(refreshError);
                    }
                }
            }
        }
        return Promise.reject(error);
    }
);

export default axiosClient;