<template>
  <el-descriptions v-if="data" :column="2" border size="small">
    <el-descriptions-item label="主队">{{ data.homeTeam }}</el-descriptions-item>
    <el-descriptions-item label="客队">{{ data.awayTeam }}</el-descriptions-item>
    <el-descriptions-item label="联赛">{{ data.league }}</el-descriptions-item>
    <el-descriptions-item label="时间">{{ data.matchTime }}</el-descriptions-item>
    <el-descriptions-item label="天气">{{ data.weather || '-' }}</el-descriptions-item>
    <el-descriptions-item label="场地">{{ data.venue || '-' }}</el-descriptions-item>
  </el-descriptions>
  <p v-else class="placeholder">暂无基本信息</p>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    default: null
  }
})
</script>

<style scoped>
.placeholder {
  color: #999;
  text-align: center;
  padding: 15px;
  font-size: 13px;
}
</style>
