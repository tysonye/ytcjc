<template>
  <el-drawer v-model="visible" title="板块配置" direction="rtl" size="360px">
    <div class="preset-bar">
      <span class="preset-label">快捷布局:</span>
      <el-button-group size="small">
        <el-button @click="applyPreset('minimal')">精简</el-button>
        <el-button @click="applyPreset('standard')">标准</el-button>
        <el-button @click="applyPreset('professional')">专业</el-button>
        <el-button @click="applyPreset('analyst')">全量</el-button>
      </el-button-group>
    </div>

    <div class="config-group" v-for="source in sources" :key="source.key">
      <h4 class="source-title" @click="toggleSource(source.key)">
        <el-icon :class="{ rotated: expanded[source.key] }"><ArrowDown /></el-icon>
        {{ source.label }}
      </h4>
      <div v-show="expanded[source.key]">
        <div v-for="(sections, group) in getGroups(source.key)" :key="group" class="group-block">
          <div class="group-label">{{ group }}</div>
          <el-checkbox-group v-model="checked[source.key]" @change="onChange(source.key)">
            <el-checkbox v-for="s in sections" :key="s.key" :label="s.label" :value="s.key" size="small" />
          </el-checkbox-group>
        </div>
      </div>
    </div>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, defineExpose } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useSectionsStore } from '../stores/sections'

const sectionsStore = useSectionsStore()
const visible = ref(false)
const expanded = reactive({ titan: true, five: true, macau: true })

const sources = [
  { key: 'titan', label: '球探数据' },
  { key: 'five', label: '500数据' },
  { key: 'macau', label: '澳门数据' },
]

function toggleSource(key) { expanded[key] = !expanded[key] }

function getGroups(sourceKey) { return sectionsStore.getGroups(sourceKey) }

const checked = reactive({
  titan: sectionsStore.titan.filter(s => s.visible).map(s => s.key),
  five: sectionsStore.five.filter(s => s.visible).map(s => s.key),
  macau: sectionsStore.macau.filter(s => s.visible).map(s => s.key),
})

function onChange(sourceKey) {
  const allKeys = sectionsStore[sourceKey].map(s => s.key)
  allKeys.forEach(k => {
    sectionsStore.setSectionVisible(sourceKey, k, checked[sourceKey].includes(k))
  })
}

function applyPreset(preset) {
  sectionsStore.applyPreset(preset)
  checked.titan = sectionsStore.titan.filter(s => s.visible).map(s => s.key)
}

defineExpose({ open: () => { visible.value = true }, close: () => { visible.value = false } })
</script>

<style scoped>
.preset-bar { display:flex; align-items:center; gap:8px; margin-bottom:15px; padding-bottom:12px; border-bottom:1px solid #eee; }
.preset-label { font-size:13px; color:#666; white-space:nowrap; }
.config-group { margin-bottom:15px; }
.source-title { cursor:pointer; font-size:15px; color:#303133; margin-bottom:8px; display:flex; align-items:center; gap:6px;
  .el-icon { transition:transform 0.2s; } .rotated { transform:rotate(180deg); }
}
.group-block { margin-bottom:10px; margin-left:12px; }
.group-label { font-size:12px; color:#999; margin-bottom:4px; font-weight:bold; }
.el-checkbox-group { display:flex; flex-direction:column; gap:4px; }
</style>
