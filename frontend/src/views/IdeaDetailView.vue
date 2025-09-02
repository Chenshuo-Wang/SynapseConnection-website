<template>
  <div class="detail-container">
    <div v-if="isLoading">正在加载...</div>
    <div v-if="error">{{ error }}</div>
    <div v-if="idea">
      <h1>{{ idea.title }}</h1>
      <div class="meta-info">
        <span>由 <strong>{{ idea.author }}</strong></span>
        <span>发布于 {{ idea.created_at }}</span>
      </div>
      
      <img v-if="idea.image_url" :src="apiBaseUrl + idea.image_url" alt="封面图片" class="cover-image"/>
      
      <md-editor v-model="idea.content" previewOnly />
    </div>
  </div>
</template>

<script setup>
// frontend/src/views/IdeaDetailView.vue 的 <script setup> (诊断版)

import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api.js';

// 导入 md-editor-v3 的预览组件
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';

const idea = ref(null);
const isLoading = ref(true);
const error = ref(null);
const route = useRoute(); // 用来获取当前页面的路由信息

// --- 【核心】获取数据的函数 ---
async function fetchIdeaDetail() {
  // 1. 打印一下，看看我们是否正确拿到了URL里的ID
  const ideaId = route.params.id;
  console.log('1. 正在为 Idea ID 获取数据:', ideaId);

  // 检查 ideaId 是否有效
  if (!ideaId) {
    error.value = '错误：在URL中没有找到Idea ID。';
    isLoading.value = false;
    console.error(error.value);
    return;
  }

  try {
    const response = await apiClient.get(`/ideas/${ideaId}`);
    
    // 2. 打印一下，看看从后端收到了什么数据
    console.log('2. 成功从后端收到数据:', response.data);
    
    idea.value = response.data;
  } catch (err) {
    // 3. 如果请求失败，打印出详细的错误信息
    console.error("3. 获取Idea详情时发生严重错误:", err);
    error.value = '无法加载该创意，它可能不存在或服务器出错。请检查浏览器控制台的详细错误信息。';
  } finally {
    isLoading.value = false;
  }
}

// 页面加载后，立即执行上面的函数
onMounted(() => {
  fetchIdeaDetail();
});
</script>

<style scoped>
.cover-image {
  width: 100%;
  max-height: 400px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 30px;
}
.content-body {
  font-size: 18px;
  line-height: 1.8;
}
/* ... 其他样式保持不变 ... */
</style>