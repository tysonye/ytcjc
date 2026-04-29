<template>
  <div class="test-page">
    <div class="test-container">
      <h1>🧪 Vercel 代理测试工具</h1>
      <p class="subtitle">测试域名：<code>{{ CUSTOM_DOMAIN }}</code></p>

      <div class="status-card" :class="statusClass">
        {{ statusText }}
      </div>

      <div class="test-cards">
        <div class="test-card" v-for="(test, index) in tests" :key="index">
          <div class="test-header">
            <span class="test-title">{{ test.title }}</span>
            <span class="test-icon">{{ test.status === 'pending' ? '⏳' : test.status === 'success' ? '✅' : '❌' }}</span>
          </div>
          <div class="test-url">{{ test.url }}</div>
          <div v-if="test.result" class="test-result" :class="test.status">
            {{ test.result }}
          </div>
        </div>
      </div>

      <button @click="runTests" :disabled="isTesting" class="test-btn">
        {{ isTesting ? '测试中...' : '🔄 重新测试' }}
      </button>

      <div class="instructions">
        <h3>✅ 测试通过后：</h3>
        <ol>
          <li>选择一场比赛</li>
          <li>查看比赛数据、赔率、积分排名等是否正常加载</li>
          <li>如果数据加载正常，说明代理配置成功！</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const CUSTOM_DOMAIN = 'https://jc.xibai.xin'

const isTesting = ref(false)
const tests = ref([
  {
    title: '测试 1：根路径',
    url: `${CUSTOM_DOMAIN}/`,
    status: 'pending',
    result: null
  },
  {
    title: '测试 2：竞彩足球代理',
    url: `${CUSTOM_DOMAIN}/titan-proxy/jc/`,
    status: 'pending',
    result: null
  },
  {
    title: '测试 3：足球数据代理',
    url: `${CUSTOM_DOMAIN}/titan-proxy/zq/`,
    status: 'pending',
    result: null
  }
])

const statusText = computed(() => {
  const pending = tests.value.filter(t => t.status === 'pending').length
  const success = tests.value.filter(t => t.status === 'success').length
  const error = tests.value.filter(t => t.status === 'error').length

  if (isTesting.value) return '⏳ 正在测试...'
  if (error > 0) return '⚠️ 部分测试失败'
  if (success === tests.value.length) return '✅ 所有测试通过！'
  return '准备测试'
})

const statusClass = computed(() => {
  if (isTesting.value) return 'status-loading'
  const error = tests.value.filter(t => t.status === 'error').length
  return error > 0 ? 'status-error' : 'status-success'
})

async function testEndpoint(url, expectJson = false) {
  try {
    const start = Date.now()
    const resp = await fetch(url, {
      mode: 'cors',
      credentials: 'omit',
      signal: AbortSignal.timeout(15000)
    })
    const duration = Date.now() - start
    
    if (resp.status !== 200) {
      return { success: false, message: `状态码：${resp.status}` }
    }
    
    if (expectJson) {
      const data = await resp.json()
      if (data.status === 'ok') {
        return { success: true, message: `正常 - ${data.message} (${duration}ms)` }
      } else {
        return { success: false, message: `响应异常：${JSON.stringify(data)}` }
      }
    } else {
      const text = await resp.text()
      if (text.length > 0) {
        return { success: true, message: `正常 - ${text.length} bytes (${duration}ms)` }
      } else {
        return { success: false, message: `响应为空` }
      }
    }
  } catch (e) {
    return { success: false, message: `失败：${e.message}` }
  }
}

async function runTests() {
  isTesting.value = true
  
  // Reset tests
  tests.value.forEach(t => {
    t.status = 'pending'
    t.result = null
  })

  // Test 1: Root (expects JSON)
  const result1 = await testEndpoint(`${CUSTOM_DOMAIN}/`, true)
  tests.value[0].status = result1.success ? 'success' : 'error'
  tests.value[0].result = result1.message

  // Test 2: JC Proxy (expects HTML)
  const result2 = await testEndpoint(`${CUSTOM_DOMAIN}/titan-proxy/jc/`, false)
  tests.value[1].status = result2.success ? 'success' : 'error'
  tests.value[1].result = result2.message

  // Test 3: ZQ Proxy (expects HTML)
  const result3 = await testEndpoint(`${CUSTOM_DOMAIN}/titan-proxy/zq/`, false)
  tests.value[2].status = result3.success ? 'success' : 'error'
  tests.value[2].result = result3.message

  isTesting.value = false
}

// Auto-run on mount
runTests()
</script>

<style scoped>
.test-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.test-container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: white;
  text-align: center;
  margin-bottom: 10px;
  font-size: 32px;
}

.subtitle {
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 30px;
  font-size: 16px;
}

.subtitle code {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 12px;
  border-radius: 4px;
  font-family: monospace;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.status-loading {
  background: #fff3cd;
  color: #856404;
}

.status-success {
  background: #d4edda;
  color: #155724;
}

.status-error {
  background: #f8d7da;
  color: #721c24;
}

.test-cards {
  display: grid;
  gap: 20px;
  margin-bottom: 30px;
}

.test-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.test-title {
  font-weight: bold;
  color: #333;
  font-size: 16px;
}

.test-icon {
  font-size: 24px;
}

.test-url {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 14px;
  color: #495057;
  word-break: break-all;
  margin-bottom: 10px;
}

.test-result {
  padding: 10px;
  border-radius: 6px;
  font-family: monospace;
  font-size: 14px;
}

.test-result.success {
  background: #d4edda;
  color: #155724;
}

.test-result.error {
  background: #f8d7da;
  color: #721c24;
}

.test-btn {
  width: 100%;
  background: white;
  color: #667eea;
  border: none;
  padding: 16px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  margin-bottom: 30px;
}

.test-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

.test-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.instructions {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.instructions h3 {
  color: #667eea;
  margin-top: 0;
  margin-bottom: 15px;
}

.instructions ol {
  color: #333;
  line-height: 2;
  padding-left: 25px;
}
</style>
