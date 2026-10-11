import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), vueDevTools()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      // API 接口代理
      '/v1': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      // 静态文件代理（头像图片）
      '/uploads': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      // SSE 流式接口代理：/api 重写到 /v1，并关闭流式响应缓冲
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/v1'),
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            // 对流式响应关掉缓冲，过程事件才能实时到浏览器
            if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['x-accel-buffering'] = 'no'
            }
          })
        }
      }
    }
  }
})
