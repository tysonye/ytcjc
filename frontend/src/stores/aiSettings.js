import { defineStore } from 'pinia'
import request from '../utils/request'

const PREFERENCE_OPTIONS = [
  { key: 'odds_trend', label: '赔率走势分析' },
  { key: 'head_to_head', label: '历史交锋记录' },
  { key: 'recent_form', label: '球队近期状态' },
  { key: 'home_away', label: '主客场战绩差异' },
  { key: 'injury', label: '伤停/阵容信息' },
  { key: 'standings', label: '联赛积分排名' },
  { key: 'fund_flow', label: '盘口资金流向' },
  { key: 'weather', label: '天气/场地影响' },
]

const PRESET_CONFIG = {
  conservative: { label: '稳健', temperature: 0.3, focus: '赔率走势、历史数据', preferences: ['odds_trend', 'head_to_head', 'standings'] },
  balanced: { label: '均衡', temperature: 0.7, focus: '综合分析', preferences: ['odds_trend', 'head_to_head'] },
  aggressive: { label: '激进', temperature: 1.0, focus: '盘口异动、资金流向', preferences: ['odds_trend', 'head_to_head', 'fund_flow', 'home_away'] },
}

const STORAGE_KEY = 'ai_settings'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch {}
  return null
}

function saveToStorage(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

export const useAISettingsStore = defineStore('aiSettings', {
  state: () => {
    const saved = loadFromStorage()
    return {
      preset: saved?.preset || 'balanced',
      preferences: saved?.preferences || ['odds_trend', 'head_to_head'],
      replyFormat: saved?.replyFormat || 'detailed',
      replyLanguage: saved?.replyLanguage || 'zh',
      customPrompt: saved?.customPrompt || '',
    }
  },
  getters: {
    preferenceOptions: () => PREFERENCE_OPTIONS,
    presetOptions: () => PRESET_CONFIG,
    temperature: (state) => PRESET_CONFIG[state.preset]?.temperature ?? 0.7,
  },
  actions: {
    setPreset(preset) {
      this.preset = preset
      this.preferences = [...(PRESET_CONFIG[preset]?.preferences || [])]
      this._save()
    },
    togglePreference(key) {
      const idx = this.preferences.indexOf(key)
      if (idx >= 0) {
        this.preferences.splice(idx, 1)
      } else {
        this.preferences.push(key)
      }
      this._save()
    },
    setReplyFormat(format) {
      this.replyFormat = format
      this._save()
    },
    setReplyLanguage(lang) {
      this.replyLanguage = lang
      this._save()
    },
    setCustomPrompt(prompt) {
      this.customPrompt = prompt
      this._save()
    },
    save() {
      this._save()
    },
    _save() {
      const data = {
        preset: this.preset,
        preferences: this.preferences,
        replyFormat: this.replyFormat,
        replyLanguage: this.replyLanguage,
        customPrompt: this.customPrompt,
      }
      saveToStorage(data)
      this._syncToServer(data)
    },
    async _syncToServer(data) {
      const token = localStorage.getItem('token')
      if (!token) return
      try {
        await request.put('/user-config/sections', { ai_settings: JSON.stringify(data) })
      } catch {}
    },
    async loadFromServer() {
      const token = localStorage.getItem('token')
      if (!token) return
      try {
        const data = await request.get('/user-config/sections')
        if (data.ai_settings) {
          const config = JSON.parse(data.ai_settings)
          this.preset = config.preset || this.preset
          this.preferences = config.preferences || this.preferences
          this.replyFormat = config.replyFormat || this.replyFormat
          this.replyLanguage = config.replyLanguage || this.replyLanguage
          this.customPrompt = config.customPrompt || this.customPrompt
          saveToStorage({
            preset: this.preset,
            preferences: this.preferences,
            replyFormat: this.replyFormat,
            replyLanguage: this.replyLanguage,
            customPrompt: this.customPrompt,
          })
        }
      } catch (e) {
        if (e.response?.status === 401) return
      }
    },
    getSettings() {
      return {
        preset: this.preset,
        preferences: [...this.preferences],
        replyFormat: this.replyFormat,
        replyLanguage: this.replyLanguage,
        customPrompt: this.customPrompt,
        temperature: this.temperature,
      }
    },
  },
})
