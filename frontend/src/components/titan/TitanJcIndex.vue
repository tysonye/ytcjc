<template>
  <div class="jc-index-panel">
    <div class="jc-section" v-if="hasJcData">
      <table class="jc-table" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd">
        <tr class="tr-header1">
          <td height="22" bgcolor="#FDEFD2">&nbsp;</td>
          <td colspan="3" bgcolor="#FDEFD2">独赢</td>
          <td colspan="3" bgcolor="#FDEFD2">亚让</td>
          <td colspan="3" bgcolor="#FDEFD2">进球数</td>
          <td colspan="2" bgcolor="#FDEFD2">单双</td>
        </tr>
        <tr bgcolor="#FFFFFF" class="odds">
          <td height="21" width="68" bgcolor="#EAEDEE" style="font-weight:normal;color:#333;">全场</td>
          <td>{{ jcData.wlOdds?.live?.win || '' }}</td>
          <td>{{ jcData.wlOdds?.live?.draw || '' }}</td>
          <td>{{ jcData.wlOdds?.live?.lose || '' }}</td>
          <td bgcolor="#E8F2FF">{{ jcData.sfOdds?.live?.win || '' }}</td>
          <td bgcolor="#E8F2FF">{{ formatRf(jcData.sfOdds?.rf) }}</td>
          <td bgcolor="#E8F2FF">{{ jcData.sfOdds?.live?.lose || '' }}</td>
          <td>{{ jcData.goalOdds?.live?.g0 || '' }}</td>
          <td>{{ goalRangeLabel }}</td>
          <td>{{ jcData.goalOdds?.live?.g7 || '' }}</td>
          <td width="60" bgcolor="#E8F2FF">单{{ jcData.scoreOdds?.live?.scoreWin || '' }}</td>
          <td width="60" bgcolor="#E8F2FF">双{{ jcData.scoreOdds?.live?.scoreDraw || '' }}</td>
        </tr>
      </table>

      <table class="jc-table" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd" style="margin-top:-1px;">
        <tr class="bui" bgcolor="#ECF4FB">
          <td width="68" height="22" bgcolor="#EAEDEE"><b>波胆</b></td>
          <td width="51">1:0</td><td width="51">2:0</td><td width="51">2:1</td>
          <td width="51">3:0</td><td width="51">3:1</td><td width="51">3:2</td>
          <td width="51">4:0</td><td width="51">4:1</td><td width="51">4:2</td>
          <td width="51">4:3</td>
          <td width="51">0:0</td><td width="51">1:1</td><td width="51">2:2</td>
          <td width="51">3:3</td><td width="51">4:4</td>
        </tr>
        <tr bgcolor="#FFFFFF" class="odds">
          <td height="21" bgcolor="#EAEDEE" style="font-weight:normal;color:#333;">主</td>
          <td>{{ s.score10 }}</td><td>{{ s.score20 }}</td><td>{{ s.score21 }}</td>
          <td>{{ s.score30 }}</td><td>{{ s.score31 }}</td><td>{{ s.score32 }}</td>
          <td>{{ s.score40 }}</td><td>{{ s.score41 }}</td><td>{{ s.score42 }}</td>
          <td>{{ s.score43 || '' }}</td>
          <td :rowspan="2">{{ s.score00 }}</td><td :rowspan="2">{{ s.score11 }}</td>
          <td :rowspan="2">{{ s.score22 }}</td><td :rowspan="2">{{ s.score33 }}</td>
          <td :rowspan="2">{{ s.score44 || '' }}</td>
        </tr>
        <tr bgcolor="#FFFFFF" class="odds">
          <td height="21" bgcolor="#EAEDEE" style="font-weight:normal;color:#333;">客</td>
          <td>{{ s.score01 }}</td><td>{{ s.score02 }}</td><td>{{ s.score12 }}</td>
          <td>{{ s.score03 }}</td><td>{{ s.score13 }}</td><td>{{ s.score23 }}</td>
          <td>{{ s.score04 }}</td><td>{{ s.score14 }}</td><td>{{ s.score24 }}</td>
          <td>{{ s.score34 || '' }}</td>
        </tr>
      </table>

      <table class="jc-table" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd">
        <tr class="bui" bgcolor="#ECF4FB">
          <td width="68" rowspan="2" bgcolor="#EAEDEE"><b>入球数</b></td>
          <td width="251" height="21">0~1</td><td width="228">2~3</td><td width="224">4~6</td><td>7+</td>
        </tr>
        <tr bgcolor="#FFFFFF" class="odds">
          <td height="21">{{ goalRange.g01 }}</td><td>{{ goalRange.g23 }}</td><td>{{ goalRange.g46 }}</td><td>{{ goalRange.g7 }}</td>
        </tr>
      </table>

      <table class="jc-table" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd" style="margin-top:-1px;">
        <tr class="bui" bgcolor="#ECF4FB">
          <td width="68" rowspan="2" bgcolor="#EAEDEE"><b>半全场</b></td>
          <td height="21">主/主</td><td>主/和</td><td>主/客</td>
          <td>和/主</td><td>和/和</td><td>和/客</td>
          <td>客/主</td><td>客/和</td><td>客/客</td>
        </tr>
        <tr bgcolor="#FFFFFF" class="odds">
          <td height="21">{{ h.hfww }}</td><td>{{ h.hfwd }}</td><td>{{ h.hfwl }}</td>
          <td>{{ h.hfdw }}</td><td>{{ h.hfdd }}</td><td>{{ h.hfdl }}</td>
          <td>{{ h.hflw }}</td><td>{{ h.hfld }}</td><td>{{ h.hfll }}</td>
        </tr>
      </table>
    </div>

    <p v-if="!hasJcData" class="empty">暂无竞彩指数数据</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: { type: Object, default: () => ({}) },
  euCompanies: { type: Array, default: () => [] },
})

const jcData = computed(() => props.data?.jc_odds || {})

const hasJcData = computed(() => {
  const d = jcData.value
  return d.wlOdds || d.sfOdds || d.goalOdds || d.scoreOdds || d.hfOdds
})

function formatRf(val) {
  if (val == null || val === '') return ''
  const num = Number(val)
  if (isNaN(num)) return ''
  if (num > 0) return '+' + num
  return String(num)
}

const s = computed(() => jcData.value.scoreOdds?.live || {})

const h = computed(() => jcData.value.hfOdds?.live || {})

const goalRangeLabel = computed(() => {
  const g = jcData.value.goalOdds?.live
  if (!g) return ''
  const parts = []
  if (g.g1) parts.push(g.g1)
  if (g.g2) parts.push(g.g2)
  if (g.g3) parts.push(g.g3)
  return parts.join('/') || ''
})

const goalRange = computed(() => {
  const g = jcData.value.goalOdds?.live || {}
  return {
    g01: [g.g0, g.g1].filter(Boolean).join('/'),
    g23: [g.g2, g.g3].filter(Boolean).join('/'),
    g46: [g.g4, g.g5, g.g6].filter(Boolean).join('/'),
    g7: g.g7 || '',
  }
})
</script>

<style scoped>
.jc-index-panel { font-size: 12px; }
.jc-section { margin-bottom: 0; }
.jc-table { border-collapse: collapse; }
.jc-table td { border: 1px solid #ddd; padding: 2px 4px; text-align: center; white-space: nowrap; height: 21px; font-size: 12px; color: #333; }

.tr-header1 td { background: #FDEFD2; font-weight: bold; }
.bui td { background: #ECF4FB; }
.odds td { background: #FFFFFF; }
.jc-table td[rowspan] { vertical-align: middle; background: #FFFFFF; }

.empty { color: #999; text-align: center; padding: 20px; font-size: 13px; }
</style>
