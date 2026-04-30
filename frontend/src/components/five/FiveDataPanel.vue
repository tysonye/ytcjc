<template>
  <div class="five-data" v-loading="loading">
    <template v-if="mapError">
      <el-empty description="未找到对应500数据" :image-size="80" />
    </template>
    <template v-else-if="parsedData">
      <div v-for="section in visibleSections" :key="section.key" class="section-block">
        <h3 class="section-title">{{ section.label }}</h3>
        <div class="section-content">
          <component :is="getComponent(section.key)" v-bind="getProps(section.key)" />
        </div>
      </div>
    </template>
    <el-empty v-else-if="!loading" description="暂无500数据" :image-size="80" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject, markRaw, onUnmounted } from 'vue'
import { useSectionsStore } from '../../stores/sections'
import { findFiveMatchId, refresher, REFRESH_INTERVAL } from '../../utils/fiveMatchMapper'
import { parseShujuPage, parseOuzhiPage, parseYazhiPage, parseDaxiaoPage } from '../../utils/fiveDataParser'
import FiveBasicInfo from './FiveBasicInfo.vue'
import FiveRecentForm from './FiveRecentForm.vue'
import FiveH2HRecord from './FiveH2HRecord.vue'
import FiveRecommendation from './FiveRecommendation.vue'
import FiveEuropeanOdds from './FiveEuropeanOdds.vue'
import FiveAsianOdds from './FiveAsianOdds.vue'
import FiveOverUnderOdds from './FiveOverUnderOdds.vue'
import FiveKellyIndex from './FiveKellyIndex.vue'

const props = defineProps({ matchUniqueId: { type: [String, Number], default: '' } })
const selectedMatchInfo = inject('selectedMatchInfo', ref(null))
const sectionsStore = useSectionsStore()
const loading = ref(false)
const parsedData = ref(null)
const mapError = ref(false)

const visibleSections = computed(() => sectionsStore.getVisibleSections('five'))

const FIVE_COMPONENTS = {
  basic_info: { comp: markRaw(FiveBasicInfo), propKey: 'basicInfo' },
  recent_form: { comp: markRaw(FiveRecentForm), propKey: 'recentForm' },
  h2h_record: { comp: markRaw(FiveH2HRecord), propKey: 'h2hRecord' },
  recommendation: { comp: markRaw(FiveRecommendation), propKey: 'recommendation' },
  european_odds: { comp: markRaw(FiveEuropeanOdds), propKey: 'europeanOdds' },
  asian_odds: { comp: markRaw(FiveAsianOdds), propKey: 'asianOdds' },
  overunder_odds: { comp: markRaw(FiveOverUnderOdds), propKey: 'overunderOdds' },
  kelly_index: { comp: markRaw(FiveKellyIndex), propKey: 'kellyIndex' },
}

function getComponent(key) {
  return FIVE_COMPONENTS[key]?.comp || null
}

function getProps(key) {
  const cfg = FIVE_COMPONENTS[key]
  if (!cfg || !parsedData.value) return {}
  return { data: parsedData.value[cfg.propKey] }
}

async function fetchWithGbk(url) {
  try {
    const resp = await fetch(url)
    if (!resp.ok) return null
    const buffer = await resp.arrayBuffer()
    const uint8 = new Uint8Array(buffer)
    const headBytes = uint8.slice(0, Math.min(4096, uint8.length))
    let headText = ''
    for (let i = 0; i < headBytes.length; i++) {
      const b = headBytes[i]
      headText += (b >= 32 && b < 127) ? String.fromCharCode(b) : ' '
    }
    const isGbk = /charset\s*=\s*["']?gb/i.test(headText)
    if (isGbk) {
      try {
        return new TextDecoder('gbk').decode(buffer)
      } catch (e) {}
    }
    try {
      return new TextDecoder('utf-8', { fatal: true }).decode(buffer)
    } catch {
      try {
        return new TextDecoder('gbk').decode(buffer)
      } catch {
        return new TextDecoder('utf-8').decode(buffer)
      }
    }
  } catch {
    return null
  }
}

async function fetchFiveData(fiveMatchId) {
  const [shujuHtml, ouzhiHtml, yazhiHtml, daxiaoHtml] = await Promise.allSettled([
    fetchWithGbk(`/500-proxy/fenxi/shuju-${fiveMatchId}.shtml`),
    fetchWithGbk(`/500-proxy/fenxi/ouzhi-${fiveMatchId}.shtml`),
    fetchWithGbk(`/500-proxy/fenxi/yazhi-${fiveMatchId}.shtml`),
    fetchWithGbk(`/500-proxy/fenxi/daxiao-${fiveMatchId}.shtml`),
  ])

  const shujuResult = shujuHtml.status === 'fulfilled' ? shujuHtml.value : null
  const ouzhiResult = ouzhiHtml.status === 'fulfilled' ? ouzhiHtml.value : null
  const yazhiResult = yazhiHtml.status === 'fulfilled' ? yazhiHtml.value : null
  const daxiaoResult = daxiaoHtml.status === 'fulfilled' ? daxiaoHtml.value : null

  const shujuData = parseShujuPage(shujuResult)
  const ouzhiData = parseOuzhiPage(ouzhiResult)
  const yazhiData = parseYazhiPage(yazhiResult)
  const daxiaoData = parseDaxiaoPage(daxiaoResult)

  const hasAnyData = shujuData || (ouzhiData && (ouzhiData.europeanOdds?.length > 0 || ouzhiData.basicInfo)) || (yazhiData && yazhiData.asianOdds?.length > 0) || (daxiaoData && daxiaoData.overunderOdds?.length > 0)
  if (!hasAnyData) {
    return null
  }

  const fallbackBasic = ouzhiData?.basicInfo || shujuData?.basicInfo || { homeTeam: '', awayTeam: '', league: '', matchTime: '', weather: '', venue: '' }
  const shujuBasic = shujuData?.basicInfo
  if (shujuBasic && shujuBasic.homeTeam) {
    fallbackBasic.homeTeam = fallbackBasic.homeTeam || shujuBasic.homeTeam
    fallbackBasic.awayTeam = fallbackBasic.awayTeam || shujuBasic.awayTeam
    fallbackBasic.league = fallbackBasic.league || shujuBasic.league
    fallbackBasic.matchTime = fallbackBasic.matchTime || shujuBasic.matchTime
  }

  return {
    basicInfo: fallbackBasic,
    recentForm: shujuData?.recentForm || { home: { formSeq: '', panSeq: '' }, away: { formSeq: '', panSeq: '' } },
    h2hRecord: shujuData?.h2hRecord || { summary: '', homeWins: 0, draws: 0, awayWins: 0, matches: [] },
    recommendation: shujuData?.recommendation || { result: '', analysis: '' },
    europeanOdds: ouzhiData?.europeanOdds || [],
    asianOdds: yazhiData?.asianOdds || [],
    overunderOdds: daxiaoData?.overunderOdds || [],
    kellyIndex: ouzhiData?.kellyIndex || [],
  }
}

async function fetchData() {
  if (!props.matchUniqueId) return
  loading.value = true
  mapError.value = false
  parsedData.value = null

  try {
    const matchInfo = selectedMatchInfo.value
    console.log('[FiveDataPanel] fetchData called, matchUniqueId:', props.matchUniqueId)
    console.log('[FiveDataPanel] matchInfo:', matchInfo ? {
      match_id: matchInfo.match_id,
      schedule_id: matchInfo.schedule_id,
      home_team: matchInfo.home_team,
      away_team: matchInfo.away_team,
      start_time: matchInfo.start_time,
    } : null)

    let fiveMatchId = null

    // 优先使用 findFiveMatchId（内部已包含match_id+球队名称验证逻辑）
    console.log('[FiveDataPanel] calling findFiveMatchId')
    fiveMatchId = await findFiveMatchId(matchInfo || { schedule_id: props.matchUniqueId })
    console.log('[FiveDataPanel] findFiveMatchId result:', fiveMatchId)

    if (!fiveMatchId) {
      console.log('[FiveDataPanel] no fiveMatchId found, showing error')
      mapError.value = true
      return
    }

    const data = await fetchFiveData(fiveMatchId)
    if (!data) {
      console.log('[FiveDataPanel] fetchFiveData returned null')
      mapError.value = true
      return
    }

    parsedData.value = data

    // 启动500数据页面的后台刷新
    startFiveDataRefresh(fiveMatchId)
  } catch (e) {
    console.error('获取500数据失败:', e)
  } finally {
    loading.value = false
  }
}

function startFiveDataRefresh(fiveMatchId) {
  refresher.stop(`five_data_${props.matchUniqueId}`)
  refresher.start(
    `five_data_${props.matchUniqueId}`,
    async () => {
      return await fetchFiveData(fiveMatchId)
    },
    { get: () => null, set: () => {} }, // 使用空缓存，直接更新UI
    REFRESH_INTERVAL.fiveData,
    (freshData) => {
      if (freshData) {
        parsedData.value = freshData
      }
    }
  )
}

function isSameMatch(info, matchId) {
  if (!info || !matchId) return false
  return String(info.schedule_id) === String(matchId) || String(info.match_unique_id) === String(matchId)
}

onMounted(() => {
  if (isSameMatch(selectedMatchInfo.value, props.matchUniqueId)) {
    fetchData()
  }
})

onUnmounted(() => {
  // 组件卸载时停止后台刷新
  refresher.stop(`five_data_${props.matchUniqueId}`)
})

watch(() => props.matchUniqueId, (newId, oldId) => {
  if (!newId) return
  // 切换比赛时停止旧比赛的后台刷新
  if (oldId) {
    refresher.stop(`five_data_${oldId}`)
  }
  if (isSameMatch(selectedMatchInfo.value, newId)) {
    fetchData()
  }
})
watch(selectedMatchInfo, (newInfo) => {
  if (isSameMatch(newInfo, props.matchUniqueId)) {
    fetchData()
  }
})
</script>

<style scoped>
.section-block { margin-bottom:15px; border:1px solid #eee; border-radius:6px; overflow:hidden; }
.section-title { background:#f5f7fa; padding:8px 12px; font-size:13px; margin:0; }
.section-content { padding:12px; }
</style>
