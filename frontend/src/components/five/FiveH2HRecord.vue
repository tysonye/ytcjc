<template>
  <div v-if="data && (data.summary || data.matches?.length)">
    <div v-if="data.summary" class="summary-bar">
      <el-row style="width:100%">
        <el-col :span="8">
          <div class="summary-item">
            <span class="summary-count win">{{ data.homeWins }}</span>
            <span class="summary-label">胜</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="summary-item">
            <span class="summary-count draw">{{ data.draws }}</span>
            <span class="summary-label">和</span>
          </div>
        </el-col>
        <el-col :span="8">
          <div class="summary-item">
            <span class="summary-count loss">{{ data.awayWins }}</span>
            <span class="summary-label">负</span>
          </div>
        </el-col>
      </el-row>
    </div>
    <el-table
      v-if="data.matches?.length"
      :data="data.matches"
      size="small"
      stripe
      max-height="250"
    >
      <el-table-column prop="date" label="日期" width="90" />
      <el-table-column prop="league" label="赛事" width="100" />
      <el-table-column prop="home" label="主队" width="90" />
      <el-table-column prop="score" label="比分" width="60" align="center" />
      <el-table-column prop="away" label="客队" width="90" />
      <el-table-column prop="handicap" label="让球" width="60" />
      <el-table-column prop="result" label="结果" width="60" />
    </el-table>
  </div>
  <p v-else class="placeholder">暂无对赛成绩数据</p>
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
.summary-bar { display:flex; justify-content:center; gap:20px; margin-bottom:12px; padding:8px; background:#fafafa; border-radius:6px; }
.summary-item { text-align:center; }
.summary-count { font-size:20px; font-weight:700; display:block; }
.summary-count.win { color:#389e0d; }
.summary-count.draw { color:#d46b08; }
.summary-count.loss { color:#cf1322; }
.summary-label { font-size:11px; color:#999; }
.placeholder { color:#999; text-align:center; padding:15px; font-size:13px; }
</style>
