<template>
  <div class="macau-data" v-loading="loading">
    <template v-if="parsedData">
      <div v-for="section in visibleSections" :key="section.key" class="section-block">
        <h3 class="section-title">{{ section.label }}</h3>
        <div class="section-content">
          <div v-if="section.key === 'instant_index'">
            <el-table :data="parsedData.instantIndex" size="small" stripe v-if="parsedData.instantIndex?.length" max-height="300">
              <el-table-column prop="league" label="联赛" width="120" />
              <el-table-column prop="home" label="主队" width="100" />
              <el-table-column prop="score" label="比分" width="70" align="center" />
              <el-table-column prop="away" label="客队" width="100" />
              <el-table-column prop="handicap" label="让球" width="70" align="center" />
              <el-table-column prop="home_odds" label="主胜" width="60" align="center" />
              <el-table-column prop="away_odds" label="客胜" width="60" align="center" />
            </el-table>
            <p v-else class="placeholder">暂无即时指数数据</p>
          </div>

          <div v-else-if="section.key === 'handicap'">
            <el-table :data="parsedData.handicapData" size="small" stripe v-if="parsedData.handicapData?.length" max-height="300">
              <el-table-column prop="company" label="公司" width="100" fixed />
              <el-table-column label="初盘" align="center">
                <el-table-column prop="home_init" label="主" width="55" />
                <el-table-column prop="hcp_init" label="盘口" width="60" />
                <el-table-column prop="away_init" label="客" width="55" />
              </el-table-column>
              <el-table-column label="即时" align="center">
                <el-table-column prop="home_curr" label="主" width="55" />
                <el-table-column prop="hcp_curr" label="盘口" width="60" />
                <el-table-column prop="away_curr" label="客" width="55" />
              </el-table-column>
            </el-table>
            <p v-else class="placeholder">暂无让球盘口数据</p>
          </div>

          <div v-else-if="section.key === 'overunder'">
            <el-table :data="parsedData.overunderData" size="small" stripe v-if="parsedData.overunderData?.length" max-height="300">
              <el-table-column prop="company" label="公司" width="100" fixed />
              <el-table-column label="初盘" align="center">
                <el-table-column prop="big_init" label="大" width="55" />
                <el-table-column prop="line_init" label="盘口" width="60" />
                <el-table-column prop="small_init" label="小" width="55" />
              </el-table-column>
              <el-table-column label="即时" align="center">
                <el-table-column prop="big_curr" label="大" width="55" />
                <el-table-column prop="line_curr" label="盘口" width="60" />
                <el-table-column prop="small_curr" label="小" width="55" />
              </el-table-column>
            </el-table>
            <p v-else class="placeholder">暂无大小球数据</p>
          </div>

          <div v-else-if="section.key === 'league_filter'">
            <el-table :data="parsedData.leagueList" size="small" stripe v-if="parsedData.leagueList?.length" max-height="200">
              <el-table-column prop="name" label="联赛名称" />
              <el-table-column prop="count" label="场次" width="70" align="center" />
            </el-table>
            <p v-else class="placeholder">暂无联赛数据</p>
          </div>

          <div v-else-if="section.key === 'match_detail'">
            <p v-if="!parsedData.matchDetail" class="placeholder">请选择比赛查看详情</p>
            <div v-else v-html="parsedData.matchDetail" class="detail-html"></div>
          </div>
        </div>
      </div>
    </template>
    <el-empty v-if="!parsedData && !loading" description="暂无澳门数据" :image-size="80" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSectionsStore } from '../../stores/sections'

const sectionsStore = useSectionsStore()
const loading = ref(false)
const parsedData = ref(null)

const visibleSections = computed(() => sectionsStore.getVisibleSections('macau'))

async function fetchData() {
  loading.value = true
  try {
    const resp = await fetch('/macau-proxy/sc/soccer/odds_in.html')
    const html = await resp.text()
    if (html) {
      parsedData.value = parseMacauData(html)
    }
  } catch (e) {
    console.error('获取澳门数据失败:', e)
  } finally {
    loading.value = false
  }
}

function parseMacauData(html) {
  if (!html) return null
  const data = { instantIndex: [], handicapData: [], overunderData: [], leagueList: [], matchDetail: null }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')

    doc.querySelectorAll('table').forEach(table => {
      const text = table.textContent
      const rows = table.querySelectorAll('tr')

      if (text.includes('让球') || text.includes('Handicap')) {
        rows.forEach((row, i) => {
          if (i === 0) return
          const cs = row.querySelectorAll('td')
          if (cs.length >= 6) {
            data.handicapData.push({
              company: cs[0]?.textContent?.trim() || '',
              home_init: cs[1]?.textContent?.trim(), hcp_init: cs[2]?.textContent?.trim(), away_init: cs[3]?.textContent?.trim(),
              home_curr: cs[4]?.textContent?.trim(), hcp_curr: cs[5]?.textContent?.trim(), away_curr: cs[6]?.textContent?.trim(),
            })
          }
        })
      }

      if (text.includes('大小') || text.includes('Over/Under')) {
        rows.forEach((row, i) => {
          if (i === 0) return
          const cs = row.querySelectorAll('td')
          if (cs.length >= 6) {
            data.overunderData.push({
              company: cs[0]?.textContent?.trim() || '',
              big_init: cs[1]?.textContent?.trim(), line_init: cs[2]?.textContent?.trim(), small_init: cs[3]?.textContent?.trim(),
              big_curr: cs[4]?.textContent?.trim(), line_curr: cs[5]?.textContent?.trim(), small_curr: cs[6]?.textContent?.trim(),
            })
          }
        })
      }
    })

    const leagueLinks = doc.querySelectorAll('a[href*="league"]')
    const leagueMap = {}
    leagueLinks.forEach(a => {
      const name = a.textContent.trim()
      if (name && !leagueMap[name]) {
        leagueMap[name] = true
        data.leagueList.push({ name, count: 0 })
      }
    })
  } catch (e) {
    console.warn('解析澳门数据失败:', e)
  }

  return data
}

onMounted(fetchData)
</script>

<style scoped>
.section-block { margin-bottom:15px; border:1px solid #eee; border-radius:6px; overflow:hidden; }
.section-title { background:#f5f7fa; padding:8px 12px; font-size:13px; margin:0; }
.section-content { padding:12px; }
.placeholder { color:#999; text-align:center; padding:15px; font-size:13px; }
.detail-html { font-size:13px; line-height:1.6; }
</style>
