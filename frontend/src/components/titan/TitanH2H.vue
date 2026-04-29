<template>
  <div class="h2h-panel">
    <el-table :data="records" size="small" stripe max-height="350" style="width:100%">
      <el-table-column prop="date" label="日期" width="80" />
      <el-table-column prop="league" label="赛事" width="80" />
      <el-table-column prop="home_team" label="主队" width="80" />
      <el-table-column prop="score" label="比分" width="65" align="center">
        <template #default="{ row }">
          <span class="score-text">{{ row.score }}</span>
          <span v-if="row.half_score" class="half-score">({{ row.half_score }})</span>
        </template>
      </el-table-column>
      <el-table-column prop="away_team" label="客队" width="80" />
      <el-table-column prop="corner" label="角球" width="55" align="center" />
      <el-table-column prop="handicap" label="盘口" width="65" align="center" />
      <el-table-column label="欧指" align="center">
        <el-table-column prop="eu_home" label="主" width="42" />
        <el-table-column prop="eu_draw" label="和" width="42" />
        <el-table-column prop="eu_away" label="客" width="42" />
      </el-table-column>
      <el-table-column prop="result" label="结果" width="50" align="center">
        <template #default="{ row }">
          <el-tag :type="row.result === '勝' ? 'success' : row.result === '負' ? 'danger' : 'warning'" size="small">{{ row.result }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
    <p v-if="!records || records.length === 0" class="empty">暂无交锋记录</p>
  </div>
</template>

<script setup>
defineProps({ records: { type: Array, default: () => [] } })
</script>

<style scoped>
.score-text { font-weight:bold; }
.half-score { font-size:10px; color:#999; }
.empty{color:#999;text-align:center;padding:20px;font-size:13px;}
</style>
