<template>
  <div class="admin-login">
    <div class="login-box">
      <h2>管理员登录</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="管理员账号" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width:100%" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <router-link to="/" style="display:block;text-align:center;margin-top:10px;color:#999;font-size:13px;">返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const formRef = ref()
const loading = ref(false)
const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value?.validate()
  loading.value = true
  try {
    const resp = await fetch('/api/admin/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    const data = await resp.json()
    if (!resp.ok) throw new Error(data.detail || '登录失败')
    localStorage.setItem('adminToken', data.access_token)
    localStorage.setItem('adminInfo', JSON.stringify(data.admin_info))
    ElMessage.success('登录成功')
    router.push('/admin')
  } catch (e) {
    ElMessage.error(e.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login { min-height:100vh;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#001529,#003a70); }
.login-box { width:380px;padding:40px;background:#fff;border-radius:8px;box-shadow:0 8px 32px rgba(0,0,0,0.2); }
.login-box h2 { text-align:center;margin-bottom:25px;color:#1890ff;font-size:20px; }
</style>
