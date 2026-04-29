<template>
  <div style="padding: 20px; font-family: monospace;">
    <h2>🔍 代理配置诊断</h2>
    
    <div style="margin: 20px 0; padding: 10px; background: #f0f0f0;">
      <strong>当前配置：</strong><br>
      WORKERS_URL: <code>{{ WORKERS_URL }}</code><br>
      是否可用：{{ WORKERS_URL ? '✅ 是' : '❌ 否' }}
    </div>

    <div style="margin: 20px 0;">
      <button @click="testProxy" :disabled="testing" style="padding: 10px 20px; margin-right: 10px;">
        {{ testing ? '测试中...' : '测试代理' }}
      </button>
      <button @click="clearLogs" style="padding: 10px 20px;">
        清空日志
      </button>
    </div>

    <div v-if="logs.length > 0" style="margin-top: 20px;">
      <h3>测试日志：</h3>
      <div v-for="(log, index) in logs" :key="index" 
           :style="{padding: '8px', margin: '5px 0', background: log.success ? '#d4edda' : '#f8d7da', color: log.success ? '#155724' : '#721c24'}">
        {{ log.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 从 MatchDetail.vue 复制配置
const WORKERS_URL = 'https://jc.xibai.xin'

const testing = ref(false)
const logs = ref([])

function addLog(message, success = true) {
  logs.value.push({ message, success, timestamp: new Date().toLocaleTimeString() })
}

function getProxyUrl(url) {
  if (url.includes('jc.titan007.com')) return url.replace('https://jc.titan007.com', '/titan-proxy/jc')
  if (url.includes('zq.titan007.com')) return url.replace('https://zq.titan007.com', '/titan-proxy/zq')
  if (url.includes('vip.titan007.com')) return url.replace('https://vip.titan007.com', '/titan-proxy/vip')
  if (url.includes('odds.500.com')) return url.replace('https://odds.500.com', '/500-proxy')
  if (url.includes('macauslot.com')) return url.replace('https://www.macauslot.com', '/macau-proxy')
  return null
}

async function testProxy() {
  testing.value = true
  logs.value = []
  
  const testUrls = [
    { name: '竞彩足球首页', url: 'https://jc.titan007.com/index.aspx' },
    { name: '足球数据首页', url: 'https://zq.titan007.com/index.aspx' },
    { name: 'VIP 数据首页', url: 'https://vip.titan007.com/' }
  ]
  
  for (const test of testUrls) {
    addLog(`📤 测试：${test.name}`)
    addLog(`   原始 URL: ${test.url}`)
    
    const proxyPath = getProxyUrl(test.url)
    addLog(`   代理路径：${proxyPath}`)
    
    if (!proxyPath) {
      addLog(`   ❌ 未找到代理路径`, false)
      continue
    }
    
    const fullUrl = WORKERS_URL + proxyPath
    addLog(`   完整 URL: ${fullUrl}`)
    
    try {
      const start = Date.now()
      const resp = await fetch(fullUrl, {
        mode: 'cors',
        credentials: 'omit',
        signal: AbortSignal.timeout(30000)
      })
      const duration = Date.now() - start
      
      addLog(`   状态码：${resp.status}`)
      
      if (resp.status === 200) {
        const text = await resp.text()
        addLog(`   ✅ 成功 - ${text.length} bytes (${duration}ms)`, true)
      } else if (resp.status === 522) {
        addLog(`   ❌ 522 错误 - 目标网站屏蔽了 Vercel IP`, false)
      } else {
        addLog(`   ❌ 异常状态码`, false)
      }
    } catch (e) {
      addLog(`   ❌ 请求失败：${e.message}`, false)
    }
    
    addLog('') // 空行分隔
  }
  
  testing.value = false
}

function clearLogs() {
  logs.value = []
}

// 自动测试
testProxy()
</script>

<style scoped>
code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
}
</style>
