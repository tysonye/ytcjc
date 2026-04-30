<template>
  <el-table v-if="data && data.length" :data="data" size="small" stripe max-height="300">
    <el-table-column prop="company" label="公司" width="100" fixed />
    <el-table-column prop="home" label="主" width="70" align="center">
      <template #default="{ row }">
        <span :class="kellyClass(row.home)">{{ row.home }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="draw" label="平" width="70" align="center">
      <template #default="{ row }">
        <span :class="kellyClass(row.draw)">{{ row.draw }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="away" label="客" width="70" align="center">
      <template #default="{ row }">
        <span :class="kellyClass(row.away)">{{ row.away }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="returnRate" label="返还率" width="80" align="center" />
  </el-table>
  <p v-else class="placeholder">暂无凯利指数数据</p>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

function kellyClass(val) {
  const n = parseFloat(val)
  if (isNaN(n)) return ''
  if (n > 1.0) return 'kelly-high'
  if (n < 0.9) return 'kelly-low'
  return ''
}
</script>

<style scoped>
.kelly-high { color:#cf1322; font-weight:600; }
.kelly-low { color:#389e0d; font-weight:600; }
.placeholder { color:#999; text-align:center; padding:15px; font-size:13px; }
</style>
