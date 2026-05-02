const CACHE_KEY = 'five_match_id_cache_v2'
const CACHE_TTL = 24 * 60 * 60 * 1000

const idCache = new Map()

function loadCacheFromStorage() {
  try {
    localStorage.removeItem('five_match_id_cache')
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw)
    if (typeof parsed !== 'object' || parsed === null) return
    const now = Date.now()
    for (const [key, value] of Object.entries(parsed)) {
      if (value && typeof value.fiveMatchId !== 'undefined' && (now - value.timestamp) < CACHE_TTL) {
        idCache.set(key, value)
      }
    }
  } catch (e) {}
}

function persistCache() {
  try {
    const obj = Object.fromEntries(idCache.entries())
    localStorage.setItem(CACHE_KEY, JSON.stringify(obj))
  } catch (e) {}
}

function extractMatchDate(startTime) {
  if (!startTime) return ''
  const parts = String(startTime).split(',')
  if (parts.length < 3) return ''
  const year = parts[0].trim()
  const month = parts[1].trim().padStart(2, '0')
  const day = parts[2].trim().padStart(2, '0')
  return `${year}-${month}-${day}`
}

function cleanCache() {
  const now = Date.now()
  for (const [key, value] of idCache) {
    if (!value || (now - value.timestamp) >= CACHE_TTL) {
      idCache.delete(key)
    }
  }
  persistCache()
}

function buildCacheKey(homeTeam, awayTeam, matchDate) {
  return `${homeTeam}_${awayTeam}_${matchDate}`
}

function normalizeTeamName(name) {
  if (!name) return ''
  return name.trim()
    .replace(/[\s·\-\.]/g, '')
    .replace(/\(.*?\)/g, '')
}

function teamNameMatch(titanName, fiveName) {
  if (!titanName || !fiveName) return false
  const a = normalizeTeamName(titanName)
  const b = normalizeTeamName(fiveName)
  if (!a || !b) return false
  if (a === b) return true
  if (a.length >= 2 && b.length >= 2) {
    if (a.includes(b) || b.includes(a)) return true
    const aFirst2 = a.substring(0, 2)
    const aLast2 = a.substring(a.length - 2)
    if (b.includes(aFirst2) && b.includes(aLast2) && aFirst2 !== aLast2) return true
    const bFirst2 = b.substring(0, 2)
    const bLast2 = b.substring(b.length - 2)
    if (a.includes(bFirst2) && a.includes(bLast2) && bFirst2 !== bLast2) return true
    const longer = a.length >= b.length ? a : b
    const shorter = a.length >= b.length ? b : a
    if (longer.length <= shorter.length + 2) {
      let diffCount = 0
      let i = 0, j = 0
      while (i < longer.length && j < shorter.length) {
        if (longer[i] === shorter[j]) {
          i++; j++
        } else {
          diffCount++; i++
          if (diffCount > 1) break
        }
      }
      diffCount += (longer.length - i)
      if (diffCount <= 1) return true
    }
    if (a.length >= 4 && b.length >= 4) {
      const aFirst3 = a.substring(0, 3)
      const bFirst3 = b.substring(0, 3)
      if (aFirst3 === bFirst3) {
        const aLast2 = a.substring(a.length - 2)
        const bLast2 = b.substring(b.length - 2)
        if (aLast2 === bLast2) return true
      }
    }
    const aliases = {
      '马竞': ['马德里竞技', '馬德里競技'],
      '皇马': ['皇家马德里', '皇家馬德里'],
      '巴萨': ['巴塞罗那', '巴塞羅那'],
      '曼联': ['曼彻斯特联', '曼徹斯特聯'],
      '曼城': ['曼彻斯特城', '曼徹斯特城'],
      '利物浦': ['利物蒲'],
      '阿森纳': ['阿仙奴', '兵工廠'],
      '切尔西': ['車路士'],
      '热刺': ['熱刺', '托特纳姆热刺', '托特納姆熱刺'],
      '尤文': ['尤文图斯', '祖雲達斯'],
      '国米': ['国际米兰', '國際米蘭'],
      '米兰': ['AC米兰', 'AC米蘭', 'ac米兰', 'ac米蘭'],
      '罗马': ['羅馬', '罗马体育会'],
      '那不勒斯': ['拿坡里', '拿玻里'],
      '拜仁': ['拜仁慕尼黑', '拜耳慕尼黑'],
      '多特': ['多特蒙德', '多蒙特'],
      '巴黎': ['巴黎圣日耳曼', '巴黎聖日耳門'],
      '里昂': ['裡昂'],
      '马赛': ['馬賽'],
      '摩纳哥': ['摩納哥'],
    }
    for (const [key, values] of Object.entries(aliases)) {
      const names = [key, ...values]
      const aMatch = names.some(n => normalizeTeamName(n) === a)
      const bMatch = names.some(n => normalizeTeamName(n) === b)
      if (aMatch && bMatch) return true
    }
    if (a.length >= 3 && b.length >= 3) {
      const minLen = Math.min(a.length, b.length)
      let sameStart = 0
      for (let i = 0; i < minLen; i++) {
        if (a[i] === b[i]) sameStart++
        else break
      }
      let sameEnd = 0
      for (let i = 1; i <= minLen; i++) {
        if (a[a.length - i] === b[b.length - i]) sameEnd++
        else break
      }
      if (sameStart >= 2 || (sameStart >= 1 && sameEnd >= 2)) {
        return true
      }
    }
  }
  return false
}

async function fetchWithGbkFallback(url) {
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
    } catch (e) {
      try {
        return new TextDecoder('gbk').decode(buffer)
      } catch (e2) {
        return new TextDecoder('utf-8').decode(buffer)
      }
    }
  } catch (e) {
    return null
  }
}

// ==================== 新增：分级缓存策略 ====================

const CACHE_STRATEGY = {
  mapping: {
    memoryTTL: 10 * 60 * 1000,
    storageTTL: 60 * 60 * 1000,
  },
  titanMatches: {
    memoryTTL: 30 * 1000,
    storageTTL: 2 * 60 * 1000,
  },
  fiveData: {
    memoryTTL: 5 * 60 * 1000,
    storageTTL: 30 * 60 * 1000,
  }
}

class SmartCache {
  constructor(name, strategy) {
    this.name = name
    this.strategy = strategy
    this.memory = new Map()
  }

  get(key) {
    if (this.memory.has(key)) {
      const item = this.memory.get(key)
      if (Date.now() - item.timestamp < this.strategy.memoryTTL) {
        return item.data
      }
    }
    try {
      const raw = localStorage.getItem(`${this.name}_${key}`)
      if (raw) {
        const item = JSON.parse(raw)
        // 检查时间戳和数据有效性
        if (Date.now() - item.timestamp < this.strategy.storageTTL) {
          // 如果数据是数组格式（Map序列化后的），恢复为Map
          if (item.dataType === 'map' && Array.isArray(item.data)) {
            const map = new Map(item.data)
            this.memory.set(key, { data: map, timestamp: item.timestamp })
            return map
          }
          // 旧数据格式兼容：如果 data 存在且不是 undefined
          if (item.data !== undefined && item.data !== null) {
            this.memory.set(key, item)
            return item.data
          }
        }
        // 数据无效或过期，删除
        localStorage.removeItem(`${this.name}_${key}`)
      }
    } catch (e) {}
    return null
  }

  set(key, data) {
    const item = { data, timestamp: Date.now() }
    this.memory.set(key, item)
    try {
      const serializable = { timestamp: item.timestamp }
      if (data instanceof Map) {
        serializable.dataType = 'map'
        serializable.data = Array.from(data.entries())
      } else {
        serializable.data = data
      }
      localStorage.setItem(`${this.name}_${key}`, JSON.stringify(serializable))
    } catch (e) {
      this.cleanupStorage()
    }
  }

  cleanupStorage() {
    const now = Date.now()
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i)
      if (key && key.startsWith(this.name + '_')) {
        try {
          const item = JSON.parse(localStorage.getItem(key))
          // 删除过期数据或无效数据（没有 dataType 且 data 为 undefined 的旧数据）
          if (now - item.timestamp > this.strategy.storageTTL ||
              (item.data === undefined && !item.dataType)) {
            localStorage.removeItem(key)
          }
        } catch (e) {
          // 解析失败，删除损坏的数据
          localStorage.removeItem(key)
        }
      }
    }
  }

  invalidate(key) {
    this.memory.delete(key)
    try {
      localStorage.removeItem(`${this.name}_${key}`)
    } catch (e) {}
  }

  // 清除所有与此缓存相关的数据
  clearAll() {
    this.memory.clear()
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i)
      if (key && key.startsWith(this.name + '_')) {
        localStorage.removeItem(key)
      }
    }
  }
}

const mappingCache = new SmartCache('five_mapping', CACHE_STRATEGY.mapping)
const titanCache = new SmartCache('titan_matches', CACHE_STRATEGY.titanMatches)

// ==================== 新增：后台静默刷新管理器 ====================

class BackgroundRefresher {
  constructor() {
    this.timers = new Map()
  }

  start(key, fetcher, cache, interval, onUpdate) {
    this.stop(key)
    const timerId = setInterval(() => {
      this.refresh(key, fetcher, cache, onUpdate)
    }, interval)
    this.timers.set(key, timerId)
  }

  async refresh(key, fetcher, cache, onUpdate) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000)
      const fresh = await fetcher({ signal: controller.signal })
      clearTimeout(timeoutId)
      if (fresh) {
        cache.set(key, fresh)
        if (onUpdate) onUpdate(fresh)
      }
    } catch (e) {
      console.warn(`[Refresher] ${key} refresh failed:`, e)
    }
  }

  stop(key) {
    if (this.timers.has(key)) {
      clearInterval(this.timers.get(key))
      this.timers.delete(key)
    }
  }

  stopAll() {
    for (const [key, timerId] of this.timers) {
      clearInterval(timerId)
    }
    this.timers.clear()
  }
}

const refresher = new BackgroundRefresher()

const REFRESH_INTERVAL = {
  titanMatches: {
    normal: 60 * 1000,
    live: 15 * 1000,
    halftime: 60 * 1000,
  },
  mapping: 30 * 60 * 1000,
  fiveData: 10 * 60 * 1000,
}

// ==================== 新增：从500.com live页面提取match_id ====================

function extractMatchIdFromRow(row) {
  // 首先尝试第一个td
  const firstTd = row.querySelector('td:first-child')
  if (firstTd) {
    const text = firstTd.textContent || ''
    const match = text.match(/周[一二三四五六日]\d{3}/)
    if (match) return match[0]
  }

  // 回退：尝试所有td
  const allTds = row.querySelectorAll('td')
  for (const td of allTds) {
    const text = td.textContent || ''
    const match = text.match(/周[一二三四五六日]\d{3}/)
    if (match) return match[0]
  }

  // 回退：尝试行内的任何文本
  const rowText = row.textContent || ''
  const match = rowText.match(/周[一二三四五六日]\d{3}/)
  return match ? match[0] : null
}

// ==================== 新增：基于match_id的精确映射 ====================

let globalMapping = null
let globalMappingPromise = null

async function getGlobalMapping() {
  if (globalMapping && globalMapping.size > 0) {
    return globalMapping
  }

  if (globalMappingPromise) {
    return globalMappingPromise
  }

  globalMappingPromise = buildGlobalMapping()
  try {
    const result = await globalMappingPromise
    return result
  } finally {
    globalMappingPromise = null
  }
}

async function buildGlobalMapping() {
  const cached = mappingCache.get('global')
  if (cached && cached instanceof Map && cached.size > 0) {
    console.log('[500Mapper] globalMapping cache hit:', cached.size, 'matches')
    globalMapping = cached
    return cached
  }

  const mapping = new Map()
  const expectDates = new Set()

  // 第一步：获取默认页面，提取当前期号
  let defaultExpectDate = ''
  try {
    const html = await fetchWithGbkFallback('/live500-proxy/')
    if (html) {
      const year = new Date().getFullYear().toString()
      parseAndMerge(html, mapping, year)
      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const options = doc.querySelectorAll('#sel_expect option')
      options.forEach(opt => {
        const val = opt.getAttribute('value')
        if (val) expectDates.add(val)
      })
      const selExpect = doc.querySelector('#sel_expect')
      if (selExpect) {
        const val = selExpect.getAttribute('value') || selExpect.value
        if (val) {
          expectDates.add(val)
          defaultExpectDate = val
        }
      }
    }
  } catch (e) {
    console.error('[500Mapper] buildGlobalMapping default page error:', e)
  }

  // 第二步：基于默认期号，也获取前一天和后一天的期号数据
  if (defaultExpectDate) {
    try {
      const d = new Date(defaultExpectDate)
      d.setDate(d.getDate() - 1)
      expectDates.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
      d.setDate(d.getDate() + 2)
      expectDates.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
    } catch (e) {}
  }

  // 第三步：获取所有期号的数据
  for (const dateStr of expectDates) {
    try {
      const html = await fetchWithGbkFallback(`/live500-proxy/?e=${dateStr}`)
      if (html) {
        const year = dateStr.split('-')[0]
        parseAndMerge(html, mapping, year)
      }
    } catch (e) {
      console.error('[500Mapper] buildGlobalMapping error for', dateStr, ':', e)
    }
  }

  // 第四步：如果映射还是空的，尝试用今天的日期和前几天
  if (mapping.size === 0) {
    const today = new Date()
    for (let i = 0; i < 3; i++) {
      const d = new Date(today)
      d.setDate(d.getDate() - i)
      const dateStr = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
      try {
        const html = await fetchWithGbkFallback(`/live500-proxy/?e=${dateStr}`)
        if (html) {
          const year = dateStr.split('-')[0]
          parseAndMerge(html, mapping, year)
        }
      } catch (e) {}
    }
  }

  console.log('[500Mapper] globalMapping built:', mapping.size, 'matches')
  if (mapping.size > 0) {
    mappingCache.set('global', mapping)
    globalMapping = mapping
  }
  return mapping
}

function parseAndMerge(html, mapping, expectYear) {
  const hasMatchData = html.includes('周') && /周[一二三四五六日]\d{3}/.test(html)
  if (!hasMatchData) return

  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')
  const rows = doc.querySelectorAll('tr[id^="a"]')

  const processRow = (row) => {
    const matchId = extractMatchIdFromRow(row)
    const fid = row.getAttribute('fid') || row.id?.replace('a', '')
    if (!matchId || !fid) return

    const gy = row.getAttribute('gy') || ''
    const gyParts = gy.split(',')
    const homeTeam = gyParts[1] || ''
    const awayTeam = gyParts[2] || ''

    const yy = row.getAttribute('yy') || ''
    const yyParts = yy.split(',')
    const homeTeamYy = yyParts[1] || ''
    const awayTeamYy = yyParts[2] || ''

    // 从td中提取比赛时间（格式：MM-DD HH:MM）
    const tds = row.querySelectorAll('td')
    let matchDate = ''
    for (const td of tds) {
      const text = (td.textContent || '').trim()
      const dateMatch = text.match(/(\d{2})-(\d{2})\s+\d{2}:\d{2}/)
      if (dateMatch) {
        const mm = dateMatch[1]
        const dd = dateMatch[2]
        matchDate = `${expectYear}-${mm}-${dd}`
        break
      }
    }

    const key = matchDate ? `${matchDate}-${matchId}` : matchId
    if (!mapping.has(key)) {
      mapping.set(key, { fid, homeTeam, awayTeam, homeTeamYy, awayTeamYy, matchDate, matchId })
      console.log('[500Mapper] mapping:', key, '-> fid:', fid, 'gy:', homeTeam, 'vs', awayTeam, 'yy:', homeTeamYy, 'vs', awayTeamYy)
    }
  }

  if (rows.length > 0) {
    rows.forEach(processRow)
  } else {
    const allRows = doc.querySelectorAll('tr')
    allRows.forEach(processRow)
  }
}

function buildMappingKey(startTime, matchId) {
  const date = extractMatchDate(startTime)
  return date ? `${date}-${matchId}` : matchId
}

function matchTeamsWithEntry(titanHomeNames, titanAwayNames, entry) {
  if (!titanHomeNames.length || !titanAwayNames.length) return 0
  const names = [
    { home: entry.homeTeam, away: entry.awayTeam },
    { home: entry.homeTeamYy, away: entry.awayTeamYy },
  ]
  for (const { home, away } of names) {
    if (!home || !away) continue
    for (const th of titanHomeNames) {
      const homeOk = teamNameMatch(th, home) || teamNameMatch(th, away)
      if (!homeOk) continue
      for (const ta of titanAwayNames) {
        const awayOk = teamNameMatch(ta, away) || teamNameMatch(ta, home)
        if (awayOk) {
          const directHome = teamNameMatch(th, home)
          const directAway = teamNameMatch(ta, away)
          return (directHome && directAway) ? 3 : 2
        }
      }
    }
  }
  return 0
}

async function findFiveMatchIdByMatchId(titanMatchInfo) {
  const { match_id, home_team, away_team, home_team_full, away_team_full, start_time } = titanMatchInfo
  if (!match_id || !/周[一二三四五六日]\d{3}/.test(match_id)) {
    return null
  }

  // Titan数据：home_team_full可能是联赛名，home_team可能是粤语名
  // 需要同时使用两个名称来匹配
  const titanHomeNames = [home_team, home_team_full].filter(Boolean)
  const titanAwayNames = [away_team, away_team_full].filter(Boolean)
  console.log('[500Mapper] titan names:', titanHomeNames, 'vs', titanAwayNames)

  const mapping = await getGlobalMapping()

  const exactKey = buildMappingKey(start_time, match_id)
  console.log('[500Mapper] looking for key:', exactKey)

  // 第一步：精确key匹配
  if (mapping.has(exactKey)) {
    const entry = mapping.get(exactKey)
    console.log('[500Mapper] exact key matched:', exactKey, '-> fid:', entry.fid)
    const score = matchTeamsWithEntry(titanHomeNames, titanAwayNames, entry)
    if (score >= 2) {
      console.log('[500Mapper] exact key + team verification passed, score:', score)
      return entry.fid
    }
    console.log('[500Mapper] exact key matched but team verification failed (score:', score, '), trying other entries')
  }

  // 第二步：只用match_id后缀匹配，验证球队名称
  for (const [key, entry] of mapping) {
    if (!key.endsWith(`-${match_id}`) && key !== match_id) continue
    const score = matchTeamsWithEntry(titanHomeNames, titanAwayNames, entry)
    if (score >= 2) {
      console.log('[500Mapper] match_id + team matched via scan:', key, '-> fid:', entry.fid, 'score:', score)
      return entry.fid
    }
  }

  // 第三步：遍历所有映射用球队名称匹配
  if (titanHomeNames.length && titanAwayNames.length) {
    let bestFid = null
    let bestScore = 0

    for (const [key, entry] of mapping) {
      const score = matchTeamsWithEntry(titanHomeNames, titanAwayNames, entry)
      if (score > bestScore) {
        bestScore = score
        bestFid = entry.fid
      }
    }

    if (bestFid && bestScore >= 2) {
      console.log('[500Mapper] team name fallback matched: fid:', bestFid, 'score:', bestScore)
      return bestFid
    }
  }

  console.log('[500Mapper] no match found for:', exactKey, titanHomeNames, 'vs', titanAwayNames)
  return null
}

// ==================== 新增：批量获取当天所有500比赛并建立映射 ====================

async function preloadFiveMapping() {
  console.log('[500Mapper] preloading global mapping')
  try {
    const mapping = await getGlobalMapping()
    console.log('[500Mapper] preloaded', mapping.size, 'matches')
    return mapping
  } catch (e) {
    console.error('[500Mapper] preload failed:', e)
    return new Map()
  }
}

// ==================== 原有函数（保留） ====================

async function tryDirect(scheduleId, homeTeam, awayTeam) {
  try {
    const html = await fetchWithGbkFallback(`/500-proxy/fenxi/shuju-${scheduleId}.shtml`)
    if (!html) return null
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const titleEl = doc.querySelector('title')
    if (!titleEl) return null
    const titleText = titleEl.textContent || ''
    const vsMatch = titleText.match(/(.+?)\s*(?:vs|VS)\s*(.+?)(?:\(|$)/i)
    if (!vsMatch) return null
    const fiveHome = vsMatch[1].trim()
    const fiveAway = vsMatch[2].trim()
    const homeOk = teamNameMatch(homeTeam, fiveHome) || teamNameMatch(homeTeam, fiveAway)
    const awayOk = teamNameMatch(awayTeam, fiveAway) || teamNameMatch(awayTeam, fiveHome)
    if (homeOk && awayOk) {
      return String(scheduleId)
    }
  } catch (e) {}
  return null
}

async function tryLivePageWithScore(homeTeam, awayTeam, matchDate) {
  // 500.com竞彩使用?e=期号参数，优先使用?e=
  const urls = []
  if (matchDate) {
    urls.push(`/live500-proxy/?e=${matchDate}`)
    urls.push(`/live500-proxy/?date=${matchDate}`)
  }
  urls.push('/live500-proxy/')

  for (const url of urls) {
    try {
      console.log('[500Mapper] tryLivePage fetching:', url)
      const html = await fetchWithGbkFallback(url)
      if (!html) {
        console.warn('[500Mapper] tryLivePage: html is null')
        continue
      }
      console.log('[500Mapper] tryLivePage: html length', html.length)

      const parser = new DOMParser()
      const doc = parser.parseFromString(html, 'text/html')
      const rows = doc.querySelectorAll('tr[id^="a"]')
      console.log('[500Mapper] tryLivePage: found', rows.length, 'rows')

      if (rows.length === 0) continue

      const candidates = []

      rows.forEach((row, idx) => {
        const gy = row.getAttribute('gy') || ''
        const yy = row.getAttribute('yy') || ''
        const fid = row.getAttribute('fid') || row.id?.replace('a', '')
        if (!fid || !gy) return

        const gyParts = gy.split(',')
        const yyParts = yy.split(',')
        if (gyParts.length < 3 && yyParts.length < 3) return

        const fiveHomeGy = gyParts[1] || ''
        const fiveAwayGy = gyParts[2] || ''
        const fiveHomeYy = yyParts[1] || ''
        const fiveAwayYy = yyParts[2] || ''

        if (idx < 5) {
          console.log('[500Mapper] row', idx, { gy, yy, fid, fiveHomeGy, fiveAwayGy, fiveHomeYy, fiveAwayYy })
        }

        let score = 0
        const homeGyOk = teamNameMatch(homeTeam, fiveHomeGy)
        const homeYyOk = teamNameMatch(homeTeam, fiveHomeYy)
        const awayGyOk = teamNameMatch(awayTeam, fiveAwayGy)
        const awayYyOk = teamNameMatch(awayTeam, fiveAwayYy)

        if (idx < 5) {
          console.log('[500Mapper] row', idx, 'match:', { homeTeam, awayTeam, homeGyOk, homeYyOk, awayGyOk, awayYyOk })
        }

        if ((homeGyOk || homeYyOk) && (awayGyOk || awayYyOk)) {
          score = 2
          if (homeGyOk && awayGyOk) score = 3
        } else if ((homeGyOk || homeYyOk) && !(awayGyOk || awayYyOk)) {
          const homeInAway = teamNameMatch(homeTeam, fiveAwayGy) || teamNameMatch(homeTeam, fiveAwayYy)
          const awayInHome = teamNameMatch(awayTeam, fiveHomeGy) || teamNameMatch(awayTeam, fiveHomeYy)
          if (homeInAway && awayInHome) {
            score = 2
          } else {
            score = 1
          }
        } else if (!(homeGyOk || homeYyOk) && (awayGyOk || awayYyOk)) {
          const homeInAway = teamNameMatch(homeTeam, fiveAwayGy) || teamNameMatch(homeTeam, fiveAwayYy)
          const awayInHome = teamNameMatch(awayTeam, fiveHomeGy) || teamNameMatch(awayTeam, fiveHomeYy)
          if (homeInAway && awayInHome) {
            score = 2
          } else {
            score = 1
          }
        }

        if (score > 0) {
          candidates.push({ id: fid, score, fiveHomeGy, fiveAwayGy, fiveHomeYy, fiveAwayYy })
          console.log('[500Mapper] candidate found:', fid, 'score:', score, 'teams:', fiveHomeGy, 'vs', fiveAwayGy)
        }
      })

      candidates.sort((a, b) => b.score - a.score)
      console.log('[500Mapper] candidates:', candidates)
      if (candidates.length > 0 && candidates[0].score >= 2) {
        return candidates[0]
      }
    } catch (e) {
      console.error('[500Mapper] tryLivePage error:', e)
    }
  }
  return null
}

async function tryJczqPage(homeTeam, awayTeam) {
  try {
    const html = await fetchWithGbkFallback('/500-proxy/jczq/')
    if (!html) return null
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const links = doc.querySelectorAll('a.hd_cz_duizhen[href*="/fenxi/shuju-"]')
    for (const link of links) {
      const href = link.getAttribute('href') || ''
      const idMatch = href.match(/shuju-(\d+)/)
      if (!idMatch) continue
      const matchId = idMatch[1]
      const homeEl = link.querySelector('.l, em.l')
      const awayEl = link.querySelector('.r, em.r')
      if (!homeEl || !awayEl) continue
      const fiveHome = (homeEl.textContent || '').trim()
      const fiveAway = (awayEl.textContent || '').trim()
      const homeOk = teamNameMatch(homeTeam, fiveHome) || teamNameMatch(homeTeam, fiveAway)
      const awayOk = teamNameMatch(awayTeam, fiveAway) || teamNameMatch(awayTeam, fiveHome)
      if (homeOk && awayOk) {
        return matchId
      }
    }
  } catch (e) {}
  return null
}

async function tryOddsPage(homeTeam, awayTeam) {
  try {
    const html = await fetchWithGbkFallback('/500-proxy/')
    if (!html) return null
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const links = doc.querySelectorAll('a.hd_cz_duizhen[href*="/fenxi/shuju-"]')
    for (const link of links) {
      const href = link.getAttribute('href') || ''
      const idMatch = href.match(/shuju-(\d+)/)
      if (!idMatch) continue
      const matchId = idMatch[1]
      const homeEl = link.querySelector('.l, em.l')
      const awayEl = link.querySelector('.r, em.r')
      if (!homeEl || !awayEl) continue
      const fiveHome = (homeEl.textContent || '').trim()
      const fiveAway = (awayEl.textContent || '').trim()
      const homeOk = teamNameMatch(homeTeam, fiveHome) || teamNameMatch(homeTeam, fiveAway)
      const awayOk = teamNameMatch(awayTeam, fiveAway) || teamNameMatch(awayTeam, fiveHome)
      if (homeOk && awayOk) {
        return matchId
      }
    }
  } catch (e) {}
  return null
}

async function verifyMatchId(matchId, homeTeam, awayTeam) {
  if (!matchId) return null
  try {
    const html = await fetchWithGbkFallback(`/500-proxy/fenxi/shuju-${matchId}.shtml`)
    if (!html) {
      console.log('[500Mapper] verifyMatchId: html is null, verification failed')
      return null
    }
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const titleEl = doc.querySelector('title')
    if (!titleEl) {
      console.log('[500Mapper] verifyMatchId: no title element, verification failed')
      return null
    }
    const titleText = titleEl.textContent || ''
    console.log('[500Mapper] verifyMatchId: title =', titleText)
    const vsMatch = titleText.match(/(.+?)\s*(?:vs|VS)\s*(.+?)(?:\(|$)/i)
    if (!vsMatch) {
      console.log('[500Mapper] verifyMatchId: no vs match in title, verification failed')
      return null
    }
    const fiveHome = vsMatch[1].trim()
    const fiveAway = vsMatch[2].trim()
    console.log('[500Mapper] verifyMatchId: parsed teams =', fiveHome, 'vs', fiveAway)
    console.log('[500Mapper] verifyMatchId: checking homeTeam =', homeTeam, 'against fiveHome =', fiveHome, '=>', teamNameMatch(homeTeam, fiveHome))
    console.log('[500Mapper] verifyMatchId: checking homeTeam =', homeTeam, 'against fiveAway =', fiveAway, '=>', teamNameMatch(homeTeam, fiveAway))
    console.log('[500Mapper] verifyMatchId: checking awayTeam =', awayTeam, 'against fiveAway =', fiveAway, '=>', teamNameMatch(awayTeam, fiveAway))
    console.log('[500Mapper] verifyMatchId: checking awayTeam =', awayTeam, 'against fiveHome =', fiveHome, '=>', teamNameMatch(awayTeam, fiveHome))
    const homeOk = teamNameMatch(homeTeam, fiveHome) || teamNameMatch(homeTeam, fiveAway)
    const awayOk = teamNameMatch(awayTeam, fiveAway) || teamNameMatch(awayTeam, fiveHome)
    console.log('[500Mapper] verifyMatchId: homeOk =', homeOk, ', awayOk =', awayOk)
    if (homeOk && awayOk) {
      return matchId
    }
    return null
  } catch (e) {
    console.error('[500Mapper] verifyMatchId error:', e)
    return matchId
  }
}

// ==================== 修改：findFiveMatchId 优先使用 match_id ====================

async function findFiveMatchId(matchInfo) {
  if (!matchInfo) {
    console.warn('[500Mapper] matchInfo is null')
    return null
  }

  const { match_id, schedule_id, home_team, away_team, home_team_full, away_team_full, start_time } = matchInfo

  // 优先使用 match_id 进行精确匹配
  if (match_id && /周[一二三四五六日]\d{3}/.test(match_id)) {
    console.log('[500Mapper] trying match_id mapping:', match_id)
    const fid = await findFiveMatchIdByMatchId(matchInfo)
    if (fid) {
      console.log('[500Mapper] match_id mapping success:', fid)
      return fid
    }
    console.log('[500Mapper] match_id mapping failed, falling back to name matching')
  }

  // 回退到球队名称匹配（旧逻辑）
  const homeTeam = home_team_full || home_team
  const awayTeam = away_team_full || away_team
  return await findFiveMatchIdInternal(homeTeam, awayTeam, schedule_id, start_time)
}

async function findFiveMatchIdInternal(homeTeam, awayTeam, schedule_id, start_time) {
  const matchDate = extractMatchDate(start_time)
  const cacheKey = buildCacheKey(homeTeam, awayTeam, matchDate)

  if (idCache.has(cacheKey)) {
    const cached = idCache.get(cacheKey)
    if (cached && (Date.now() - cached.timestamp) < CACHE_TTL) {
      console.log('[500Mapper] cache hit:', cached.fiveMatchId)
      return cached.fiveMatchId
    }
    idCache.delete(cacheKey)
  }

  let fiveMatchId = null
  let bestScore = 0

  // 使用全局映射中的球队名称进行匹配
  const globalMap = await getGlobalMapping()
  if (globalMap && globalMap.size > 0) {
    // 遍历全局映射，通过fid获取球队名称进行匹配
    // 但全局映射只有match_id->fid，没有球队名称
    // 所以还是需要用tryLivePageWithScore
  }

  // 500.com期号可能不是比赛日期，尝试多个日期
  const datesToTry = new Set([matchDate])
  try {
    const d = new Date(matchDate)
    d.setDate(d.getDate() - 1)
    datesToTry.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
    d.setDate(d.getDate() - 1)
    datesToTry.add(`${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`)
  } catch (e) {}

  // 也尝试不带日期参数（获取当前默认期号）
  datesToTry.add('')

  for (const dateStr of datesToTry) {
    console.log('[500Mapper] trying tryLivePage with date:', dateStr || '(default)')
    const liveResult = await tryLivePageWithScore(homeTeam, awayTeam, dateStr)
    console.log('[500Mapper] tryLivePage result:', liveResult)
    if (liveResult && liveResult.score > bestScore) {
      fiveMatchId = liveResult.id
      bestScore = liveResult.score
      if (bestScore >= 3) break
    }
  }

  if (fiveMatchId) {
    console.log('[500Mapper] verifying matchId:', fiveMatchId, 'with teams:', homeTeam, 'vs', awayTeam)
    const verified = await verifyMatchId(fiveMatchId, homeTeam, awayTeam)
    console.log('[500Mapper] verify result:', verified)
    if (!verified && bestScore >= 3) {
      console.log('[500Mapper] verification failed but score is high, accepting matchId:', fiveMatchId)
    } else if (!verified) {
      fiveMatchId = null
    }
  }

  if (!fiveMatchId) {
    console.log('[500Mapper] trying tryJczqPage...')
    fiveMatchId = await tryJczqPage(homeTeam, awayTeam)
    console.log('[500Mapper] tryJczqPage result:', fiveMatchId)
  }

  if (!fiveMatchId) {
    console.log('[500Mapper] trying tryOddsPage...')
    fiveMatchId = await tryOddsPage(homeTeam, awayTeam)
    console.log('[500Mapper] tryOddsPage result:', fiveMatchId)
  }

  if (!fiveMatchId && schedule_id) {
    console.log('[500Mapper] trying tryDirect...')
    fiveMatchId = await tryDirect(schedule_id, homeTeam, awayTeam)
    console.log('[500Mapper] tryDirect result:', fiveMatchId)
  }

  if (fiveMatchId) {
    idCache.set(cacheKey, { fiveMatchId, timestamp: Date.now() })
    persistCache()
    console.log('[500Mapper] final result:', fiveMatchId)
  } else {
    console.warn('[500Mapper] no match found for:', homeTeam, 'vs', awayTeam)
  }

  return fiveMatchId
}

loadCacheFromStorage()
cleanCache()

// 清除所有旧的损坏缓存（Map序列化问题导致的空数据）
// 使用新的版本号来区分缓存格式
const CACHE_VERSION = 'v9'
const CACHE_VERSION_KEY = 'five_mapper_cache_version'
try {
  const currentVersion = localStorage.getItem(CACHE_VERSION_KEY)
  if (currentVersion !== CACHE_VERSION) {
    console.log('[500Mapper] clearing old corrupted caches, upgrading to', CACHE_VERSION)
    // 清除所有 five_mapping_ 缓存
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i)
      if (key && (key.startsWith('five_mapping_') || key.startsWith('titan_matches_') || key.startsWith('five_data_'))) {
        localStorage.removeItem(key)
      }
    }
    localStorage.setItem(CACHE_VERSION_KEY, CACHE_VERSION)
  }
} catch (e) {}

// ==================== 导出新增功能 ====================

export {
  findFiveMatchId,
  preloadFiveMapping,
  SmartCache,
  BackgroundRefresher,
  refresher,
  REFRESH_INTERVAL,
  CACHE_STRATEGY,
  titanCache,
}
