<template>
  <div class="recent-form-panel">
    <div class="form-section" v-if="homeRecords.length">
      <h4>主队近期战绩</h4>
      <el-table :data="homeRecords" size="small" stripe max-height="250" style="width:100%">
        <el-table-column prop="date" label="日期" width="80" />
        <el-table-column prop="league" label="赛事" width="80" />
        <el-table-column prop="home_team" label="主队" width="80" />
        <el-table-column prop="score" label="比分" width="65" align="center">
          <template #default="{ row }">
            <span class="score-text">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="away_team" label="客队" width="80" />
        <el-table-column prop="corner" label="角球" width="55" align="center" />
        <el-table-column prop="handicap" label="盘口" width="65" align="center" />
        <el-table-column prop="result" label="结果" width="50" align="center">
          <template #default="{ row }">
            <el-tag :type="row.result === '勝' ? 'success' : row.result === '負' ? 'danger' : 'warning'" size="small">{{ row.result }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="form-section" v-if="awayRecords.length">
      <h4>客队近期战绩</h4>
      <el-table :data="awayRecords" size="small" stripe max-height="250" style="width:100%">
        <el-table-column prop="date" label="日期" width="80" />
        <el-table-column prop="league" label="赛事" width="80" />
        <el-table-column prop="home_team" label="主队" width="80" />
        <el-table-column prop="score" label="比分" width="65" align="center">
          <template #default="{ row }">
            <span class="score-text">{{ row.score }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="away_team" label="客队" width="80" />
        <el-table-column prop="corner" label="角球" width="55" align="center" />
        <el-table-column prop="handicap" label="盘口" width="65" align="center" />
        <el-table-column prop="result" label="结果" width="50" align="center">
          <template #default="{ row }">
            <el-tag :type="row.result === '勝' ? 'success' : row.result === '負' ? 'danger' : 'warning'" size="small">{{ row.result }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <p v-if="!homeRecords.length && !awayRecords.length" class="empty">暂无近期战绩</p>
  </div>
</template>

<script setup>
defineProps({
  homeRecords: { type: Array, default: () => [] },
  awayRecords: { type: Array, default: () => [] },
})
</script>

<style scoped>
.form-section { margin-bottom:15px; }
.form-section h4 { font-size:14px; margin-bottom:6px; color:#303133; }
.score-text { font-weight:bold; }
.empty{color:#999;text-align:center;padding:20px;font-size:13px;}
</style>
