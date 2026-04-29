<template>
  <div class="handicap-trend" v-if="data">
    <div class="trend-teams">
      <div class="trend-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <el-tabs v-model="team.activeTab" size="small">
          <el-tab-pane label="全場" name="full">
            <div class="trend-section">
              <span class="section-label">亚讓盤</span>
              <table class="trend-table">
                <thead><tr><th></th><th>賽</th><th>贏盤</th><th>走水</th><th>輸盤</th><th>贏盤率</th><th></th><th>大球</th><th>大球率</th><th>小球</th><th>小球率</th></tr></thead>
                <tbody>
                  <tr v-for="row in team.fullRows" :key="row.type">
                    <td class="row-type">{{ row.type }}</td>
                    <td>{{ row.played }}</td>
                    <td class="text-green">{{ row.won }}</td>
                    <td>{{ row.walk }}</td>
                    <td class="text-red">{{ row.lost }}</td>
                    <td>{{ row.win_rate }}</td>
                    <td></td>
                    <td>{{ row.big }}</td>
                    <td>{{ row.big_rate }}</td>
                    <td>{{ row.small }}</td>
                    <td>{{ row.small_rate }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </el-tab-pane>
          <el-tab-pane label="半場" name="half">
            <div class="trend-section">
              <span class="section-label">亚讓盤</span>
              <table class="trend-table">
                <thead><tr><th></th><th>賽</th><th>贏盤</th><th>走水</th><th>輸盤</th><th>贏盤率</th><th></th><th>大球</th><th>大球率</th><th>小球</th><th>小球率</th></tr></thead>
                <tbody>
                  <tr v-for="row in team.halfRows" :key="row.type">
                    <td class="row-type">{{ row.type }}</td>
                    <td>{{ row.played }}</td>
                    <td class="text-green">{{ row.won }}</td>
                    <td>{{ row.walk }}</td>
                    <td class="text-red">{{ row.lost }}</td>
                    <td>{{ row.win_rate }}</td>
                    <td></td>
                    <td>{{ row.big }}</td>
                    <td>{{ row.big_rate }}</td>
                    <td>{{ row.small }}</td>
                    <td>{{ row.small_rate }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </el-tab-pane>
        </el-tabs>
        <div class="recent6" v-if="team.recent6">
          <span class="recent-label">近6場: </span>
          <span v-for="(r,i) in team.recent6" :key="i" class="recent-dot" :class="r">{{ r === 'won' ? '贏' : r === 'lost' ? '輸' : '走' }}</span>
        </div>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无盘路数据</p>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })

const teams = computed(() => {
  const raw = props.data?.handicap_trend
  if (!raw) return []
  return raw.map(t => ({ ...t, activeTab: 'full' }))
})
</script>

<style scoped>
.trend-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .trend-teams { grid-template-columns:1fr; } }
.trend-team h4 { font-size:14px; margin-bottom:6px; color:#303133; }
.trend-section { margin-bottom:10px; }
.section-label { font-size:12px; font-weight:bold; color:#0066cc; display:inline-block; margin-bottom:4px; }
.trend-table { width:100%; border-collapse:collapse; font-size:11px;
  th,td { border:1px solid #ebeef5; padding:3px 4px; text-align:center; }
  th { background:#fafafa; font-weight:600; }
  .row-type { font-weight:600; color:#303133; }
}
.text-green { color:#67c23a; }
.text-red { color:#f56c6c; }
.recent6 { margin-top:6px; font-size:12px; }
.recent-label { color:#666; }
.recent-dot { display:inline-block; padding:1px 5px; margin:0 2px; border-radius:2px; font-size:11px; font-weight:bold;
  &.won { background:#f0f9eb; color:#67c23a; }
  &.lost { background:#fef0f0; color:#f56c6c; }
  &.walk { background:#f4f4f5; color:#909399; }
}
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
