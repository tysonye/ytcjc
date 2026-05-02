<template>
  <div class="membership-permission-manage">
    <div class="page-header">
      <h3>会员等级权限管理</h3>
      <span class="page-desc">配置不同会员等级可访问的功能板块和数据权限</span>
    </div>

    <el-table :data="levels" stripe size="small" v-loading="loading">
      <el-table-column prop="label" label="会员等级" width="100">
        <template #default="{ row }">
          <el-tag :type="levelType(row.level)" size="small">{{ row.label }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="可访问板块" min-width="280">
        <template #default="{ row }">
          <el-tag
            v-for="s in row.sections"
            :key="s"
            size="small"
            effect="plain"
            style="margin: 2px"
          >{{ sectionLabel(s) }}</el-tag>
          <span v-if="!row.sections.length" style="color:#999;font-size:12px;">暂无权限</span>
        </template>
      </el-table-column>
      <el-table-column prop="token_amount" label="Token额度" width="100" />
      <el-table-column label="操作" width="100">
        <template #default="{ row }">
          <el-button size="small" type="primary" @click="openEdit(row)">编辑权限</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="editVisible" :title="'编辑 ' + editForm.label + ' 权限'" width="520px">
      <el-form :model="editForm" label-width="0" size="small">
        <el-form-item>
          <div class="section-check-header">选择该等级可访问的功能板块：</div>
          <el-checkbox-group v-model="editForm.sections">
            <div class="section-grid">
              <el-checkbox
                v-for="opt in availableSections"
                :key="opt.key"
                :label="opt.key"
                :value="opt.key"
              >{{ opt.label }}</el-checkbox>
            </div>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="Token额度">
          <el-input-number v-model="editForm.token_amount" :min="0" :step="100" />
          <span class="form-hint">该等级用户注册时默认分配的Token数量</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const saving = ref(false)
const levels = ref([])
const availableSections = ref([])
const editVisible = ref(false)
const editForm = ref({})

function levelType(l) {
  return { free: 'info', silver: '', gold: 'warning', diamond: 'danger' }[l] || 'info'
}

function sectionLabel(key) {
  const found = availableSections.value.find(s => s.key === key)
  return found ? found.label : key
}

async function fetchPermissions() {
  loading.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/membership-levels', {
      headers: { Authorization: `Bearer ${token}` },
    })
    const data = await resp.json()
    levels.value = data.levels || []
    availableSections.value = data.available_sections || []
  } catch {
    ElMessage.error('获取权限配置失败')
  } finally {
    loading.value = false
  }
}

function openEdit(row) {
  editForm.value = {
    ...row,
    sections: [...(row.sections || [])],
  }
  editVisible.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch(`/api/admin/membership-permissions/${editForm.value.plan_id}`, {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sections: editForm.value.sections,
        token_amount: editForm.value.token_amount,
      }),
    })
    if (!resp.ok) throw new Error()
    ElMessage.success('保存成功')
    editVisible.value = false
    fetchPermissions()
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(fetchPermissions)
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
.form-hint {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}
</style>
