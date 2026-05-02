import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    const adminToken = localStorage.getItem('adminToken')
    const authToken = adminToken || token
    if (authToken) {
      config.headers.Authorization = `Bearer ${authToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

const isLoginRelated = (path) => ['/login', '/register'].includes(path)
const isAdminRelated = (path) => path.startsWith('/admin')

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      const currentPath = router.currentRoute.value.path
      if (status === 401) {
        if (isLoginRelated(currentPath)) {
          ElMessage.error(data.detail || '用户名或密码错误')
        } else if (isAdminRelated(currentPath)) {
          localStorage.removeItem('adminToken')
          localStorage.removeItem('adminInfo')
          router.push('/admin/login')
          ElMessage.error('管理员登录已过期，请重新登录')
        } else {
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          router.push('/login')
          ElMessage.error('登录已过期，请重新登录')
        }
      } else if (status === 403) {
        ElMessage.error(data.detail || '权限不足')
      } else if (status === 404) {
        ElMessage.error('请求的资源不存在')
      } else {
        ElMessage.error(data.detail || '请求失败')
      }
    } else {
      ElMessage.error('网络错误，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export default request
