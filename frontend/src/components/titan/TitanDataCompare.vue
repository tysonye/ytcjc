<template>
  <div class="data-compare" v-if="data">
    <div class="compare-header">
      <span>數據對比</span>
      <el-select v-model="compareScope" size="small" style="width:100px;margin-left:10px">
        <el-option label="全部" value="all" />
        <el-option label="同主客" value="homeaway" />
      </el-select>
      <el-input-number v-model="compareN" :min="3" :max="20" size="small" style="width:90px;margin-left:8px" />
      <span style="font-size:12px;color:#999;margin-left:4px">場</span>
    </div>
    <table class="compare-table" v-if="currentData">
      <thead>
        <tr>
          <th></th>
          <th colspan="2">勝平負</th>
          <th>進球</th>
          <th>失球</th>
          <th>凈勝球</th>
          <th>場均進球</th>
          <th>場均角球</th>
          <th>場均黃牌</th>
          <th>進球</th>
          <th>失球</th>
          <th>凈勝球</th>
          <th>場均進球</th>
          <th colspan="3">勝平負</th>
        </tr>
        <tr>
          <th>球隊</th>
          <th>勝</th><th>負</th>
          <th></th><th></th><th></th><th></th><th></th><th></th>
          <th></th><th></th><th></th><th></th>
          <th>勝</th><th>平</th><th>負</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="team in currentData" :key="team.name">
          <td class="team-name">{{ team.name }}</td>
          <td>{{ team.win_pct }}</td>
          <td>{{ team.lose_pct }}</td>
          <td>{{ team.gf }}</td>
          <td>{{ team.ga }}</td>
          <td :class="{'text-green': team.gd > 0, 'text-red': team.gd < 0}">{{ team.gd > 0 ? '+' : '' }}{{ team.gd }}</td>
          <td>{{ team.avg_gf }}</td>
          <td>{{ team.avg_corner }}</td>
          <td>{{ team.avg_yellow }}</td>
          <td>{{ team.recent_gf }}</td>
          <td>{{ team.recent_ga }}</td>
          <td :class="{'text-green': team.recent_gd > 0, 'text-red': team.recent_gd < 0}">{{ team.recent_gd > 0 ? '+' : '' }}{{ team.recent_gd }}</td>
          <td>{{ team.recent_avg_gf }}</td>
          <td>{{ team.recent_win }}</td>
          <td>{{ team.recent_draw }}</td>
          <td>{{ team.recent_lose }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="empty">暂无数据对比</p>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })
const compareScope = ref('all')
const compareN = ref(6)

const currentData = computed(() => {
  const d = props.data?.data_compare
  if (!d) return null
  if (compareScope.value === 'homeaway') return d.homeaway || d.all || d
  return d.all || d
})
</script>

<style scoped>
.compare-header { display:flex; align-items:center; margin-bottom:8px; font-size:14px; font-weight:bold; }
.compare-table { width:100%; border-collapse:collapse; font-size:12px;
  th,td { border:1px solid #ebeef5; padding:4px 6px; text-align:center; }
  th { background:#fafafa; font-weight:600; }
  .team-name { text-align:left; font-weight:600; min-width:60px; }
}
.text-green { color:#67c23a; }
.text-red { color:#f56c6c; }
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
