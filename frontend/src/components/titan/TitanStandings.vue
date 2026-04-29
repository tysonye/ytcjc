<template>
  <div class="standings-panel">
    <div class="team-standing" v-if="homeTeam">
      <h4>{{ homeTeam.name || '主队' }}</h4>
      <el-table :data="[homeTeam.total || {}, homeTeam.home || {}]" size="small" stripe :show-header="false">
        <el-table-column prop="_label" label="" width="50">
          <template #default="{ row }">{{ row._type || (homeTeam.home && homeTeam.total ? '总' : '') }}</template>
        </el-table-column>
        <el-table-column prop="played" label="场" width="45" />
        <el-table-column prop="won" label="胜" width="40" />
        <el-table-column prop="drawn" label="平" width="40" />
        <el-table-column prop="lost" label="负" width="40" />
        <el-table-column prop="gf" label="进" width="40" />
        <el-table-column prop="ga" label="失" width="40" />
        <el-table-column prop="gd" label="差" width="45" />
        <el-table-column prop="points" label="积分" width="55" />
        <el-table-column prop="rank" label="排名" width="55" />
      </el-table>
    </div>
    <el-divider v-if="homeTeam && awayTeam" />
    <div class="team-standing" v-if="awayTeam">
      <h4>{{ awayTeam.name || '客队' }}</h4>
      <el-table :data="[awayTeam.total || {}, awayTeam.away || {}]" size="small" stripe :show-header="false">
        <el-table-column prop="_label" label="" width="50">
          <template #default="{ row }">{{ row._type || (awayTeam.away && awayTeam.total ? '总' : '') }}</template>
        </el-table-column>
        <el-table-column prop="played" label="场" width="45" />
        <el-table-column prop="won" label="胜" width="40" />
        <el-table-column prop="drawn" label="平" width="40" />
        <el-table-column prop="lost" label="负" width="40" />
        <el-table-column prop="gf" label="进" width="40" />
        <el-table-column prop="ga" label="失" width="40" />
        <el-table-column prop="gd" label="差" width="45" />
        <el-table-column prop="points" label="积分" width="55" />
        <el-table-column prop="rank" label="排名" width="55" />
      </el-table>
    </div>

    <div v-if="leagueStandings.length > 0" style="margin-top:15px">
      <h4>联赛积分榜（前10名）</h4>
      <el-table :data="leagueStandings.slice(0,10)" size="small" stripe>
        <el-table-column prop="rank" label="排名" width="60" />
        <el-table-column prop="team" label="球队" />
        <el-table-column prop="points" label="积分" width="70" align="center" />
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Object, default: () => ({}) } })

const homeTeam = computed(() => {
  const s = props.data?.standings_data
  if (!s) return null
  const ht = s.home_team || {}
  ht.total = s.total?.find(t => t.team === ht.name) || {}
  ht.home = s.home?.find(t => t.team === ht.name) || {}
  return Object.keys(ht).length > 1 ? ht : null
})

const awayTeam = computed(() => {
  const s = props.data?.standings_data
  if (!s) return null
  const at = s.away_team || {}
  at.total = s.total?.find(t => t.team === at.name) || {}
  at.away = s.away?.find(t => t.team === at.name) || {}
  return Object.keys(at).length > 1 ? at : null
})

const leagueStandings = computed(() => props.data?.standings_data?.total || [])
</script>

<style scoped>
.team-standing h4 { margin-bottom:8px; font-size:14px; color:#303133; }
</style>
