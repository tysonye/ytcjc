<template>
  <div class="standings-panel" v-if="standingsData">
    <table cellspacing="0" cellpadding="0" width="100%" border="0">
      <tbody>
        <tr>
          <td width="50%" valign="top">
            <table v-if="homeTeamData" width="100%" border="0" align="center" cellPadding="3" cellSpacing="1" borderColorLight="#ffffff" borderColorDark="#666666" bgcolor="#CECECE">
              <tbody>
                <tr bgcolor="#FDEFD2" height="28">
                  <td colspan="11" class="team-title-td">
                    <a :href="'//zq.titan007.com/cn/team/Summary/' + homeTeamData.team_id + '.html'" target="_blank" class="vander16" style="color:#000;padding-right:4px;"><b>{{ homeTeamLabel }}</b></a>
                  </td>
                </tr>
                <tr align="middle" class="y_bg" bgcolor="#FAF1DE">
                  <td width="43px" height="20">全场</td>
                  <td width="25px">赛</td>
                  <td width="25px">胜</td>
                  <td width="25px">平</td>
                  <td width="25px">负</td>
                  <td width="25px">得</td>
                  <td width="25px">失</td>
                  <td width="25px">净</td>
                  <td width="48px">得分</td>
                  <td width="30px">排名</td>
                  <td>胜率</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#FFFFFF">总</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeTotal?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(homeTotal?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(homeTotal?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ homeTotal ? homeTotal.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#F5F5F5"><font color="red">主</font></td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHome?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(homeHome?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(homeHome?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ homeHome ? homeHome.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#FFFFFF"><font color="blue">客</font></td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeAway?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(homeAway?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(homeAway?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ homeAway ? homeAway.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#F5F5F5">近6</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.near_six_stats?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(homeTeamData?.near_six_stats?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(homeTeamData?.near_six_stats?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(homeTeamData?.near_six_stats?.win_rate) }}</td>
                </tr>
                <tr align="middle" class="y_bg" bgcolor="#FAF1DE">
                  <td width="43px" height="20">半场</td>
                  <td width="25px">赛</td>
                  <td width="25px">胜</td>
                  <td width="25px">平</td>
                  <td width="25px">负</td>
                  <td width="25px">得</td>
                  <td width="25px">失</td>
                  <td width="25px">净</td>
                  <td width="48px">得分</td>
                  <td width="30px">排名</td>
                  <td>胜率</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#FFFFFF">总</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfTotal?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(homeHalfTotal?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(homeHalfTotal?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ homeHalfTotal ? homeHalfTotal.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#F5F5F5"><font color="red">主</font></td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeHalfHome?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(homeHalfHome?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(homeHalfHome?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ homeHalfHome ? homeHalfHome.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#FFFFFF"><font color="blue">客</font></td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(homeHalfAway?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(homeHalfAway?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(homeHalfAway?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ homeHalfAway ? homeHalfAway.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#FFECEC">
                  <td height="20" bgcolor="#F5F5F5">近6</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(homeTeamData?.half_near_six_stats?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(homeTeamData?.half_near_six_stats?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(homeTeamData?.half_near_six_stats?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(homeTeamData?.half_near_six_stats?.win_rate) }}</td>
                </tr>
              </tbody>
            </table>
          </td>
          <td width="50%" valign="top">
            <table v-if="awayTeamData" width="100%" border="0" align="center" cellPadding="3" cellSpacing="1" borderColorLight="#ffffff" borderColorDark="#666666" bgcolor="#B0D2E3">
              <tbody>
                <tr bgcolor="#DCE8ED" height="28">
                  <td colspan="11" class="team-title-td">
                    <a :href="'//zq.titan007.com/cn/team/Summary/' + awayTeamData.team_id + '.html'" target="_blank" class="vander16" style="color:#000;padding-right:4px;"><b>{{ awayTeamLabel }}</b></a>
                  </td>
                </tr>
                <tr align="middle" class="blue_t2">
                  <td width="43px" height="20">全场</td>
                  <td width="25px">赛</td>
                  <td width="25px">胜</td>
                  <td width="25px">平</td>
                  <td width="25px">负</td>
                  <td width="25px">得</td>
                  <td width="25px">失</td>
                  <td width="25px">净</td>
                  <td width="48px">得分</td>
                  <td width="30px">排名</td>
                  <td>胜率</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#FFFFFF">总</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayTotal?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(awayTotal?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(awayTotal?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ awayTotal ? awayTotal.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#F5F5F5"><font color="red">主</font></td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHome?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(awayHome?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(awayHome?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ awayHome ? awayHome.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#FFFFFF"><font color="blue">客</font></td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayAway?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(awayAway?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(awayAway?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ awayAway ? awayAway.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#F5F5F5">近6</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.near_six_stats?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(awayTeamData?.near_six_stats?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(awayTeamData?.near_six_stats?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(awayTeamData?.near_six_stats?.win_rate) }}</td>
                </tr>
                <tr align="middle" class="blue_t2">
                  <td width="43px" height="20">半场</td>
                  <td width="25px">赛</td>
                  <td width="25px">胜</td>
                  <td width="25px">平</td>
                  <td width="25px">负</td>
                  <td width="25px">得</td>
                  <td width="25px">失</td>
                  <td width="25px">净</td>
                  <td width="48px">得分</td>
                  <td width="30px">排名</td>
                  <td>胜率</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#FFFFFF">总</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfTotal?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(awayHalfTotal?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(awayHalfTotal?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ awayHalfTotal ? awayHalfTotal.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#F5F5F5"><font color="red">主</font></td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayHalfHome?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(awayHalfHome?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(awayHalfHome?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ awayHalfHome ? awayHalfHome.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#FFFFFF"><font color="blue">客</font></td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.played) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.won) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.drawn) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.lost) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.gf) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.ga) }}</td>
                  <td bgcolor="#FFFFFF">{{ v(awayHalfAway?.gd) }}</td>
                  <td bgcolor="#FFFFFF" class="red">{{ v(awayHalfAway?.points) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ v(awayHalfAway?.rank) }}</td>
                  <td bgcolor="#FFFFFF" class="blue">{{ awayHalfAway ? awayHalfAway.win_rate + '%' : '' }}</td>
                </tr>
                <tr align="middle" bgcolor="#CCCCFF">
                  <td height="20" bgcolor="#F5F5F5">近6</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.played) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.won) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.drawn) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.lost) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.gf) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.ga) }}</td>
                  <td bgcolor="#F5F5F5">{{ v(awayTeamData?.half_near_six_stats?.gd) }}</td>
                  <td bgcolor="#F5F5F5" class="red">{{ v(awayTeamData?.half_near_six_stats?.points) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(awayTeamData?.half_near_six_stats?.rank) }}</td>
                  <td bgcolor="#F5F5F5" class="blue">{{ v(awayTeamData?.half_near_six_stats?.win_rate) }}</td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  <div v-else class="no-data">暂无积分数据</div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })

const standingsData = computed(() => props.data?.standings_data)

function v(val) {
  if (val === undefined || val === null || val === '') return '\u00A0'
  return val
}

const homeTeamData = computed(() => standingsData.value?.home_team || null)
const awayTeamData = computed(() => standingsData.value?.away_team || null)

const homeTeamLabel = computed(() => {
  const ht = homeTeamData.value
  if (!ht) return ''
  const ls = standingsData.value?.league_short
  if (ls && ht.rank) return `[${ls}-${ht.rank}]${ht.team_cn || ht.team}`
  return ht.team_cn || ht.team
})

const awayTeamLabel = computed(() => {
  const at = awayTeamData.value
  if (!at) return ''
  const ls = standingsData.value?.league_short
  if (ls && at.rank) return `[${ls}-${at.rank}]${at.team_cn || at.team}`
  return at.team_cn || at.team
})

const homeId = computed(() => homeTeamData.value?.team_id)
const awayId = computed(() => awayTeamData.value?.team_id)

const homeTotal = computed(() => {
  const id = homeId.value
  if (!id) return null
  return standingsData.value?.total?.find(t => t.team_id === id) || null
})
const homeHome = computed(() => {
  const id = homeId.value
  if (!id) return null
  return standingsData.value?.home?.find(t => t.team_id === id) || null
})
const homeAway = computed(() => {
  const id = homeId.value
  if (!id) return null
  return standingsData.value?.away?.find(t => t.team_id === id) || null
})

const homeHalfTotal = computed(() => {
  const id = homeId.value
  if (!id || !standingsData.value?.half) return null
  return standingsData.value.half[id] || null
})
const homeHalfHome = computed(() => {
  const id = homeId.value
  if (!id || !standingsData.value?.half_home) return null
  return standingsData.value.half_home[id] || null
})
const homeHalfAway = computed(() => {
  const id = homeId.value
  if (!id || !standingsData.value?.half_away) return null
  return standingsData.value.half_away[id] || null
})

const awayTotal = computed(() => {
  const id = awayId.value
  if (!id) return null
  return standingsData.value?.total?.find(t => t.team_id === id) || null
})
const awayHome = computed(() => {
  const id = awayId.value
  if (!id) return null
  return standingsData.value?.home?.find(t => t.team_id === id) || null
})
const awayAway = computed(() => {
  const id = awayId.value
  if (!id) return null
  return standingsData.value?.away?.find(t => t.team_id === id) || null
})

const awayHalfTotal = computed(() => {
  const id = awayId.value
  if (!id || !standingsData.value?.half) return null
  return standingsData.value.half[id] || null
})
const awayHalfHome = computed(() => {
  const id = awayId.value
  if (!id || !standingsData.value?.half_home) return null
  return standingsData.value.half_home[id] || null
})
const awayHalfAway = computed(() => {
  const id = awayId.value
  if (!id || !standingsData.value?.half_away) return null
  return standingsData.value.half_away[id] || null
})
</script>

<style scoped>
.standings-panel {
  font-family: "Microsoft YaHei", "Tahoma", "SimSun";
  font-size: 12px;
}
.standings-panel table {
  border-collapse: separate;
}
.standings-panel td {
  line-height: 22px;
  white-space: nowrap;
}
.team-title-td {
  text-align: center;
  font-size: 14px;
  font-weight: bold;
  color: #000;
}
.vander16 {
  font-size: 14px;
  font-weight: bold;
  text-decoration: none;
  color: #000;
}
.vander16:hover {
  color: #FF5106;
  text-decoration: underline;
}
.y_bg td {
  background-color: #FAF1DE;
  font-weight: normal;
  color: #000;
}
.blue_t2 td {
  background-color: #DBE4EC;
  font-weight: normal;
  color: #000;
}
.red, a.red, a.red:hover {
  color: #F00;
}
.blue, a.blue, a.blue:hover {
  color: #06C;
}
.no-data {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 20px 0;
}
</style>
