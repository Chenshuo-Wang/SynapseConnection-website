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
        <v-md-editor 
        v-model="content" 
        height="500px"
        :upload-image="handleEditorImageUpload"
        placeholder="在这里详细描述您的创意..."
        ></v-md-editor>
      </div>

      <button type="submit">提交创意</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import apiClient from '@/services/api.js';
import { useRouter } from 'vue-router';

// --- Markdown 编辑器配置 (中文版) ---
import VMdEditor from '@kangc/v-md-editor';
import '@kangc/v-md-editor/lib/style/base-editor.css';
import vuepressTheme from '@kangc/v-md-editor/lib/theme/vuepress.js';
import '@kangc/v-md-editor/lib/theme/style/vuepress.css';
import zhCN from '@kangc/v-md-editor/lib/lang/zh-CN';
VMdEditor.use(vuepressTheme, {
  // 在这里将我们的上传函数注册到主题中
  uploadImage: {
    upload: handleEditorImageUpload,
  },
});
VMdEditor.lang.use('zh-CN', zhCN);

// --- 核心逻辑 ---
const router = useRouter();
const title = ref('');
const content = ref('');
const uploadedImageFilename = ref(null);

// 1. 新增：用于“防抖”的变量
let debounceTimer = null;

// --- 云端草稿逻辑 ---
async function fetchDraft() {
  try {
    const response = await apiClient.get('/draft');
    // 增加一个更严格的检查，确保草稿有内容
    if (response.data && (response.data.title || response.data.content)) {
      console.log("从云端恢复草稿:", response.data);
      // 在恢复前，弹窗询问用户
      if (confirm('检测到您有云端草稿，是否需要恢复？')) {
          title.value = response.data.title || '';
          content.value = response.data.content || '';
      }
    } else {
      console.log("云端没有草稿。");
    }
  } catch (error) {
    console.error("获取云端草稿失败:", error);
    // 如果是因为未登录(401)，则不需要打扰用户
    if (error.response && error.response.status === 401) {
      console.log("用户未登录，无法获取草稿。");
    } else {
      // 对于其他错误（比如网络问题），明确地提示用户
      alert('获取云端草稿失败！请检查您的网络连接和浏览器控制台的错误信息。');
    }
  }
}

// 页面加载时，尝试从云端获取草稿
onMounted(() => {
  fetchDraft();
});

// 2. 改造：使用“防抖”技术来智能地自动保存
watch([title, content], () => {
  // 先清除上一次的计时器
  clearTimeout(debounceTimer);
  
  // 设置一个新的计时器，在2秒后执行保存操作
  debounceTimer = setTimeout(() => {
    saveDraft();
  }, 2000); // 2000毫秒 = 2秒
});

// 3. 新增：保存草稿到云端的函数
async function saveDraft() {
  console.log('正在保存草稿到云端...');
  try {
    await apiClient.post('/draft', {
      title: title.value,
      content: content.value
    });
    console.log('草稿已成功保存到云端！');
    // 这里可以给用户一个不打扰的、“已保存”的提示
  } catch (error) {
    console.error("保存草稿到云端失败:", error);
  }
}

// 4. 新增：提交成功后，删除云端草稿的函数
async function deleteDraft() {
  try {
    await apiClient.delete('/draft');
    console.log('云端草稿已成功删除。');
  } catch (error) {
    console.error("删除云端草稿失败:", error);
  }
}

// --- 文件导入与图片上传逻辑 (保持不变) ---
function handleFileImport(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    content.value = e.target.result;
  };
  reader.readAsText(file);
  event.target.value = '';
}

async function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  try {
    const response = await apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    uploadedImageFilename.value = response.data.filename;
    alert('图片上传成功！');
  } catch (error) {
    alert('图片上传失败，请重试。');
    console.error(error);
  }
}

// --- 新增：处理 Markdown 编辑器内部图片上传的函数 ---
async function handleEditorImageUpload(event, insertImage, files) {
  // event: 原生事件
  // insertImage: 编辑器提供的一个函数，用来插入图片
  // files: 用户选择的文件列表

  if (files.length === 0) return;

  const file = files[0];
  const formData = new FormData();
  formData.append('file', file);

  console.log("编辑器正在上传图片...");

  try {
    // 调用我们现有的/upload接口
    const response = await apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    
    // 从后端获取上传成功后的文件名
    const filename = response.data.filename;
    
    // 使用 insertImage 函数将图片插入到编辑器中
    // 我们需要构建完整的图片URL
    insertImage({
      url: `http://localhost:5000/uploads/${filename}`,
      desc: '图片描述', // 您可以自定义默认的图片描述
      // width: 'auto',
      // height: 'auto',
    });
    console.log("编辑器图片上传成功！");

  } catch (error) {
    alert('编辑器内图片上传失败，请重试。');
    console.error("编辑器图片上传失败:", error);
  }
}

// --- 表单提交逻辑 (改造) ---
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
    const response = await apiClient.post('/ideas', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    alert(response.data.message);
    
    // 5. 提交成功后，调用删除云端草稿的函数
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
/* 样式部分保持不变 */
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