<template>
  <div class="token-stats">
    <div class="page-header"><h3>Token 使用统计</h3></div>
    <el-row :gutter="15" style="margin-bottom:20px">
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="总配额" :value="stats.totalQuota" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="已使用" :value="stats.totalUsed" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="使用率" :value="stats.usageRate" suffix="%" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="活跃用户" :value="stats.activeUsers" /></el-card></el-col>
    </el-row>
    <el-card>
      <el-table :data="tokenRecords" stripe size="small" v-loading="loading">
        <el-table-column prop="username" label="用户" width="120" />
        <el-table-column prop="token_quota" label="配额" width="100" />
        <el-table-column prop="token_used" label="已用" width="100" />
        <el-table-column prop="usage_rate" label="使用率" width="100">
          <template #default="{ row }">{{ row.token_quota > 0 ? Math.round(row.token_used / row.token_quota * 100) : 0 }}%</template>
        </el-table-column>
        <el-table-column prop="last_used_at" label="最后使用" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const tokenRecords = ref([])
const stats = reactive({ totalQuota: 0, totalUsed: 0, usageRate: 0, activeUsers: 0 })

async function fetchStats() {
  loading.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/token-stats', { headers: { Authorization: `Bearer ${token}` } })
    const data = await resp.json()
    tokenRecords.value = data.records || []
    stats.totalQuota = data.total_quota || 0
    stats.totalUsed = data.total_used || 0
    stats.usageRate = stats.totalQuota > 0 ? Math.round(stats.totalUsed / stats.totalQuota * 100) : 0
    stats.activeUsers = data.active_users || 0
  } catch { ElMessage.error('获取统计失败') }
  finally { loading.value = false }
}

onMounted(fetchStats)
</script>

<style scoped>
.page-header h3 { margin:0 0 15px;font-size:18px; }
</style>
