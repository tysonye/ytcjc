<template>
  <div class="goal-timing" v-if="data">
    <div class="timing-teams">
      <div class="timing-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <table class="timing-table">
          <thead>
            <tr><th></th><th>1-10</th><th>11-20</th><th>21-30</th><th>31-40</th><th>41-45</th><th>46-50</th><th>51-60</th><th>61-70</th><th>71-80</th><th>81-90+</th></tr>
          </thead>
          <tbody>
            <tr v-for="row in team.rows" :key="row.type">
              <td class="row-type">{{ row.type }}</td>
              <td v-for="(v,i) in row.slots" :key="i" :class="slotClass(v)">{{ v }}</td>
            </tr>
          </tbody>
        </table>
        <div class="first-goal" v-if="team.firstGoalRows?.length">
          <span class="fg-label">第壹個進球時間統計</span>
          <table class="timing-table fg">
            <thead>
              <tr><th></th><th>1-10</th><th>11-20</th><th>21-30</th><th>31-40</th><th>41-45</th><th>46-50</th><th>51-60</th><th>61-70</th><th>71-80</th><th>81-90+</th></tr>
            </thead>
            <tbody>
              <tr v-for="row in team.firstGoalRows" :key="row.type">
                <td class="row-type">{{ row.type }}</td>
                <td v-for="(v,i) in row.slots" :key="i" :class="slotClass(v)">{{ v }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无进球时间数据</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })
const teams = computed(() => props.data?.goal_timing || [])

function slotClass(v) {
  const n = parseInt(v)
  if (isNaN(n)) return ''
  if (n >= 6) return 'hot'
  if (n >= 3) return 'warm'
  return ''
}
</script>

<style scoped>
.timing-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .timing-teams { grid-template-columns:1fr; } }
.timing-team h4 { font-size:14px; margin-bottom:6px; }
.timing-table { width:100%; border-collapse:collapse; font-size:11px;
  th,td { border:1px solid #ebeef5; padding:2px 4px; text-align:center; }
  th { background:#fafafa; font-weight:600; }
  .row-type { font-weight:600; }
  .hot { background:#fef0f0; color:#f56c6c; font-weight:bold; }
  .warm { background:#fdf6ec; color:#e6a23c; }
}
.first-goal { margin-top:10px; }
.fg-label { font-size:12px; color:#0066cc; font-weight:bold; display:block; margin-bottom:4px; }
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
