// frontend/vite.config.js

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // --- 新增的核心部分：服务器代理配置 ---
  server: {
    proxy: {
      // 匹配所有以 /uploads 开头的请求
      '/uploads': {
        target: 'http://localhost:5000', // 目标是我们的后端服务器
        changeOrigin: true, // 必须设置为 true
      },
      // (可选) 如果您希望所有/api的请求也通过代理，可以添加下面这段
      // '/api': {
      //   target: 'http://localhost:5000',
      //   changeOrigin: true,
      // }
    }
  }
})