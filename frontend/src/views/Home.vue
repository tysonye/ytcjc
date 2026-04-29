<template>
  <div class="home-page">
    <div class="left-panel">
      <div class="panel-header">
        <span class="panel-title">比赛列表</span>
        <div class="header-controls">
          <el-select v-model="selectedDate" size="small" class="date-select" @change="onDateChange" :teleported="true">
            <el-option v-for="d in dateOptions" :key="d.value" :label="d.label" :value="d.value" />
          </el-select>
          <span class="panel-count" v-if="filteredCount > 0">{{ filteredCount }} 场</span>
        </div>
      </div>
      <MatchList :selectedId="selectedMatchId" :matchDate="selectedDate" @select="onMatchSelect" @count-change="v => filteredCount = v" />
    </div>
    <div class="right-panel" v-if="selectedMatchId">
      <div class="match-info-section">
        <div class="match-teams" v-if="matchInfo">
          <div class="team home">
            <img v-if="analysisData?.home_logo" :src="analysisData.home_logo" class="team-logo" @error="onLogoError" />
            <span class="team-name">{{ matchInfo.home_team }}</span>
          </div>
          <div class="match-score">
            <span class="score">{{ matchInfo.home_score || 0 }} - {{ matchInfo.away_score || 0 }}</span>
            <span class="half-score" v-if="matchInfo.home_half_score">({{ matchInfo.home_half_score }}-{{ matchInfo.away_half_score }})</span>
            <span class="status">{{ statusText(matchInfo.status) }}</span>
          </div>
          <div class="team away">
            <img v-if="analysisData?.away_logo" :src="analysisData.away_logo" class="team-logo" @error="onLogoError" />
            <span class="team-name">{{ matchInfo.away_team }}</span>
          </div>
        </div>
        <div class="match-meta" v-if="matchInfo">
          <span v-if="analysisData?.league_round">{{ analysisData.league_round }}</span>
          <span>{{ formatMatchTime(matchInfo.start_time) }}</span>
        </div>
        <div class="match-extra" v-if="analysisData && (analysisData.venue || analysisData.weather)">
          <span v-if="analysisData.venue">场地：{{ analysisData.venue }}</span>
          <span v-if="analysisData.weather">天气：{{ analysisData.weather }}</span>
          <span v-if="analysisData.temperature">温度：{{ analysisData.temperature }}</span>
        </div>
      </div>
      <div class="detail-toolbar">
        <div class="toolbar-tabs">
          <span class="toolbar-tab" :class="{ active: activeTab === 'titan' }" @click="activeTab = 'titan'">球探数据</span>
          <span class="toolbar-tab" :class="{ active: activeTab === 'five' }" @click="activeTab = 'five'">500数据</span>
        </div>
        <el-button size="small" @click="sectionConfigRef?.open()">
          <el-icon><Setting /></el-icon> 板块配置
        </el-button>
      </div>
      <div class="tab-content">
        <MatchDetail :key="selectedMatchId" />
      </div>
    </div>
    <div class="right-panel empty" v-else>
      <el-empty description="请从左侧选择一场比赛查看详情" :image-size="120" />
    </div>
    <SectionConfig ref="sectionConfigRef" />
    <AIChat :match-id="selectedMatchId" />
  </div>
</template>

<script setup>
import { ref, provide, computed } from 'vue'
import { Setting } from '@element-plus/icons-vue'
import MatchList from '../components/MatchList.vue'
import MatchDetail from '../views/MatchDetail.vue'
import SectionConfig from '../components/SectionConfig.vue'
import AIChat from '../components/AIChat.vue'

const selectedMatchId = ref(null)
const selectedMatchInfo = ref(null)
const matchInfo = ref(null)
const sectionConfigRef = ref(null)
const filteredCount = ref(0)
const activeTab = ref('titan')
const analysisData = ref(null)

function formatDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const today = new Date()
const selectedDate = ref(formatDate(today))

const dateOptions = computed(() => {
  const options = []
  for (let i = 0; i >= -6; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() + i)
    options.push({ value: formatDate(d), label: formatDate(d) })
  }
  return options
})

provide('selectedMatchInfo', selectedMatchInfo)
provide('activeTab', activeTab)
provide('analysisData', analysisData)

function onDateChange() {
  selectedMatchId.value = null
  selectedMatchInfo.value = null
  matchInfo.value = null
  analysisData.value = null
}

function onMatchSelect(matchData) {
  if (typeof matchData === 'object' && matchData.schedule_id) {
    selectedMatchId.value = matchData.schedule_id
    selectedMatchInfo.value = matchData
    matchInfo.value = matchData
  } else {
    selectedMatchId.value = matchData
    selectedMatchInfo.value = null
    matchInfo.value = null
  }
}

function statusText(s) {
  return { '0': '未开始', '1': '上半场', '2': '中场', '3': '下半场', '4': '加时', '5': '点球', '-1': '结束' }[String(s)] || ''
}

function formatMatchTime(t) {
  if (!t) return ''
  try {
    const parts = String(t).split(',')
    if (parts.length >= 5) return `${parts[3]}:${parts[4]}`
    const d = new Date(t)
    if (isNaN(d.getTime())) return ''
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } catch { return '' }
}

function onLogoError(e) {
  const img = e.target
  const src = img.src
  if (src.includes('/titan-proxy/zq/')) {
    img.src = src.replace('/titan-proxy/zq/', 'https://zq.titan007.com/')
  } else {
    img.style.display = 'none'
  }
}
</script>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.home-page {
  display: flex;
  gap: 0;
  height: calc(100vh - 50px);
}

.left-panel {
  width: 300px;
  flex-shrink: 0;
  overflow: hidden;
  height: 100%;
  background: $text-white;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;

  @include mobile {
    width: 100%;
    height: auto;
    border-right: none;
  }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  flex-shrink: 0;
}

.panel-title {
  font-size: 15px;
  font-weight: bold;
  letter-spacing: 1px;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-select {
  width: 150px;
  :deep(.el-input__wrapper) {
    background: rgba(255,255,255,0.15);
    box-shadow: none;
    border: 1px solid rgba(255,255,255,0.3);
  }
  :deep(.el-input__inner) {
    color: #fff;
    font-size: 12px;
  }
  :deep(.el-input__suffix) {
    color: rgba(255,255,255,0.7);
  }
}

.panel-count {
  font-size: 12px;
  background: rgba(255,255,255,0.2);
  padding: 2px 8px;
  border-radius: 10px;
}

.right-panel {
  flex: 1;
  overflow: hidden;
  height: 100%;
  display: flex;
  flex-direction: column;

  @include mobile {
    display: none;
  }

  &.empty {
    display: flex;
    align-items: center;
    justify-content: center;
    background: $text-white;

    @include mobile {
      display: none;
    }
  }
}

.match-info-section {
  background: $text-white;
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}
.match-teams { display:flex; align-items:center; justify-content:center; gap:30px; }
.team { flex:1; text-align:center; display:flex; align-items:center; justify-content:center; gap:8px; flex-direction:column; }
.team-name { font-size:16px; font-weight:bold; color:$text-primary; }
.team-logo { width:36px; height:36px; object-fit:contain; }
.match-score { text-align:center; .score{ display:block; font-size:24px; font-weight:bold; color:$danger-color; } .half-score{ display:block; font-size:12px; color:#8c8c8c; } .status{ display:block; font-size:12px; color:$text-secondary; } }
.match-meta { display:flex; justify-content:center; gap:12px; margin-top:8px; font-size:12px; color:$text-secondary; align-items:center; }
.match-extra { display:flex; justify-content:center; gap:12px; margin-top:6px; font-size:11px; color:#999; }

.detail-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
  background: $text-white;
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}
.toolbar-tabs { display: flex; align-items: stretch; height: 36px; }
.toolbar-tab {
  display: flex; align-items: center; padding: 0 16px; font-size: 13px; color: #666;
  cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s;
  &:hover { color: #1890ff; }
  &.active { color: #1890ff; font-weight: 600; border-bottom-color: #1890ff; }
}

.tab-content {
  flex: 1;
  overflow-y: auto;
}
</style>
