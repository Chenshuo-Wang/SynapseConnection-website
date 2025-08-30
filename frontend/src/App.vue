<template>
  <header>
    <div class="wrapper">
      <nav>
        <RouterLink to="/">首页</RouterLink>
        <RouterLink to="/ideas">创意广场</RouterLink>

        <template v-if="isLoggedIn">
          <RouterLink to="/submit-idea">提交创意</RouterLink>
          <a @click="logout" href="#">登出</a>
        </template>
        <template v-else>
          <RouterLink to="/login">登录</RouterLink>
          <RouterLink to="/register">注册</RouterLink>
        </template>
      </nav>
    </div>
  </header>
  <RouterView />
</template>

<script setup>
import { ref, watch } from 'vue';
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router';

const isLoggedIn = ref(!!localStorage.getItem('token'));
const router = useRouter();
const route = useRoute();

// 监听路由变化，以更新登录状态（例如，用户手动跳转页面）
watch(route, () => {
  isLoggedIn.value = !!localStorage.getItem('token');
});

function logout() {
  localStorage.removeItem('token');
  isLoggedIn.value = false;
  alert('您已成功登出。');
  router.push('/login');
}
</script>

<style scoped>
/* 样式保持不变，但为登出链接添加一个指针样式 */
nav a[href="#"] {
  cursor: pointer;
}
header {
  line-height: 1.5;
  max-height: 100vh;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e7e7e7;
  padding: 0 2rem;
}
nav {
  width: 100%;
  font-size: 16px;
  text-align: center;
  margin-top: 1rem;
  margin-bottom: 1rem;
}
nav a {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-left: 1px solid var(--color-border);
  text-decoration: none;
  color: #2c3e50;
  transition: color 0.3s;
}
nav a:first-of-type {
  border: 0;
}
nav a.router-link-exact-active {
  color: #42b983;
  font-weight: bold;
}
nav a.router-link-exact-active:hover {
  background-color: transparent;
}
nav a:hover {
  background-color: #f2f2f2;
}
</style>