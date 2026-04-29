<template>
  <div class="season-stats" v-if="data">
    <div class="stats-row">
      <div class="stats-team home" v-if="data.home">
        <h4>主隊戰績統計</h4>
        <div class="stat-item" v-for="item in data.home.records" :key="item.label">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-value">{{ item.value }}</span>
        </div>
        <h4 style="margin-top:12px">主隊得失球統計</h4>
        <div class="stat-item" v-for="item in data.home.goals" :key="item.label">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-value">{{ item.value }}</span>
        </div>
        <h4 style="margin-top:12px">主隊凈勝球統計</h4>
        <div class="stat-item" v-for="item in data.home.gd" :key="item.label">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-value">{{ item.value }}</span>
        </div>
      </div>
      <div class="stats-team away" v-if="data.away">
        <h4>客隊戰績統計</h4>
        <div class="stat-item" v-for="item in data.away.records" :key="item.label">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-value">{{ item.value }}</span>
        </div>
        <h4 style="margin-top:12px">客隊得失球統計</h4>
        <div class="stat-item" v-for="item in data.away.goals" :key="item.label">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-value">{{ item.value }}</span>
        </div>
        <h4 style="margin-top:12px">客隊凈勝球統計</h4>
        <div class="stat-item" v-for="item in data.away.gd" :key="item.label">
          <span class="stat-label">{{ item.label }}</span>
          <span class="stat-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
    <p v-if="!data?.home && !data?.away" class="empty">暂无赛季统计数据</p>
  </div>
</template>

<script setup>
const props = defineProps({ data: { type: Object, default: () => ({}) } })
</script>

<style scoped>
.stats-row { display:grid; grid-template-columns:1fr 1fr; gap:15px; }
@media(max-width:768px) { .stats-row { grid-template-columns:1fr; } }
.stats-team h4 { font-size:13px; margin-bottom:6px; color:#303133; }
.stat-item { display:flex; justify-content:space-between; padding:3px 0; font-size:12px; border-bottom:1px solid #f5f5f5; }
.stat-label { color:#666; }
.stat-value { font-weight:600; color:#303133; }
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
