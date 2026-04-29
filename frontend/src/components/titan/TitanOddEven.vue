<template>
  <div class="odd-even" v-if="data">
    <div class="oe-teams">
      <div class="oe-team" v-for="team in teams" :key="team.name">
        <h4>{{ team.name }}</h4>
        <table class="oe-table">
          <thead><tr><th></th><th>大</th><th>小</th><th>走</th><th>單</th><th>雙</th></tr></thead>
          <tbody>
            <tr v-for="row in team.rows" :key="row.type">
              <td class="row-type">{{ row.type }}</td>
              <td>{{ row.big }}<span class="pct" v-if="row.big_pct">({{ row.big_pct }})</span></td>
              <td>{{ row.small }}<span class="pct" v-if="row.small_pct">({{ row.small_pct }})</span></td>
              <td>{{ row.walk }}<span class="pct" v-if="row.walk_pct">({{ row.walk_pct }})</span></td>
              <td>{{ row.odd }}<span class="pct" v-if="row.odd_pct">({{ row.odd_pct }})</span></td>
              <td>{{ row.even }}<span class="pct" v-if="row.even_pct">({{ row.even_pct }})</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <p v-if="!teams?.length" class="empty">暂无单双数据</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })
const teams = computed(() => props.data?.odd_even || [])
</script>

<style scoped>
.oe-teams { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .oe-teams { grid-template-columns:1fr; } }
.oe-team h4 { font-size:14px; margin-bottom:6px; }
.oe-table { width:100%; border-collapse:collapse; font-size:12px;
  th,td { border:1px solid #ebeef5; padding:3px 6px; text-align:center; }
  th { background:#fafafa; }
  .row-type { font-weight:600; }
}
.pct { color:#999; font-size:10px; }
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
