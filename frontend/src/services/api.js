// frontend/src/services/api.js

import axios from 'axios';

// 创建一个axios实例，我们可以对它进行统一的配置
const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api', // 统一设置API的基础路径
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加一个“请求拦截器” (Request Interceptor)
// 这是一个魔法，它会在每一次请求被发送出去之前执行
apiClient.interceptors.request.use(config => {
  // 从 localStorage 获取 token
  const token = localStorage.getItem('token');
  if (token) {
    // 如果 token 存在，就在请求的 Authorization 头部添加它
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config; // 返回配置好的请求
}, error => {
  return Promise.reject(error);
});

// 导出我们配置好的实例
export default apiClient;