// frontend/src/services/api.js (带自动续签功能的最终版)

import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// --- 请求拦截器 (保持不变) ---
// 每次发送请求前，都检查一下口袋里有没有房卡(access_token)，有就带上
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});


// --- 【关键】新增一个“响应拦截器” ---
// 每次收到后端的回复后，都先检查一下回复的内容
apiClient.interceptors.response.use(
  // 1. 如果收到的回复是成功的，直接把回复交给页面
  (response) => {
    return response;
  },
  // 2. 如果收到的回复是错误的，我们在这里进行处理
  async (error) => {
    const originalRequest = error.config;

    // 检查是不是因为“房卡过期”(401错误)导致的，并且这个请求不是一个重试请求
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // 给这个请求盖一个“已重试”的戳

      try {
        // 尝试用口袋里的“续签卡”(refresh_token)去换一张新房卡
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            // 如果连续签卡都没有，直接跳转登录
            window.location.href = '/login';
            return Promise.reject(error);
        }

        const response = await axios.post('http://localhost:5000/api/refresh', {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        });
        
        // 成功换到新房卡！
        const newAccessToken = response.data.access_token;
        localStorage.setItem('access_token', newAccessToken);
        
        // 更新我们axios实例的默认头部，让后续请求都用上新房卡
        apiClient.defaults.headers.common['Authorization'] = `Bearer ${newAccessToken}`;
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        
        // 用新房卡，把刚才失败的那个请求重新发一次
        return apiClient(originalRequest);

      } catch (refreshError) {
        // 如果用“续签卡”都失败了（比如续签卡也过期了）
        // 那就彻底登出，并把用户带回登录页
        console.error("无法刷新Token:", refreshError);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // 使用 window.location.href 来强制刷新页面并跳转
        window.location.href = '/login'; 
        return Promise.reject(refreshError);
      }
    }

    // 对于其他所有错误，直接把错误丢出去
    return Promise.reject(error);
  }
);

export default apiClient;