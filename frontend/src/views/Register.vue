<template>
  <div class="register-page">
    <div class="register-card">
      <div class="back-home" @click="router.push('/')">
        <el-icon><ArrowLeft /></el-icon>
        <span>返回首页</span>
      </div>
      <h2 class="register-title">注册账号</h2>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0">
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名（3-20位字母、数字或下划线）"
            prefix-icon="User"
            size="large"
            @input="checkUsername"
          />
          <div v-if="usernameFeedback" class="field-feedback" :class="usernameFeedback.type">
            <el-icon><component :is="usernameFeedback.icon" /></el-icon>
            <span>{{ usernameFeedback.text }}</span>
          </div>
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @input="checkPassword"
          />
          <div v-if="form.password" class="password-strength">
            <div class="strength-bar">
              <div class="strength-fill" :class="strengthClass" :style="{ width: strengthPercent + '%' }"></div>
            </div>
            <span class="strength-label" :class="strengthClass">{{ strengthLabel }}</span>
          </div>
          <div v-if="form.password" class="password-rules">
            <div class="rule-item" :class="{ passed: passwordChecks.length }">
              <el-icon><component :is="passwordChecks.length ? 'Select' : 'CloseBold'" /></el-icon>
              <span>8-30个字符</span>
            </div>
            <div class="rule-item" :class="{ passed: passwordChecks.hasLetter }">
              <el-icon><component :is="passwordChecks.hasLetter ? 'Select' : 'CloseBold'" /></el-icon>
              <span>包含字母</span>
            </div>
            <div class="rule-item" :class="{ passed: passwordChecks.hasNumber }">
              <el-icon><component :is="passwordChecks.hasNumber ? 'Select' : 'CloseBold'" /></el-icon>
              <span>包含数字</span>
            </div>
            <div class="rule-item" :class="{ passed: passwordChecks.hasSpecial }">
              <el-icon><component :is="passwordChecks.hasSpecial ? 'Select' : 'CloseBold'" /></el-icon>
              <span>包含特殊字符（推荐）</span>
            </div>
          </div>
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="确认密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @input="checkConfirm"
          />
          <div v-if="confirmFeedback" class="field-feedback" :class="confirmFeedback.type">
            <el-icon><component :is="confirmFeedback.icon" /></el-icon>
            <span>{{ confirmFeedback.text }}</span>
          </div>
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱（选填）" prefix-icon="Message" size="large" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" :loading="loading" style="width:100%" @click="handleRegister">
            注册
          </el-button>
        </el-form-item>
      </el-form>
      <div class="register-footer">
        已有账号？<router-link to="/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Select, CloseBold } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({ username: '', password: '', confirmPassword: '', email: '' })

const usernameFeedback = ref(null)
const confirmFeedback = ref(null)

const passwordChecks = reactive({
  length: false,
  hasLetter: false,
  hasNumber: false,
  hasSpecial: false,
})

const strengthLevel = ref(0)

const strengthClass = computed(() => {
  if (strengthLevel.value <= 1) return 'weak'
  if (strengthLevel.value === 2) return 'medium'
  if (strengthLevel.value === 3) return 'strong'
  return ''
})

const strengthPercent = computed(() => {
  return Math.min((strengthLevel.value / 4) * 100, 100)
})

const strengthLabel = computed(() => {
  if (strengthLevel.value <= 1) return '弱'
  if (strengthLevel.value === 2) return '中等'
  if (strengthLevel.value >= 3) return '强'
  return ''
})

function checkUsername() {
  const val = form.username
  if (!val) {
    usernameFeedback.value = null
    return
  }
  if (val.length < 3) {
    usernameFeedback.value = { type: 'error', icon: 'CloseBold', text: '用户名至少需要3个字符' }
  } else if (val.length > 20) {
    usernameFeedback.value = { type: 'error', icon: 'CloseBold', text: '用户名不能超过20个字符' }
  } else if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(val)) {
    usernameFeedback.value = { type: 'error', icon: 'CloseBold', text: '用户名只能包含字母、数字、下划线或中文' }
  } else if (/^\d+$/.test(val)) {
    usernameFeedback.value = { type: 'warning', icon: 'WarningFilled', text: '不建议使用纯数字作为用户名' }
  } else {
    usernameFeedback.value = { type: 'success', icon: 'Select', text: '用户名格式正确' }
  }
}

function checkPassword() {
  const val = form.password
  passwordChecks.length = val.length >= 8 && val.length <= 30
  passwordChecks.hasLetter = /[a-zA-Z]/.test(val)
  passwordChecks.hasNumber = /\d/.test(val)
  passwordChecks.hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(val)

  let score = 0
  if (passwordChecks.length) score++
  if (passwordChecks.hasLetter && passwordChecks.hasNumber) score++
  if (passwordChecks.hasSpecial) score++
  if (val.length >= 12) score++
  strengthLevel.value = score

  if (form.confirmPassword) checkConfirm()
}

function checkConfirm() {
  if (!form.confirmPassword) {
    confirmFeedback.value = null
    return
  }
  if (form.confirmPassword === form.password) {
    confirmFeedback.value = { type: 'success', icon: 'Select', text: '两次密码一致' }
  } else {
    confirmFeedback.value = { type: 'error', icon: 'CloseBold', text: '两次密码不一致' }
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
    return
  }
  if (value.length < 8) {
    callback(new Error('密码至少8个字符'))
    return
  }
  if (value.length > 30) {
    callback(new Error('密码不能超过30个字符'))
    return
  }
  if (!/[a-zA-Z]/.test(value)) {
    callback(new Error('密码必须包含字母'))
    return
  }
  if (!/\d/.test(value)) {
    callback(new Error('密码必须包含数字'))
    return
  }
  if (strengthLevel.value < 2) {
    callback(new Error('密码强度过低，建议包含字母、数字和特殊字符'))
    return
  }
  callback()
}

const validateConfirm = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== form.password) {
    callback(new Error('两次密码不一致'))
  } else {
    callback()
  }
}

const validateUsername = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入用户名'))
    return
  }
  if (value.length < 3) {
    callback(new Error('用户名至少3个字符'))
    return
  }
  if (value.length > 20) {
    callback(new Error('用户名不能超过20个字符'))
    return
  }
  if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(value)) {
    callback(new Error('用户名只能包含字母、数字、下划线或中文'))
    return
  }
  callback()
}

const rules = {
  username: [
    { required: true, validator: validateUsername, trigger: 'blur' },
  ],
  password: [
    { required: true, validator: validatePassword, trigger: 'change' },
  ],
  confirmPassword: [
    { required: true, validator: validateConfirm, trigger: 'change' },
  ],
  email: [
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
}

const handleRegister = async () => {
  await formRef.value?.validate()
  loading.value = true
  try {
    await userStore.register(form.username, form.password, form.email || undefined)
    ElMessage.success('注册成功')
    router.push('/')
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

.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $bg-dark 0%, $bg-header 100%);
}

.register-card {
  width: 420px;
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

.register-title {
  text-align: center;
  margin-bottom: 30px;
  color: $primary-color;
}

.register-footer {
  text-align: center;
  margin-top: 15px;
  color: $text-secondary;
  font-size: 13px;
}

.field-feedback {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  margin-top: 4px;
  padding-left: 2px;

  &.success { color: #67c23a; }
  &.warning { color: #e6a23c; }
  &.error { color: #f56c6c; }
}

.password-strength {
  margin-top: 6px;
  display: flex;
  align-items: center;
  gap: 8px;

  .strength-bar {
    flex: 1;
    height: 4px;
    background: #e4e7ed;
    border-radius: 2px;
    overflow: hidden;

    .strength-fill {
      height: 100%;
      border-radius: 2px;
      transition: width 0.3s, background 0.3s;

      &.weak { background: #f56c6c; }
      &.medium { background: #e6a23c; }
      &.strong { background: #67c23a; }
    }
  }

  .strength-label {
    font-size: 12px;
    min-width: 32px;
    text-align: right;

    &.weak { color: #f56c6c; }
    &.medium { color: #e6a23c; }
    &.strong { color: #67c23a; }
  }
}

.password-rules {
  margin-top: 8px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 12px;

  .rule-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #c0c4cc;

    &.passed {
      color: #67c23a;
    }
  }
}
</style>
