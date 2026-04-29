<template>
  <div class="data-stats">
    <div class="page-header"><h3>数据统计</h3></div>
    <el-row :gutter="15" style="margin-bottom:20px">
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="总用户数" :value="overview.totalUsers" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="付费用户" :value="overview.paidUsers" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="月收入" :value="overview.monthlyRevenue" prefix="¥" /></el-card></el-col>
      <el-col :span="6"><el-card shadow="hover"><el-statistic title="今日新增" :value="overview.todayNew" /></el-card></el-col>
    </el-row>
    <el-row :gutter="15">
      <el-col :span="12">
        <el-card>
          <template #header><span>会员等级分布</span></template>
          <div class="level-chart" ref="levelChartRef" style="height:300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>近7日注册趋势</span></template>
          <div class="trend-chart" ref="trendChartRef" style="height:300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const levelChartRef = ref(null)
const trendChartRef = ref(null)
const overview = reactive({ totalUsers: 0, paidUsers: 0, monthlyRevenue: 0, todayNew: 0 })

async function fetchOverview() {
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/stats/overview', { headers: { Authorization: `Bearer ${token}` } })
    const data = await resp.json()
    Object.assign(overview, data)
  } catch { ElMessage.error('获取统计失败') }
}

onMounted(async () => {
  await fetchOverview()
  try {
    const echarts = (await import('echarts')).default
    if (levelChartRef.value) {
      const chart = echarts.init(levelChartRef.value)
      chart.setOption({
        tooltip: { trigger: 'item' },
        series: [{
          type: 'pie', radius: ['40%', '70%'],
          data: [
            { value: overview.freeCount || 0, name: '免费' },
            { value: overview.silverCount || 0, name: '白银' },
            { value: overview.goldCount || 0, name: '黄金' },
            { value: overview.diamondCount || 0, name: '钻石' },
          ],
        }],
      })
    }
    if (trendChartRef.value) {
      const chart = echarts.init(trendChartRef.value)
      chart.setOption({
        tooltip: { trigger: 'axis' },
        xAxis: { type: 'category', data: overview.recentDays || [] },
        yAxis: { type: 'value' },
        series: [{ type: 'line', data: overview.recentCounts || [], smooth: true, areaStyle: {} }],
      })
    }
  } catch (e) { console.warn('ECharts加载失败:', e) }
})
</script>

<style scoped>
.page-header h3 { margin:0 0 15px;font-size:18px; }
</style>
