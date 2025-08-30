<template>
  <div class="auth-container">
    <h1>登录您的账户</h1>
    <form @submit.prevent="handleLogin" class="auth-form">
      <div class="form-group">
        <label for="email">邮箱地址</label>
        <input type="email" id="email" v-model="email" placeholder="请输入您的邮箱" required />
      </div>
      <div class="form-group">
        <label for="password">密码</label>
        <input type="password" id="password" v-model="password" placeholder="请输入您的密码" required />
      </div>
      <button type="submit">登 录</button>
    </form>
  </div>
</template>

<script setup>
// frontend/src/views/LoginView.vue 的 <script setup>

import { ref } from 'vue';
// 导入我们配置好的axios实例
import apiClient from '@/services/api.js';
// 导入Vue Router，用于页面跳转
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter(); // 获取router实例

async function handleLogin() {
  if (!email.value || !password.value) {
    alert('邮箱和密码不能为空！');
    return;
  }
  try {
    const response = await apiClient.post('/login', {
      email: email.value,
      password: password.value,
    });
    
    // 从后端响应中获取 access_token
    const token = response.data.access_token;
    // 将 token 存入浏览器的 localStorage
    localStorage.setItem('token', token);

    alert('登录成功！');
    // 登录成功后，跳转到提交创意的页面
    router.push('/submit-idea');

  } catch (error) {
    if (error.response) {
      alert('登录失败：' + error.response.data.message);
    } else {
      alert('登录失败：无法连接到服务器。');
    }
  }
}
</script>

<style scoped>
/* 为了方便，登录和注册页可以共用一套样式 */
.auth-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px 30px;
  background-color: #f9f9f9;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}
h1 {
  font-size: 24px;
  margin-bottom: 25px;
}
.auth-form .form-group {
  margin-bottom: 15px;
  text-align: left;
}
.auth-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.auth-form input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border: none;
  border-radius: 5px;
  background-color: #28a745;
  color: white;
  cursor: pointer;
}
</style>