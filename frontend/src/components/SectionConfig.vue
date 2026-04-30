<template>
  <el-drawer v-model="visible" title="板块配置" direction="rtl" size="360px">
    <div class="preset-bar">
      <span class="preset-label">选择板块</span>
      <el-button-group size="small">
        <el-button :type="activeSource === 'titan' ? 'primary' : ''" @click="activeSource = 'titan'">球探数据</el-button>
        <el-button :type="activeSource === 'five' ? 'primary' : ''" @click="activeSource = 'five'">500数据</el-button>
        <el-button :type="activeSource === 'aipredict' ? 'primary' : ''" @click="activeSource = 'aipredict'">AI设置</el-button>
      </el-button-group>
    </div>

    <AISettings v-if="activeSource === 'aipredict'" />

    <template v-else>
      <div class="config-group" v-for="source in filteredSources" :key="source.key">
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
    </template>
  </el-drawer>
</template>

<script setup>
import { ref, reactive, computed, defineExpose, watch } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { useSectionsStore } from '../stores/sections'
import AISettings from './AISettings.vue'

const sectionsStore = useSectionsStore()
const visible = ref(false)
const activeSource = ref('titan')
const expanded = reactive({ titan: true, five: true, macau: true })

const sources = [
  { key: 'titan', label: '球探数据' },
  { key: 'five', label: '500数据' },
]

const filteredSources = computed(() => {
  return sources
})

function toggleSource(key) { expanded[key] = !expanded[key] }

function getGroups(sourceKey) { return sectionsStore.getGroups(sourceKey) }

const checked = reactive({
  titan: [],
  five: [],
  macau: [],
})

function syncCheckedFromStore() {
  checked.titan = sectionsStore.titan.filter(s => s.visible).map(s => s.key)
  checked.five = sectionsStore.five.filter(s => s.visible).map(s => s.key)
  checked.macau = sectionsStore.macau.filter(s => s.visible).map(s => s.key)
}

function onChange(sourceKey) {
  const allKeys = sectionsStore[sourceKey].map(s => s.key)
  allKeys.forEach(k => {
    sectionsStore.setSectionVisible(sourceKey, k, checked[sourceKey].includes(k))
  })
  sectionsStore.saveToServer()
}

async function openDrawer(tab) {
  if (tab) activeSource.value = tab
  if (!sectionsStore.loaded) {
    await sectionsStore.loadFromServer()
  }
  syncCheckedFromStore()
  visible.value = true
}

defineExpose({ open: openDrawer, close: () => { visible.value = false } })
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
