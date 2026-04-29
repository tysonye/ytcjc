<template>
  <div class="goal-half-dist" v-if="data">
    <div class="dist-teams">
      <div class="dist-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <table class="dist-table">
          <thead><tr><th></th><th>0</th><th>1</th><th>2</th><th>3</th><th>4+</th><th>上半場</th><th>下半場</th></tr></thead>
          <tbody>
            <tr v-for="row in team.rows" :key="row.type">
              <td class="row-type">{{ row.type }}</td>
              <td v-for="k in ['g0','g1','g2','g3','g4plus']" :key="k">{{ row[k] }}</td>
              <td>{{ row.first_half }}</td>
              <td>{{ row.second_half }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无进球分布数据</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })
const teams = computed(() => props.data?.goal_half_dist || [])
</script>

<style scoped>
.dist-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .dist-teams { grid-template-columns:1fr; } }
.dist-team h4 { font-size:14px; margin-bottom:6px; }
.dist-table { width:100%; border-collapse:collapse; font-size:12px;
  th,td { border:1px solid #ebeef5; padding:3px 6px; text-align:center; }
  th { background:#fafafa; }
  .row-type { font-weight:600; }
}
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
