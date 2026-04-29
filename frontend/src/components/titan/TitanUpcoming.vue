<template>
  <div class="upcoming" v-if="data">
    <div class="upcoming-teams">
      <div class="upcoming-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <table class="upcoming-table">
          <thead><tr><th>時間</th><th>賽事</th><th>對陣</th><th>相隔</th></tr></thead>
          <tbody>
            <tr v-for="m in team.matches" :key="m.date + m.opponent">
              <td>{{ m.date }}</td>
              <td>{{ m.league }}</td>
              <td>{{ m.opponent }}</td>
              <td>{{ m.days_later }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无未来赛程</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })
const teams = computed(() => props.data?.upcoming || [])
</script>

<style scoped>
.upcoming-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .upcoming-teams { grid-template-columns:1fr; } }
.upcoming-team h4 { font-size:14px; margin-bottom:6px; }
.upcoming-table { width:100%; border-collapse:collapse; font-size:12px;
  th,td { border:1px solid #ebeef5; padding:4px 6px; text-align:center; }
  th { background:#fafafa; }
}
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
