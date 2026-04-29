<template>
  <div class="match-list">
    <div class="filter-bar">
      <el-select v-model="filterLeague" placeholder="全部联赛" clearable size="small" style="width:120px" :teleported="true">
        <el-option label="全部比赛" value="" />
        <el-option v-for="l in leagues" :key="l.id" :label="l.name" :value="l.name" />
      </el-select>
      <el-select v-model="filterStatus" placeholder="状态" clearable size="small" style="width:90px" :teleported="true">
        <el-option label="全部" value="" />
        <el-option label="未开始" value="0" />
        <el-option label="进行中" value="live" />
        <el-option label="完场" value="-1" />
      </el-select>
      <el-button size="small" :icon="Refresh" @click="fetchMatches" :loading="loading" circle />
    </div>

    <div class="match-cards" v-loading="loading">
      <div v-if="filteredMatches.length === 0 && !loading" class="empty-tip">暂无比赛数据</div>
      <div v-for="m in filteredMatches" :key="m.schedule_id" class="match-card"
           :class="{ selected: selectedId === m.schedule_id, live: isLive(m) }"
           @click="selectMatch(m)">
        <div class="card-top">
          <span class="match-id">{{ m.match_id }}</span>
          <div class="card-league">{{ m.league }}</div>
          <span class="time">{{ m.match_time }}</span>
        </div>
        <div class="card-teams">
          <span class="team home">{{ m.home_team }}</span>
          <div class="score-wrap"
               @mouseenter="showDetail(m, $event)"
               @mouseleave="hideDetail">
            <span class="vs" v-if="m.status === 0 || !m.home_score">VS</span>
            <template v-else>
              <span class="score">{{ m.home_score }}-{{ m.away_score }}</span>
              <span class="half" :class="{ invisible: !m.home_half_score }">({{ m.home_half_score || '0' }}-{{ m.away_half_score || '0' }})</span>
            </template>
          </div>
          <span class="team away">{{ m.away_team }}</span>
        </div>
        <div class="card-meta">
          <span class="status-tag" :class="statusClass(m)">{{ statusText(m) }}</span>
          <span class="minute" v-if="m.minute">{{ m.minute }}'</span>
        </div>
        <div class="card-odds" v-if="m.jc_home">
          <span class="odds-val">{{ m.jc_home }}</span>
          <span class="odds-val">{{ m.jc_draw }}</span>
          <span class="odds-val">{{ m.jc_away }}</span>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="detailVisible" class="match-detail-popup" :style="popupStyle" @mouseenter="onPopupEnter" @mouseleave="onPopupLeave">
        <div class="popup-header">
          初盘参考：{{ goalToCn(detailData.handicap) }}
        </div>
        <table class="popup-table" v-if="detailData.events.length > 0">
          <tr class="popup-team-row">
            <th width="14%"></th>
            <th width="43%">{{ detailData.homeTeam }}</th>
            <th width="43%">{{ detailData.awayTeam }}</th>
          </tr>
          <tr v-for="(evt, idx) in detailData.events" :key="idx" class="popup-event-row">
            <td class="evt-time">{{ evt.minute }}'</td>
            <td :class="evt.side === 'home' ? 'evt-active' : 'evt-empty'" :style="{textAlign: evt.side === 'home' ? 'left' : 'right'}">
              <span v-if="evt.side === 'home'" class="evt-icon">{{ evt.icon }}</span>
              {{ evt.side === 'home' ? evt.player : '' }}
            </td>
            <td :class="evt.side === 'away' ? 'evt-active' : 'evt-empty'" :style="{textAlign: evt.side === 'away' ? 'right' : 'left'}">
              {{ evt.side === 'away' ? evt.player : '' }}
              <span v-if="evt.side === 'away'" class="evt-icon">{{ evt.icon }}</span>
            </td>
          </tr>
        </table>
        <table class="popup-table popup-tech" v-if="detailData.tech.length > 0">
          <tr class="popup-tech-header">
            <th width="43%"></th>
            <th width="14%"></th>
            <th width="43%"></th>
          </tr>
          <tr v-for="(t, idx) in detailData.tech" :key="idx" class="popup-tech-row">
            <td>{{ t.home }}</td>
            <td class="tech-name">{{ t.name }}</td>
            <td>{{ t.away }}</td>
          </tr>
        </table>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { Refresh } from '@element-plus/icons-vue'

const props = defineProps({
  selectedId: [String, Number],
  matchDate: { type: String, default: '' },
})
const emit = defineEmits(['select', 'count-change'])

const loading = ref(false)
const matches = ref([])
const filterLeague = ref('')
const filterStatus = ref('')
const REFRESH_INTERVAL = 30000 // 每 30 秒自动刷新
let refreshTimer = null

const detailVisible = ref(false)
const popupStyle = ref({})
const detailCache = {}
const detailData = ref({
  handicap: '',
  homeTeam: '',
  awayTeam: '',
  events: [],
  tech: [],
})

const TECH_NAMES = { 3: '射门', 4: '射正', 14: '控球率', 6: '角球', 5: '黄牌', 8: '犯规', 15: '越位', 36: '红牌', 45: '换人' }
const EVENT_ICONS = { 1: '⚽', 3: '🟥', 11: '🔄' }
const EVENT_NAMES = { 1: '进球', 3: '红牌', 11: '换人' }
const GOAL_CN = '平手,平/半,半球,半/一,一球,一/球半,球半,球半/两,两球,两/两球半,两球半,两球半/三,三球,三/三球半,三球半,三球半/四球,四球,四/四球半,四球半,四球半/五,五球,五/五球半,五球半,五球半/六,六球,六/六球半,六球半,六球半/七,七球,七/七球半,七球半,七球半/八,八球,八/八球半,八球半,八球半/九,九球,九/九球半,九球半,九球半/十,十球'.split(',')

function goalToCn(goal) {
  if (goal == null || goal === '') return ''
  const num = parseFloat(goal)
  if (isNaN(num)) return goal
  if (num > 10 || num < -10) return Math.abs(num) + '球'
  const idx = Math.abs(parseInt(num * 4))
  const text = GOAL_CN[idx] || goal
  return num < 0 ? '受' + text : text
}

const leagues = computed(() => {
  const map = {}
  matches.value.forEach(m => { if (m.league) map[m.league] = true })
  return Object.keys(map).map((name, i) => ({ id: i, name })).sort()
})

const filteredMatches = computed(() => {
  return matches.value.filter(m => {
    if (filterLeague.value && m.league !== filterLeague.value) return false
    const sv = filterStatus.value
    if (sv && sv !== '') {
      if (sv === 'live') {
        if (!isLive(m)) return false
      } else if (String(m.status) !== sv) {
        return false
      }
    }
    return true
  })
})

function isLive(m) { return ['1', '2', '3', '4', '5'].includes(String(m.status)) }

function statusText(m) {
  switch (String(m.status)) {
    case '0': return '未开始'
    case '1': return '上半场'
    case '2': return '中场'
    case '3': return '下半场'
    case '4': return '加时'
    case '5': return '点球'
    case '-1': return '结束'
    default: return ''
  }
}

function statusClass(m) {
  const s = String(m.status)
  if (s === '-1') return 'finished'
  if (['1', '3', '4', '5'].includes(s)) return 'live'
  if (s === '2') return 'halftime'
  return ''
}

function selectMatch(m) { emit('select', m) }

function isToday(dateStr) {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return dateStr === `${y}-${m}-${day}`
}

async function fetchMatches() {
  loading.value = true
  try {
    await fetchTitanMatches()
  } catch (e) {
    console.error('获取比赛列表失败:', e)
  } finally {
    loading.value = false
  }
}

async function decodeResp(resp, encoding = 'utf-8') {
  if (!resp.ok) return ''
  const buffer = await resp.arrayBuffer()
  return new TextDecoder(encoding).decode(buffer)
}

async function fetchTitanMatches() {
  const date = props.matchDate
  try {
    if (isToday(date)) {
      let liveText = ''
      let resultText = ''
      const [liveResp, resultResp] = await Promise.all([
        fetch(`/titan-proxy/jc/xml/bf_jc.txt?${Date.now()}`),
        fetch(`/titan-proxy/jc/handle/JcResult.aspx?d=${date}&${Date.now()}`),
      ])
      liveText = await decodeResp(liveResp)
      resultText = await decodeResp(resultResp)
      const liveList = parseTitanData(liveText)
      const resultList = parseTitanData(resultText)
      const existIds = new Set(liveList.map(m => m.schedule_id))
      const merged = [...liveList, ...resultList.filter(m => !existIds.has(m.schedule_id))]
      matches.value = merged
      if (merged.length > 0 && !props.selectedId) selectMatch(merged[0])
    } else {
      const resp = await fetch(`/titan-proxy/jc/handle/JcResult.aspx?d=${date}&${Date.now()}`)
      const text = await decodeResp(resp)
      if (!text) { matches.value = []; return }
      parseTitanList(text)
    }
  } catch (e) {
    console.error('请求球探数据失败:', e)
    matches.value = []
  }
}

function parseTitanData(text) {
  if (!text || text.trim() === '$$') return []
  const parts = text.split('$')
  if (parts.length < 2) return []
  const leagueData = parts[0]
  const matchData = parts.length >= 3 ? parts[1] : parts[parts.length - 1]
  if (!matchData || !matchData.trim()) return []

  const leagueInfo = {}
  leagueData.split('!').forEach(entry => {
    if (!entry.trim() || !entry.includes('^')) return
    const lp = entry.split('^')
    if (lp.length >= 4) {
      const raw = lp[3]
      leagueInfo[lp[0]] = raw.includes(',') ? raw.split(',')[1]?.trim() || raw.split(',')[0]?.trim() : raw.trim()
    }
  })

  const list = []
  matchData.trim().split('!').forEach(line => {
    if (!line.trim()) return
    const f = line.split('^')
    if (f.length < 24) return
    const matchId = f[4] || ''
    if (!matchId || !/周[一二三四五六日]\d{3}/.test(matchId)) return

    const leagueId = f[5] || ''
    const homeTeamFull = f[8] || ''
    const awayTeamFull = f[10] || ''
    const startTimeStr = f[1] || ''
    const timeParts = startTimeStr.split(',')
    const matchTime = timeParts.length >= 5 ? `${timeParts[3]}:${timeParts[4]}` : ''

    const state = parseInt(f[3]) || 0
    let minute = ''
    if (state === 1 || state === 3 || state === 4) {
      const actualStartStr = f[2] || ''
      const ap = actualStartStr.split(',')
      if (ap.length >= 6) {
        const startDate = new Date(parseInt(ap[0]), parseInt(ap[1]), parseInt(ap[2]), parseInt(ap[3]), parseInt(ap[4]), parseInt(ap[5]))
        const elapsed = Math.floor((Date.now() - startDate.getTime()) / 60000)
        if (state === 1) {
          minute = Math.min(Math.max(elapsed, 1), 45)
          if (elapsed > 45) minute = '45+'
        } else if (state === 3) {
          minute = Math.min(Math.max(elapsed, 46), 90)
          if (elapsed > 90) minute = '90+'
        } else if (state === 4) {
          minute = Math.min(Math.max(elapsed, 91), 120)
          if (elapsed > 120) minute = '120+'
        }
      }
    }

    list.push({
      schedule_id: f[0],
      match_unique_id: f[0],
      match_id: matchId,
      league: leagueInfo[leagueId] || '',
      league_id: leagueId,
      home_team: homeTeamFull.includes(',') ? homeTeamFull.split(',')[2]?.trim() || homeTeamFull.split(',')[0].trim() : homeTeamFull.trim(),
      away_team: awayTeamFull.includes(',') ? awayTeamFull.split(',')[2]?.trim() || awayTeamFull.split(',')[0].trim() : awayTeamFull.trim(),
      start_time: startTimeStr,
      match_time: matchTime,
      status: state,
      minute,
      home_score: f[11] || '',
      away_score: f[12] || '',
      home_half_score: f[13] || '',
      away_half_score: f[14] || '',
      home_red: f[15] || '',
      away_red: f[16] || '',
      home_yellow: f[17] || '',
      away_yellow: f[18] || '',
      handicap: f[22] || '',
      is_turned: f[23] || '0',
      jc_home: '', jc_draw: '', jc_away: '',
      source: 'titan',
    })
  })
  return list
}

function parseTitanList(text) {
  const list = parseTitanData(text)
  matches.value = list
  if (list.length > 0 && !props.selectedId) selectMatch(list[0])
}

async function loadDetailData(scheduleId) {
  if (detailCache[scheduleId]) return detailCache[scheduleId]
  try {
    let text = ''
    try {
      const resp = await fetch(`/titan-proxy/jc/xml/detail.js?${Date.now()}`)
      if (resp.ok) {
        const buffer = await resp.arrayBuffer()
        text = new TextDecoder('gbk').decode(buffer)
      }
    } catch {}
    if (!text) {
      const resp = await fetch('/api/proxy/fetch', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ url: `https://jc.titan007.com/xml/detail.js?${Date.now()}` }) })
      if (resp.ok) { const d = await resp.json(); text = d.body || '' }
    }
    if (!text) return null
    const rqLines = []
    const tcLines = []
    const lineRegex = /rq\[(\d+)\]="([^"]*)"/g
    const tcRegex = /tc\[(\d+)\]="([^"]*)"/g
    let m
    while ((m = lineRegex.exec(text)) !== null) rqLines.push(m[2])
    while ((m = tcRegex.exec(text)) !== null) tcLines.push(m[2])
    detailCache._rq = rqLines
    detailCache._tc = tcLines
    detailCache._time = Date.now()
  } catch (e) {
    console.error('加载详情数据失败:', e)
    return null
  }
  return detailCache
}

async function showDetail(match, event) {
  if (!match.schedule_id) return
  const ver = ++hoverVersion
  clearTimeout(hideTimer)
  triggerEl = event.currentTarget
  const data = await loadDetailData(match.schedule_id)
  if (!data || hoverVersion !== ver) return

  const rqList = detailCache._rq || []
  const tcList = detailCache._tc || []

  const events = []
  const isTurned = match.is_turned === '1'
  rqList.forEach(line => {
    const f = line.split('^')
    if (f[0] !== match.schedule_id) return
    const side = (f[1] === '1') !== isTurned ? 'home' : 'away'
    const evtType = parseInt(f[2]) || 0
    const minute = f[3] || ''
    const playerCn = f[6] || f[4] || ''
    const playerEn = f[9] || ''
    const player = playerCn || playerEn
    if (!player && evtType !== 1) return
    events.push({ side, type: evtType, minute, player, icon: EVENT_ICONS[evtType] || '', name: EVENT_NAMES[evtType] || '' })
  })

  const tech = []
  tcList.forEach(line => {
    const f = line.split('^')
    if (f[0] !== match.schedule_id) return
    const stats = f[1].split(';')
    stats.forEach(s => {
      if (!s) return
      const parts = s.split(',')
      const id = parseInt(parts[0])
      if (!TECH_NAMES[id]) return
      tech.push({ name: TECH_NAMES[id], home: isTurned ? (parts[2] || '') : (parts[1] || ''), away: isTurned ? (parts[1] || '') : (parts[2] || '') })
    })
  })

  detailData.value = {
    handicap: match.handicap || '无',
    homeTeam: match.home_team,
    awayTeam: match.away_team,
    events,
    tech,
  }

  if (hoverVersion !== ver) return
  detailVisible.value = true
  await nextTick()
  positionPopup()
}

let triggerEl = null
let hoverVersion = 0
let popupHovered = false
let hideTimer = null

function positionPopup() {
  const popup = document.querySelector('.match-detail-popup')
  if (!popup || !triggerEl) return
  const elRect = triggerEl.getBoundingClientRect()
  const vw = window.innerWidth
  const vh = window.innerHeight
  const maxH = vh - 16
  popup.style.maxHeight = maxH + 'px'
  const popRect = popup.getBoundingClientRect()
  const popH = Math.min(popRect.height, maxH)
  let left = elRect.left + elRect.width / 2 - popRect.width / 2
  let top = elRect.bottom + 8
  if (left + popRect.width > vw - 8) left = vw - popRect.width - 8
  if (left < 8) left = 8
  if (top + popH > vh - 8) top = elRect.top - popH - 8
  if (top < 8) top = 8
  popupStyle.value = { left: left + 'px', top: top + 'px', maxHeight: maxH + 'px' }
}

function hideDetail() {
  hoverVersion++
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    if (!popupHovered) detailVisible.value = false
  }, 200)
}

function onPopupEnter() {
  popupHovered = true
  clearTimeout(hideTimer)
}

function onPopupLeave() {
  popupHovered = false
  clearTimeout(hideTimer)
  hideTimer = setTimeout(() => {
    detailVisible.value = false
  }, 100)
}

onMounted(() => {
  fetchMatches()
  // 启动定时刷新
  refreshTimer = setInterval(() => {
    fetchMatches()
  }, REFRESH_INTERVAL)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})

watch(() => props.matchDate, () => {
  filterLeague.value = ''
  filterStatus.value = ''
  fetchMatches()
})

watch(filteredMatches, (newVal) => {
  emit('count-change', newVal.length)
}, { immediate: true })
</script>

<style lang="scss" scoped>
@use '../styles/variables' as *;

.match-list { width: 100%; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
.filter-bar { display:flex; align-items:center; gap:6px; padding:8px 10px; flex-shrink:0; flex-wrap:wrap; }

.match-cards { display:flex; flex-direction:column; gap:5px; overflow-y:auto; flex:1; padding:0 10px 10px; }

.match-card {
  background: $text-white; border-radius:8px; padding:10px 12px; cursor:pointer;
  border:2px solid #e8e8e8; transition:all 0.15s;
  margin-bottom:6px;
  &:hover { box-shadow:0 2px 8px rgba(0,0,0,0.08); border-color:#d0d0d0; }
  &.selected { border-color:$primary-color; background:linear-gradient(135deg, #e6f0ff, #f0f7ff); }
  &.live { border-left:3px solid #ff4d4f; }
}

.card-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; gap:6px; }
.match-id { font-size:11px; color:#1890ff; font-weight:600; flex-shrink:0; }
.card-league { font-size:12px; color:#595959; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; flex:1; }
.card-teams { display:flex; align-items:center; margin-bottom:6px; }
.team { font-size:13px; font-weight:500; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; flex:1; &.home{text-align:left;} &.away{text-align:right;} }
.score-wrap { display:flex; flex-direction:column; align-items:center; flex-shrink:0; min-width:42px; margin:0 8px; cursor:pointer; }
.vs,.score { font-size:14px; font-weight:700; color:#d4380d; text-align:center; }
.half { font-size:10px; color:#8c8c8c; margin-top:2px; &.invisible { visibility:hidden; } }
.card-meta { display:flex; align-items:center; justify-content:space-between; }
.time { font-size:12px; color:#595959; flex-shrink:0; }
.status-tag { padding:2px 6px; border-radius:3px; font-size:11px; font-weight:600;
  &.live { background:#fff1f0; color:#cf1322; }
  &.halftime { background:#fff7e6; color:#d46b08; }
  &.finished { background:#f6ffed; color:#389e0d; }
}
.minute { font-size:11px; color:#cf1322; font-weight:700; }
.card-odds { display:flex; gap:4px; margin-top:6px; }
.odds-val { font-size:11px; color:#1890ff; background:#e6f7ff; padding:2px 6px; border-radius:3px; flex:1; text-align:center; }
.empty-tip { text-align:center; color:#8c8c8c; padding:40px 0; font-size:13px; }
</style>

<style lang="scss">
.match-detail-popup {
  position: fixed;
  z-index: 9999;
  background: #fff;
  border: 1px solid #999;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  width: max-content;
  min-width: 200px;
  max-width: 400px;
  font-size: 12px;
  pointer-events: auto;
  overflow-y: auto;

  .popup-header {
    background: #666699;
    color: #fff;
    text-align: center;
    padding: 4px 8px;
    font-weight: bold;
    font-size: 12px;
    border-radius: 3px 3px 0 0;
  }

  .popup-table {
    width: 100%;
    border-collapse: collapse;

    th, td {
      padding: 3px 6px;
      font-size: 12px;
      border: 1px solid #e8e8e8;
    }
  }

  .popup-team-row {
    th {
      background: #D5F2B7;
      color: #006600;
      font-weight: bold;
      text-align: center;
    }
  }

  .popup-event-row {
    .evt-time {
      background: #EFF4EA;
      text-align: center;
      color: #333;
      font-size: 11px;
      width: 14%;
    }
    .evt-active {
      color: #333;
      font-size: 11px;
    }
    .evt-empty {
      font-size: 11px;
    }
    .evt-icon {
      margin: 0 2px;
    }
  }

  .popup-tech-header {
    th {
      background: #D5F2B7;
      color: #006600;
      font-weight: bold;
      text-align: center;
    }
  }

  .popup-tech-row {
    td {
      text-align: center;
      font-size: 11px;
    }
    .tech-name {
      background: #F0F0FF;
      color: #333;
    }
  }
}
</style>
