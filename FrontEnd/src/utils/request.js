import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const service = axios.create({
  baseURL: '/', // 修改为相对路径，使用 Vite 代理
  timeout: 120000,  // 增加到120秒
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 检查是否需要静默处理404错误
    const isSilent404 = error.config?.silentNotFound && error.response?.status === 404
    
    if (!isSilent404) {
      console.error('响应错误:', error)
    }
    
    if (error.response) {
      // 服务器返回错误状态码
      if (error.response.status === 401) {
        ElMessage.error('登录已过期，请重新登录')
        localStorage.removeItem('token')
        window.location.href = '/login'
      } else if (error.response.status === 403) {
        ElMessage.error('没有权限访问该资源')
      } else if (error.response.status === 404 && !isSilent404) {
        ElMessage.error('请求的资源不存在')
      } else if (error.response.status === 500) {
        ElMessage.error('服务器内部错误，请稍后重试')
      } else if (!isSilent404) {
        ElMessage.error(error.response.data?.detail || '请求失败')
      }
    } else if (error.request) {
      // 请求发出但没有收到响应
      ElMessage.error('无法连接到服务器，请检查网络连接')
    } else {
      // 请求配置出错
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export default service 