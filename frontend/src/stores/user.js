import { defineStore } from 'pinia'
import request from '../utils/request'

const DEFAULT_SECTIONS = ['titan', 'detail']

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
    accessibleSections: JSON.parse(localStorage.getItem('accessibleSections') || 'null') || DEFAULT_SECTIONS,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    membershipLevel: (state) => state.userInfo?.membership_level || 'free',
    isDiamond: (state) => state.userInfo?.membership_level === 'diamond',
    isGold: (state) => state.userInfo?.membership_level === 'gold',
    isSilver: (state) => state.userInfo?.membership_level === 'silver',
    canAccess: (state) => (sectionKey) => {
      if (!state.isLoggedIn) return DEFAULT_SECTIONS.includes(sectionKey)
      return state.accessibleSections.includes(sectionKey)
    },
  },

  actions: {
    async login(username, password) {
      const data = await request.post('/auth/login', { username, password })
      this.token = data.access_token
      this.userInfo = data.user_info
      this.accessibleSections = data.accessible_sections || DEFAULT_SECTIONS
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('userInfo', JSON.stringify(data.user_info))
      localStorage.setItem('accessibleSections', JSON.stringify(this.accessibleSections))
      return data
    },

    async register(username, password, email) {
      const data = await request.post('/auth/register', { username, password, email })
      this.token = data.access_token
      this.userInfo = data.user_info
      this.accessibleSections = data.accessible_sections || DEFAULT_SECTIONS
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('userInfo', JSON.stringify(data.user_info))
      localStorage.setItem('accessibleSections', JSON.stringify(this.accessibleSections))
      return data
    },

    async fetchUserInfo() {
      const data = await request.get('/auth/me')
      this.userInfo = data
      localStorage.setItem('userInfo', JSON.stringify(data))
      try {
        const sectionsData = await request.get('/auth/sections')
        this.accessibleSections = sectionsData.sections || DEFAULT_SECTIONS
        localStorage.setItem('accessibleSections', JSON.stringify(this.accessibleSections))
      } catch {}
      return data
    },

    async refreshSections() {
      if (!this.token) return
      try {
        const data = await request.get('/auth/sections')
        this.accessibleSections = data.sections || DEFAULT_SECTIONS
        localStorage.setItem('accessibleSections', JSON.stringify(this.accessibleSections))
      } catch {}
    },

    logout() {
      this.token = ''
      this.userInfo = null
      this.accessibleSections = DEFAULT_SECTIONS
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('accessibleSections')
    },
  },
})
