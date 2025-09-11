import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/course': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/user': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/users': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/students': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/login': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/register': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/me': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/chat': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/material': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/student': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/teacher': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/assignment': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/preparation': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/ppt': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
}) 