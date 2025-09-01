<template>
  <div class="submit-container">
    <h1>分享您的下一个伟大创意</h1>
    <p>您的草稿将自动同步到云端</p>

    <form @submit.prevent="submitIdea" class="idea-form">
      <div class="form-group file-import">
        <label for="md-importer">或者，直接导入一个 .md 文件</label>
        <input type="file" id="md-importer" @change="handleFileImport" accept=".md,.txt" />
      </div>

      <div class="form-group">
        <label for="title">创意标题</label>
        <input 
          type="text" 
          id="title" 
          v-model="title" 
          placeholder="给您的创意起一个响亮的名字" 
          required 
        />
      </div>

      <div class="form-group">
        <label for="image">封面图片 (可选)</label>
        <input type="file" id="image" @change="handleImageUpload" accept="image/*" />
      </div>
      
      <div class="form-group">
        <label>详细内容 (支持 Markdown)</label>
        <md-editor 
          v-model="content" 
          language="zh-CN"
          :onUploadImg="handleEditorImageUploadV3"
          placeholder="在这里详细描述您的创意..."
          style="height: 500px;"
        />
      </div>

      <button type="submit">提交创意</button>
    </form>
  </div>
</template>

<script setup>
// frontend/src/views/SubmitIdeaView.vue 的 <script setup> (md-editor-v3 版本)

import { ref, onMounted, watch } from 'vue';
import apiClient from '@/services/api.js';
import { useRouter } from 'vue-router';

// 1. 导入新的 md-editor-v3 编辑器和它的样式
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';


// --- 核心逻辑 (大部分保持不变) ---
const router = useRouter();
const title = ref('');
const content = ref('');
const uploadedImageFilename = ref(null);
let debounceTimer = null;


// 2. 【关键】为 md-editor-v3 重写图片上传函数
const handleEditorImageUploadV3 = async (files, callback) => {
  if (files.length === 0) {
    return;
  }

  // 使用 Promise.all 来处理可能的多图片上传
  const results = await Promise.all(
    Array.from(files).map(async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      
      try {
        const response = await apiClient.post('/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        // 返回后端提供的完整图片 URL
        return `http://localhost:5000/uploads/${response.data.filename}`;
      } catch (error) {
        console.error("图片上传失败:", error);
        // 返回一个空字符串或错误提示，表示此图片上传失败
        return null;
      }
    })
  )

  // 过滤掉上传失败的结果，然后调用回调函数将图片URL插入编辑器
  callback(results.filter(url => url !== null));
};


// --- 云端草稿逻辑 (保持不变) ---
async function fetchDraft() {
  try {
    const response = await apiClient.get('/draft');
    if (response.data && (response.data.title || response.data.content)) {
      if (confirm('检测到您有云端草稿，是否需要恢复？')) {
        title.value = response.data.title || '';
        content.value = response.data.content || '';
      }
    }
  } catch (error) {
    console.error("获取云端草稿失败:", error);
    if (error.response && error.response.status !== 401) {
      alert('获取云端草稿失败！请检查网络连接。');
    }
  }
}
onMounted(fetchDraft);
watch([title, content], () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(saveDraft, 2000);
});
async function saveDraft() {
  try {
    await apiClient.post('/draft', { title: title.value, content: content.value });
    console.log('草稿已成功保存到云端！');
  } catch (error) {
    console.error("保存草稿到云端失败:", error);
  }
}
async function deleteDraft() {
  try {
    await apiClient.delete('/draft');
    console.log('云端草稿已成功删除。');
  } catch (error) {
    console.error("删除云端草稿失败:", error);
  }
}


// --- 封面图片和文件导入逻辑 (保持不变) ---
function handleFileImport(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => { content.value = e.target.result; };
  reader.readAsText(file);
  event.target.value = '';
}
async function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await apiClient.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    uploadedImageFilename.value = response.data.filename;
    alert('封面图片上传成功！');
  } catch (error) {
    alert('封面图片上传失败，请重试。');
    console.error(error);
  }
}


// --- 表单提交逻辑 (保持不变) ---
async function submitIdea() {
  if (!title.value || !content.value) {
    alert('标题和内容都不能为空！');
    return;
  }
  const formData = new FormData();
  formData.append('title', title.value);
  formData.append('content', content.value);
  if (uploadedImageFilename.value) {
    formData.append('image_filename', uploadedImageFilename.value);
  }
  try {
    const response = await apiClient.post('/ideas', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
    alert(response.data.message);
    await deleteDraft();
    router.push('/ideas');
  } catch (error) {
    if (error.response && error.response.status === 401) {
      alert('认证失败，请先登录！');
      router.push('/login');
    } else if (error.response) {
      alert('提交失败：' + error.response.data.message);
    } else {
      alert('提交失败：无法连接到服务器。');
    }
  }
}
</script>

<style scoped>
.file-import {
  background-color: #f0f7ff;
  border: 1px dashed #a0c4e4;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.file-import label {
  font-weight: normal !important;
  color: #333;
}
.submit-container {
  max-width: 800px;
  margin: 40px auto;
  padding: 20px 30px;
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
h1 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 10px;
}
p {
  text-align: center;
  color: #666;
  margin-bottom: 30px;
}
.idea-form .form-group {
  margin-bottom: 20px;
}
.idea-form label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 16px;
}
.idea-form input[type="text"],
.idea-form input[type="file"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-sizing: border-box;
  font-size: 16px;
  font-family: inherit;
}
button {
  width: 100%;
  padding: 15px;
  font-size: 18px;
  border: none;
  border-radius: 8px;
  background-color: #5a67d8;
  color: white;
  cursor: pointer;
  transition: background-color 0.2s;
} 
button:hover {  
  background-color: #434190;    
}
</style>
