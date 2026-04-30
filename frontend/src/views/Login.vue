<template>
  <div class="login-page">
    <div class="login-card">
      <div class="back-home" @click="router.push('/')">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回首页</span>
      </div>
      <h2 class="login-title">竞彩足球数据分析平台</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password @keyup.enter="handleLogin" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width:100%" @click="handleLogin">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        还没有账号？<router-link to="/register">立即注册</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  await formRef.value?.validate()
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect || '/'
    const tab = route.query.tab
    if (tab) {
      router.push({ path: redirect, query: { tab } })
    } else {
      router.push(redirect)
    }
  } catch (e) {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $bg-dark 0%, $bg-header 100%);
}

.login-card {
  width: 400px;
  padding: 40px;
  background: $text-white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  position: relative;

  @include mobile {
    width: 100%;
    min-height: 100vh;
    border-radius: 0;
    padding: 60px 20px;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
}

.back-home {
  position: absolute;
  top: 16px;
  left: 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  color: $text-secondary;
  font-size: 13px;
  cursor: pointer;
  transition: color 0.2s;

  &:hover {
    color: $primary-color;
  }
}

.login-title {
  text-align: center;
  margin-bottom: 30px;
  color: $primary-color;
  font-size: 22px;
}

.login-footer {
  text-align: center;
  margin-top: 15px;
  color: $text-secondary;
  font-size: 13px;
}
</style>
