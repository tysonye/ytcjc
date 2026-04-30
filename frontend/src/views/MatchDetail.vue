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
    <div v-show="activeTab === 'jcbet'" class="jcbet-container">
      <JcBetPanel />
    </div>
    <div v-show="activeTab === 'macau'" class="macau-container">
      <MacauOddsPanel />
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
import { ref, computed, onMounted, onUnmounted, watch, inject, markRaw } from 'vue'
import { useSectionsStore } from '../stores/sections'
import { ElMessage } from 'element-plus'
import { SmartCache, BackgroundRefresher, REFRESH_INTERVAL, CACHE_STRATEGY } from '../utils/fiveMatchMapper'
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
import JcBetPanel from '../components/jc/JcBetPanel.vue'
import MacauOddsPanel from '../components/jc/MacauOddsPanel.vue'

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

const titanDetailCache = new SmartCache('titan_detail', CACHE_STRATEGY.titanMatches)
const titanRefresher = new BackgroundRefresher()

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

function decodeBuffer(buffer) {
  const bytes = new Uint8Array(buffer)
  let encoding = 'utf-8'
  if (bytes.length >= 3 && bytes[0] === 0xEF && bytes[1] === 0xBB && bytes[2] === 0xBF) {
    encoding = 'utf-8'
  } else {
    try {
      new TextDecoder('utf-8', { fatal: true }).decode(buffer)
    } catch {
      encoding = 'gbk'
    }
  }
  const text = new TextDecoder(encoding).decode(buffer)
  if (encoding === 'gbk' && text.includes('ï»¿')) {
    return new TextDecoder('utf-8').decode(buffer)
  }
  return text
}

function getProxyUrl(url) {
  if (url.includes('jc.titan007.com')) return url.replace('https://jc.titan007.com', '/titan-proxy/jc')
  if (url.includes('zq.titan007.com')) return url.replace('https://zq.titan007.com', '/titan-proxy/zq')
  if (url.includes('vip.titan007.com')) return url.replace('https://vip.titan007.com', '/titan-proxy/vip')
  if (url.includes('info.titan007.com')) return url.replace('https://info.titan007.com', '/titan-proxy/info')
  if (url.includes('odds.500.com')) return url.replace('https://odds.500.com', '/500-proxy')
  if (url.includes('macauslot.com')) return url.replace('https://www.macauslot.com', '/macau-proxy')
  return null
}

async function proxyFetch(url) {
  const proxyUrl = getProxyUrl(url)
  if (!proxyUrl) return { body: '' }
  try {
    const resp = await fetch(proxyUrl)
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
    const buffer = await resp.arrayBuffer()
    const text = decodeBuffer(buffer)
    if (text && text.length > 0) return { body: text }
  } catch (e) {
    console.warn('proxyFetch failed:', url, e.message)
  }
  return { body: '' }
}

async function fetchMatchDetail() {
  const info = selectedMatchInfo.value
  if (info) matchInfo.value = info
  const uid = info?.match_unique_id
  if (!uid) return

  // 先查缓存
  const cached = titanDetailCache.get(uid)
  if (cached) {
    analysisData.value = cached.analysisData
    sharedAnalysisData.value = cached.analysisData
    oddsTrendData.value = cached.oddsTrendData || []
    jcOddsData.value = cached.jcOddsData || {}
    loading.value = false
  } else {
    loading.value = true
  }

  try {
    const [analysisResult, oddsResult, jcResult] = await Promise.allSettled([
      proxyFetch(`https://zq.titan007.com/analysis/${uid}cn.htm`),
      proxyFetch(`https://zq.titan007.com/analysis/odds/${uid}.htm`),
      proxyFetch(`https://zq.titan007.com/default/getAnalyData?sid=${uid}&t=1&r=${Date.now()}`),
    ])

    let newAnalysisData = null
    let newOddsTrendData = null
    let newJcOddsData = null

    if (analysisResult.status === 'fulfilled' && analysisResult.value?.body) {
      newAnalysisData = parseAnalysisPage(analysisResult.value.body)
      // 保留缓存中的jc_odds，直到新的jcOddsData解析完成
      if (cached?.analysisData?.jc_odds && !newAnalysisData.jc_odds) {
        newAnalysisData.jc_odds = cached.analysisData.jc_odds
      }
      analysisData.value = newAnalysisData
      sharedAnalysisData.value = newAnalysisData
      // 如果HTML中没有解析到积分数据，再尝试从JS获取
      if (!newAnalysisData.standings_data) {
        await fetchStandingsData(analysisResult.value.body)
      }
    }
    if (oddsResult.status === 'fulfilled' && oddsResult.value?.body) {
      newOddsTrendData = parseOddsTrend(oddsResult.value.body)
      oddsTrendData.value = newOddsTrendData
    }
    if (jcResult.status === 'fulfilled' && jcResult.value?.body) {
      try {
        const jcObj = JSON.parse(jcResult.value.body)
        newJcOddsData = parseJcOdds(jcObj)
        jcOddsData.value = newJcOddsData
        if (analysisData.value) analysisData.value.jc_odds = newJcOddsData
      } catch (e) { console.warn('解析竞彩指数失败:', e) }
    }

    // 存入缓存
    if (newAnalysisData || newOddsTrendData || newJcOddsData) {
      titanDetailCache.set(uid, {
        analysisData: analysisData.value,
        oddsTrendData: oddsTrendData.value,
        jcOddsData: jcOddsData.value,
      })
    }

    // 启动后台静默刷新
    startTitanDetailRefresh(uid)
  } catch (e) {
    console.error('获取比赛详情失败:', e)
    if (!cached) ElMessage.error('获取比赛详情失败')
  } finally {
    loading.value = false
  }
}

function startTitanDetailRefresh(uid) {
  titanRefresher.stop(`titan_detail_${uid}`)
  titanRefresher.start(
    `titan_detail_${uid}`,
    async () => {
      const [analysisResult, oddsResult, jcResult] = await Promise.allSettled([
        proxyFetch(`https://zq.titan007.com/analysis/${uid}cn.htm`),
        proxyFetch(`https://zq.titan007.com/analysis/odds/${uid}.htm`),
        proxyFetch(`https://zq.titan007.com/default/getAnalyData?sid=${uid}&t=1&r=${Date.now()}`),
      ])
      const result = { analysisData: null, oddsTrendData: null, jcOddsData: null }
      if (analysisResult.status === 'fulfilled' && analysisResult.value?.body) {
        result.analysisData = parseAnalysisPage(analysisResult.value.body)
      }
      if (oddsResult.status === 'fulfilled' && oddsResult.value?.body) {
        result.oddsTrendData = parseOddsTrend(oddsResult.value.body)
      }
      if (jcResult.status === 'fulfilled' && jcResult.value?.body) {
        try {
          const jcObj = JSON.parse(jcResult.value.body)
          result.jcOddsData = parseJcOdds(jcObj)
        } catch (e) {}
      }
      return result
    },
    titanDetailCache,
    REFRESH_INTERVAL.titanMatches.normal,
    (freshData) => {
      if (freshData) {
        if (freshData.analysisData) {
          // 保留现有的jc_odds，直到新的jcOddsData可用
          if (!freshData.analysisData.jc_odds && freshData.jcOddsData) {
            freshData.analysisData.jc_odds = freshData.jcOddsData
          } else if (!freshData.analysisData.jc_odds && analysisData.value?.jc_odds) {
            freshData.analysisData.jc_odds = analysisData.value.jc_odds
          }
          analysisData.value = freshData.analysisData
          sharedAnalysisData.value = freshData.analysisData
        }
        if (freshData.oddsTrendData) oddsTrendData.value = freshData.oddsTrendData
        if (freshData.jcOddsData) {
          jcOddsData.value = freshData.jcOddsData
          if (analysisData.value) analysisData.value.jc_odds = freshData.jcOddsData
        }
      }
    }
  )
}

async function fetchStandingsData(analysisHtml) {
  let h2hHome = 0, h2hAway = 0
  let m
  m = analysisHtml.match(/var\s+h2h_home\s*=\s*(\d+)/)
  if (m) h2hHome = parseInt(m[1])
  m = analysisHtml.match(/var\s+h2h_away\s*=\s*(\d+)/)
  if (m) h2hAway = parseInt(m[1])

  const isShowMatch = analysisHtml.match(/var\s+isShowIntegral\s*=\s*(\d+)/)
  if (isShowMatch && parseInt(isShowMatch[1]) === 0 && h2hHome === 0 && h2hAway === 0) return

  let season = '', sclassId = ''
  const scoreUrlMatch = analysisHtml.match(/info\.titan007\.com\/score\/([\d-]+)\/(\d+)/)
  if (scoreUrlMatch) {
    season = scoreUrlMatch[1]
    sclassId = scoreUrlMatch[2]
  } else {
    const sclassIdMatches = [...new Set([...analysisHtml.matchAll(/sclassid=(\d+)/g)].map(x => x[1]))]
    const seasonMatches = [...new Set([...analysisHtml.matchAll(/matchseason=([\d-]+)/g)].map(x => x[1]))]
    if (sclassIdMatches.length > 0 && seasonMatches.length > 0) {
      sclassId = sclassIdMatches[0]
      season = seasonMatches[0]
    } else return
  }

  const applyStandings = (standings) => {
    if (standings && analysisData.value) {
      const updated = { ...analysisData.value, standings_data: standings }
      analysisData.value = updated
      sharedAnalysisData.value = updated
    }
  }

  const scorePageResult = await proxyFetch(`https://info.titan007.com/cn/SubLeague/${sclassId}.html`)
  if (scorePageResult?.body && scorePageResult.body.length > 500) {
    const dataJsMatch = scorePageResult.body.match(/\/jsData\/matchResult\/([^'"]+\.js[^'"]*)/)
    if (dataJsMatch) {
      const dataJsResult = await proxyFetch(`https://info.titan007.com/jsData/matchResult/${dataJsMatch[1]}`)
      if (dataJsResult?.body && dataJsResult.body.includes('totalScore')) {
        applyStandings(parseStandingsJs(dataJsResult.body, h2hHome, h2hAway))
        return
      }
    }

    const seasonInPage = scorePageResult.body.match(/\/jsData\/matchResult\/([^/]+)\/s/)
    if (seasonInPage) season = seasonInPage[1]
  }

  const jsPatterns = []
  if (season.includes('-')) {
    jsPatterns.push(`${season}/s${sclassId}.js`)
  } else {
    jsPatterns.push(`${season}/s${sclassId}.js`)
    jsPatterns.push(`${season}-${parseInt(season) + 1}/s${sclassId}.js`)
  }

  for (const pattern of jsPatterns) {
    const dataJsResult = await proxyFetch(`https://info.titan007.com/jsData/matchResult/${pattern}`)
    if (dataJsResult?.body && dataJsResult.body.includes('totalScore')) {
      applyStandings(parseStandingsJs(dataJsResult.body, h2hHome, h2hAway))
      return
    }
  }

  const seaResult = await proxyFetch(`https://info.titan007.com/jsData/LeagueSeason/sea${sclassId}.js`)
  if (seaResult?.body) {
    const seasonList = [...seaResult.body.matchAll(/'([\d-]+)'/g)].map(x => x[1])
    for (const s of seasonList) {
      for (const subId of [0, 1, 2, 3]) {
        const suffix = subId === 0 ? '' : `_${subId}`
        const dataJsResult = await proxyFetch(`https://info.titan007.com/jsData/matchResult/${s}/s${sclassId}${suffix}.js`)
        if (dataJsResult?.body && dataJsResult.body.includes('totalScore')) {
          applyStandings(parseStandingsJs(dataJsResult.body, h2hHome, h2hAway))
          return
        }
      }
    }
  }
}

function parseStandingsFromHtml(doc, html) {
  const porlet5 = doc.getElementById('porlet_5')
  if (!porlet5) return null

  // 获取所有直接包含积分表格的table
  const tables = porlet5.querySelectorAll('table')
  if (tables.length < 2) return null

  const result = {
    total: [], home: [], away: [],
    half: {}, half_home: {}, half_away: {},
    home_team: null, away_team: null,
    league_short: ''
  }

  // 从HTML中提取h2h_home和h2h_away
  let h2hHome = 0, h2hAway = 0
  let m = html.match(/var\s+h2h_home\s*=\s*(\d+)/)
  if (m) h2hHome = parseInt(m[1])
  m = html.match(/var\s+h2h_away\s*=\s*(\d+)/)
  if (m) h2hAway = parseInt(m[1])

  // 查找包含积分数据的表格
  // 原网页结构：外层table > tbody > tr > td(50%) + td(50%)
  // 每个td内包含两个table：全场和半场
  const outerTable = Array.from(tables).find(t => {
    const tds = t.querySelectorAll('td[width="50%"]')
    return tds.length >= 2
  })

  if (!outerTable) return null

  const halfWidthTds = outerTable.querySelectorAll('td[width="50%"]')
  if (halfWidthTds.length < 2) return null

  function extractTeamData(tdCell, isHome) {
    const innerTables = tdCell.querySelectorAll('table')
    const teamData = { team_id: 0, team_cn: '', team: '' }

    for (const tbl of innerTables) {
      const rows = tbl.querySelectorAll('tr')
      if (rows.length < 5) continue

      // 检查是否是积分表格（有标题行+表头行+数据行）
      const firstRow = rows[0]
      const titleLink = firstRow.querySelector('a[href*="/team/"]')
      if (!titleLink) continue

      // 提取球队信息
      const titleText = titleLink.textContent?.trim() || ''
      const href = titleLink.getAttribute('href') || ''
      const teamIdMatch = href.match(/\/team\/(\d+)/)
      if (teamIdMatch) teamData.team_id = parseInt(teamIdMatch[1])

      // 提取联赛简称和排名 [乌克超-11]查诺莫斯
      const leagueMatch = titleText.match(/\[([^\]]+)\]/)
      if (leagueMatch) result.league_short = leagueMatch[1].split('-')[0]
      teamData.team_cn = titleText.replace(/\[[^\]]+\]/, '').trim()

      // 判断是全场表格还是半场表格
      const headerRow = rows[1]
      const headerCells = headerRow.querySelectorAll('td')
      const headerText = headerCells[0]?.textContent?.trim() || ''
      const isFullTime = headerText === '全场' || headerText.includes('全场')
      const isHalfTime = headerText === '半场' || headerText.includes('半场')

      if (!isFullTime && !isHalfTime) continue

      // 提取数据行：总、主、客、近6
      const dataRows = []
      for (let i = 2; i < rows.length; i++) {
        const cells = rows[i].querySelectorAll('td')
        if (cells.length >= 9) {
          const typeText = cells[0]?.textContent?.trim() || ''
          let type = ''
          if (typeText === '总') type = 'total'
          else if (typeText === '主' || typeText.includes('主')) type = 'home'
          else if (typeText === '客' || typeText.includes('客')) type = 'away'
          else if (typeText === '近6') type = 'near6'

          if (type) {
            const entry = {
              type: typeText,
              played: cells[1]?.textContent?.trim() || '',
              won: cells[2]?.textContent?.trim() || '',
              drawn: cells[3]?.textContent?.trim() || '',
              lost: cells[4]?.textContent?.trim() || '',
              gf: cells[5]?.textContent?.trim() || '',
              ga: cells[6]?.textContent?.trim() || '',
              gd: cells[7]?.textContent?.trim() || '',
              points: cells[8]?.textContent?.trim() || '',
              rank: cells[9]?.textContent?.trim() || '',
              win_rate: cells[10]?.textContent?.trim() || '',
            }
            dataRows.push({ type, entry })
          }
        }
      }

      // 将数据存入结果
      const targetId = isHome ? h2hHome : h2hAway
      if (isFullTime) {
        for (const { type, entry } of dataRows) {
          if (type === 'total') {
            result.total.push({ ...entry, team_id: targetId, team_cn: teamData.team_cn })
            if (isHome) result.home_team = { ...entry, name: teamData.team_cn, team_id: targetId, team_cn: teamData.team_cn }
            else result.away_team = { ...entry, name: teamData.team_cn, team_id: targetId, team_cn: teamData.team_cn }
          } else if (type === 'home') {
            result.home.push({ ...entry, team_id: targetId, team_cn: teamData.team_cn })
          } else if (type === 'away') {
            result.away.push({ ...entry, team_id: targetId, team_cn: teamData.team_cn })
          } else if (type === 'near6') {
            // 近6数据附加到team对象
            const teamKey = isHome ? 'home_team' : 'away_team'
            if (result[teamKey]) {
              result[teamKey].near_six_stats = entry
            }
          }
        }
      } else if (isHalfTime) {
        for (const { type, entry } of dataRows) {
          let container = null
          if (type === 'total') {
            container = result.half
          } else if (type === 'home') {
            container = isHome ? result.half_home : result.half_home
          } else if (type === 'away') {
            container = isHome ? result.half_away : result.half_away
          } else if (type === 'near6') {
            // 半场近6数据附加到team对象
            const teamKey = isHome ? 'home_team' : 'away_team'
            if (result[teamKey]) {
              result[teamKey].half_near_six_stats = entry
            }
            continue
          }
          if (container) {
            container[targetId] = { ...entry, team_id: targetId, team_cn: teamData.team_cn }
          }
        }
      }
    }

    return teamData
  }

  // 提取主队数据（第一个td）
  extractTeamData(halfWidthTds[0], true)
  // 提取客队数据（第二个td）
  extractTeamData(halfWidthTds[1], false)

  if (!result.home_team && !result.away_team) return null
  return result
}

function parseStandingsJs(js, h2hHome, h2hAway) {
  const sg = (arr, i) => (i < arr.length && arr[i] !== undefined && arr[i] !== null) ? String(arr[i]) : ''
  const result = { total: [], home: [], away: [], home_team: null, away_team: null, league_short: '' }

  let m
  let arrTeam = []
  m = js.match(/var\s+arrTeam\s*=\s*(\[\[.+?\]);/s)
  if (m) {
    try {
      arrTeam = JSON.parse(m[1].replace(/'/g, '"'))
    } catch { arrTeam = [] }
  }

  let leagueShort = ''
  m = js.match(/var\s+arrLeague\s*=\s*\[\d+\s*,\s*'([^']*)'/)
  if (m) leagueShort = m[1]
  result.league_short = leagueShort

  function getTeamName(teamId) {
    const team = arrTeam.find(t => parseInt(t[0]) === teamId)
    return team ? (team[3] || team[1] || '') : ''
  }

  function getTeamCnName(teamId) {
    const team = arrTeam.find(t => parseInt(t[0]) === teamId)
    return team ? (team[1] || team[3] || '') : ''
  }

  function formatTeamLabel(entry) {
    const cn = entry.team_cn || entry.team
    if (leagueShort && entry.rank) {
      return `[${leagueShort}-${entry.rank}]${cn}`
    }
    return cn
  }

  m = js.match(/var\s+totalScore\s*=\s*(\[\[.+?\]);/s)
  if (m) {
    try {
      const data = JSON.parse(m[1].replace(/'/g, '"'))
      for (const item of data) {
        const teamId = parseInt(item[2])
        const teamEn = getTeamName(teamId)
        const teamCn = getTeamCnName(teamId)
        const nearSix = []
        for (let ni = 19; ni <= 24; ni++) {
          const v = item[ni]
          if (v !== undefined && v !== null && v !== '') nearSix.push(parseInt(v))
        }
        let nearSixStats = null
        if (nearSix.length > 0) {
          const nsWon = nearSix.filter(v => v === 0).length
          const nsDrawn = nearSix.filter(v => v === 1).length
          const nsLost = nearSix.filter(v => v === 2).length
          const nsPlayed = nearSix.length
          const nsPoints = 3 * nsWon + nsDrawn
          const nsWinRate = nsPlayed > 0 ? ((nsWon / nsPlayed) * 100).toFixed(1) : ''
          nearSixStats = {
            played: String(nsPlayed), won: String(nsWon), drawn: String(nsDrawn),
            lost: String(nsLost), gf: '', ga: '', gd: '',
            points: String(nsPoints), rank: '', win_rate: nsWinRate,
          }
        }
        const entry = {
          rank: sg(item, 1), team_id: teamId, team: teamEn, team_cn: teamCn,
          red_card: sg(item, 3), played: sg(item, 4), won: sg(item, 5),
          drawn: sg(item, 6), lost: sg(item, 7), gf: sg(item, 8), ga: sg(item, 9),
          gd: sg(item, 10), win_rate: sg(item, 11), draw_rate: sg(item, 12),
          lose_rate: sg(item, 13), avg_gf: sg(item, 14), avg_ga: sg(item, 15),
          points: String(parseInt(item[16] || 0) - parseInt(item[17] || 0)),
          notes: sg(item, 18), near_six: nearSix, near_six_stats: nearSixStats,
        }
        entry.label = formatTeamLabel(entry)
        result.total.push(entry)
        if (teamId === h2hHome) result.home_team = { name: teamCn, ...entry }
        if (teamId === h2hAway) result.away_team = { name: teamCn, ...entry }
      }
    } catch (e) { console.warn('totalScore parse:', e) }
  }

  m = js.match(/var\s+homeScore\s*=\s*(\[\[.+?\]\]);/s)
  if (m) {
    try {
      const data = JSON.parse(m[1].replace(/'/g, '"'))
      for (const item of data) {
        const teamId = parseInt(item[1])
        const teamCn = getTeamCnName(teamId)
        result.home.push({
          rank: sg(item, 0), team_id: teamId, team: getTeamName(teamId), team_cn: teamCn,
          played: sg(item, 2), won: sg(item, 3), drawn: sg(item, 4), lost: sg(item, 5),
          gf: sg(item, 6), ga: sg(item, 7), gd: sg(item, 8),
          win_rate: sg(item, 9), draw_rate: sg(item, 10), lose_rate: sg(item, 11),
          avg_gf: sg(item, 12), avg_ga: sg(item, 13), points: sg(item, 14),
        })
      }
    } catch (e) { console.warn('homeScore parse:', e) }
  }

  m = js.match(/var\s+guestScore\s*=\s*(\[\[.+?\]\]);/s)
  if (m) {
    try {
      const data = JSON.parse(m[1].replace(/'/g, '"'))
      for (const item of data) {
        const teamId = parseInt(item[1])
        const teamCn = getTeamCnName(teamId)
        result.away.push({
          rank: sg(item, 0), team_id: teamId, team: getTeamName(teamId), team_cn: teamCn,
          played: sg(item, 2), won: sg(item, 3), drawn: sg(item, 4), lost: sg(item, 5),
          gf: sg(item, 6), ga: sg(item, 7), gd: sg(item, 8),
          win_rate: sg(item, 9), draw_rate: sg(item, 10), lose_rate: sg(item, 11),
          avg_gf: sg(item, 12), avg_ga: sg(item, 13), points: sg(item, 14),
        })
      }
    } catch (e) { console.warn('guestScore parse:', e) }
  }

  m = js.match(/var\s+halfScore\s*=\s*(\[\[.+?\]\]);/s)
  if (m) {
    try {
      const data = JSON.parse(m[1].replace(/'/g, '"'))
      for (const item of data) {
        const teamId = parseInt(item[1])
        const teamCn = getTeamCnName(teamId)
        const entry = {
          rank: sg(item, 0), team_id: teamId, team: getTeamName(teamId), team_cn: teamCn,
          played: sg(item, 2), won: sg(item, 3), drawn: sg(item, 4), lost: sg(item, 5),
          gf: sg(item, 6), ga: sg(item, 7), gd: sg(item, 8),
          win_rate: sg(item, 9), draw_rate: sg(item, 10), lose_rate: sg(item, 11),
          avg_gf: sg(item, 12), avg_ga: sg(item, 13), points: sg(item, 14),
        }
        if (!result.half) result.half = {}
        result.half[teamId] = entry
      }
    } catch (e) { console.warn('halfScore parse:', e) }
  }

  m = js.match(/var\s+halfHomeScore\s*=\s*(\[\[.+?\]\]);/s)
  if (m) {
    try {
      const data = JSON.parse(m[1].replace(/'/g, '"'))
      for (const item of data) {
        const teamId = parseInt(item[1])
        const entry = {
          rank: sg(item, 0), team_id: teamId, team_cn: getTeamCnName(teamId),
          played: sg(item, 2), won: sg(item, 3), drawn: sg(item, 4), lost: sg(item, 5),
          gf: sg(item, 6), ga: sg(item, 7), gd: sg(item, 8),
          win_rate: sg(item, 9), points: sg(item, 14),
        }
        if (!result.half_home) result.half_home = {}
        result.half_home[teamId] = entry
      }
    } catch (e) { console.warn('halfHomeScore parse:', e) }
  }

  m = js.match(/var\s+halfGuestScore\s*=\s*(\[\[.+?\]\]);/s)
  if (m) {
    try {
      const data = JSON.parse(m[1].replace(/'/g, '"'))
      for (const item of data) {
        const teamId = parseInt(item[1])
        const entry = {
          rank: sg(item, 0), team_id: teamId, team_cn: getTeamCnName(teamId),
          played: sg(item, 2), won: sg(item, 3), drawn: sg(item, 4), lost: sg(item, 5),
          gf: sg(item, 6), ga: sg(item, 7), gd: sg(item, 8),
          win_rate: sg(item, 9), points: sg(item, 14),
        }
        if (!result.half_away) result.half_away = {}
        result.half_away[teamId] = entry
      }
    } catch (e) { console.warn('halfGuestScore parse:', e) }
  }

  if (!result.total.length && !result.home.length && !result.away.length) return null
  return result
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
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const allTables = doc.querySelectorAll('table')

    // 解析积分排名表格（直接从HTML中提取，包含完整的近6和半场数据）
    try {
      const standingsResult = parseStandingsFromHtml(doc, html)
      if (standingsResult) data.standings_data = standingsResult
    } catch (e) { console.warn('解析积分排名表格失败:', e) }

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
        const seasonText = seasonDoc?.textContent || ''
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
        if (seasonText) {
          const homeIdx = seasonText.indexOf('主隊') >= 0 ? seasonText.indexOf('主隊') : seasonText.indexOf('主队')
          const awayIdx = seasonText.indexOf('客隊') >= 0 ? seasonText.indexOf('客隊') : seasonText.indexOf('客队')
          if (homeIdx >= 0 && awayIdx >= 0) {
            const homeText = seasonText.substring(homeIdx, awayIdx)
            const awayText = seasonText.substring(awayIdx)
            data.season_stats = {
              home: {
                win_pct: extractPctStat('總勝 | 总胜', homeText), draw_pct: extractPctStat('平', homeText), lose_pct: extractPctStat('負 | 负', homeText),
                home_win_pct: extractPctStat('主場勝 | 主场胜', homeText),
                total_gf: extractStat('進球總數 | 进球总数', homeText), total_ga: extractStat('失球總數 | 失球总数', homeText),
                avg_gf: extractStat('平均進球 | 平均进球', homeText), avg_ga: extractStat('平均失球', homeText),
              },
              away: {
                win_pct: extractPctStat('總勝 | 总胜', awayText), draw_pct: extractPctStat('平', awayText), lose_pct: extractPctStat('負 | 负', awayText),
                away_win_pct: extractPctStat('客場勝 | 客场胜', awayText),
                total_gf: extractStat('進球總數 | 进球总数', awayText), total_ga: extractStat('失球總數 | 失球总数', awayText),
                avg_gf: extractStat('平均進球 | 平均进球', awayText), avg_ga: extractStat('平均失球', awayText),
              },
            }
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

onUnmounted(() => {
  const uid = matchInfo.value?.match_unique_id
  if (uid) titanRefresher.stop(`titan_detail_${uid}`)
})

watch(selectedMatchInfo, (val, oldVal) => {
  if (val) {
    // 停止旧比赛的后台刷新
    const oldUid = oldVal?.match_unique_id
    if (oldUid) titanRefresher.stop(`titan_detail_${oldUid}`)

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

.match-detail { max-width: 1200px; margin: 0 auto; height: 100%; }
.jcbet-container { height: 100%; display: flex; flex-direction: column; overflow: hidden; }
.macau-container { height: 100%; display: flex; flex-direction: column; overflow: hidden; }
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
