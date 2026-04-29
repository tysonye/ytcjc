<template>
  <div class="member-manage">
    <div class="page-header">
      <h3>会员管理</h3>
      <div class="header-actions">
        <el-input v-model="searchText" placeholder="搜索用户名/邮箱" clearable size="small" style="width:200px" />
        <el-select v-model="filterLevel" placeholder="会员等级" clearable size="small" style="width:130px">
          <el-option label="免费" value="free" />
          <el-option label="白银" value="silver" />
          <el-option label="黄金" value="gold" />
          <el-option label="钻石" value="diamond" />
        </el-select>
      </div>
    </div>

    <el-table :data="filteredUsers" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="username" label="用户名" width="120" />
      <el-table-column prop="email" label="邮箱" width="160" />
      <el-table-column prop="phone" label="手机" width="120" />
      <el-table-column prop="membership_level" label="等级" width="80">
        <template #default="{ row }">
          <el-tag :type="levelType(row.membership_level)" size="small">{{ levelLabel(row.membership_level) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="membership_expires_at" label="到期时间" width="110">
        <template #default="{ row }">{{ row.membership_expires_at ? formatDate(row.membership_expires_at) : '-' }}</template>
      </el-table-column>
      <el-table-column prop="token_quota" label="Token配额" width="90" />
      <el-table-column prop="token_used" label="已用Token" width="90" />
      <el-table-column prop="is_active" label="状态" width="70">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">{{ row.is_active ? '正常' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="warning" @click="openLevelDialog(row)">调整等级</el-button>
          <el-button size="small" :type="row.is_active ? 'danger' : 'success'" @click="toggleActive(row)">
            {{ row.is_active ? '禁用' : '启用' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="编辑会员" width="450px">
      <el-form :model="editForm" label-width="80px" size="small">
        <el-form-item label="用户名"><el-input v-model="editForm.username" disabled /></el-form-item>
        <el-form-item label="邮箱"><el-input v-model="editForm.email" /></el-form-item>
        <el-form-item label="手机"><el-input v-model="editForm.phone" /></el-form-item>
        <el-form-item label="Token配额"><el-input-number v-model="editForm.token_quota" :min="0" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="levelVisible" title="调整会员等级" width="400px">
      <el-form :model="levelForm" label-width="80px" size="small">
        <el-form-item label="会员等级">
          <el-select v-model="levelForm.level">
            <el-option label="免费" value="free" />
            <el-option label="白银" value="silver" />
            <el-option label="黄金" value="gold" />
            <el-option label="钻石" value="diamond" />
          </el-select>
        </el-form-item>
        <el-form-item label="有效期">
          <el-select v-model="levelForm.duration">
            <el-option label="1个月" :value="30" />
            <el-option label="3个月" :value="90" />
            <el-option label="6个月" :value="180" />
            <el-option label="1年" :value="365" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="levelVisible = false">取消</el-button>
        <el-button type="primary" @click="saveLevel">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const users = ref([])
const searchText = ref('')
const filterLevel = ref('')
const editVisible = ref(false)
const levelVisible = ref(false)
const editForm = ref({})
const levelForm = ref({ user_id: null, level: 'free', duration: 30 })

const filteredUsers = computed(() => {
  return users.value.filter(u => {
    if (searchText.value) {
      const s = searchText.value.toLowerCase()
      if (!u.username?.toLowerCase().includes(s) && !u.email?.toLowerCase().includes(s)) return false
    }
    if (filterLevel.value && u.membership_level !== filterLevel.value) return false
    return true
  })
})

function levelType(l) { return { free: 'info', silver: '', gold: 'warning', diamond: 'danger' }[l] || 'info' }
function levelLabel(l) { return { free: '免费', silver: '白银', gold: '黄金', diamond: '钻石' }[l] || l }
function formatDate(d) { try { return new Date(d).toLocaleDateString('zh-CN') } catch { return d } }

async function fetchUsers() {
  loading.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/users', { headers: { Authorization: `Bearer ${token}` } })
    const data = await resp.json()
    users.value = data.items || data
  } catch (e) {
    ElMessage.error('获取会员列表失败')
  } finally {
    loading.value = false
  }
}

function openEdit(row) {
  editForm.value = { ...row }
  editVisible.value = true
}

async function saveEdit() {
  try {
    const token = localStorage.getItem('adminToken')
    await fetch(`/api/admin/users/${editForm.value.id}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm.value),
    })
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchUsers()
  } catch (e) { ElMessage.error('保存失败') }
}

function openLevelDialog(row) {
  levelForm.value = { user_id: row.id, level: row.membership_level, duration: 30 }
  levelVisible.value = true
}

async function saveLevel() {
  try {
    const token = localStorage.getItem('adminToken')
    await fetch(`/api/admin/users/${levelForm.value.user_id}/level`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ membership_level: levelForm.value.level, duration_days: levelForm.value.duration }),
    })
    ElMessage.success('等级调整成功')
    levelVisible.value = false
    fetchUsers()
  } catch (e) { ElMessage.error('调整失败') }
}

async function toggleActive(row) {
  try {
    const token = localStorage.getItem('adminToken')
    await fetch(`/api/admin/users/${row.id}/toggle-active`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` },
    })
    ElMessage.success('操作成功')
    fetchUsers()
  } catch (e) { ElMessage.error('操作失败') }
}

onMounted(fetchUsers)
</script>

<style scoped>
.page-header { display:flex;align-items:center;justify-content:space-between;margin-bottom:15px; }
.page-header h3 { margin:0;font-size:18px; }
.header-actions { display:flex;gap:8px; }
</style>
