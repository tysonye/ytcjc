<template>
  <div v-if="data && (data.result || data.analysis)">
    <div v-if="data.result" :class="['rec-result', resultClass]">{{ data.result }}</div>
    <p v-if="data.analysis" class="analysis-text">{{ data.analysis }}</p>
  </div>
  <p v-else class="placeholder">暂无推介数据</p>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  }
})

const resultClass = computed(() => {
  const r = props.data?.result || ''
  if (r.includes('主胜') || r.includes('主贏')) return 'home-win'
  if (r.includes('和') || r.includes('平')) return 'draw'
  if (r.includes('客胜') || r.includes('客贏')) return 'away-win'
  return 'other'
})
</script>

<style scoped>
.rec-result { display:inline-block; padding:6px 16px; border-radius:4px; font-size:14px; font-weight:700; margin-bottom:10px; }
.rec-result.home-win { background:#f6ffed; color:#389e0d; border:1px solid #b7eb8f; }
.rec-result.draw { background:#fff7e6; color:#d46b08; border:1px solid #ffd591; }
.rec-result.away-win { background:#fff1f0; color:#cf1322; border:1px solid #ffa39e; }
.rec-result.other { background:#e6f7ff; color:#1890ff; border:1px solid #91d5ff; }
.analysis-text { font-size:13px; color:#595959; line-height:1.8; padding:8px 0; }
.placeholder { color:#999; text-align:center; padding:15px; font-size:13px; }
</style>
