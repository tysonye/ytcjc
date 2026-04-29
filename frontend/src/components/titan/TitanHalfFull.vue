<template>
  <div class="stats-panel">
    <div class="stat-team" v-if="homeData">
      <h4>主队半全场</h4>
      <el-table :data="homeData" size="small" stripe>
        <el-table-column prop="type" label="类型" width="50" />
        <el-table-column prop="played" label="场次" width="55" />
        <el-table-column prop="won" label="胜" width="40" />
        <el-table-column prop="drawn" label="平" width="40" />
        <el-table-column prop="lost" label="负" width="40" />
        <el-table-column prop="win_rate" label="胜率" width="60" />
      </el-table>
    </div>
    <div class="stat-team" v-if="awayData">
      <h4>客队半全场</h4>
      <el-table :data="awayData" size="small" stripe>
        <el-table-column prop="type" label="类型" width="50" />
        <el-table-column prop="played" label="场次" width="55" />
        <el-table-column prop="won" label="胜" width="40" />
        <el-table-column prop="drawn" label="平" width="40" />
        <el-table-column prop="lost" label="负" width="40" />
        <el-table-column prop="win_rate" label="胜率" width="60" />
      </el-table>
    </div>
    <p v-if="!homeData?.length && !awayData?.length" class="empty">暂无数据</p>
  </div>
</template>

<script setup>
defineProps({
  homeData: { type: Array, default: () => [] },
  awayData: { type: Array, default: () => [] },
})
</script>

<style scoped>
.stat-team { margin-bottom:12px; }
.stat-team h4 { font-size:14px; margin-bottom:6px; color:#303133; }
.empty{color:#999;text-align:center;padding:20px;font-size:13px;}
</style>
