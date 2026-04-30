<template>
  <div class="jc-bet-panel">
    <div class="bet-header">
      <span class="bet-title">竞彩模拟投注</span>
      <span class="bet-update" v-if="updateTime">奖金更新：{{ updateTime }}</span>
      <button class="refresh-btn" @click="fetchData">刷新</button>
    </div>

    <div class="play-nav">
      <a :class="{ active: playType === 'single' }" @click="switchPlay('single')">单关</a>
      <a :class="{ active: playType === 'had' }" @click="switchPlay('had')">胜平负</a>
      <a :class="{ active: playType === 'hhad' }" @click="switchPlay('hhad')">让球胜平负</a>
      <a :class="{ active: playType === 'mix' }" @click="switchPlay('mix')">混合过关</a>
      <a :class="{ active: playType === 'crs' }" @click="switchPlay('crs')">比分</a>
      <a :class="{ active: playType === 'ttg' }" @click="switchPlay('ttg')">进球数</a>
      <a :class="{ active: playType === 'hafu' }" @click="switchPlay('hafu')">半全场</a>
    </div>

    <div class="match-list" v-loading="loading">
      <template v-if="groupedMatches.length">
        <div v-for="group in groupedMatches" :key="group.date" class="date-group">
          <div class="date-header">
            <span>{{ group.label }}</span>
            <span class="match-count">共{{ group.matches.length }}场比赛</span>
          </div>
          <div v-for="m in group.matches" :key="m.matchId" class="match-row" :class="'match-row-' + playType">
            <div class="match-info">
              <span class="match-num">{{ m.matchNum }}</span>
              <span class="match-league">{{ m.leagueName }}</span>
              <span class="match-time">{{ m.matchTime }}</span>
            </div>
            <div class="match-teams">
              <span class="team-home">{{ m.homeTeam }}</span>
              <span class="vs">VS</span>
              <span class="team-away">{{ m.awayTeam }}</span>
            </div>

            <template v-if="playType === 'single'">
              <div class="single-odds-wrap">
                <div class="single-odds-group" v-if="m.hadSelling && m.hadSingle && m.hadH">
                  <span class="single-type-tag">胜平负</span>
                  <div class="odds-cells">
                    <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'h') }" @click="selectBet(m, 'had', 'h')">
                      <span class="odds-label">胜</span><span class="odds-val">{{ m.hadH }}</span>
                    </div>
                    <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'd') }" @click="selectBet(m, 'had', 'd')">
                      <span class="odds-label">平</span><span class="odds-val">{{ m.hadD }}</span>
                    </div>
                    <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'a') }" @click="selectBet(m, 'had', 'a')">
                      <span class="odds-label">负</span><span class="odds-val">{{ m.hadA }}</span>
                    </div>
                  </div>
                </div>
                <div class="single-odds-group" v-if="m.hhadSelling && m.hhadSingle && m.hhadH">
                  <span class="single-type-tag">让球({{ m.handicapDisplay }})</span>
                  <div class="odds-cells">
                    <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'h') }" @click="selectBet(m, 'hhad', 'h')">
                      <span class="odds-label">让胜</span><span class="odds-val">{{ m.hhadH }}</span>
                    </div>
                    <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'd') }" @click="selectBet(m, 'hhad', 'd')">
                      <span class="odds-label">让平</span><span class="odds-val">{{ m.hhadD }}</span>
                    </div>
                    <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'a') }" @click="selectBet(m, 'hhad', 'a')">
                      <span class="odds-label">让负</span><span class="odds-val">{{ m.hhadA }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="playType === 'had'">
              <div class="match-odds">
                <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'h'), disabled: !m.hadH }" @click="m.hadH && selectBet(m, 'had', 'h')">
                  <span class="odds-label">胜</span><span class="odds-val">{{ m.hadH || '-' }}</span>
                </div>
                <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'd'), disabled: !m.hadD }" @click="m.hadD && selectBet(m, 'had', 'd')">
                  <span class="odds-label">平</span><span class="odds-val">{{ m.hadD || '-' }}</span>
                </div>
                <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'a'), disabled: !m.hadA }" @click="m.hadA && selectBet(m, 'had', 'a')">
                  <span class="odds-label">负</span><span class="odds-val">{{ m.hadA || '-' }}</span>
                </div>
              </div>
            </template>

            <template v-else-if="playType === 'hhad'">
              <div class="match-odds">
                <div class="handicap-tag">{{ m.handicapDisplay || '0' }}</div>
                <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'h'), disabled: !m.hhadH }" @click="m.hhadH && selectBet(m, 'hhad', 'h')">
                  <span class="odds-label">让胜</span><span class="odds-val">{{ m.hhadH || '-' }}</span>
                </div>
                <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'd'), disabled: !m.hhadD }" @click="m.hhadD && selectBet(m, 'hhad', 'd')">
                  <span class="odds-label">让平</span><span class="odds-val">{{ m.hhadD || '-' }}</span>
                </div>
                <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'a'), disabled: !m.hhadA }" @click="m.hhadA && selectBet(m, 'hhad', 'a')">
                  <span class="odds-label">让负</span><span class="odds-val">{{ m.hhadA || '-' }}</span>
                </div>
              </div>
            </template>

            <template v-else-if="playType === 'mix'">
              <div class="single-odds-wrap">
                <div class="single-odds-group" v-if="m.hadSelling && m.hadH">
                  <span class="single-type-tag">胜平负</span>
                  <div class="odds-cells">
                    <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'h') }" @click="selectBet(m, 'had', 'h')">
                      <span class="odds-label">胜</span><span class="odds-val">{{ m.hadH }}</span>
                    </div>
                    <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'd') }" @click="selectBet(m, 'had', 'd')">
                      <span class="odds-label">平</span><span class="odds-val">{{ m.hadD }}</span>
                    </div>
                    <div class="odds-cell" :class="{ selected: isSelected(m.matchId, 'had', 'a') }" @click="selectBet(m, 'had', 'a')">
                      <span class="odds-label">负</span><span class="odds-val">{{ m.hadA }}</span>
                    </div>
                  </div>
                </div>
                <div class="single-odds-group" v-if="m.hhadSelling && m.hhadH">
                  <span class="single-type-tag">让球({{ m.handicapDisplay }})</span>
                  <div class="odds-cells">
                    <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'h') }" @click="selectBet(m, 'hhad', 'h')">
                      <span class="odds-label">让胜</span><span class="odds-val">{{ m.hhadH }}</span>
                    </div>
                    <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'd') }" @click="selectBet(m, 'hhad', 'd')">
                      <span class="odds-label">让平</span><span class="odds-val">{{ m.hhadD }}</span>
                    </div>
                    <div class="odds-cell blue" :class="{ selected: isSelected(m.matchId, 'hhad', 'a') }" @click="selectBet(m, 'hhad', 'a')">
                      <span class="odds-label">让负</span><span class="odds-val">{{ m.hhadA }}</span>
                    </div>
                  </div>
                </div>
                <div class="single-odds-group" v-if="m.crsSelling && hasCrsOdds(m)">
                  <span class="single-type-tag">比分</span>
                  <div class="odds-cells score-cells">
                    <div v-for="sc in getScoreOptions(m)" :key="sc.key" class="score-cell" :class="{ selected: isSelected(m.matchId, 'crs', sc.key), disabled: !sc.odds }" @click="sc.odds && selectBet(m, 'crs', sc.key)">
                      <span class="score-label">{{ sc.label }}</span><span class="score-val">{{ sc.odds || '-' }}</span>
                    </div>
                  </div>
                </div>
                <div class="single-odds-group" v-if="m.ttgSelling && hasTtgOdds(m)">
                  <span class="single-type-tag">进球数</span>
                  <div class="odds-cells goal-cells">
                    <div v-for="g in getGoalOptions(m)" :key="g.key" class="goal-cell" :class="{ selected: isSelected(m.matchId, 'ttg', g.key), disabled: !g.odds }" @click="g.odds && selectBet(m, 'ttg', g.key)">
                      <span class="goal-label">{{ g.label }}</span><span class="goal-val">{{ g.odds || '-' }}</span>
                    </div>
                  </div>
                </div>
                <div class="single-odds-group" v-if="m.hafuSelling && hasHafuOdds(m)">
                  <span class="single-type-tag">半全场</span>
                  <div class="odds-cells hafu-cells">
                    <div v-for="hf in getHafuOptions(m)" :key="hf.key" class="hafu-cell" :class="{ selected: isSelected(m.matchId, 'hafu', hf.key), disabled: !hf.odds }" @click="hf.odds && selectBet(m, 'hafu', hf.key)">
                      <span class="hafu-label">{{ hf.label }}</span><span class="hafu-val">{{ hf.odds || '-' }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="playType === 'crs'">
              <div class="match-odds score-odds">
                <div class="score-grid">
                  <div v-for="sc in getScoreOptions(m)" :key="sc.key" class="score-cell" :class="{ selected: isSelected(m.matchId, 'crs', sc.key), disabled: !sc.odds }" @click="sc.odds && selectBet(m, 'crs', sc.key)">
                    <span class="score-label">{{ sc.label }}</span>
                    <span class="score-val">{{ sc.odds || '-' }}</span>
                  </div>
                </div>
              </div>
            </template>

            <template v-else-if="playType === 'ttg'">
              <div class="match-odds goal-odds">
                <div v-for="g in getGoalOptions(m)" :key="g.key" class="goal-cell" :class="{ selected: isSelected(m.matchId, 'ttg', g.key), disabled: !g.odds }" @click="g.odds && selectBet(m, 'ttg', g.key)">
                  <span class="goal-label">{{ g.label }}</span>
                  <span class="goal-val">{{ g.odds || '-' }}</span>
                </div>
              </div>
            </template>

            <template v-else-if="playType === 'hafu'">
              <div class="match-odds hafu-odds">
                <div v-for="hf in getHafuOptions(m)" :key="hf.key" class="hafu-cell" :class="{ selected: isSelected(m.matchId, 'hafu', hf.key), disabled: !hf.odds }" @click="hf.odds && selectBet(m, 'hafu', hf.key)">
                  <span class="hafu-label">{{ hf.label }}</span>
                  <span class="hafu-val">{{ hf.odds || '-' }}</span>
                </div>
              </div>
            </template>
          </div>
        </div>
      </template>
      <div v-else-if="!loading" class="empty">暂无赛事数据</div>
    </div>

    <div class="bet-slip" v-if="selectedBets.length">
      <div class="slip-toggle" @click="slipExpanded = !slipExpanded">
        <span class="slip-toggle-text">已选<b>{{ selectedBets.length }}</b>场</span>
        <span class="slip-toggle-arrow" :class="{ up: slipExpanded }">▼</span>
      </div>
      <div class="slip-detail" v-show="slipExpanded">
        <div class="slip-detail-header">
          <button class="slip-clear" @click="selectedBets = []">清空</button>
        </div>
        <div class="slip-list-scroll">
          <table class="slip-table" width="100%" border="0" cellpadding="0" cellspacing="0">
            <colgroup>
              <col width="24" /><col width="56" /><col /><col width="90" /><col width="70" />
            </colgroup>
            <thead><tr><th></th><th>编号</th><th>赛事</th><th>投注选项</th><th>预计奖金</th></tr></thead>
            <tbody>
              <tr v-for="(bet, i) in selectedBets" :key="i">
                <td><button class="row-del" @click="removeBet(i)" title="删除">✕</button></td>
                <td class="col-num">{{ bet.matchNum }}</td>
                <td class="col-match"><span class="match-home">{{ bet.homeTeam }}</span><span class="match-vs">VS</span><span class="match-away">{{ bet.awayTeam }}</span></td>
                <td class="col-pick"><a class="pick-tag" @click="removeBet(i)">{{ bet.pickLabel }}@{{ bet.odds }}</a></td>
                <td class="col-prize"><span class="prize-val">￥{{ bet.prize }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="slip-guog" v-if="playType !== 'single'">
        <span class="guog-label">过关方式：</span>
        <span v-if="selectedBets.length < 2" class="guog-tip">请至少选择两场比赛</span>
        <template v-else>
          <span v-for="g in availableGuog" :key="g" class="guog-item" :class="{ active: selectedGuog.includes(g) }" @click="toggleGuog(g)">
            <span class="chkbox"></span> {{ g }}
          </span>
          <span class="guog-more" @click="showMoreGuog = !showMoreGuog">
            <span class="guog-more-tit">更多过关</span>
            <span class="guog-more-arrow" :class="{ up: showMoreGuog }">▼</span>
          </span>
          <div class="guog-more-panel" v-if="showMoreGuog">
            <template v-for="group in moreGuogGroups" :key="group[0]">
              <div class="guog-more-row" v-if="group.some(g => isGuogAvailable(g))">
                <span v-for="g in group" :key="g" v-show="isGuogAvailable(g)" class="guog-item" :class="{ active: selectedGuog.includes(g) }" @click="toggleGuog(g)">
                  <span class="chkbox"></span> {{ g }}
                </span>
              </div>
            </template>
          </div>
        </template>
      </div>
      <div class="slip-footer">
        <div class="slip-multiply">
          <span>倍数：</span>
          <button class="mul-btn" @click="multiply = Math.max(1, multiply - 1)">－</button>
          <input type="text" v-model.number="multiply" class="mul-input" />
          <button class="mul-btn" @click="multiply = multiply + 1">＋</button>
        </div>
        <div class="slip-summary">
          <span class="summary-bets">共{{ totalBets }}注</span>
          <span class="summary-amount">金额：<b>{{ totalBetAmount }}</b>元</span>
          <span class="summary-prize">预计奖金：<b class="red">￥{{ potentialWin }}</b></span>
        </div>
        <button class="place-bet-btn" @click="placeBet">确认投注</button>
      </div>
    </div>

    <div class="bet-history" v-if="betHistory.length">
      <div class="history-header">
        <span>投注记录</span>
        <button class="history-clear" @click="betHistory = []">清空</button>
      </div>
      <table class="history-table" width="100%" border="0" cellpadding="0" cellspacing="1" bgcolor="#dddddd">
        <tr bgcolor="#ECF4FB" class="bui"><td>场次</td><td>玩法</td><td>选项</td><td>赔率</td><td>投注</td><td>预计奖金</td><td>状态</td></tr>
        <tr v-for="(b, i) in betHistory" :key="i" bgcolor="#FFFFFF" class="odds">
          <td>{{ b.matchLabel }}</td><td>{{ b.typeLabel }}</td><td>{{ b.pickLabel }}</td><td>{{ b.odds }}</td><td>{{ b.amount }}元</td><td>{{ b.potentialWin }}元</td><td :class="b.status">{{ b.statusLabel }}</td>
        </tr>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { SmartCache, BackgroundRefresher, REFRESH_INTERVAL, CACHE_STRATEGY } from '../../utils/fiveMatchMapper'

const loading = ref(false)
const matches = ref([])
const updateTime = ref('')
const playType = ref('single')
const slipExpanded = ref(false)
const showMoreGuog = ref(false)
const selectedGuog = ref([])
const betAmount = ref(2)
const multiply = ref(10)
const selectedBets = ref([])
const betHistory = ref([])

const jcBetCache = new SmartCache('jc_bet', CACHE_STRATEGY.titanMatches)
const jcBetRefresher = new BackgroundRefresher()

const PLAY_LABELS = { had: '胜平负', hhad: '让球胜平负', crs: '比分', ttg: '进球数', hafu: '半全场' }
const HAD_PICKS = { h: '胜', d: '平', a: '负' }
const HHAD_PICKS = { h: '让胜', d: '让平', a: '让负' }
const CRS_PICKS = {
  's01s00': '1:0', 's02s00': '2:0', 's02s01': '2:1', 's03s00': '3:0', 's03s01': '3:1', 's03s02': '3:2',
  's04s00': '4:0', 's04s01': '4:1', 's04s02': '4:2', 's05s00': '5:0', 's05s01': '5:1', 's05s02': '5:2',
  's00s00': '0:0', 's01s01': '1:1', 's02s02': '2:2', 's03s03': '3:3',
  's00s01': '0:1', 's00s02': '0:2', 's01s02': '1:2', 's00s03': '0:3', 's01s03': '1:3', 's02s03': '2:3',
  's00s04': '0:4', 's01s04': '1:4', 's02s04': '2:4', 's00s05': '0:5', 's01s05': '1:5', 's02s05': '2:5',
  's1sh': '胜其他', 's1sd': '平其他', 's1sa': '负其他',
}
const TTG_PICKS = { 's0': '0球', 's1': '1球', 's2': '2球', 's3': '3球', 's4': '4球', 's5': '5球', 's6': '6球', 's7': '7+球' }
const HAFU_PICKS = { 'hh': '胜胜', 'hd': '胜平', 'ha': '胜负', 'dh': '平胜', 'dd': '平平', 'da': '平负', 'ah': '负胜', 'ad': '负平', 'aa': '负负' }

const CRS_ODDS_KEYS = ['s01s00','s02s00','s02s01','s03s00','s03s01','s03s02','s04s00','s04s01','s04s02','s05s00','s05s01','s05s02','s00s00','s01s01','s02s02','s03s03','s00s01','s00s02','s01s02','s00s03','s01s03','s02s03','s00s04','s01s04','s02s04','s00s05','s01s05','s02s05','s1sh','s1sd','s1sa']
const TTG_ODDS_KEYS = ['s0','s1','s2','s3','s4','s5','s6','s7']
const HAFU_ODDS_KEYS = ['hh','hd','ha','dh','dd','da','ah','ad','aa']

function C(n, m) { if (m < 0 || m > n) return 0; if (m === 0 || m === n) return 1; let r = 1; for (let i = 0; i < m; i++) r = r * (n - i) / (i + 1); return Math.round(r) }

const GUOG_MAP = {
  '2串1': { n: 2, combos: [[2]] }, '3串1': { n: 3, combos: [[3]] }, '3串3': { n: 3, combos: [[2, 2, 2]] }, '3串4': { n: 3, combos: [[3], [2, 2, 2]] },
  '4串1': { n: 4, combos: [[4]] }, '4串4': { n: 4, combos: [[3, 3, 3, 3]] }, '4串5': { n: 4, combos: [[4], [3, 3, 3, 3]] }, '4串6': { n: 4, combos: [[2]] }, '4串11': { n: 4, combos: [[4], [3, 3, 3, 3], [2]] },
  '5串1': { n: 5, combos: [[5]] }, '5串5': { n: 5, combos: [[4]] }, '5串6': { n: 5, combos: [[5], [4]] }, '5串10': { n: 5, combos: [[3]] }, '5串16': { n: 5, combos: [[5], [4], [3]] }, '5串20': { n: 5, combos: [[3], [2]] }, '5串26': { n: 5, combos: [[5], [4], [3], [2]] },
  '6串1': { n: 6, combos: [[6]] }, '6串6': { n: 6, combos: [[5]] }, '6串7': { n: 6, combos: [[6], [5]] }, '6串15': { n: 6, combos: [[4]] }, '6串20': { n: 6, combos: [[3]] }, '6串22': { n: 6, combos: [[6], [5], [4]] }, '6串35': { n: 6, combos: [[4], [3]] }, '6串42': { n: 6, combos: [[6], [5], [4], [3]] }, '6串50': { n: 6, combos: [[5], [4], [3], [2]] }, '6串57': { n: 6, combos: [[6], [5], [4], [3], [2]] },
  '7串1': { n: 7, combos: [[7]] }, '8串1': { n: 8, combos: [[8]] },
}
const MAIN_GUOG = ['2串1', '3串1', '4串1', '5串1', '6串1', '7串1', '8串1']
const MORE_GUOG_GROUPS = [
  ['7串1', '8串1'], ['3串3', '3串4'], ['4串4', '4串5', '4串6', '4串11'],
  ['5串5', '5串6', '5串10', '5串16', '5串20', '5串26'],
  ['6串6', '6串7', '6串15', '6串20', '6串22', '6串35', '6串42', '6串50', '6串57'],
]

const availableGuog = computed(() => MAIN_GUOG.filter(g => (GUOG_MAP[g]?.n || 0) <= selectedBets.value.length))
const moreGuogGroups = computed(() => MORE_GUOG_GROUPS)
function isGuogAvailable(g) { return (GUOG_MAP[g]?.n || 0) <= selectedBets.value.length }
function toggleGuog(g) { const idx = selectedGuog.value.indexOf(g); if (idx >= 0) selectedGuog.value.splice(idx, 1); else selectedGuog.value.push(g) }

function getGuogBets(guogType, n) {
  const info = GUOG_MAP[guogType]; if (!info || n < info.n) return 0
  let total = 0
  for (const combo of info.combos) { if (combo.length === 1 && combo[0] === info.n) total += 1; else if (combo.length === 1) total += C(n, combo[0]); else total += 1 }
  return total
}

const totalBets = computed(() => {
  const n = selectedBets.value.length
  if (playType.value === 'single') return n
  if (!selectedGuog.value.length) return 0
  let total = 0; for (const g of selectedGuog.value) total += getGuogBets(g, n); return total
})

function hasCrsOdds(m) {
  const c = m.crsOdds
  if (!c || !Object.keys(c).length) return false
  return CRS_ODDS_KEYS.some(k => c[k])
}

function hasTtgOdds(m) {
  const t = m.ttgOdds
  if (!t || !Object.keys(t).length) return false
  return TTG_ODDS_KEYS.some(k => t[k])
}

function hasHafuOdds(m) {
  const h = m.hafuOdds
  if (!h || !Object.keys(h).length) return false
  return HAFU_ODDS_KEYS.some(k => h[k])
}

const groupedMatches = computed(() => {
  const now = new Date()
  const bjOffset = 8 * 60 * 60 * 1000
  const bjNow = new Date(now.getTime() + bjOffset + now.getTimezoneOffset() * 60000)
  const bjToday = `${bjNow.getFullYear()}-${String(bjNow.getMonth() + 1).padStart(2, '0')}-${String(bjNow.getDate()).padStart(2, '0')}`
  const groups = {}
  for (const m of matches.value) {
    if (!m.matchSelling) continue
    if (m.date < bjToday) continue
    if (m.matchStartTime && m.matchStartTime <= now) continue
    let show = false
    if (playType.value === 'single') {
      show = (m.hadSelling && m.hadSingle && m.hadH) || (m.hhadSelling && m.hhadSingle && m.hhadH)
    } else if (playType.value === 'had') {
      show = m.hadSelling && !!m.hadH
    } else if (playType.value === 'hhad') {
      show = m.hhadSelling && !!m.hhadH
    } else if (playType.value === 'mix') {
      show = (m.hadSelling && !!m.hadH) || (m.hhadSelling && !!m.hhadH) || (m.crsSelling && hasCrsOdds(m)) || (m.ttgSelling && hasTtgOdds(m)) || (m.hafuSelling && hasHafuOdds(m))
    } else if (playType.value === 'crs') {
      show = m.crsSelling && hasCrsOdds(m)
    } else if (playType.value === 'ttg') {
      show = m.ttgSelling && hasTtgOdds(m)
    } else if (playType.value === 'hafu') {
      show = m.hafuSelling && hasHafuOdds(m)
    }
    if (!show) continue
    if (!groups[m.date]) groups[m.date] = { date: m.date, label: m.dateLabel, matches: [] }
    groups[m.date].matches.push(m)
  }
  return Object.values(groups).filter(g => g.matches.length > 0)
})

function switchPlay(type) {
  playType.value = type
  selectedBets.value = []
  selectedGuog.value = []
  showMoreGuog.value = false
  fetchData()
}

function getPoolCode(type) {
  if (type === 'single') return 'had,hhad'
  if (type === 'had') return 'had'
  if (type === 'hhad') return 'hhad'
  if (type === 'mix') return 'had,hhad,crs,ttg,hafu'
  if (type === 'crs') return 'crs'
  if (type === 'ttg') return 'ttg'
  if (type === 'hafu') return 'hafu'
  return 'had'
}

async function fetchData() {
  const poolCode = getPoolCode(playType.value)
  const cacheKey = `jc_${poolCode}`

  // 先查缓存
  const cached = jcBetCache.get(cacheKey)
  if (cached) {
    matches.value = cached.matches
    updateTime.value = cached.updateTime
    loading.value = false
  } else {
    loading.value = true
  }

  try {
    const url = `/sporttery-proxy/gateway/jc/football/getMatchCalculatorV1.qry?poolCode=${poolCode}&channel=c`
    const resp = await fetch(url)
    const data = await resp.json()
    if (data.value) {
      const newUpdateTime = extractUpdateTime(data.value)
      const newMatches = parseMatches(data.value)
      updateTime.value = newUpdateTime
      matches.value = newMatches

      // 存入缓存
      jcBetCache.set(cacheKey, { matches: newMatches, updateTime: newUpdateTime })

      // 启动后台静默刷新
      startJcBetRefresh(poolCode)
    }
  } catch (e) {
    console.warn('获取竞彩数据失败:', e)
  } finally {
    loading.value = false
  }
}

function startJcBetRefresh(poolCode) {
  const cacheKey = `jc_${poolCode}`
  jcBetRefresher.stop(cacheKey)
  jcBetRefresher.start(
    cacheKey,
    async () => {
      const url = `/sporttery-proxy/gateway/jc/football/getMatchCalculatorV1.qry?poolCode=${poolCode}&channel=c`
      const resp = await fetch(url)
      const data = await resp.json()
      if (data.value) {
        return {
          matches: parseMatches(data.value),
          updateTime: extractUpdateTime(data.value),
        }
      }
      return null
    },
    jcBetCache,
    REFRESH_INTERVAL.titanMatches.normal,
    (freshData) => {
      if (freshData) {
        matches.value = freshData.matches
        updateTime.value = freshData.updateTime
      }
    }
  )
}

function extractUpdateTime(value) {
  const list = value.matchInfoList || []
  for (const g of list) {
    for (const m of (g.subMatchList || [])) {
      if (m.had?.updateTime) return (m.had.updateDate || '') + ' ' + m.had.updateTime
      if (m.hhad?.updateTime) return (m.hhad.updateDate || '') + ' ' + m.hhad.updateTime
      if (m.crs?.updateTime) return (m.crs.updateDate || '') + ' ' + m.crs.updateTime
      if (m.ttg?.updateTime) return (m.ttg.updateDate || '') + ' ' + m.ttg.updateTime
      if (m.hafu?.updateTime) return (m.hafu.updateDate || '') + ' ' + m.hafu.updateTime
    }
  }
  return ''
}

function parseMatches(value) {
  const result = []
  const matchInfoList = value.matchInfoList || []
  for (const group of matchInfoList) {
    const date = group.businessDate || ''
    const dateLabel = group.businessDate || ''
    for (const m of (group.subMatchList || [])) {
      const matchNum = m.matchNumStr || ''
      const leagueName = m.leagueAbbName || ''
      const homeTeam = m.homeTeamAbbName || ''
      const awayTeam = m.awayTeamAbbName || ''
      const matchTime = (m.matchTime || '').replace(/:00$/, '')
      const matchId = m.matchId || `${date}_${matchNum}`
      const matchDate = m.matchDate || ''
      const matchFullTime = m.matchTime || ''
      const matchStartTime = matchDate && matchFullTime ? new Date(`${matchDate}T${matchFullTime}+08:00`) : null

      let handicap = m.hhad?.goalLine || '0'
      let handicapDisplay = handicap
      if (handicap && Number(handicap) > 0) handicapDisplay = '+' + handicap

      const poolList = m.poolList || []
      const hadPool = poolList.find(p => p.poolCode === 'HAD')
      const hhadPool = poolList.find(p => p.poolCode === 'HHAD')
      const crsPool = poolList.find(p => p.poolCode === 'CRS')
      const ttgPool = poolList.find(p => p.poolCode === 'TTG')
      const hafuPool = poolList.find(p => p.poolCode === 'HAFU')

      const hadH = m.had?.h && m.had.h !== '0' ? m.had.h : ''
      const hadD = m.had?.d && m.had.d !== '0' ? m.had.d : ''
      const hadA = m.had?.a && m.had.a !== '0' ? m.had.a : ''
      const hhadH = m.hhad?.h && m.hhad.h !== '0' ? m.hhad.h : ''
      const hhadD = m.hhad?.d && m.hhad.d !== '0' ? m.hhad.d : ''
      const hhadA = m.hhad?.a && m.hhad.a !== '0' ? m.hhad.a : ''

      const crsOdds = {}
      if (m.crs) {
        for (const k of CRS_ODDS_KEYS) {
          if (m.crs[k] && m.crs[k] !== '0') crsOdds[k] = m.crs[k]
        }
      }
      const ttgOdds = {}
      if (m.ttg) {
        for (const k of TTG_ODDS_KEYS) {
          if (m.ttg[k] && m.ttg[k] !== '0') ttgOdds[k] = m.ttg[k]
        }
      }
      const hafuOdds = {}
      if (m.hafu) {
        for (const k of HAFU_ODDS_KEYS) {
          if (m.hafu[k] && m.hafu[k] !== '0') hafuOdds[k] = m.hafu[k]
        }
      }

      result.push({
        matchId, matchNum, leagueName, homeTeam, awayTeam, matchTime,
        date, dateLabel, handicap, handicapDisplay,
        matchStartTime,
        matchSelling: m.matchStatus === 'Selling',
        hadH, hadD, hadA,
        hadSelling: hadPool?.poolStatus === 'Selling',
        hadSingle: hadPool?.bettingSingle === 1,
        hhadH, hhadD, hhadA,
        hhadSelling: hhadPool?.poolStatus === 'Selling',
        hhadSingle: hhadPool?.bettingSingle === 1,
        crsSelling: crsPool?.poolStatus === 'Selling',
        crsSingle: crsPool?.bettingSingle === 1,
        ttgSelling: ttgPool?.poolStatus === 'Selling',
        ttgSingle: ttgPool?.bettingSingle === 1,
        hafuSelling: hafuPool?.poolStatus === 'Selling',
        hafuSingle: hafuPool?.bettingSingle === 1,
        crsOdds, ttgOdds, hafuOdds,
      })
    }
  }
  return result
}

function getScoreOptions(m) {
  const c = m.crsOdds
  return [
    { key: 's01s00', label: '1:0', odds: c?.s01s00 }, { key: 's02s00', label: '2:0', odds: c?.s02s00 }, { key: 's02s01', label: '2:1', odds: c?.s02s01 },
    { key: 's03s00', label: '3:0', odds: c?.s03s00 }, { key: 's03s01', label: '3:1', odds: c?.s03s01 }, { key: 's03s02', label: '3:2', odds: c?.s03s02 },
    { key: 's04s00', label: '4:0', odds: c?.s04s00 }, { key: 's04s01', label: '4:1', odds: c?.s04s01 }, { key: 's04s02', label: '4:2', odds: c?.s04s02 },
    { key: 's05s00', label: '5:0', odds: c?.s05s00 }, { key: 's05s01', label: '5:1', odds: c?.s05s01 }, { key: 's05s02', label: '5:2', odds: c?.s05s02 },
    { key: 's00s00', label: '0:0', odds: c?.s00s00 }, { key: 's01s01', label: '1:1', odds: c?.s01s01 }, { key: 's02s02', label: '2:2', odds: c?.s02s02 }, { key: 's03s03', label: '3:3', odds: c?.s03s03 },
    { key: 's00s01', label: '0:1', odds: c?.s00s01 }, { key: 's00s02', label: '0:2', odds: c?.s00s02 }, { key: 's01s02', label: '1:2', odds: c?.s01s02 },
    { key: 's00s03', label: '0:3', odds: c?.s00s03 }, { key: 's01s03', label: '1:3', odds: c?.s01s03 }, { key: 's02s03', label: '2:3', odds: c?.s02s03 },
    { key: 's00s04', label: '0:4', odds: c?.s00s04 }, { key: 's01s04', label: '1:4', odds: c?.s01s04 }, { key: 's02s04', label: '2:4', odds: c?.s02s04 },
    { key: 's00s05', label: '0:5', odds: c?.s00s05 }, { key: 's01s05', label: '1:5', odds: c?.s01s05 }, { key: 's02s05', label: '2:5', odds: c?.s02s05 },
    { key: 's1sh', label: '胜其他', odds: c?.s1sh }, { key: 's1sd', label: '平其他', odds: c?.s1sd }, { key: 's1sa', label: '负其他', odds: c?.s1sa },
  ]
}

function getGoalOptions(m) {
  const t = m.ttgOdds
  return [
    { key: 's0', label: '0球', odds: t?.s0 }, { key: 's1', label: '1球', odds: t?.s1 }, { key: 's2', label: '2球', odds: t?.s2 }, { key: 's3', label: '3球', odds: t?.s3 },
    { key: 's4', label: '4球', odds: t?.s4 }, { key: 's5', label: '5球', odds: t?.s5 }, { key: 's6', label: '6球', odds: t?.s6 }, { key: 's7', label: '7+球', odds: t?.s7 },
  ]
}

function getHafuOptions(m) {
  const h = m.hafuOdds
  return [
    { key: 'hh', label: '胜胜', odds: h?.hh }, { key: 'hd', label: '胜平', odds: h?.hd }, { key: 'ha', label: '胜负', odds: h?.ha },
    { key: 'dh', label: '平胜', odds: h?.dh }, { key: 'dd', label: '平平', odds: h?.dd }, { key: 'da', label: '平负', odds: h?.da },
    { key: 'ah', label: '负胜', odds: h?.ah }, { key: 'ad', label: '负平', odds: h?.ad }, { key: 'aa', label: '负负', odds: h?.aa },
  ]
}

function isSelected(matchId, type, pick) { return selectedBets.value.some(b => b.matchId === matchId && b.type === type && b.pick === pick) }

function selectBet(match, type, pick) {
  const idx = selectedBets.value.findIndex(b => b.matchId === match.matchId && b.type === type && b.pick === pick)
  if (idx >= 0) { selectedBets.value.splice(idx, 1); return }
  if (playType.value === 'single') {
    const existingSameType = selectedBets.value.findIndex(b => b.matchId === match.matchId && b.type === type)
    if (existingSameType >= 0) selectedBets.value.splice(existingSameType, 1)
  } else if (playType.value === 'mix') {
    const existingSameType = selectedBets.value.findIndex(b => b.matchId === match.matchId && b.type === type)
    if (existingSameType >= 0) selectedBets.value.splice(existingSameType, 1)
  } else {
    const existingIdx = selectedBets.value.findIndex(b => b.matchId === match.matchId && b.type === type)
    if (existingIdx >= 0) selectedBets.value.splice(existingIdx, 1)
  }
  let odds = '', pickLabel = ''
  if (type === 'had') { odds = pick === 'h' ? match.hadH : pick === 'd' ? match.hadD : match.hadA; pickLabel = HAD_PICKS[pick] }
  else if (type === 'hhad') { odds = pick === 'h' ? match.hhadH : pick === 'd' ? match.hhadD : match.hhadA; pickLabel = HHAD_PICKS[pick] }
  else if (type === 'crs') { odds = getScoreOptions(match).find(s => s.key === pick)?.odds || ''; pickLabel = CRS_PICKS[pick] || pick }
  else if (type === 'ttg') { odds = getGoalOptions(match).find(g => g.key === pick)?.odds || ''; pickLabel = TTG_PICKS[pick] || pick }
  else if (type === 'hafu') { odds = getHafuOptions(match).find(hf => hf.key === pick)?.odds || ''; pickLabel = HAFU_PICKS[pick] || pick }
  selectedBets.value.push({
    matchId: match.matchId, matchNum: match.matchNum, homeTeam: match.homeTeam, awayTeam: match.awayTeam,
    matchLabel: `${match.matchNum} ${match.homeTeam}VS${match.awayTeam}`,
    type, pick, odds: odds || '0', pickLabel, typeLabel: PLAY_LABELS[type],
    prize: odds ? (betAmount.value * multiply.value * Number(odds)).toFixed(2) : '0.00',
  })
}

function removeBet(idx) { selectedBets.value.splice(idx, 1) }

const totalBetAmount = computed(() => (betAmount.value * multiply.value * totalBets.value).toFixed(0))

const potentialWin = computed(() => {
  if (!selectedBets.value.length) return '0.00'
  if (playType.value === 'single') {
    let total = 0; for (const b of selectedBets.value) total += betAmount.value * multiply.value * Number(b.odds); return total.toFixed(2)
  }
  if (!selectedGuog.value.length) return '0.00'
  const oddsList = selectedBets.value.map(b => Number(b.odds) || 1)
  let totalWin = 0
  for (const g of selectedGuog.value) {
    const info = GUOG_MAP[g]; if (!info || oddsList.length < info.n) continue
    for (const combo of info.combos) {
      if (combo.length === 1 && combo[0] === info.n) { totalWin += oddsList.reduce((a, b) => a * b, 1) }
      else if (combo.length === 1) { const indices = combinations(oddsList.length, combo[0]); for (const idx of indices) totalWin += idx.reduce((a, i) => a * oddsList[i], 1) }
      else { totalWin += combo.reduce((a, odds) => a + odds, 0) }
    }
  }
  return (betAmount.value * multiply.value * totalWin).toFixed(2)
})

function combinations(n, m) { const result = []; function bt(s, c) { if (c.length === m) { result.push([...c]); return } for (let i = s; i < n; i++) { c.push(i); bt(i + 1, c); c.pop() } } bt(0, []); return result }

function placeBet() {
  if (!selectedBets.value.length) return
  const amount = betAmount.value * multiply.value
  for (const bet of selectedBets.value) {
    betHistory.value.unshift({ matchLabel: bet.matchLabel, typeLabel: bet.typeLabel, pickLabel: bet.pickLabel, odds: bet.odds, amount, potentialWin: (amount * Number(bet.odds)).toFixed(2), status: 'pending', statusLabel: '待开奖' })
  }
  selectedBets.value = []; selectedGuog.value = []
}

onMounted(() => { fetchData() })
onUnmounted(() => { jcBetRefresher.stopAll() })
</script>

<style scoped>
.jc-bet-panel { font-size: 12px; padding: 0; background: #fff; display: flex; flex-direction: column; height: 100%; overflow: hidden; }
.bet-header { display: flex; align-items: center; gap: 10px; padding: 8px 12px; background: linear-gradient(135deg, #c4270c, #e84e0e); color: #fff; flex-shrink: 0; }
.bet-title { font-size: 14px; font-weight: bold; letter-spacing: 1px; }
.bet-update { font-size: 11px; opacity: 0.8; flex: 1; }
.refresh-btn { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.4); color: #fff; padding: 2px 10px; border-radius: 3px; cursor: pointer; font-size: 11px; }
.refresh-btn:hover { background: rgba(255,255,255,0.3); }

.play-nav { display: flex; background: #f5f5f5; border-bottom: 2px solid #c4270c; flex-shrink: 0; overflow-x: auto; }
.play-nav a { display: block; padding: 8px 12px; font-size: 12px; color: #333; cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all 0.2s; text-decoration: none; white-space: nowrap; }
.play-nav a:hover { color: #c4270c; background: #fff5f0; }
.play-nav a.active { color: #c4270c; font-weight: bold; border-bottom-color: #c4270c; background: #fff; }

.match-list { flex: 1; overflow-y: auto; min-height: 0; }
.date-group { border-bottom: 1px solid #eee; }
.date-header { display: flex; align-items: center; gap: 6px; padding: 6px 12px; background: #fafafa; font-size: 12px; font-weight: bold; color: #333; border-bottom: 1px solid #eee; }
.match-count { font-weight: normal; color: #999; margin-left: auto; }

.match-row { display: flex; align-items: center; padding: 6px 12px; border-bottom: 1px solid #f0f0f0; transition: background 0.15s; }
.match-row:hover { background: #fafafa; }
.match-row:nth-child(even) { background: #fcfcfc; }

.match-row-single, .match-row-mix { flex-wrap: wrap; align-items: flex-start; }

.match-info { width: 120px; flex-shrink: 0; display: flex; flex-direction: column; gap: 1px; }
.match-num { font-weight: bold; color: #c4270c; font-size: 11px; }
.match-league { font-size: 11px; color: #666; }
.match-time { font-size: 11px; color: #999; }

.match-teams { width: 140px; flex-shrink: 0; display: flex; align-items: center; gap: 4px; }
.team-home { font-size: 12px; font-weight: 600; color: #333; text-align: right; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.vs { font-size: 10px; color: #999; flex-shrink: 0; }
.team-away { font-size: 12px; font-weight: 600; color: #333; text-align: left; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.match-odds { flex: 1; display: flex; gap: 4px; align-items: center; justify-content: center; }
.odds-group { display: flex; gap: 4px; align-items: center; }
.odds-divider { width: 1px; height: 28px; background: #ddd; margin: 0 4px; flex-shrink: 0; }
.odds-cell { flex: 1; max-width: 80px; display: flex; flex-direction: column; align-items: center; padding: 4px 6px; border: 1px solid #eee; border-radius: 4px; cursor: pointer; transition: all 0.15s; background: #fff; }
.odds-cell:hover { border-color: #c4270c; background: #fff5f0; }
.odds-cell.selected { border-color: #c4270c; background: #ffe0b2; }
.odds-cell.disabled { cursor: not-allowed; opacity: 0.5; }
.odds-cell.blue { background: #f0f7ff; }
.odds-cell.blue:hover { border-color: #c4270c; background: #e0efff; }
.odds-cell.blue.selected { background: #ffe0b2; }
.odds-label { font-size: 11px; color: #999; }
.odds-val { font-size: 13px; font-weight: bold; color: #c4270c; }
.odds-cell.selected .odds-label { color: #c4270c; font-weight: 600; }
.handicap-tag { width: 30px; text-align: center; font-size: 11px; font-weight: bold; color: #c4270c; background: #fff3e0; padding: 2px 0; border-radius: 3px; flex-shrink: 0; }

.single-odds-wrap { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.single-odds-group { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.single-type-tag { font-size: 10px; color: #fff; background: #c4270c; padding: 1px 6px; border-radius: 2px; flex-shrink: 0; white-space: nowrap; }
.odds-cells { display: flex; gap: 3px; flex-wrap: wrap; }

.score-odds { flex-wrap: wrap; }
.score-grid { display: flex; flex-wrap: wrap; gap: 3px; width: 100%; }
.score-cell { display: flex; flex-direction: column; align-items: center; padding: 2px 4px; border: 1px solid #eee; border-radius: 3px; cursor: pointer; min-width: 42px; transition: all 0.15s; background: #fff; }
.score-cell:hover { border-color: #c4270c; background: #fff5f0; }
.score-cell.selected { border-color: #c4270c; background: #ffe0b2; }
.score-cell.disabled { cursor: not-allowed; opacity: 0.5; }
.score-label { font-size: 10px; color: #666; }
.score-val { font-size: 11px; font-weight: bold; color: #c4270c; }

.goal-odds { flex-wrap: wrap; }
.goal-cell { display: flex; flex-direction: column; align-items: center; padding: 3px 6px; border: 1px solid #eee; border-radius: 3px; cursor: pointer; min-width: 48px; transition: all 0.15s; background: #fff; }
.goal-cell:hover { border-color: #c4270c; background: #fff5f0; }
.goal-cell.selected { border-color: #c4270c; background: #ffe0b2; }
.goal-cell.disabled { cursor: not-allowed; opacity: 0.5; }
.goal-label { font-size: 10px; color: #666; }
.goal-val { font-size: 11px; font-weight: bold; color: #c4270c; }

.hafu-odds { flex-wrap: wrap; }
.hafu-cell { display: flex; flex-direction: column; align-items: center; padding: 3px 6px; border: 1px solid #eee; border-radius: 3px; cursor: pointer; min-width: 48px; transition: all 0.15s; background: #fff; }
.hafu-cell:hover { border-color: #c4270c; background: #fff5f0; }
.hafu-cell.selected { border-color: #c4270c; background: #ffe0b2; }
.hafu-cell.disabled { cursor: not-allowed; opacity: 0.5; }
.hafu-label { font-size: 10px; color: #666; }
.hafu-val { font-size: 11px; font-weight: bold; color: #c4270c; }

.empty { color: #999; text-align: center; padding: 40px 0; font-size: 14px; }

.bet-slip { flex-shrink: 0; border-top: 2px solid #c4270c; background: #fff; }
.slip-toggle { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; background: #c4270c; color: #fff; cursor: pointer; font-size: 13px; font-weight: bold; }
.slip-toggle:hover { background: #d63218; }
.slip-toggle-text b { font-size: 16px; margin: 0 2px; }
.slip-toggle-arrow { font-size: 10px; transition: transform 0.2s; }
.slip-toggle-arrow.up { transform: rotate(180deg); }
.slip-detail { border-bottom: 1px solid #eee; }
.slip-detail-header { display: flex; justify-content: flex-end; padding: 4px 10px; background: #fafafa; }
.slip-clear { background: none; border: none; color: #c4270c; cursor: pointer; font-size: 11px; text-decoration: underline; }
.slip-clear:hover { color: #a01e08; }
.slip-list-scroll { max-height: 200px; overflow-y: auto; }
.slip-table { border-collapse: collapse; font-size: 12px; }
.slip-table th { background: #f5f5f5; padding: 4px 6px; text-align: center; font-weight: normal; color: #999; border-bottom: 1px solid #eee; font-size: 11px; }
.slip-table td { padding: 5px 6px; border-bottom: 1px solid #f0f0f0; vertical-align: middle; }
.row-del { background: none; border: none; color: #ccc; cursor: pointer; font-size: 12px; padding: 0; }
.row-del:hover { color: #f56c6c; }
.col-num { color: #c4270c; font-weight: bold; text-align: center; font-size: 11px; }
.col-match { font-size: 11px; }
.col-match .match-home { color: #333; }
.col-match .match-vs { color: #ccc; font-size: 10px; margin: 0 2px; }
.col-match .match-away { color: #333; }
.col-pick { text-align: center; }
.pick-tag { display: inline-block; padding: 2px 8px; background: #fff3e0; color: #c4270c; border-radius: 3px; font-size: 11px; cursor: pointer; text-decoration: none; }
.pick-tag:hover { background: #ffe0b2; }
.col-prize { text-align: center; }
.prize-val { color: #c4270c; font-weight: bold; font-size: 12px; }

.slip-guog { padding: 6px 10px; background: #fafafa; border-top: 1px solid #eee; font-size: 12px; color: #333; display: flex; flex-wrap: wrap; align-items: center; gap: 4px; }
.guog-label { color: #999; flex-shrink: 0; }
.guog-tip { color: #c4270c; font-size: 11px; }
.guog-item { display: inline-flex; align-items: center; gap: 3px; padding: 2px 8px; border: 1px solid #dcdfe6; border-radius: 3px; cursor: pointer; font-size: 11px; color: #333; background: #fff; transition: all 0.15s; user-select: none; }
.guog-item:hover { border-color: #c4270c; color: #c4270c; }
.guog-item.active { border-color: #c4270c; background: #fff3e0; color: #c4270c; }
.guog-item .chkbox { width: 12px; height: 12px; border: 1px solid #bbb; border-radius: 2px; display: inline-block; position: relative; }
.guog-item.active .chkbox { border-color: #c4270c; background: #c4270c; }
.guog-item.active .chkbox::after { content: ''; position: absolute; left: 3px; top: 1px; width: 4px; height: 7px; border: solid #fff; border-width: 0 1.5px 1.5px 0; transform: rotate(45deg); }
.guog-more { display: inline-flex; align-items: center; gap: 2px; padding: 2px 8px; cursor: pointer; font-size: 11px; color: #409eff; user-select: none; }
.guog-more:hover { color: #66b1ff; }
.guog-more-arrow { font-size: 9px; transition: transform 0.2s; }
.guog-more-arrow.up { transform: rotate(180deg); }
.guog-more-panel { width: 100%; background: #fff; border: 1px solid #eee; border-radius: 4px; padding: 6px; margin-top: 4px; display: flex; flex-wrap: wrap; gap: 4px; }
.guog-more-row { display: flex; flex-wrap: wrap; gap: 4px; width: 100%; }

.slip-footer { display: flex; align-items: center; gap: 10px; padding: 6px 10px; background: #fafafa; border-top: 1px solid #eee; }
.slip-multiply { display: flex; align-items: center; gap: 3px; font-size: 12px; color: #333; flex-shrink: 0; }
.mul-btn { width: 22px; height: 22px; border: 1px solid #dcdfe6; background: #fff; border-radius: 2px; cursor: pointer; font-size: 12px; color: #666; display: flex; align-items: center; justify-content: center; }
.mul-btn:hover { background: #f5f5f5; }
.mul-input { width: 36px; height: 22px; text-align: center; border: 1px solid #dcdfe6; border-radius: 2px; font-size: 12px; }
.mul-input:focus { outline: none; border-color: #c4270c; }
.slip-summary { display: flex; align-items: center; gap: 10px; font-size: 11px; color: #666; flex: 1; }
.summary-amount b { color: #333; }
.summary-prize .red { color: #c4270c; font-size: 13px; }
.place-bet-btn { padding: 6px 20px; font-size: 13px; font-weight: bold; color: #fff; background: linear-gradient(135deg, #c4270c, #e84e0e); border: none; border-radius: 4px; cursor: pointer; transition: opacity 0.2s; flex-shrink: 0; }
.place-bet-btn:hover { opacity: 0.9; }

.bet-history { margin: 12px; }
.history-header { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 13px; font-weight: bold; color: #333; }
.history-clear { background: none; border: 1px solid #dcdfe6; color: #999; padding: 1px 8px; border-radius: 3px; cursor: pointer; font-size: 11px; }
.history-clear:hover { border-color: #f56c6c; color: #f56c6c; }
.history-table { border-collapse: collapse; }
.history-table td { border: 1px solid #ddd; padding: 4px 6px; text-align: center; font-size: 11px; color: #333; }
.bui td { background: #ECF4FB; }
.odds td { background: #FFFFFF; }
.history-table td.pending { color: #e6a23c; }
.history-table td.won { color: #67c23a; font-weight: bold; }
.history-table td.lost { color: #f56c6c; }
</style>
