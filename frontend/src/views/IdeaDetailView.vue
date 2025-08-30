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
      
      <div class="content-body" v-html="renderedContent"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import apiClient from '@/services/api';
// (3) 导入 markdown-it
import MarkdownIt from 'markdown-it';

const idea = ref(null);
const isLoading = ref(true);
const error = ref(null);
const route = useRoute();
const apiBaseUrl = 'http://localhost:5000'; // 后端地址

const md = new MarkdownIt(); // 创建 markdown-it 实例

// (4) 计算属性，用来动态渲染内容
const renderedContent = computed(() => {
  if (!idea.value || !idea.value.content) return '';
  // 在真实项目中，这里可以根据 idea.content_type 来判断
  // 现在我们简单地假设，如果内容包含HTML标签，就直接显示，否则用Markdown渲染
  if (idea.value.content.includes('<p>') || idea.value.content.includes('<h1>')) {
    return idea.value.content; // 假设是HTML，直接返回
  }
  return md.render(idea.value.content); // 否则，用markdown-it渲染
});

async function fetchIdeaDetail() {
  const ideaId = route.params.id;
  try {
    const response = await apiClient.get(`/ideas/${ideaId}`);
    idea.value = response.data;
  } catch (err) {
    error.value = '无法加载该创意。';
  } finally {
    isLoading.value = false;
  }
}
onMounted(fetchIdeaDetail);
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