import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const LEVEL_ORDER = { free: 0, silver: 1, gold: 2, diamond: 3 }

const routes = [
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('../views/Home.vue') },
      { path: 'match/:id', name: 'MatchDetail', component: () => import('../views/MatchDetail.vue') },
      {
        path: 'member',
        name: 'MemberCenter',
        component: () => import('../views/MemberCenter.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    meta: { requiresAdmin: true },
    children: [
      { path: '', redirect: '/admin/members' },
      { path: 'members', name: 'AdminMembers', component: () => import('../views/admin/MemberManage.vue') },
      { path: 'orders', name: 'AdminOrders', component: () => import('../views/admin/OrderManage.vue') },
      { path: 'tokens', name: 'AdminTokens', component: () => import('../views/admin/TokenStats.vue') },
      { path: 'stats', name: 'AdminStats', component: () => import('../views/admin/DataStats.vue') },
      { path: 'roles', name: 'AdminRoles', component: () => import('../views/admin/RoleManage.vue') },
      { path: 'membership-permissions', name: 'AdminMembershipPermissions', component: () => import('../views/admin/MembershipPermissionManage.vue') },
      { path: 'ai-manage', name: 'AdminAIManage', component: () => import('../views/admin/AIManage.vue') },
    ],
  },
  { path: '/admin/login', name: 'AdminLogin', component: () => import('../views/admin/AdminLogin.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresLevel) {
    const requiredLevel = to.meta.requiresLevel
    const userLevel = userStore.membershipLevel || 'free'
    if (LEVEL_ORDER[userLevel] < LEVEL_ORDER[requiredLevel]) {
      next({ name: 'MemberCenter', query: { upgrade: requiredLevel } })
      return
    }
  }

  if (to.meta.requiresAdmin) {
    const adminToken = localStorage.getItem('adminToken')
    if (!adminToken) {
      next({ name: 'AdminLogin' })
      return
    }
  }

  next()
})

export default router
