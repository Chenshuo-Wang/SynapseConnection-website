<template>
  <div class="register-container">
    <h1>创建您的新账户</h1>
    <p>开启您的创意之旅</p>

    <form @submit.prevent="handleRegister" class="register-form">
      
      <div class="form-group">
        <label for="email">邮箱地址</label>
        <input 
          type="email" 
          id="email" 
          v-model="email" 
          placeholder="请输入您的邮箱" 
          required 
        />
      </div>

      <div class="form-group">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="password" 
          placeholder="请输入您的密码" 
          required 
        />
      </div>

      <button type="submit">立即注册</button>
    </form>
  </div>
</template>

<script setup>
// frontend/src/views/RegisterView.vue 的 <script setup>

import { ref } from 'vue';
import apiClient from '@/services/api.js';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const router = useRouter();

async function handleRegister() {
  if (!email.value || !password.value) {
    alert('邮箱和密码不能为空！');
    return;
  }
  try {
    const response = await apiClient.post('/register', {
      email: email.value,
      password: password.value,
      username: email.value
    });
    alert(response.data.message);
    // 注册成功后，跳转到登录页面
    router.push('/login');
  } catch (error) {
    if (error.response) {
      alert('注册失败：' + error.response.data.message);
    } else {
      alert('注册失败：无法连接到服务器。');
    }
  }
}
</script>

<style scoped>
.register-container {
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
  margin-bottom: 10px;
}
p {
  color: #666;
  margin-bottom: 25px;
}
.register-form .form-group {
  margin-bottom: 15px;
  text-align: left;
}
.register-form label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
.register-form input {
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
  background-color: #007bff;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
}
button:hover {
  background-color: #0056b3;
}
</style>