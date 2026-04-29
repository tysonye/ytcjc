<template>
  <div class="lineup-panel" v-if="data">
    <div class="lineup-teams">
      <div class="lineup-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <table class="lineup-table">
          <thead><tr><th>號碼</th><th>球員</th><th>位置</th><th>首發</th><th>評分</th></tr></thead>
          <tbody>
            <tr v-for="p in team.players" :key="p.number + p.name" :class="{ starter: p.starter }">
              <td>{{ p.number }}</td>
              <td class="player-name">{{ p.name }}</td>
              <td>{{ p.position }}</td>
              <td>{{ p.starter ? '★' : '' }}</td>
              <td :class="scoreClass(p.rating)">{{ p.rating }}</td>
            </tr>
          </tbody>
        </table>
        <div class="avg-score" v-if="team.avgRating">
          平均評分: <span :class="scoreClass(team.avgRating)">{{ team.avgRating }}</span>
        </div>
        <div class="score-trend" v-if="team.recentScores?.length" ref="chartRefs">
          <span class="trend-label">近10場評分走勢</span>
        </div>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无阵容数据</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })

const teams = computed(() => props.data?.lineup_data || [])

function scoreClass(r) {
  const v = parseFloat(r)
  if (isNaN(v)) return ''
  if (v >= 7.5) return 'score-high'
  if (v >= 6.5) return 'score-mid'
  return 'score-low'
}
</script>

<style scoped>
.lineup-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .lineup-teams { grid-template-columns:1fr; } }
.lineup-team h4 { font-size:14px; margin-bottom:6px; color:#303133; }
.lineup-table { width:100%; border-collapse:collapse; font-size:12px;
  th,td { border:1px solid #ebeef5; padding:3px 5px; text-align:center; }
  th { background:#fafafa; font-weight:600; }
  .player-name { text-align:left; max-width:120px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  tr.starter { background:#f0f9eb; }
}
.avg-score { margin-top:6px; font-size:12px; color:#666; }
.score-trend { margin-top:8px; }
.trend-label { font-size:11px; color:#999; }
.score-high { color:#67c23a; font-weight:bold; }
.score-mid { color:#e6a23c; }
.score-low { color:#f56c6c; }
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
