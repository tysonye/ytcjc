<template>
  <div class="role-manage">
    <div class="page-header">
      <h3>角色权限管理</h3>
    </div>
    <el-table :data="roles" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="角色名称" width="120" />
      <el-table-column prop="level" label="会员等级" width="100">
        <template #default="{ row }">
          <el-tag :type="levelType(row.level)" size="small">{{ levelLabel(row.level) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" />
      <el-table-column label="可访问板块" min-width="200">
        <template #default="{ row }">
          <el-tag v-for="s in row.sections" :key="s" size="small" style="margin:2px">{{ s }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" title="编辑角色权限" width="500px">
      <el-form :model="editForm" label-width="80px" size="small">
        <el-form-item label="角色名称"><el-input v-model="editForm.name" /></el-form-item>
        <el-form-item label="描述"><el-input v-model="editForm.description" type="textarea" :rows="2" /></el-form-item>
        <el-form-item label="可访问板块">
          <el-checkbox-group v-model="editForm.sections">
            <el-checkbox label="球探数据" value="titan" />
            <el-checkbox label="500数据" value="five" />
            <el-checkbox label="澳门数据" value="macau" />
            <el-checkbox label="即时指数" value="odds_trend" />
            <el-checkbox label="竞足数据" value="jc_index" />
            <el-checkbox label="盘口详情" value="detail" />
            <el-checkbox label="AI分析" value="ai_chat" />
            <el-checkbox label="历史数据" value="history" />
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRole">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const roles = ref([])
const editVisible = ref(false)
const editForm = ref({})

function levelType(l) { return { free: 'info', silver: '', gold: 'warning', diamond: 'danger' }[l] || 'info' }
function levelLabel(l) { return { free: '免费', silver: '白银', gold: '黄金', diamond: '钻石' }[l] || l }

async function fetchRoles() {
  loading.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/roles', { headers: { Authorization: `Bearer ${token}` } })
    roles.value = await resp.json()
  } catch { ElMessage.error('获取角色列表失败') }
  finally { loading.value = false }
}

function openEdit(row) {
  editForm.value = { ...row, sections: row.sections || [] }
  editVisible.value = true
}

async function saveRole() {
  try {
    const token = localStorage.getItem('adminToken')
    await fetch(`/api/admin/roles/${editForm.value.id}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm.value),
    })
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchRoles()
  } catch { ElMessage.error('保存失败') }
}

onMounted(fetchRoles)
</script>

<style scoped>
.page-header h3 { margin:0 0 15px;font-size:18px; }
</style>
