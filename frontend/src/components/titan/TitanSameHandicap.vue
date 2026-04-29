<template>
  <div class="same-handicap" v-if="data">
    <div class="same-teams">
      <div class="same-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <div class="handicap-info">初盤: {{ team.handicap_label }}</div>
        <table class="same-table">
          <thead><tr><th></th><th>贏</th><th>走</th><th>輸</th><th>贏盤率</th></tr></thead>
          <tbody>
            <tr v-for="row in team.rows" :key="row.type">
              <td class="row-type">{{ row.type }}</td>
              <td class="text-green">{{ row.won }}</td>
              <td>{{ row.walk }}</td>
              <td class="text-red">{{ row.lost }}</td>
              <td>{{ row.win_rate }}</td>
            </tr>
          </tbody>
        </table>
        <div class="recent6" v-if="team.recent6">
          <span>近6場盤路: </span>
          <span v-for="(r,i) in team.recent6" :key="i" class="dot" :class="r">{{ r === 'won' ? '贏' : r === 'lost' ? '輸' : '走' }}</span>
        </div>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无相同盘路数据</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })
const teams = computed(() => props.data?.same_handicap || [])
</script>

<style scoped>
.same-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .same-teams { grid-template-columns:1fr; } }
.same-team h4 { font-size:14px; margin-bottom:4px; }
.handicap-info { font-size:12px; color:#0066cc; margin-bottom:6px; font-weight:bold; }
.same-table { width:100%; border-collapse:collapse; font-size:12px;
  th,td { border:1px solid #ebeef5; padding:3px 6px; text-align:center; }
  th { background:#fafafa; }
  .row-type { font-weight:600; }
}
.text-green { color:#67c23a; }
.text-red { color:#f56c6c; }
.recent6 { margin-top:6px; font-size:12px; }
.dot { display:inline-block; padding:1px 5px; margin:0 2px; border-radius:2px; font-size:11px; font-weight:bold;
  &.won { background:#f0f9eb; color:#67c23a; }
  &.lost { background:#fef0f0; color:#f56c6c; }
  &.walk { background:#f4f4f5; color:#909399; }
}
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
