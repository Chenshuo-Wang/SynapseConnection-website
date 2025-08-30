<template>
  <div class="idea-list-container">
    <h1>创意广场</h1>
    <p>看看大家都在想些什么！</p>
    
    <div v-if="isLoading">正在加载...</div>
    <div v-if="error">{{ error }}</div>
    
    <div v-if="!isLoading && !error" class="ideas-grid">
      <RouterLink v-for="idea in ideas" :key="idea.id" :to="'/ideas/' + idea.id" class="idea-card-link">
        <div class="idea-card">
          <img v-if="idea.image_url" :src="apiBaseUrl + idea.image_url" class="card-image"/>
          <div class="card-content">
            <h2>{{ idea.title }}</h2>
            <p class="idea-summary">{{ idea.content_summary }}</p>
            <div class="card-footer">
              <span>作者: {{ idea.author }}</span>
              <span>{{ idea.created_at }}</span>
            </div>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
const apiBaseUrl = 'http://localhost:5000';

// (5) 定义状态变量
const ideas = ref([])       // 用来存放从后端获取的创意列表
const isLoading = ref(true) // 用来控制加载提示的显示
const error = ref(null)     // 用来存放错误信息

// (6) 定义获取数据的方法
async function fetchIdeas() {
  try {
    const response = await axios.get('http://localhost:5000/api/ideas')
    ideas.value = response.data // 将获取到的数据赋值给 ideas 变量
  } catch (err) {
    console.error("获取Ideas失败:", err)
    error.value = '无法加载创意列表，请稍后再试。'
  } finally {
    // (7) 无论成功还是失败，最后都要结束加载状态
    isLoading.value = false
  }
}

// (8) onMounted 生命周期钩子
onMounted(() => {
  fetchIdeas() // 当组件被挂载到页面上后，立即执行获取数据的操作
})
</script>

<style scoped>
.idea-list-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
}
h1, p {
  text-align: center;
}
.loading, .error {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}
.error {
  color: #e53e3e;
}
.ideas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}
.idea-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}
.idea-card h2 {
  font-size: 20px;
  margin-top: 0;
  margin-bottom: 15px;
}
.idea-content {
  flex-grow: 1; /* 让内容区域尽可能伸展，把footer推到底部 */
  color: #333;
  line-height: 1.6;
}
.card-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #888;
}
.idea-card-link {
  text-decoration: none;
  color: inherit;
}
.card-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-top-left-radius: 12px;
  border-top-right-radius: 12px;
}
.idea-card {
  padding: 0; /* 移除内边距，让图片能贴边 */
  display: flex;
  flex-direction: column;
  height: 100%;
}
.card-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}
.idea-summary {
  flex-grow: 1;
}

</style>