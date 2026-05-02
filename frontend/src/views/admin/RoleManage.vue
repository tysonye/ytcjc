<template>
  <div class="role-manage">
    <div class="page-header">
      <h3>角色权限管理</h3>
      <span class="page-desc">管理后台管理员角色及其可访问的板块权限</span>
    </div>

    <el-table :data="roles" stripe size="small" v-loading="loading">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="角色名称" width="120" />
      <el-table-column prop="description" label="描述" min-width="120" />
      <el-table-column label="可访问板块" min-width="200">
        <template #default="{ row }">
          <el-tag
            v-for="s in row.sections"
            :key="s"
            size="small"
            effect="plain"
            style="margin: 2px"
          >{{ sectionLabel(s) }}</el-tag>
          <span v-if="!row.sections || !row.sections.length" style="color:#999;font-size:12px;">暂无权限</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140">
        <template #default="{ row }">
          <el-button size="small" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteRole(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div style="margin-top:15px;">
      <el-button size="small" type="primary" @click="openCreate">新建角色</el-button>
    </div>

    <el-dialog v-model="editVisible" :title="editForm.id ? '编辑角色权限' : '新建角色'" width="520px">
      <el-form :model="editForm" label-width="80px" size="small">
        <el-form-item label="角色名称">
          <el-input v-model="editForm.name" placeholder="输入角色名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" placeholder="角色描述" />
        </el-form-item>
        <el-form-item label="可访问板块">
          <div class="section-check-header">选择该角色可访问的功能板块：</div>
          <el-checkbox-group v-model="editForm.sections">
            <div class="section-grid">
              <el-checkbox
                v-for="opt in sectionOptions"
                :key="opt.key"
                :label="opt.key"
                :value="opt.key"
              >{{ opt.label }}</el-checkbox>
            </div>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveRole" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const roles = ref([])
const editVisible = ref(false)
const editForm = ref({})

const sectionOptions = [
  { key: 'titan', label: '球探数据' },
  { key: 'five', label: '500数据' },
  { key: 'macau', label: '澳门数据' },
  { key: 'odds_trend', label: '即时指数' },
  { key: 'jc_index', label: '竞足数据' },
  { key: 'detail', label: '盘口详情' },
  { key: 'ai_chat', label: 'AI分析' },
  { key: 'history', label: '历史数据' },
]

function sectionLabel(key) {
  const found = sectionOptions.find(s => s.key === key)
  return found ? found.label : key
}

async function fetchRoles() {
  loading.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/roles', { headers: { Authorization: `Bearer ${token}` } })
    roles.value = await resp.json()
  } catch {
    ElMessage.error('获取角色列表失败')
  } finally {
    loading.value = false
  }
}

function openEdit(row) {
  editForm.value = {
    id: row.id,
    name: row.name,
    description: row.description || '',
    sections: [...(row.sections || [])],
  }
  editVisible.value = true
}

function openCreate() {
  editForm.value = {
    id: null,
    name: '',
    description: '',
    sections: [],
  }
  editVisible.value = true
}

async function saveRole() {
  if (!editForm.value.name) {
    ElMessage.warning('请输入角色名称')
    return
  }
  saving.value = true
  try {
    const token = localStorage.getItem('adminToken')
    if (editForm.value.id) {
      const resp = await fetch(`/api/admin/roles/${editForm.value.id}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm.value),
      })
      if (!resp.ok) throw new Error()
    } else {
      const resp = await fetch('/api/admin/roles', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(editForm.value),
      })
      if (!resp.ok) throw new Error()
    }
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchRoles()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function deleteRole(row) {
  try {
    await ElMessageBox.confirm(`确认删除角色"${row.name}"？`, '确认操作', { type: 'warning' })
  } catch {
    return
  }
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch(`/api/admin/roles/${row.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!resp.ok) throw new Error()
    ElMessage.success('删除成功')
    fetchRoles()
  } catch {
    ElMessage.error('删除失败')
  }
}

onMounted(fetchRoles)
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
.section-check-header {
  font-size: 13px;
  color: #606266;
  margin-bottom: 10px;
}
.section-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px 12px;
}
</style>
