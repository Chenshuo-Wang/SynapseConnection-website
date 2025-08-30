// frontend/vite.config.js

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

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
  // --- 新增的服务器配置块 ---
  server: {
    // 明确指定服务器监听的地址
    host: 'localhost', 
    // 明确指定端口号
    port: 5173,
    // 如果端口被占用，直接退出而不是尝试其他端口
    strictPort: true,
    // 明确配置热更新 (HMR) 的连接方式
    hmr: {
      host: 'localhost',
      protocol: 'ws' // 使用 WebSocket 协议
    }
  }
})