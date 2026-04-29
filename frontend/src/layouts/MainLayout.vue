<template>
  <div class="main-layout">
    <header class="top-header">
      <div class="header-left">
        <div class="logo">
          <el-icon :size="22"><Football /></el-icon>
          <span class="logo-text">竞彩助手</span>
        </div>
        <nav class="header-nav">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">
            <el-icon><Football /></el-icon>
            <span>竞足</span>
          </router-link>
          <router-link v-if="userStore.isLoggedIn" to="/member" class="nav-item" :class="{ active: $route.path === '/member' }">
            <el-icon><User /></el-icon>
            <span>会员中心</span>
          </router-link>
        </nav>
      </div>
      <div class="header-right">
        <template v-if="userStore.isLoggedIn">
          <span class="user-greeting">{{ userStore.userInfo?.username }}</span>
          <el-button size="small" @click="handleLogout">退出</el-button>
        </template>
        <template v-else>
          <router-link to="/login">
            <el-button size="small" type="primary">登录</el-button>
          </router-link>
          <router-link to="/register">
            <el-button size="small">注册</el-button>
          </router-link>
        </template>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <nav v-if="!isDesktop" class="bottom-nav">
      <router-link to="/" class="bottom-nav-item" :class="{ active: $route.path === '/' }">
        <el-icon><Football /></el-icon>
        <span>比赛</span>
      </router-link>
      <router-link v-if="userStore.isLoggedIn" to="/member" class="bottom-nav-item" :class="{ active: $route.path === '/member' }">
        <el-icon><User /></el-icon>
        <span>会员</span>
      </router-link>
      <template v-else>
        <router-link to="/login" class="bottom-nav-item">
          <el-icon><User /></el-icon>
          <span>登录</span>
        </router-link>
        <router-link to="/register" class="bottom-nav-item">
          <el-icon><CirclePlus /></el-icon>
          <span>注册</span>
        </router-link>
      </template>
    </nav>

    <AIChat />
  </div>
</template>

<script setup>
import { useUserStore } from '../stores/user'
import { useResponsive } from '../utils/responsive'
import { useRouter } from 'vue-router'
import AIChat from '../components/AIChat.vue'

const userStore = useUserStore()
const router = useRouter()
const { isDesktop } = useResponsive()

const handleLogout = () => {
  userStore.logout()
  router.push('/')
}
</script>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.main-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.top-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 50px;
  padding: 0 20px;
  background: $bg-dark;
  color: $text-white;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);

  @include mobile {
    padding: 0 12px;
    height: 44px;
  }
}

.header-left {
  display: flex;
  align-items: center;
  gap: 30px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: bold;
  letter-spacing: 1px;
  white-space: nowrap;
  color: $text-white;

  @include mobile {
    font-size: 15px;
    gap: 5px;
  }
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 4px;

  @include mobile {
    display: none;
  }
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 6px 14px;
  border-radius: 4px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  font-size: 13px;
  transition: all 0.2s;

  &:hover, &.active {
    background: rgba(255,255,255,0.12);
    color: $text-white;
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-greeting {
  font-size: 13px;
  color: rgba(255,255,255,0.85);
  margin-right: 4px;
}

.main-content {
  flex: 1;
  min-height: 0;

  @include mobile {
    padding-bottom: 56px;
  }
}

.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: $text-white;
  display: flex;
  border-top: 1px solid #ddd;
  z-index: 100;
}

.bottom-nav-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
  color: $text-secondary;
  text-decoration: none;
  font-size: 12px;

  &.active {
    color: $primary-color;
  }
}
</style>
