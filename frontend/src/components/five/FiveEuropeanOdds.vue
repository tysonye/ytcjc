<template>
  <el-table v-if="data && data.length" :data="data" size="small" stripe max-height="300">
    <el-table-column prop="company" label="公司" width="100" fixed />
    <el-table-column label="初盘" align="center">
      <el-table-column prop="initHome" label="胜" width="55" />
      <el-table-column prop="initDraw" label="平" width="55" />
      <el-table-column prop="initAway" label="负" width="55" />
    </el-table-column>
    <el-table-column label="即时" align="center">
      <el-table-column label="胜" width="55">
        <template #default="{ row }">
          {{ row.currHome }}<span v-if="changeDir(row.initHome, row.currHome) === 'up'" class="odds-up">↑</span><span v-else-if="changeDir(row.initHome, row.currHome) === 'down'" class="odds-down">↓</span>
        </template>
      </el-table-column>
      <el-table-column label="平" width="55">
        <template #default="{ row }">
          {{ row.currDraw }}<span v-if="changeDir(row.initDraw, row.currDraw) === 'up'" class="odds-up">↑</span><span v-else-if="changeDir(row.initDraw, row.currDraw) === 'down'" class="odds-down">↓</span>
        </template>
      </el-table-column>
      <el-table-column label="负" width="55">
        <template #default="{ row }">
          {{ row.currAway }}<span v-if="changeDir(row.initAway, row.currAway) === 'up'" class="odds-up">↑</span><span v-else-if="changeDir(row.initAway, row.currAway) === 'down'" class="odds-down">↓</span>
        </template>
      </el-table-column>
    </el-table-column>
  </el-table>
  <p v-else class="placeholder">暂无欧指数据</p>
</template>

<script setup>
defineProps({
  data: {
    type: Array,
    default: () => []
  }
})

function changeDir(init, curr) {
  const a = parseFloat(init), b = parseFloat(curr)
  if (isNaN(a) || isNaN(b) || a === b) return ''
  return b > a ? 'up' : 'down'
}
</script>

<style scoped>
.odds-up { color:#cf1322; font-size:11px; }
.odds-down { color:#389e0d; font-size:11px; }
.placeholder { color:#999; text-align:center; padding:15px; font-size:13px; }
</style>
