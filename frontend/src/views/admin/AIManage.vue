<template>
  <div class="ai-manage">
    <div class="page-header">
      <h3>系统配置管理</h3>
      <span class="page-desc">统一管理AI服务配置和系统密钥，所有会员通过后端统一API通信</span>
    </div>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="AI服务配置" name="global">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">AI服务全局配置</span>
            <span class="card-desc">所有会员共用此配置，通过后端统一转发，后端自动记录每用户Token用量</span>
          </template>
          <el-form :model="globalForm" label-width="110px" size="small">
            <el-form-item label="Base URL">
              <el-input
                v-model="globalForm.base_url"
                placeholder="https://api.openai.com/v1"
              />
              <div class="form-hint">AI API的基础地址，例如 OpenAI: https://api.openai.com/v1</div>
            </el-form-item>
            <el-form-item label="API Key">
              <el-input
                v-model="globalForm.api_key"
                type="password"
                show-password
                placeholder="sk-..."
              />
              <div class="form-hint">API访问密钥，请妥善保管</div>
            </el-form-item>
            <el-form-item label="模型名称">
              <el-input
                v-model="globalForm.model_name"
                placeholder="gpt-4o-mini"
              />
              <div class="form-hint">默认使用的AI模型名称，如 gpt-4o, gpt-4o-mini, claude-3 等</div>
            </el-form-item>
            <el-form-item label="系统提示词">
              <el-input
                v-model="globalForm.system_prompt"
                type="textarea"
                :rows="4"
                placeholder="自定义AI助手的系统提示词..."
              />
              <div class="form-hint">可自定义AI分析师的系统角色和回复风格</div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingGlobal" @click="saveGlobal">
                保存AI配置
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="系统密钥" name="security">
        <el-card shadow="never">
          <template #header>
            <span class="card-title">系统安全配置</span>
            <span class="card-desc warning-desc">修改后所有用户需重新登录</span>
          </template>
          <el-form :model="securityForm" label-width="110px" size="small">
            <el-form-item label="SECRET_KEY">
              <el-input
                v-model="securityForm.secret_key"
                type="password"
                show-password
                placeholder="JWT令牌加密密钥"
              />
              <div class="form-hint">
                用于JWT令牌签名的密钥。修改后所有已登录用户的Token将失效，需要重新登录。
                <br/>留空表示使用环境变量中的默认值，建议设置为一段随机复杂字符串。
              </div>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="savingSecurity" @click="saveSecurity">
                保存密钥配置
              </el-button>
              <el-button @click="generateSecretKey">随机生成</el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="Token用量统计" name="tokens">
        <el-card shadow="never">
          <template #header>
            <div class="user-header">
              <span class="card-title">用户Token用量</span>
              <el-input
                v-model="userSearch"
                placeholder="搜索用户名"
                clearable
                size="small"
                style="width:200px"
              />
            </div>
          </template>
          <el-table :data="filteredTokenStats" stripe size="small" v-loading="loadingTokens">
            <el-table-column prop="username" label="用户名" width="140" />
            <el-table-column prop="membership_level" label="等级" width="80">
              <template #default="{ row }">
                <el-tag :type="levelType(row.membership_level)" size="small">
                  {{ levelLabel(row.membership_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_input_tokens" label="输入Token" width="110" />
            <el-table-column prop="total_output_tokens" label="输出Token" width="110" />
            <el-table-column prop="total_tokens" label="总Token" width="110" />
            <el-table-column prop="request_count" label="请求次数" width="90" />
            <el-table-column prop="token_quota" label="Token额度" width="100" />
            <el-table-column label="额度使用" width="120">
              <template #default="{ row }">
                <el-progress
                  :percentage="row.token_quota > 0 ? Math.min(Math.round(row.total_tokens / row.token_quota * 100), 100) : 0"
                  :stroke-width="6"
                  :status="row.token_quota > 0 && row.total_tokens / row.token_quota > 0.8 ? 'exception' : ''"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('global')

const globalForm = ref({
  base_url: '',
  api_key: '',
  model_name: '',
  system_prompt: '',
})
const savingGlobal = ref(false)

const securityForm = ref({
  secret_key: '',
})
const savingSecurity = ref(false)

const tokenStats = ref([])
const userSearch = ref('')
const loadingTokens = ref(false)

const filteredTokenStats = computed(() => {
  if (!userSearch.value) return tokenStats.value
  const s = userSearch.value.toLowerCase()
  return tokenStats.value.filter(u => u.username?.toLowerCase().includes(s))
})

function levelType(l) {
  return { free: 'info', silver: '', gold: 'warning', diamond: 'danger' }[l] || 'info'
}
function levelLabel(l) {
  return { free: '免费', silver: '白银', gold: '黄金', diamond: '钻石' }[l] || l
}

async function fetchGlobalConfig() {
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/ai-config', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await resp.json()
    globalForm.value = {
      base_url: data.base_url || '',
      api_key: data.api_key || '',
      model_name: data.model_name || '',
      system_prompt: data.system_prompt || '',
    }
    securityForm.value = {
      secret_key: data.secret_key || '',
    }
  } catch {
    ElMessage.error('获取配置失败')
  }
}

async function saveGlobal() {
  savingGlobal.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/ai-config', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(globalForm.value),
    })
    if (!resp.ok) throw new Error()
    ElMessage.success('AI配置已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingGlobal.value = false
  }
}

async function saveSecurity() {
  if (!securityForm.value.secret_key) {
    ElMessage.warning('SECRET_KEY不能为空')
    return
  }
  try {
    await ElMessageBox.confirm(
      '修改 SECRET_KEY 后，所有已登录用户的Token将立即失效，需要重新登录。确认修改？',
      '重要操作确认',
      { type: 'warning', confirmButtonText: '确认修改', cancelButtonText: '取消' }
    )
  } catch {
    return
  }
  savingSecurity.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/ai-config', {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ secret_key: securityForm.value.secret_key }),
    })
    if (!resp.ok) throw new Error()
    ElMessage.success('SECRET_KEY已更新，所有用户需重新登录')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingSecurity.value = false
  }
}

function generateSecretKey() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*'
  let key = ''
  for (let i = 0; i < 48; i++) {
    key += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  securityForm.value.secret_key = key
  ElMessage.success('已生成随机密钥，请点击保存')
}

async function fetchTokenStats() {
  loadingTokens.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/token-stats', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await resp.json()
    tokenStats.value = data.items || []
  } catch {
    ElMessage.error('获取Token统计失败')
  } finally {
    loadingTokens.value = false
  }
}

onMounted(() => {
  fetchGlobalConfig()
  fetchTokenStats()
})
</script>

<style scoped>
.page-header {
  margin-bottom: 15px;
}
.page-header h3 {
  margin: 0;
  font-size: 18px;
}
.page-desc {
  font-size: 12px;
  color: #999;
}
.card-title {
  font-size: 15px;
  font-weight: 600;
}
.card-desc {
  font-size: 12px;
  color: #999;
  margin-left: 10px;
}
.warning-desc {
  color: #e6a23c;
  font-weight: 600;
}
.form-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}
.user-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
