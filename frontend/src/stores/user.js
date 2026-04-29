import { defineStore } from 'pinia'
import request from '../utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    membershipLevel: (state) => state.userInfo?.membership_level || 'free',
    isDiamond: (state) => state.userInfo?.membership_level === 'diamond',
    isGold: (state) => state.userInfo?.membership_level === 'gold',
    isSilver: (state) => state.userInfo?.membership_level === 'silver',
  },

  actions: {
    async login(username, password) {
      const data = await request.post('/auth/login', { username, password })
      this.token = data.access_token
      this.userInfo = data.user_info
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('userInfo', JSON.stringify(data.user_info))
      return data
    },

    async register(username, password, email) {
      const data = await request.post('/auth/register', { username, password, email })
      this.token = data.access_token
      this.userInfo = data.user_info
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('userInfo', JSON.stringify(data.user_info))
      return data
    },

    async fetchUserInfo() {
      const data = await request.get('/auth/me')
      this.userInfo = data
      localStorage.setItem('userInfo', JSON.stringify(data))
      return data
    },

    logout() {
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    },
  },
})
