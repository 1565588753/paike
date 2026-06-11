import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

request.interceptors.request.use(config => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

request.interceptors.response.use(
  response => {
    const data = response.data
    if (data && typeof data === 'object' && 'code' in data) {
      if (data.code !== 0) {
        ElMessage.error(data.message || '请求失败')
        return Promise.reject(data)
      }
      return data
    }
    return data
  },
  error => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      auth.logout()
      ElMessageBox.alert('登录已过期，请重新登录', '提示', { type: 'warning' }).then(() => {
        window.location.href = '/login'
      })
    } else if (error.response?.status === 403) {
      ElMessage.error('权限不足')
    } else {
      ElMessage.error(error.response?.data?.detail || error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
