<template>
  <div class="briefing" v-if="text">
    <div class="briefing-content">{{ text }}</div>
  </div>
  <p v-else class="empty">暂无赛前简报</p>
</template>

<script setup>
defineProps({ text: { type: String, default: '' } })
</script>

<style scoped>
.briefing-content {
  font-size:13px; line-height:1.8; color:#303133;
  padding:12px; background:#fafafa; border-radius:6px;
  border-left:3px solid #0066cc;
}
.empty { color:#999; text-align:center; padding:20px; font-size:13px; }
</style>
