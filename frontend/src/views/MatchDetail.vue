<template>
  <div class="match-detail" v-loading="loading">
    <div v-show="activeTab === 'titan'" class="section-list">
      <div v-for="section in visibleTitanSections" :key="section.key" class="section-block">
        <h3 class="section-title">
          {{ section.label }}
          <span v-if="section.key === 'odds_trend'" class="title-actions">
            <button class="config-btn" @click="openCompanyDialog">数源配置</button>
          </span>
        </h3>
        <div class="section-content">
          <component :is="getTitanComponent(section.key)" v-bind="getTitanProps(section.key)" />
        </div>
      </div>
    </div>
    <div v-show="activeTab === 'five'">
      <FiveDataPanel :match-unique-id="matchUniqueId" />
    </div>
    <div v-if="showCompanyDialog" class="dialog-overlay" @click.self="showCompanyDialog = false">
      <div class="dialog-box">
        <div class="dialog-header">
          <span>数源配置</span>
          <button class="dialog-close" @click="showCompanyDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <label class="check-all">
            <input type="checkbox" :checked="allCompaniesSelected" @change="toggleAllCompanies" />
            <span>全选/取消</span>
          </label>
          <div class="company-list">
            <label v-for="c in allCompanyNames" :key="c" class="company-item">
              <input type="checkbox" v-model="tempSelectedCompanies" :value="c" />
              <span>{{ c }}</span>
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="dialog-btn" @click="confirmCompanySelection">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, inject, markRaw } from 'vue'
import { useSectionsStore } from '../stores/sections'
import { ElMessage } from 'element-plus'
import TitanMatchInfo from '../components/titan/TitanMatchInfo.vue'
import TitanStandings from '../components/titan/TitanStandings.vue'
import TitanOddsTrend from '../components/titan/TitanOddsTrend.vue'
import TitanJcIndex from '../components/titan/TitanJcIndex.vue'
import TitanH2H from '../components/titan/TitanH2H.vue'
import TitanRecentForm from '../components/titan/TitanRecentForm.vue'
import TitanHalfFull from '../components/titan/TitanHalfFull.vue'
import TitanGoalStats from '../components/titan/TitanGoalStats.vue'
import TitanDataCompare from '../components/titan/TitanDataCompare.vue'
import TitanLineup from '../components/titan/TitanLineup.vue'
import TitanHandicapTrend from '../components/titan/TitanHandicapTrend.vue'
import TitanSameHandicap from '../components/titan/TitanSameHandicap.vue'
import TitanGoalHalfDist from '../components/titan/TitanGoalHalfDist.vue'
import TitanOddEven from '../components/titan/TitanOddEven.vue'
import TitanGoalTiming from '../components/titan/TitanGoalTiming.vue'
import TitanSeasonStats from '../components/titan/TitanSeasonStats.vue'
import TitanBriefing from '../components/titan/TitanBriefing.vue'
import TitanUpcoming from '../components/titan/TitanUpcoming.vue'
import FiveDataPanel from '../components/five/FiveDataPanel.vue'

const selectedMatchInfo = inject('selectedMatchInfo', ref(null))
const sharedAnalysisData = inject('analysisData', ref(null))
const sectionsStore = useSectionsStore()
const loading = ref(false)
const matchInfo = ref(null)
const analysisData = ref(null)
const oddsTrendData = ref([])
const jcOddsData = ref({})
const activeTab = inject('activeTab', ref('titan'))
const showCompanyDialog = ref(false)
const tempSelectedCompanies = ref([])
const confirmedCompanies = ref([])

const allCompanyNames = computed(() => oddsTrendData.value.map(r => r.company))

const allCompaniesSelected = computed(() => {
  if (allCompanyNames.value.length === 0) return false
  return tempSelectedCompanies.value.length === allCompanyNames.value.length
})

function toggleAllCompanies() {
  if (allCompaniesSelected.value) {
    tempSelectedCompanies.value = []
  } else {
    tempSelectedCompanies.value = [...allCompanyNames.value]
  }
}

function openCompanyDialog() {
  tempSelectedCompanies.value = [...confirmedCompanies.value]
  showCompanyDialog.value = true
}

function confirmCompanySelection() {
  confirmedCompanies.value = [...tempSelectedCompanies.value]
  showCompanyDialog.value = false
}

const filteredOddsTrendData = computed(() => {
  if (confirmedCompanies.value.length === 0) return oddsTrendData.value
  return oddsTrendData.value.filter(r => confirmedCompanies.value.includes(r.company))
})

const DEFAULT_COMPANIES = ['澳*', '威*', '36*']

watch(allCompanyNames, (names) => {
  const defaults = names.filter(n => DEFAULT_COMPANIES.includes(n))
  confirmedCompanies.value = defaults.length > 0 ? defaults : [...names]
}, { immediate: true })

const matchUniqueId = computed(() => matchInfo.value?.match_unique_id || '')

const TITAN_COMPONENTS = {
  jc_index: { comp: markRaw(TitanJcIndex), props: ['data', 'euCompanies'] },
  standings: { comp: markRaw(TitanStandings), props: ['data'] },
  data_compare: { comp: markRaw(TitanDataCompare), props: ['data'] },
  lineup: { comp: markRaw(TitanLineup), props: ['data'] },
  h2h: { comp: markRaw(TitanH2H), props: ['records'] },
  recent_form: { comp: markRaw(TitanRecentForm), props: ['homeRecords', 'awayRecords'] },
  handicap_trend: { comp: markRaw(TitanHandicapTrend), props: ['data'] },
  same_handicap: { comp: markRaw(TitanSameHandicap), props: ['data'] },
  goal_half_dist: { comp: markRaw(TitanGoalHalfDist), props: ['data'] },
  half_full: { comp: markRaw(TitanHalfFull), props: ['homeData', 'awayData'] },
  odd_even: { comp: markRaw(TitanOddEven), props: ['data'] },
  goal_timing: { comp: markRaw(TitanGoalTiming), props: ['data'] },
  goal_stats: { comp: markRaw(TitanGoalStats), props: ['homeData', 'awayData'] },
  season_stats: { comp: markRaw(TitanSeasonStats), props: ['data'] },
  briefing: { comp: markRaw(TitanBriefing), props: ['text'] },
  upcoming: { comp: markRaw(TitanUpcoming), props: ['data'] },
  odds_trend: { comp: markRaw(TitanOddsTrend), props: ['trendData'] },
}

const visibleTitanSections = computed(() => sectionsStore.getVisibleSections('titan'))

function getTitanComponent(key) { return TITAN_COMPONENTS[key]?.comp || null }

function getTitanProps(key) {
  const cfg = TITAN_COMPONENTS[key]
  if (!cfg) return {}
  const result = {}
  for (const p of cfg.props) {
    switch (p) {
      case 'data': result.data = analysisData.value; break
      case 'trendData': result.trendData = filteredOddsTrendData.value; break
      case 'records': result.records = analysisData.value?.h2h_records || []; break
      case 'homeRecords': result.homeRecords = analysisData.value?.home_recent || []; break
      case 'awayRecords': result.awayRecords = analysisData.value?.away_recent || []; break
      case 'homeData': result.homeData = analysisData.value?.half_full_stats?.home || []; break
      case 'awayData': result.awayData = analysisData.value?.half_full_stats?.away || []; break
      case 'euCompanies': result.euCompanies = analysisData.value?.european_odds || []; break
      case 'text': result.text = analysisData.value?.briefing || ''; break
    }
  }
  return result
}

function statusText(s) {
  return { '0': '未开始', '1': '上半场', '-1': '中场', '2': '下半场', '-2': '完场' }[String(s)] || ''
}

function formatTime(t) {
  if (!t) return ''
  try {
    const d = new Date(t)
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`
  } catch { return t }
}

async function proxyFetch(url) {
  const proxyUrl = getProxyUrl(url)
  if (proxyUrl) {
    try {
      const resp = await fetch(proxyUrl)
      const buffer = await resp.arrayBuffer()
      const bytes = new Uint8Array(buffer)
      const ct = (resp.headers.get('content-type') || '').toLowerCase()
      let encoding = 'utf-8'
      if (ct.includes('charset=gb') || ct.includes('charset=gb2312') || ct.includes('charset=gbk') || ct.includes('charset=gb18030')) {
        encoding = 'gbk'
      } else if (bytes.length >= 3 && bytes[0] === 0xEF && bytes[1] === 0xBB && bytes[2] === 0xBF) {
        encoding = 'utf-8'
      } else {
        const utf8Test = new TextDecoder('utf-8', { fatal: true }).decode(buffer)
        encoding = 'utf-8'
        void utf8Test
      }
      const text = new TextDecoder(encoding).decode(buffer)
      if (text && text.length > 0) return { body: text }
    } catch (e) {
      try {
        const resp2 = await fetch(proxyUrl)
        const buffer2 = await resp2.arrayBuffer()
        const text2 = new TextDecoder('gbk').decode(buffer2)
        if (text2 && text2.length > 0) return { body: text2 }
      } catch {}
    }
  }
  try {
    const resp = await fetch('/api/proxy/fetch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' } }),
    })
    const data = await resp.json()
    return { body: data.body || '' }
  } catch (e) {
    console.error('proxyFetch failed:', e)
    return { body: '' }
  }
}

function getProxyUrl(url) {
  if (url.includes('jc.titan007.com')) {
    return url.replace('https://jc.titan007.com', '/titan-proxy/jc')
  }
  if (url.includes('zq.titan007.com')) {
    return url.replace('https://zq.titan007.com', '/titan-proxy/zq')
  }
  if (url.includes('vip.titan007.com')) {
    return url.replace('https://vip.titan007.com', '/titan-proxy/vip')
  }
  if (url.includes('odds.500.com')) {
    return url.replace('https://odds.500.com', '/500-proxy')
  }
  if (url.includes('macauslot.com')) {
    return url.replace('https://www.macauslot.com', '/macau-proxy')
  }
  return null
}

async function fetchMatchDetail() {
  const info = selectedMatchInfo.value
  if (info) matchInfo.value = info
  const uid = info?.match_unique_id
  if (!uid) return

  loading.value = true
  try {
    const [analysisResult, oddsResult, jcResult] = await Promise.allSettled([
      proxyFetch(`https://zq.titan007.com/analysis/${uid}cn.htm`),
      proxyFetch(`https://zq.titan007.com/analysis/odds/${uid}.htm`),
      proxyFetch(`https://zq.titan007.com/default/getAnalyData?sid=${uid}&t=1&r=${Date.now()}`),
    ])

    if (analysisResult.status === 'fulfilled' && analysisResult.value?.body) {
      analysisData.value = parseAnalysisPage(analysisResult.value.body)
      sharedAnalysisData.value = analysisData.value
    }
    if (oddsResult.status === 'fulfilled' && oddsResult.value?.body) {
      oddsTrendData.value = parseOddsTrend(oddsResult.value.body)
    }
    if (jcResult.status === 'fulfilled' && jcResult.value?.body) {
      try {
        const jcObj = JSON.parse(jcResult.value.body)
        jcOddsData.value = parseJcOdds(jcObj)
        if (analysisData.value) analysisData.value.jc_odds = jcOddsData.value
      } catch (e) { console.warn('解析竞彩指数失败:', e) }
    }
  } catch (e) {
    console.error('获取比赛详情失败:', e)
    ElMessage.error('获取比赛详情失败')
  } finally {
    loading.value = false
  }
}

function parseOddsTrend(html) {
  const results = []
  const valueMatch = html.match(/value='([^']+)'\s+id='iframeAOdds'/)
  if (!valueMatch) {
    console.warn('[parseOddsTrend] iframeAOdds not found, trying fallback regex')
    const fallback = html.match(/value='([^']+)'/)
    if (fallback) console.warn('[parseOddsTrend] fallback matched, first 200 chars:', fallback[1].substring(0, 200))
    return results
  }
  const raw = valueMatch[1]
  const entries = raw.split('^')
  for (const entry of entries) {
    if (!entry.trim()) continue
    const parts = entry.split(';')
    if (parts.length < 5) continue
    const initVals = parts[2].replace(/,$/, '').split(',')
    const currVals = parts[3].replace(/,$/, '').split(',')
    const liveVals = (parts[4] || '').replace(/,$/, '').split(',')
    if (initVals.length !== 14) {
      console.warn('[parseOddsTrend] Company', parts[1], 'init has', initVals.length, 'elements (expected 14):', initVals.join('|'))
    }
    const sg = (arr, i) => (i < arr.length && arr[i].trim()) ? arr[i].trim() : ''
    const hasLive = !!(sg(liveVals, 0) || sg(liveVals, 1) || sg(liveVals, 2) || sg(liveVals, 7) || sg(liveVals, 8) || sg(liveVals, 9) || sg(liveVals, 11) || sg(liveVals, 12) || sg(liveVals, 13))
    const liveEuChanged = hasLive && sg(currVals, 1) !== sg(liveVals, 1)
    results.push({
      company_id: parts[0], company: parts[1], has_live: hasLive, live_eu_changed: liveEuChanged,
      eu_init_home: sg(initVals, 0), eu_init_draw: sg(initVals, 1), eu_init_away: sg(initVals, 2),
      eua_init_home: sg(initVals, 3), eua_init_handicap: sg(initVals, 4), eua_init_away: sg(initVals, 5),
      real_init_home: sg(initVals, 7), real_init_handicap: sg(initVals, 8), real_init_away: sg(initVals, 9),
      goal_init_big: sg(initVals, 11), goal_init_line: sg(initVals, 12), goal_init_small: sg(initVals, 13),
      eu_curr_home: sg(currVals, 0), eu_curr_draw: sg(currVals, 1), eu_curr_away: sg(currVals, 2),
      eua_curr_home: sg(currVals, 3), eua_curr_handicap: sg(currVals, 4), eua_curr_away: sg(currVals, 5),
      real_curr_home: sg(currVals, 7), real_curr_handicap: sg(currVals, 8), real_curr_away: sg(currVals, 9),
      goal_curr_big: sg(currVals, 11), goal_curr_line: sg(currVals, 12), goal_curr_small: sg(currVals, 13),
      eu_live_home: sg(liveVals, 0), eu_live_draw: sg(liveVals, 1), eu_live_away: sg(liveVals, 2),
      eua_live_home: sg(liveVals, 3), eua_live_handicap: sg(liveVals, 4), eua_live_away: sg(liveVals, 5),
      real_live_home: sg(liveVals, 7), real_live_handicap: sg(liveVals, 8), real_live_away: sg(liveVals, 9),
      goal_live_big: sg(liveVals, 11), goal_live_line: sg(liveVals, 12), goal_live_small: sg(liveVals, 13),
    })
  }
  return results
}

function parseJcOdds(obj) {
  const jc = obj?.jcOdds || obj || {}
  const result = {}
  if (jc.wlOdds) {
    const f = jc.wlOdds.first || {}, l = jc.wlOdds.live || {}
    result.wlOdds = {
      first: { win: f.win, draw: f.draw, lose: f.lose },
      live: { win: l.win, draw: l.draw, lose: l.lose },
    }
  }
  if (jc.sfOdds) {
    const f = jc.sfOdds.first || {}, l = jc.sfOdds.live || {}
    result.sfOdds = {
      rf: jc.sfOdds.rf,
      first: { win: f.win, draw: f.draw, lose: f.lose },
      live: { win: l.win, draw: l.draw, lose: l.lose },
    }
  }
  if (jc.goalOdds) {
    const l = jc.goalOdds.live || jc.goalOdds.init || jc.goalOdds.first || {}
    result.goalOdds = {
      live: { g0: l.g0, g1: l.g1, g2: l.g2, g3: l.g3, g4: l.g4, g5: l.g5, g6: l.g6, g7: l.g7 },
    }
  }
  if (jc.scoreOdds) {
    const l = jc.scoreOdds.live || {}
    result.scoreOdds = {
      live: {
        score10: l.score10, score20: l.score20, score21: l.score21,
        score30: l.score30, score31: l.score31, score32: l.score32,
        score40: l.score40, score41: l.score41, score42: l.score42,
        score50: l.score50, score51: l.score51, score52: l.score52,
        scoreWin: l.scoreWin,
        score00: l.score00, score11: l.score11, score22: l.score22, score33: l.score33,
        scoreDraw: l.scoreDraw,
        score01: l.score01, score02: l.score02, score12: l.score12,
        score03: l.score03, score13: l.score13, score23: l.score23,
        score04: l.score04, score14: l.score14, score24: l.score24,
        score05: l.score05, score15: l.score15, score25: l.score25,
        scoreLose: l.scoreLose,
      },
    }
  }
  if (jc.hfOdds) {
    const l = jc.hfOdds.live || {}
    result.hfOdds = {
      live: {
        hfww: l.hfww, hfwd: l.hfwd, hfwl: l.hfwl,
        hfdw: l.hfdw, hfdd: l.hfdd, hfdl: l.hfdl,
        hflw: l.hflw, hfld: l.hfld, hfll: l.hfll,
      },
    }
  }

  const COMPANY_MAP = { 3: 'SBOBET', 31: '皇冠', 1: '澳门', 8: 'Bet365', 4: '易胜博', 12: '明陞', 14: '金宝博', 17: '12BET', 19: '利记', 23: '10BET', 24: '永利高', 35: '平博', 7: '沙巴' }
  function extractOdds(sbArr, kind) {
    if (!sbArr) return []
    return sbArr.filter(x => x.kind === kind).map(x => ({
      company: COMPANY_MAP[x.odds.companyId] || `公司${x.odds.companyId}`,
      companyId: x.odds.companyId,
      firstHome: x.odds.firstHomeOdds,
      firstLine: x.odds.firstDrawOdds,
      firstAway: x.odds.firstAwayOdds,
      home: x.odds.homeOdds,
      line: x.odds.drawOdds,
      away: x.odds.awayOdds,
    }))
  }

  const allSources = [
    obj?.sbOdds?.sbOdds || [],
    obj?.sbobetOdds?.sbOdds || [],
    obj?.bet365Odds?.sbOdds || [],
    obj?.vcbetOdds?.sbOdds || [],
  ]
  const allSb = allSources.flat()
  const seen = new Set()
  result.asianOdds = extractOdds(allSb, 'ASIAN').filter(x => { if (seen.has(x.companyId)) return false; seen.add(x.companyId); return true })
  result.ouOdds = extractOdds(allSb, 'OU').filter(x => { const k = 'ou_' + x.companyId; if (seen.has(k)) return false; seen.add(k); return true })
  result.euroOdds = extractOdds(allSb, 'EURO').filter(x => { const k = 'eu_' + x.companyId; if (seen.has(k)) return false; seen.add(k); return true })

  const allSourcesHalf = [
    obj?.sbOdds?.sbOddsHalf || [],
    obj?.sbobetOdds?.sbOddsHalf || [],
    obj?.bet365Odds?.sbOddsHalf || [],
    obj?.vcbetOdds?.sbOddsHalf || [],
  ]
  const allSbHalf = allSourcesHalf.flat()
  const seenHalf = new Set()
  result.asianOddsHalf = extractOdds(allSbHalf, 'ASIAN').filter(x => { if (seenHalf.has(x.companyId)) return false; seenHalf.add(x.companyId); return true })
  result.ouOddsHalf = extractOdds(allSbHalf, 'OU').filter(x => { const k = 'ou_' + x.companyId; if (seenHalf.has(k)) return false; seenHalf.add(k); return true })
  result.euroOddsHalf = extractOdds(allSbHalf, 'EURO').filter(x => { const k = 'eu_' + x.companyId; if (seenHalf.has(k)) return false; seenHalf.add(k); return true })

  result.companyOdds = []
  const companyIds = [...new Set(result.asianOdds.map(x => x.companyId))]
  for (const cid of companyIds) {
    const asian = result.asianOdds.find(x => x.companyId === cid)
    const ou = result.ouOdds.find(x => x.companyId === cid)
    const euro = result.euroOdds.find(x => x.companyId === cid)
    if (asian || ou || euro) {
      result.companyOdds.push({
        company: asian?.company || ou?.company || euro?.company || `公司${cid}`,
        companyId: cid,
        asian: asian || null,
        ou: ou || null,
        euro: euro || null,
      })
    }
  }

  return result
}

function parseAnalysisPage(html) {
  if (!html) return {}
  const data = {
    league_round: '', venue: '', weather: '', temperature: '',
    home_logo: '', away_logo: '',
    instant_eu_odds: {},
    standings_data: null,
    h2h_records: [], home_recent: [], away_recent: [],
    half_full_stats: { home: [], away: [] },
    goal_stats: { home: null, away: null },
    data_compare: null,
    lineup_data: [],
    handicap_trend: [],
    same_handicap: [],
    goal_half_dist: [],
    odd_even: [],
    goal_timing: [],
    season_stats: null,
    briefing: '',
    upcoming: [],
    european_odds: [], asian_odds: [], goal_odds: [],
  }

  let m
  m = html.match(/class=['"]place['"][^>]*>(.*?)<\/a>/i)
  if (m) data.venue = m[1].replace(/^.*?[：:]/, '').trim()
  m = html.match(/(?:天氣|天气)[：:]\s*([\u4e00-\u9fa5]+)/)
  if (m) data.weather = m[1]
  m = html.match(/(?:溫度|温度)[：:]\s*([\d～℃\u2103\-~]+[℃\u2103]?)/)
  if (m) data.temperature = m[1]
  m = html.match(/class=['"]LName['"][^>]*>(.*?)<\/a>/i)
  if (m) data.league_round = m[1].trim()

  const imgMatches = [...html.matchAll(/<img[^>]*src="([^"]*image\/team[^"]*)"[^>]*alt="([^"]*)"/g)]
  if (imgMatches.length >= 2) {
    const toProxyUrl = (u) => {
      const full = (u.startsWith('//') ? 'https:' : '') + u
      return full.replace('https://zq.titan007.com', '/titan-proxy/zq')
    }
    data.home_logo = toProxyUrl(imgMatches[0][1])
    data.away_logo = toProxyUrl(imgMatches[1][1])
  }

  try {
    m = html.match(/var\s+Vs_eOdds\s*=\s*(\[.+?\]);/s)
    if (m) {
      const eOdds = JSON.parse(m[1].replace(/'/g, '"'))
      for (const cid of [3, 1, 8, 12, 4, 18, 115, 281, 80]) {
        const item = eOdds.find(i => i.length >= 8 && i[1] === cid)
        if (item) {
          data.instant_eu_odds = { company: String(cid), init_home: item[2], init_draw: item[3], init_away: item[4], curr_home: item[5], curr_draw: item[6], curr_away: item[7] }
          break
        }
      }
    }
  } catch (e) { console.warn('Vs_eOdds:', e) }

  try {
    const standings = { total: [], home: [], away: [] }
    m = html.match(/var\s+totalScoreStr\s*=\s*(\[\[.*?\]\]);/s)
    if (m) JSON.parse(m[1].replace(/'/g, '"')).forEach(item => { if (item.length >= 5) standings.total.push({ rank: String(item[1]), team: String(item[3]), points: String(item[4]) }) })
    m = html.match(/var\s+homeScoreStr\s*=\s*(\[\[.*?\]\]);/s)
    if (m) JSON.parse(m[1].replace(/'/g, '"')).forEach(item => { if (item.length >= 4) standings.home.push({ rank: String(item[0]), team: String(item[2]), points: String(item[3]) }) })
    m = html.match(/var\s+guestScoreStr\s*=\s*(\[\[.*?\]\]);/s)
    if (m) JSON.parse(m[1].replace(/'/g, '"')).forEach(item => { if (item.length >= 4) standings.away.push({ rank: String(item[0]), team: String(item[2]), points: String(item[3]) }) })
    if (standings.total.length || standings.home.length || standings.away.length) {
      data.standings_data = { ...standings, home_team: { name: '' }, away_team: { name: '' } }
    }
  } catch (e) { console.warn('积分榜:', e) }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const allTables = doc.querySelectorAll('table')

    allTables.forEach(table => {
      const text = table.textContent
      const rows = table.querySelectorAll('tr')
      if (rows.length < 2) return

      if (text.includes('對賽往績') || text.includes('对赛往绩')) {
        rows.forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 7) data.h2h_records.push({
            date: cs[0]?.textContent?.trim(), league: cs[1]?.textContent?.trim(),
            home_team: cs[2]?.textContent?.trim(), score: cs[3]?.textContent?.trim(),
            away_team: cs[4]?.textContent?.trim(), handicap: cs[5]?.textContent?.trim(),
            result: cs[6]?.textContent?.trim(),
            corner: cs[7]?.textContent?.trim() || '', eu_home: cs[8]?.textContent?.trim() || '',
            eu_draw: cs[9]?.textContent?.trim() || '', eu_away: cs[10]?.textContent?.trim() || '',
          })
        })
      }

      if (text.includes('近期戰績') || text.includes('近期战绩')) {
        let isHome = true
        rows.forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 7) {
            const r = {
              date: cs[0]?.textContent?.trim(), league: cs[1]?.textContent?.trim(),
              home_team: cs[2]?.textContent?.trim(), score: cs[3]?.textContent?.trim(),
              away_team: cs[4]?.textContent?.trim(), handicap: cs[5]?.textContent?.trim(),
              result: cs[6]?.textContent?.trim(),
              corner: cs[7]?.textContent?.trim() || '',
            }
            if (isHome) data.home_recent.push(r); else data.away_recent.push(r)
            if (data.home_recent.length > data.away_recent.length) isHome = false
          }
        })
      }

      if (text.includes('數據對比') || text.includes('数据对比')) {
        const teams = []
        rows.forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 10) {
            teams.push({
              name: cs[0]?.textContent?.trim(), win_pct: cs[1]?.textContent?.trim(),
              lose_pct: cs[2]?.textContent?.trim(), gf: cs[3]?.textContent?.trim(),
              ga: cs[4]?.textContent?.trim(), gd: cs[5]?.textContent?.trim(),
              avg_gf: cs[6]?.textContent?.trim(), avg_corner: cs[7]?.textContent?.trim(),
              avg_yellow: cs[8]?.textContent?.trim(),
            })
          }
        })
        if (teams.length) data.data_compare = { all: teams }
      }

      if (text.includes('陣容') || text.includes('球員')) {
        const currentTeams = []
        let currentTeam = null
        rows.forEach((row) => {
          const cs = row.querySelectorAll('td, th')
          const firstText = cs[0]?.textContent?.trim() || ''
          if (firstText && !/^\d+$/.test(firstText) && cs.length <= 3) {
            currentTeam = { name: firstText, players: [], avgRating: '', recentScores: [] }
            currentTeams.push(currentTeam)
          } else if (cs.length >= 5 && currentTeam) {
            currentTeam.players.push({
              number: cs[0]?.textContent?.trim(), name: cs[1]?.textContent?.trim(),
              position: cs[2]?.textContent?.trim(), starter: cs[3]?.textContent?.trim() === '*',
              rating: cs[4]?.textContent?.trim(),
            })
          }
        })
        if (currentTeams.length) data.lineup_data = currentTeams
      }

      if (text.includes('盤路走勢') || text.includes('盘路走势')) {
        const trendTeams = []
        let currentTeam = null
        rows.forEach((row) => {
          const cs = row.querySelectorAll('td, th')
          const firstText = cs[0]?.textContent?.trim() || ''
          if (['總', '主', '客', '近6場', '近6'].includes(firstText) && currentTeam) {
            currentTeam.fullRows.push({
              type: firstText, played: cs[1]?.textContent?.trim(), won: cs[2]?.textContent?.trim(),
              walk: cs[3]?.textContent?.trim(), lost: cs[4]?.textContent?.trim(),
              win_rate: cs[5]?.textContent?.trim(), big: cs[6]?.textContent?.trim(),
              big_rate: cs[7]?.textContent?.trim(), small: cs[8]?.textContent?.trim(),
              small_rate: cs[9]?.textContent?.trim(),
            })
          } else if (firstText && cs.length <= 2) {
            currentTeam = { name: firstText, fullRows: [], halfRows: [], recent6: [] }
            trendTeams.push(currentTeam)
          }
        })
        if (trendTeams.length) data.handicap_trend = trendTeams
      }

      if (text.includes('相同盤路') || text.includes('相同盘路')) {
        const sameTeams = []
        let currentTeam = null
        rows.forEach((row) => {
          const cs = row.querySelectorAll('td, th')
          const firstText = cs[0]?.textContent?.trim() || ''
          if (['總', '主', '客'].includes(firstText) && currentTeam) {
            currentTeam.rows.push({
              type: firstText, won: cs[1]?.textContent?.trim(), walk: cs[2]?.textContent?.trim(),
              lost: cs[3]?.textContent?.trim(), win_rate: cs[4]?.textContent?.trim(),
            })
          } else if (firstText && cs.length <= 2) {
            currentTeam = { name: firstText, handicap_label: '', rows: [], recent6: [] }
            sameTeams.push(currentTeam)
          }
        })
        if (sameTeams.length) data.same_handicap = sameTeams
      }

      if ((text.includes('入球數') || text.includes('进球数')) && text.includes('上半場')) {
        const distTeams = []
        let currentTeam = null
        rows.forEach((row) => {
          const cs = row.querySelectorAll('td, th')
          const firstText = cs[0]?.textContent?.trim() || ''
          if (['總', '主', '客'].includes(firstText) && currentTeam) {
            currentTeam.rows.push({
              type: firstText, g0: cs[1]?.textContent?.trim(), g1: cs[2]?.textContent?.trim(),
              g2: cs[3]?.textContent?.trim(), g3: cs[4]?.textContent?.trim(),
              g4plus: cs[5]?.textContent?.trim(), first_half: cs[6]?.textContent?.trim(),
              second_half: cs[7]?.textContent?.trim(),
            })
          } else if (firstText && cs.length <= 2) {
            currentTeam = { name: firstText, rows: [] }
            distTeams.push(currentTeam)
          }
        })
        if (distTeams.length) data.goal_half_dist = distTeams
      }

      if (text.includes('半全場') || text.includes('半全场')) {
        const stats = []
        rows.forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 9) stats.push({
            type: cs[0]?.textContent?.trim(), played: cs[1]?.textContent?.trim(),
            won: cs[2]?.textContent?.trim(), drawn: cs[3]?.textContent?.trim(),
            lost: cs[4]?.textContent?.trim(), gf: cs[5]?.textContent?.trim(),
            ga: cs[6]?.textContent?.trim(), gd: cs[7]?.textContent?.trim(),
            win_rate: cs[8]?.textContent?.trim(),
          })
        })
        if (stats.length >= 2) {
          data.half_full_stats.home = stats.slice(0, Math.ceil(stats.length / 2))
          data.half_full_stats.away = stats.slice(Math.ceil(stats.length / 2))
        }
      }

      if (text.includes('單雙') || text.includes('单双')) {
        const oeTeams = []
        let currentTeam = null
        rows.forEach((row) => {
          const cs = row.querySelectorAll('td, th')
          const firstText = cs[0]?.textContent?.trim() || ''
          if (['總', '主', '客'].includes(firstText) && currentTeam) {
            currentTeam.rows.push({
              type: firstText, big: cs[1]?.textContent?.trim(), big_pct: cs[2]?.textContent?.trim(),
              small: cs[3]?.textContent?.trim(), small_pct: cs[4]?.textContent?.trim(),
              walk: cs[5]?.textContent?.trim(), walk_pct: cs[6]?.textContent?.trim(),
              odd: cs[7]?.textContent?.trim(), odd_pct: cs[8]?.textContent?.trim(),
              even: cs[9]?.textContent?.trim(), even_pct: cs[10]?.textContent?.trim(),
            })
          } else if (firstText && cs.length <= 2) {
            currentTeam = { name: firstText, rows: [] }
            oeTeams.push(currentTeam)
          }
        })
        if (oeTeams.length) data.odd_even = oeTeams
      }

      if (text.includes('進球時間') || text.includes('进球时间')) {
        const timingTeams = []
        let currentTeam = null
        let isSection = 'main'
        rows.forEach((row) => {
          const cs = row.querySelectorAll('td, th')
          const firstText = cs[0]?.textContent?.trim() || ''
          if (['總', '主', '客'].includes(firstText) && currentTeam) {
            const slots = []
            for (let i = 1; i <= 10 && i < cs.length; i++) slots.push(cs[i]?.textContent?.trim())
            if (isSection === 'first') {
              currentTeam.firstGoalRows.push({ type: firstText, slots })
            } else {
              currentTeam.rows.push({ type: firstText, slots })
            }
          } else if (firstText?.includes('第壹') || firstText?.includes('第一')) {
            isSection = 'first'
          } else if (firstText && cs.length <= 2) {
            currentTeam = { name: firstText, rows: [], firstGoalRows: [] }
            timingTeams.push(currentTeam)
            isSection = 'main'
          }
        })
        if (timingTeams.length) data.goal_timing = timingTeams
      }

      if (text.includes('0球') && text.includes('1球') && !text.includes('進球時間')) {
        rows.forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 9) {
            const gd = { type: cs[0]?.textContent?.trim() }
            ;['0','1','2','3','4','5','6','7+'].forEach((k, i) => { gd[k] = cs[i + 1]?.textContent?.trim() })
            if (!data.goal_stats.home) data.goal_stats.home = gd; else data.goal_stats.away = gd
          }
        })
      }
    })

    doc.querySelectorAll('table').forEach(table => {
      const tr = table.querySelector('tr')
      if (!tr) return
      const hdr = Array.from(tr.querySelectorAll('th, td')).map(c => c.textContent.trim()).join(' ')
      if (hdr.includes('勝') || hdr.includes('平') || hdr.includes('負') || hdr.includes('主胜')) {
        table.querySelectorAll('tr').forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 6 && cs[0]?.textContent?.trim()) data.european_odds.push({
            company: cs[0].textContent.trim(),
            eu_init_home: cs[1]?.textContent?.trim(), eu_init_draw: cs[2]?.textContent?.trim(), eu_init_away: cs[3]?.textContent?.trim(),
            eu_curr_home: cs[4]?.textContent?.trim(), eu_curr_draw: cs[5]?.textContent?.trim(), eu_curr_away: cs[6]?.textContent?.trim(),
          })
        })
      }
      if (hdr.includes('亞') || hdr.includes('讓') || hdr.includes('让球')) {
        table.querySelectorAll('tr').forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 6 && cs[0]?.textContent?.trim()) data.asian_odds.push({
            company: cs[0].textContent.trim(),
            home_init: cs[1]?.textContent?.trim(), handicap_init: cs[2]?.textContent?.trim(), away_init: cs[3]?.textContent?.trim(),
            home_curr: cs[4]?.textContent?.trim(), handicap_curr: cs[5]?.textContent?.trim(), away_curr: cs[6]?.textContent?.trim(),
          })
        })
      }
      if (hdr.includes('大') && hdr.includes('小')) {
        table.querySelectorAll('tr').forEach((row, ri) => {
          if (ri === 0) return
          const cs = row.querySelectorAll('td, th')
          if (cs.length >= 6 && cs[0]?.textContent?.trim()) data.goal_odds.push({
            company: cs[0].textContent.trim(),
            home_init: cs[1]?.textContent?.trim(), handicap_init: cs[2]?.textContent?.trim(), away_init: cs[3]?.textContent?.trim(),
            home_curr: cs[4]?.textContent?.trim(), handicap_curr: cs[5]?.textContent?.trim(), away_curr: cs[6]?.textContent?.trim(),
          })
        })
      }
    })

    const briefingMatch = html.match(/賽前簡報[\s\S]*?<div[^>]*>([\s\S]*?)<\/div>/)
    if (briefingMatch) data.briefing = briefingMatch[1].replace(/<[^>]+>/g, '').trim()
    const briefingMatch2 = html.match(/赛前简报[\s\S]*?>([\s\S]{20,500}?)<\/div>/)
    if (!data.briefing && briefingMatch2) data.briefing = briefingMatch2[1].replace(/<[^>]+>/g, '').trim()

    try {
      const seasonMatch = html.match(/本賽季數據統計比較[\s\S]*?<\/div>/) || html.match(/本赛季数据统计比较[\s\S]*?<\/div>/)
      if (seasonMatch) {
        const seasonDoc = parser.parseFromString(seasonMatch[0], 'text/html')
        const seasonText = seasonDoc.textContent
        function extractStat(label, text) {
          const re = new RegExp(label + '[^\\d]*([\\d.]+)')
          const m = text.match(re)
          return m ? m[1] : ''
        }
        function extractPctStat(label, text) {
          const re = new RegExp(label + '[^\\d]*([\\d.]+)%')
          const m = text.match(re)
          return m ? m[1] + '%' : ''
        }
        function extractCountStat(label, text) {
          const re = new RegExp(label + '[^\\d]*\\[?(\\d+)[\\]場场]?')
          const m = text.match(re)
          return m ? m[1] : ''
        }
        const homeIdx = seasonText.indexOf('主隊') >= 0 ? seasonText.indexOf('主隊') : seasonText.indexOf('主队')
        const awayIdx = seasonText.indexOf('客隊') >= 0 ? seasonText.indexOf('客隊') : seasonText.indexOf('客队')
        if (homeIdx >= 0 && awayIdx >= 0) {
          const homeText = seasonText.substring(homeIdx, awayIdx)
          const awayText = seasonText.substring(awayIdx)
          data.season_stats = {
            home: {
              win_pct: extractPctStat('總勝|总胜', homeText), draw_pct: extractPctStat('平', homeText), lose_pct: extractPctStat('負|负', homeText),
              home_win_pct: extractPctStat('主場勝|主场胜', homeText),
              total_gf: extractStat('進球總數|进球总数', homeText), total_ga: extractStat('失球總數|失球总数', homeText),
              avg_gf: extractStat('平均進球|平均进球', homeText), avg_ga: extractStat('平均失球', homeText),
            },
            away: {
              win_pct: extractPctStat('總勝|总胜', awayText), draw_pct: extractPctStat('平', awayText), lose_pct: extractPctStat('負|负', awayText),
              away_win_pct: extractPctStat('客場勝|客场胜', awayText),
              total_gf: extractStat('進球總數|进球总数', awayText), total_ga: extractStat('失球總數|失球总数', awayText),
              avg_gf: extractStat('平均進球|平均进球', awayText), avg_ga: extractStat('平均失球', awayText),
            },
          }
        }
      }
    } catch (e) { console.warn('赛季统计:', e) }

    const upcomingMatch = html.match(/未來五場[\s\S]*?<\/table>/g)
    if (upcomingMatch) {
      const upcomingDoc = parser.parseFromString(upcomingMatch.join(''), 'text/html')
      const upcomingTeams = []
      let currentTeam = null
      upcomingDoc.querySelectorAll('tr').forEach(row => {
        const cs = row.querySelectorAll('td, th')
        const firstText = cs[0]?.textContent?.trim() || ''
        if (firstText && cs.length <= 2) {
          currentTeam = { name: firstText, matches: [] }
          upcomingTeams.push(currentTeam)
        } else if (cs.length >= 4 && currentTeam) {
          currentTeam.matches.push({
            date: cs[0]?.textContent?.trim(), league: cs[1]?.textContent?.trim(),
            opponent: cs[2]?.textContent?.trim(), days_later: cs[3]?.textContent?.trim(),
          })
        }
      })
      if (upcomingTeams.length) data.upcoming = upcomingTeams
    }
  } catch (e) { console.warn('DOM解析:', e) }

  return data
}

onMounted(() => {
  if (selectedMatchInfo.value) {
    matchInfo.value = selectedMatchInfo.value
    fetchMatchDetail()
  }
})

watch(selectedMatchInfo, (val) => {
  if (val) {
    matchInfo.value = val
    analysisData.value = null
    sharedAnalysisData.value = null
    oddsTrendData.value = []
    jcOddsData.value = {}
    fetchMatchDetail()
  }
})
</script>

<style lang="scss" scoped>
@use '../styles/variables' as *;
@use '../styles/mixins' as *;

.match-detail { max-width: 1200px; margin: 0 auto; }
.section-block { margin-bottom:20px; border:1px solid #eee; border-radius:6px; overflow:hidden; }
.section-title { background:$header-bg; padding:10px 15px; font-size:14px; color:$text-primary; display:flex; align-items:center; justify-content:space-between; }
.title-actions { display:flex; align-items:center; gap:8px; }
.config-btn { cursor:pointer; padding:3px 10px; font-size:12px; color:#495057; background:#fff; border:1px solid #dcdfe6; border-radius:4px; transition:all 0.2s; }
.config-btn:hover { color:#409eff; border-color:#409eff; }
.section-content { padding:0; }

.dialog-overlay { position:fixed; top:0; left:0; right:0; bottom:0; background:rgba(0,0,0,0.4); z-index:2000; display:flex; align-items:center; justify-content:center; }
.dialog-box { background:#fff; border-radius:8px; width:360px; max-height:70vh; display:flex; flex-direction:column; box-shadow:0 4px 20px rgba(0,0,0,0.15); }
.dialog-header { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-bottom:1px solid #eee; font-size:14px; font-weight:600; color:#333; }
.dialog-close { cursor:pointer; background:none; border:none; font-size:18px; color:#999; padding:0 4px; line-height:1; }
.dialog-close:hover { color:#333; }
.dialog-body { padding:12px 16px; overflow-y:auto; flex:1; }
.check-all { display:flex; align-items:center; gap:6px; padding:6px 0; border-bottom:1px solid #f0f0f0; margin-bottom:6px; cursor:pointer; font-size:13px; color:#333; user-select:none; }
.check-all input { width:16px; height:16px; accent-color:#409eff; cursor:pointer; }
.company-list { display:flex; flex-wrap:wrap; gap:4px 12px; }
.company-item { display:flex; align-items:center; gap:5px; cursor:pointer; font-size:12px; color:#555; user-select:none; padding:4px 0; min-width:80px; }
.company-item input { width:15px; height:15px; accent-color:#409eff; cursor:pointer; }
.dialog-footer { padding:10px 16px; border-top:1px solid #eee; text-align:right; }
.dialog-btn { cursor:pointer; padding:6px 20px; font-size:13px; color:#fff; background:#409eff; border:none; border-radius:4px; transition:background 0.2s; }
.dialog-btn:hover { background:#66b1ff; }
</style>
