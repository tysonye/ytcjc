<template>
  <div class="odds-trend-panel">
    <table width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd" v-if="trendData.length">
      <tr class="y_bg">
        <td rowspan="2" width="6%" height="24" bgcolor="#EAEDEE">公司</td>
        <td rowspan="2" width="4%" height="24" bgcolor="#EAEDEE">类型</td>
        <td colspan="3" bgcolor="#F0F2F4">欧洲指数</td>
        <td colspan="3" bgcolor="#F0F2F4">欧转亚盘</td>
        <td colspan="3" bgcolor="#F0F2F4">实际最新亚盘</td>
        <td colspan="3" bgcolor="#F0F2F4">进球数</td>
      </tr>
      <tr class="y_bg">
        <td width="4%" bgcolor="#ECF4FB">胜</td><td width="4%" bgcolor="#ECF4FB">平</td><td width="4%" bgcolor="#ECF4FB">负</td>
        <td width="4%" bgcolor="#ECF4FB">主</td><td width="4%" bgcolor="#ECF4FB">盘口</td><td width="4%" bgcolor="#ECF4FB">客</td>
        <td width="4%" bgcolor="#ECF4FB">主</td><td width="4%" bgcolor="#ECF4FB">盘口</td><td width="4%" bgcolor="#ECF4FB">客</td>
        <td width="4%" bgcolor="#ECF4FB">大</td><td width="4%" bgcolor="#ECF4FB">盘口</td><td width="4%" bgcolor="#ECF4FB">小</td>
      </tr>
      <template v-for="(row, idx) in trendData" :key="idx">
        <tr :bgcolor="idx % 2 === 0 ? '#FFFFFF' : '#F5F5F5'" class="odds">
          <td :rowspan="rowspanCount(row)" height="21" bgcolor="#EAEDEE" style="font-weight:normal;color:#333;">{{ row.company }}</td>
          <td bgcolor="#EAEDEE"><font color="#555555">初</font></td>
          <td>{{ row.eu_init_home }}</td>
          <td>{{ row.eu_init_draw }}</td>
          <td>{{ row.eu_init_away }}</td>
          <td bgcolor="#E8F2FF">{{ row.eua_init_home }}</td>
          <td bgcolor="#E8F2FF"><font color="#1a6fb5">{{ formatHandicap(row.eua_init_handicap) }}</font></td>
          <td bgcolor="#E8F2FF">{{ row.eua_init_away }}</td>
          <td>{{ row.real_init_home }}</td>
          <td><font color="#1a6fb5">{{ formatHandicap(row.real_init_handicap) }}</font></td>
          <td>{{ row.real_init_away }}</td>
          <td bgcolor="#E8F2FF">{{ row.goal_init_big }}</td>
          <td bgcolor="#E8F2FF"><font color="#1a6fb5">{{ formatHandicap(row.goal_init_line) }}</font></td>
          <td bgcolor="#E8F2FF">{{ row.goal_init_small }}</td>
        </tr>
        <tr :bgcolor="idx % 2 === 0 ? '#FFFFFF' : '#F5F5F5'" class="odds">
          <td bgcolor="#EAEDEE"><font color="#555555">{{ row.has_live ? '终' : '即时' }}</font></td>
          <td :class="diffClass(row.eu_curr_home, row.eu_init_home)">{{ row.eu_curr_home }}</td>
          <td :class="diffClass(row.eu_curr_draw, row.eu_init_draw)">{{ row.eu_curr_draw }}</td>
          <td :class="diffClass(row.eu_curr_away, row.eu_init_away)">{{ row.eu_curr_away }}</td>
          <td bgcolor="#E8F2FF" :class="diffClass(row.eua_curr_home, row.eua_init_home)">{{ row.eua_curr_home }}</td>
          <td bgcolor="#E8F2FF" :class="diffClass(row.eua_curr_handicap, row.eua_init_handicap)"><font color="#1a6fb5">{{ formatHandicap(row.eua_curr_handicap) }}</font></td>
          <td bgcolor="#E8F2FF" :class="diffClass(row.eua_curr_away, row.eua_init_away)">{{ row.eua_curr_away }}</td>
          <td :class="diffClass(row.real_curr_home, row.real_init_home)">{{ row.real_curr_home }}</td>
          <td :class="diffClass(row.real_curr_handicap, row.real_init_handicap)"><font color="#1a6fb5">{{ formatHandicap(row.real_curr_handicap) }}</font></td>
          <td :class="diffClass(row.real_curr_away, row.real_init_away)">{{ row.real_curr_away }}</td>
          <td bgcolor="#E8F2FF" :class="diffClass(row.goal_curr_big, row.goal_init_big)">{{ row.goal_curr_big }}</td>
          <td bgcolor="#E8F2FF" :class="diffClass(row.goal_curr_line, row.goal_init_line)"><font color="#1a6fb5">{{ formatHandicap(row.goal_curr_line) }}</font></td>
          <td bgcolor="#E8F2FF" :class="diffClass(row.goal_curr_small, row.goal_init_small)">{{ row.goal_curr_small }}</td>
        </tr>
        <tr v-if="hasLiveData(row)" :bgcolor="idx % 2 === 0 ? '#FFFFFF' : '#F5F5F5'" class="odds">
          <td bgcolor="#EAEDEE" style="font-weight:normal;color:red;"><font color="red">滚球</font></td>
          <td>{{ row.live_eu_changed ? row.eu_live_home : '' }}</td>
          <td>{{ row.live_eu_changed ? row.eu_live_draw : '' }}</td>
          <td>{{ row.live_eu_changed ? row.eu_live_away : '' }}</td>
          <td bgcolor="#E8F2FF"></td>
          <td bgcolor="#E8F2FF"></td>
          <td bgcolor="#E8F2FF"></td>
          <td>{{ row.real_live_home }}</td>
          <td><font color="#1a6fb5">{{ formatHandicap(row.real_live_handicap) }}</font></td>
          <td>{{ row.real_live_away }}</td>
          <td bgcolor="#E8F2FF">{{ row.goal_live_big }}</td>
          <td bgcolor="#E8F2FF"><font color="#1a6fb5">{{ formatHandicap(row.goal_live_line) }}</font></td>
          <td bgcolor="#E8F2FF">{{ row.goal_live_small }}</td>
        </tr>
      </template>
    </table>
    <p v-if="!trendData.length" class="empty">暂无走势数据</p>
  </div>
</template>

<script setup>
const props = defineProps({
  trendData: { type: Array, default: () => [] },
})

function hasLiveData(row) {
  if (row.has_live !== undefined) return row.has_live
  const fields = [
    row.eu_live_home, row.eu_live_draw, row.eu_live_away,
    row.real_live_home, row.real_live_handicap, row.real_live_away,
    row.goal_live_big, row.goal_live_line, row.goal_live_small,
  ]
  return fields.some(v => v && v.trim() !== '')
}

const GOAL_CN = '平手,平/半,半球,半/一,一球,一/球半,球半,球半/两,两球,两/两球半,两球半,两球半/三,三球,三/三球半,三球半,三球半/四球,四球,四/四球半,四球半,四球半/五,五球,五/五球半,五球半,五球半/六,六球,六/六球半,六球半,六球半/七,七球,七/七球半,七球半,七球半/八,八球,八/八球半,八球半,八球半/九,九球,九/九球半,九球半,九球半/十,十球'.split(',')

function formatHandicap(val) {
  if (val == null || val === '') return ''
  const num = parseFloat(val)
  if (isNaN(num)) return val
  if (num === 0) return '平手'
  if (num > 10 || num < -10) return Math.abs(num).toFixed(1)
  const idx = Math.abs(parseInt(num * 4))
  const text = GOAL_CN[idx] || val
  return num < 0 ? '受' + text : text
}

function rowspanCount(row) {
  let count = 2
  if (hasLiveData(row)) count++
  return count
}

function diffClass(curr, init) {
  if (!curr || !init) return ''
  const c = parseFloat(curr), i = parseFloat(init)
  if (isNaN(c) || isNaN(i)) return ''
  if (c > i) return 'odds-up'
  if (c < i) return 'odds-down'
  return ''
}
</script>

<style scoped>
.odds-trend-panel { font-size: 12px; }
table { border-collapse: collapse; width: 100%; border: 1px solid #ddd; }
table td { border: 1px solid #ddd; padding: 2px 3px; text-align: center; white-space: nowrap; height: 20px; font-size: 12px; color: #333; }
.y_bg td { font-weight: bold; }

.odds-up { color: #f56c6c !important; font-weight: 600; }
.odds-down { color: #67c23a !important; font-weight: 600; }

.empty { color: #999; text-align: center; padding: 20px; font-size: 13px; }
</style>
