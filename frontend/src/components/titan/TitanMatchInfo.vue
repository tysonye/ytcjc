<template>
  <div class="match-info-panel">
    <el-descriptions :column="isMobile ? 1 : 3" border size="small" v-if="data">
      <el-descriptions-item label="联赛">{{ data.league_round || '-' }}</el-descriptions-item>
      <el-descriptions-item label="比赛时间">{{ data.match_date || '-' }} {{ data.match_time || '' }}</el-descriptions-item>
      <el-descriptions-item label="场地">{{ data.venue || '-' }}</el-descriptions-item>
      <el-descriptions-item label="天气">{{ data.weather || '-' }}</el-descriptions-item>
      <el-descriptions-item label="温度">{{ data.temperature || '-' }}</el-descriptions-item>
    </el-descriptions>
    <div v-else class="empty">暂无比赛信息</div>
  </div>
</template>

<script setup>
defineProps({ data: { type: Object, default: null } })
</script>

<style scoped>
.empty { text-align:center; color:#999; padding:20px; }
</style>
