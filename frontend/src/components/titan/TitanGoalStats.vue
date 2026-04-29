<template>
  <div class="goal-stats-panel">
    <div class="stat-team" v-if="homeData">
      <h4>主队进球分布</h4>
      <el-table :data="[homeData]" size="small" stripe>
        <el-table-column prop="type" label="" width="40" />
        <el-table-column prop="0" label="0球" width="50" align="center" />
        <el-table-column prop="1" label="1球" width="50" align="center" />
        <el-table-column prop="2" label="2球" width="50" align="center" />
        <el-table-column prop="3" label="3球" width="50" align="center" />
        <el-table-column prop="4" label="4球" width="50" align="center" />
        <el-table-column prop="5" label="5球" width="50" align="center" />
        <el-table-column prop="6" label="6球" width="50" align="center" />
        <el-table-column prop="7+" label="7+" width="50" align="center" />
      </el-table>
    </div>
    <div class="stat-team" v-if="awayData">
      <h4>客队进球分布</h4>
      <el-table :data="[awayData]" size="small" stripe>
        <el-table-column prop="type" label="" width="40" />
        <el-table-column prop="0" label="0球" width="50" align="center" />
        <el-table-column prop="1" label="1球" width="50" align="center" />
        <el-table-column prop="2" label="2球" width="50" align="center" />
        <el-table-column prop="3" label="3球" width="50" align="center" />
        <el-table-column prop="4" label="4球" width="50" align="center" />
        <el-table-column prop="5" label="5球" width="50" align="center" />
        <el-table-column prop="6" label="6球" width="50" align="center" />
        <el-table-column prop="7+" label="7+" width="50" align="center" />
      </el-table>
    </div>
    <p v-if="!homeData && !awayData" class="empty">暂无数据</p>
  </div>
</template>

<script setup>
defineProps({
  homeData: { type: Object, default: null },
  awayData: { type: Object, default: null },
})
</script>

<style scoped>
.stat-team { margin-bottom:12px; }
.stat-team h4 { font-size:14px; margin-bottom:6px; color:#303133; }
.empty{color:#999;text-align:center;padding:20px;font-size:13px;}
</style>
