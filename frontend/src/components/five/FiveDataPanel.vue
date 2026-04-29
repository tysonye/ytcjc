<template>
  <div class="five-data" v-loading="loading">
    <template v-if="parsedData">
      <div v-for="section in visibleSections" :key="section.key" class="section-block">
        <h3 class="section-title">{{ section.label }}</h3>
        <div class="section-content">
          <div v-if="section.key === 'basic_info'">
            <el-descriptions :column="2" border size="small" v-if="parsedData.basicInfo">
              <el-descriptions-item label="主队">{{ parsedData.basicInfo.homeTeam }}</el-descriptions-item>
              <el-descriptions-item label="客队">{{ parsedData.basicInfo.awayTeam }}</el-descriptions-item>
              <el-descriptions-item label="联赛">{{ parsedData.basicInfo.league }}</el-descriptions-item>
              <el-descriptions-item label="时间">{{ parsedData.basicInfo.matchTime }}</el-descriptions-item>
              <el-descriptions-item label="天气">{{ parsedData.basicInfo.weather || '-' }}</el-descriptions-item>
              <el-descriptions-item label="场地">{{ parsedData.basicInfo.venue || '-' }}</el-descriptions-item>
            </el-descriptions>
            <p v-else class="placeholder">暂无基本信息</p>
          </div>

          <div v-else-if="section.key === 'yapan'">
            <el-table :data="parsedData.yapanData" size="small" stripe v-if="parsedData.yapanData?.length" max-height="300">
              <el-table-column prop="company" label="公司" width="100" fixed />
              <el-table-column label="初盘" align="center">
                <el-table-column prop="home_init" label="主" width="55" />
                <el-table-column prop="handicap_init" label="盘口" width="60" />
                <el-table-column prop="away_init" label="客" width="55" />
              </el-table-column>
              <el-table-column label="即时" align="center">
                <el-table-column prop="home_curr" label="主" width="55" />
                <el-table-column prop="handicap_curr" label="盘口" width="60" />
                <el-table-column prop="away_curr" label="客" width="55" />
              </el-table-column>
            </el-table>
            <p v-else class="placeholder">暂无亚盘数据</p>
          </div>

          <div v-else-if="section.key === 'ouzhi'">
            <el-table :data="parsedData.ouzhiData" size="small" stripe v-if="parsedData.ouzhiData?.length" max-height="300">
              <el-table-column prop="company" label="公司" width="100" fixed />
              <el-table-column label="初盘" align="center">
                <el-table-column prop="home_init" label="胜" width="55" />
                <el-table-column prop="draw_init" label="平" width="55" />
                <el-table-column prop="away_init" label="负" width="55" />
              </el-table-column>
              <el-table-column label="即时" align="center">
                <el-table-column prop="home_curr" label="胜" width="55" />
                <el-table-column prop="draw_curr" label="平" width="55" />
                <el-table-column prop="away_curr" label="负" width="55" />
              </el-table-column>
            </el-table>
            <p v-else class="placeholder">暂无欧指数据</p>
          </div>

          <div v-else-if="section.key === 'daxiao'">
            <el-table :data="parsedData.daxiaoData" size="small" stripe v-if="parsedData.daxiaoData?.length" max-height="300">
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

          <div v-else-if="section.key === 'jiben'">
            <div v-if="parsedData.jibenData" class="jiben-info">
              <el-row :gutter="15">
                <el-col :span="12" v-if="parsedData.jibenData.homeForm">
                  <h4>主队近况</h4>
                  <p>{{ parsedData.jibenData.homeForm }}</p>
                  <p>盘路: {{ parsedData.jibenData.homePan }}</p>
                </el-col>
                <el-col :span="12" v-if="parsedData.jibenData.awayForm">
                  <h4>客队近况</h4>
                  <p>{{ parsedData.jibenData.awayForm }}</p>
                  <p>盘路: {{ parsedData.jibenData.awayPan }}</p>
                </el-col>
              </el-row>
            </div>
            <p v-else class="placeholder">暂无基本面数据</p>
          </div>

          <div v-else-if="section.key === 'jiaofeng'">
            <el-table :data="parsedData.h2hData" size="small" stripe v-if="parsedData.h2hData?.length" max-height="250">
              <el-table-column prop="date" label="日期" width="90" />
              <el-table-column prop="league" label="赛事" width="100" />
              <el-table-column prop="home" label="主队" width="90" />
              <el-table-column prop="score" label="比分" width="60" align="center" />
              <el-table-column prop="away" label="客队" width="90" />
            </el-table>
            <p v-else class="placeholder">暂无交锋数据</p>
          </div>
        </div>
      </div>
    </template>
    <el-empty v-if="!parsedData && !loading" description="暂无500数据" :image-size="80" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useSectionsStore } from '../../stores/sections'

const props = defineProps({ matchUniqueId: { type: [String, Number], default: '' } })
const sectionsStore = useSectionsStore()
const loading = ref(false)
const parsedData = ref(null)

const visibleSections = computed(() => sectionsStore.getVisibleSections('five'))

async function fetchData() {
  if (!props.matchUniqueId) return
  loading.value = true
  try {
    const resp = await fetch(`/500-proxy/fenxi/shuju-${props.matchUniqueId}.shtml`)
    const html = await resp.text()
    if (html) {
      parsedData.value = parseFiveData(html)
    }
  } catch (e) {
    console.error('获取500数据失败:', e)
  } finally {
    loading.value = false
  }
}

function parseFiveData(html) {
  if (!html) return null
  const data = { basicInfo: null, yapanData: [], ouzhiData: [], daxiaoData: [], jibenData: null, h2hData: [] }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')

    const titleEl = doc.querySelector('title')
    if (titleEl) {
      const titleText = titleEl.textContent
      const vsMatch = titleText.match(/(.+?)\s*(?:vs|VS)\s*(.+)/)
      if (vsMatch) {
        data.basicInfo = { homeTeam: vsMatch[1].trim(), awayTeam: vsMatch[2].trim(), league: '', matchTime: '', weather: '', venue: '' }
      }
    }

    doc.querySelectorAll('table').forEach(table => {
      const text = table.textContent
      const rows = table.querySelectorAll('tr')
      if (rows.length < 2) return

      const headerText = rows[0]?.textContent || ''

      if (headerText.includes('亚盘') || headerText.includes('让球')) {
        rows.forEach((row, i) => {
          if (i === 0) return
          const cs = row.querySelectorAll('td')
          if (cs.length >= 6) {
            data.yapanData.push({
              company: cs[0]?.textContent?.trim() || '',
              home_init: cs[1]?.textContent?.trim(), handicap_init: cs[2]?.textContent?.trim(), away_init: cs[3]?.textContent?.trim(),
              home_curr: cs[4]?.textContent?.trim(), handicap_curr: cs[5]?.textContent?.trim(), away_curr: cs[6]?.textContent?.trim(),
            })
          }
        })
      }

      if (headerText.includes('欧指') || headerText.includes('胜平负')) {
        rows.forEach((row, i) => {
          if (i === 0) return
          const cs = row.querySelectorAll('td')
          if (cs.length >= 6) {
            data.ouzhiData.push({
              company: cs[0]?.textContent?.trim() || '',
              home_init: cs[1]?.textContent?.trim(), draw_init: cs[2]?.textContent?.trim(), away_init: cs[3]?.textContent?.trim(),
              home_curr: cs[4]?.textContent?.trim(), draw_curr: cs[5]?.textContent?.trim(), away_curr: cs[6]?.textContent?.trim(),
            })
          }
        })
      }

      if (headerText.includes('大小') || headerText.includes('进球')) {
        rows.forEach((row, i) => {
          if (i === 0) return
          const cs = row.querySelectorAll('td')
          if (cs.length >= 6) {
            data.daxiaoData.push({
              company: cs[0]?.textContent?.trim() || '',
              big_init: cs[1]?.textContent?.trim(), line_init: cs[2]?.textContent?.trim(), small_init: cs[3]?.textContent?.trim(),
              big_curr: cs[4]?.textContent?.trim(), line_curr: cs[5]?.textContent?.trim(), small_curr: cs[6]?.textContent?.trim(),
            })
          }
        })
      }
    })

    const formMatch = html.match(/近况走势\s*[-–]\s*([WDL]+)/g)
    const panMatch = html.match(/盘路赢输\s*[-–]\s*([WDL\d/]+)/g)
    if (formMatch?.length >= 2 || panMatch?.length >= 2) {
      data.jibenData = {
        homeForm: formMatch?.[0]?.replace(/近况走势\s*[-–]\s*/, '') || '',
        awayForm: formMatch?.[1]?.replace(/近况走势\s*[-–]\s*/, '') || '',
        homePan: panMatch?.[0]?.replace(/盘路赢输\s*[-–]\s*/, '') || '',
        awayPan: panMatch?.[1]?.replace(/盘路赢输\s*[-–]\s*/, '') || '',
      }
    }
  } catch (e) {
    console.warn('解析500数据失败:', e)
  }

  return data
}

onMounted(fetchData)
watch(() => props.matchUniqueId, fetchData)
</script>

<style scoped>
.section-block { margin-bottom:15px; border:1px solid #eee; border-radius:6px; overflow:hidden; }
.section-title { background:#f5f7fa; padding:8px 12px; font-size:13px; margin:0; }
.section-content { padding:12px; }
.placeholder { color:#999; text-align:center; padding:15px; font-size:13px; }
.jiben-info h4 { font-size:13px; margin:4px 0; }
.jiben-info p { font-size:12px; color:#666; margin:2px 0; }
</style>
