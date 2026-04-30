<template>
  <div class="macau-odds-panel">
    <div class="macau-header">
      <span class="macau-title">澳博数据</span>
      <span class="macau-source">数据来源：澳门彩票有限公司</span>
    </div>
    <div class="macau-nav">
      <a :class="{ active: activePage === 'odds' }" @click="switchPage('odds')">赔率</a>
      <a :class="{ active: activePage === 'schedule' }" @click="switchPage('schedule')">赛程</a>
      <a :class="{ active: activePage === 'result' }" @click="switchPage('result')">比数</a>
      <a :class="{ active: activePage === 'analysis' }" @click="switchPage('analysis')">分析</a>
    </div>
    <div class="macau-content">
      <iframe
        ref="iframeRef"
        :src="iframeSrc"
        class="macau-iframe"
        frameborder="0"
        sandbox="allow-scripts allow-same-origin allow-popups"
        @load="onIframeLoad"
      ></iframe>
      <div class="iframe-loading" v-if="iframeLoading">
        <span v-if="!loadTimeout">加载中...</span>
        <div v-else class="timeout-tip">
          <p>页面加载超时</p>
          <p class="tip-detail">澳门彩票网站启用了WAF防护，iframe嵌入可能被拦截</p>
          <button class="open-origin-btn" @click="openOrigin">点击在新窗口打开原站</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const activePage = ref('odds')
const iframeLoading = ref(true)
const iframeRef = ref(null)
const loadTimeout = ref(false)
let timeoutTimer = null

const PAGE_MAP = {
  odds: '/macau-proxy/sc/soccer/odds_in.html',
  schedule: '/macau-proxy/sc/soccer/schedule.html',
  result: '/macau-proxy/sc/soccer/result.html',
  analysis: '/macau-proxy/sc/soccer/analysis.html',
}

const ORIGIN_MAP = {
  odds: 'https://www.macauslot.com/sc/soccer/odds_in.html',
  schedule: 'https://www.macauslot.com/sc/soccer/schedule.html',
  result: 'https://www.macauslot.com/sc/soccer/result.html',
  analysis: 'https://www.macauslot.com/sc/soccer/analysis.html',
}

const iframeSrc = computed(() => PAGE_MAP[activePage.value] || PAGE_MAP.odds)
const originUrl = computed(() => ORIGIN_MAP[activePage.value] || ORIGIN_MAP.odds)

function switchPage(page) {
  if (activePage.value === page) return
  activePage.value = page
  iframeLoading.value = true
  loadTimeout.value = false
  startTimeout()
}

function onIframeLoad() {
  iframeLoading.value = false
  loadTimeout.value = false
  if (timeoutTimer) {
    clearTimeout(timeoutTimer)
    timeoutTimer = null
  }
}

function startTimeout() {
  if (timeoutTimer) clearTimeout(timeoutTimer)
  timeoutTimer = setTimeout(() => {
    if (iframeLoading.value) {
      loadTimeout.value = true
    }
  }, 8000)
}

function openOrigin() {
  window.open(originUrl.value, '_blank')
}

onMounted(() => {
  iframeLoading.value = true
  startTimeout()
})

onUnmounted(() => {
  if (timeoutTimer) clearTimeout(timeoutTimer)
})
</script>

<style scoped>
.macau-odds-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #fff;
}

.macau-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #1a5c2e, #2d8f4e);
  color: #fff;
  flex-shrink: 0;
}

.macau-title {
  font-size: 14px;
  font-weight: bold;
  letter-spacing: 1px;
}

.macau-source {
  font-size: 11px;
  opacity: 0.8;
  flex: 1;
}

.macau-nav {
  display: flex;
  background: #f5f5f5;
  border-bottom: 2px solid #1a5c2e;
  flex-shrink: 0;
}

.macau-nav a {
  display: block;
  padding: 8px 16px;
  font-size: 12px;
  color: #333;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.2s;
  text-decoration: none;
}

.macau-nav a:hover {
  color: #1a5c2e;
  background: #f0faf3;
}

.macau-nav a.active {
  color: #1a5c2e;
  font-weight: bold;
  border-bottom-color: #1a5c2e;
  background: #fff;
}

.macau-content {
  flex: 1;
  position: relative;
  min-height: 0;
}

.macau-iframe {
  width: 100%;
  height: 100%;
  border: none;
  display: block;
}

.iframe-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
  color: #999;
  font-size: 14px;
}

.timeout-tip {
  text-align: center;
}

.timeout-tip p {
  margin-bottom: 10px;
  color: #666;
}

.timeout-tip .tip-detail {
  font-size: 11px;
  color: #999;
  margin-bottom: 15px;
}

.open-origin-btn {
  padding: 6px 16px;
  font-size: 12px;
  color: #fff;
  background: linear-gradient(135deg, #1a5c2e, #2d8f4e);
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.open-origin-btn:hover {
  opacity: 0.9;
}
</style>
