<template>
  <template v-if="data">
    <el-row :gutter="15">
      <el-col :span="12">
        <h4>主队近况</h4>
        <div class="form-badges">
          <span
            v-for="(ch, idx) in data.home.formSeq"
            :key="idx"
            class="form-badge"
            :class="badgeClass(ch)"
          >{{ ch }}</span>
        </div>
        <div class="pan-text">盘路：{{ data.home.panSeq }}</div>
      </el-col>
      <el-col :span="12">
        <h4>客队近况</h4>
        <div class="form-badges">
          <span
            v-for="(ch, idx) in data.away.formSeq"
            :key="idx"
            class="form-badge"
            :class="badgeClass(ch)"
          >{{ ch }}</span>
        </div>
        <div class="pan-text">盘路：{{ data.away.panSeq }}</div>
      </el-col>
    </el-row>
  </template>
  <p v-else class="placeholder">暂无近况走势数据</p>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    default: null
  }
})

const badgeClass = (ch) => {
  if (ch === 'W') return 'win'
  if (ch === 'D') return 'draw'
  if (ch === 'L') return 'loss'
  return ''
}
</script>

<style scoped>
.form-badges {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}
.form-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid;
}
.form-badge.win {
  background: #f6ffed;
  color: #389e0d;
  border-color: #b7eb8f;
}
.form-badge.draw {
  background: #fff7e6;
  color: #d46b08;
  border-color: #ffd591;
}
.form-badge.loss {
  background: #fff1f0;
  color: #cf1322;
  border-color: #ffa39e;
}
.pan-text {
  font-size: 12px;
  color: #666;
}
h4 {
  font-size: 13px;
  margin: 4px 0;
}
.placeholder {
  color: #999;
  text-align: center;
  padding: 15px;
  font-size: 13px;
}
</style>
