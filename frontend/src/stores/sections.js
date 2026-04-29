import { defineStore } from 'pinia'

const TITAN_SECTIONS = [
  { key: 'odds_trend', label: '即时指数', visible: true, group: '赔率数据' },
  { key: 'jc_index', label: '竞足数据', visible: true, group: '赔率数据' },
  { key: 'standings', label: '积分排名', visible: true, group: '基础数据' },
  { key: 'data_compare', label: '数据对比', visible: true, group: '基础数据' },
  { key: 'lineup', label: '阵容情况', visible: true, group: '基础数据' },
  { key: 'h2h', label: '对赛往绩', visible: true, group: '基础数据' },
  { key: 'recent_form', label: '近期战绩', visible: true, group: '基础数据' },
  { key: 'handicap_trend', label: '盘路走势', visible: true, group: '赔率数据' },
  { key: 'same_handicap', label: '相同盘路', visible: false, group: '赔率数据' },
  { key: 'goal_half_dist', label: '入球分布', visible: true, group: '统计分析' },
  { key: 'half_full', label: '半全场', visible: true, group: '统计分析' },
  { key: 'odd_even', label: '进球数/单双', visible: true, group: '统计分析' },
  { key: 'goal_timing', label: '进球时间', visible: true, group: '统计分析' },
  { key: 'goal_stats', label: '进球数分布', visible: true, group: '统计分析' },
  { key: 'season_stats', label: '赛季数据统计', visible: true, group: '统计分析' },
  { key: 'briefing', label: '赛前简报', visible: true, group: '预测信息' },
  { key: 'upcoming', label: '未来五场', visible: true, group: '预测信息' },
]

const FIVE_SECTIONS = [
  { key: 'basic_info', label: '基本信息', visible: true, group: '基础数据' },
  { key: 'jiben', label: '基本面', visible: true, group: '基础数据' },
  { key: 'jiaofeng', label: '交锋记录', visible: true, group: '基础数据' },
  { key: 'ouzhi', label: '欧指详情', visible: true, group: '赔率数据' },
  { key: 'yapan', label: '亚盘详情', visible: true, group: '赔率数据' },
  { key: 'daxiao', label: '大小球详情', visible: true, group: '赔率数据' },
]

const MACAU_SECTIONS = [
  { key: 'instant_index', label: '即时指数', visible: true, group: '赔率数据' },
  { key: 'handicap', label: '让球盘口', visible: true, group: '赔率数据' },
  { key: 'overunder', label: '大小球', visible: true, group: '赔率数据' },
  { key: 'league_filter', label: '联赛筛选', visible: false, group: '基础数据' },
  { key: 'match_detail', label: '比赛详情', visible: true, group: '基础数据' },
]

export const useSectionsStore = defineStore('sections', {
  state: () => ({
    titan: TITAN_SECTIONS.map(s => ({ ...s })),
    five: FIVE_SECTIONS.map(s => ({ ...s })),
    macau: MACAU_SECTIONS.map(s => ({ ...s })),
  }),
  getters: {
    getVisibleSections: (state) => (source) => {
      return state[source]?.filter(s => s.visible) || []
    },
    getGroups: (state) => (source) => {
      const groups = {}
      state[source]?.forEach(s => {
        const g = s.group || '其他'
        if (!groups[g]) groups[g] = []
        groups[g].push(s)
      })
      return groups
    },
  },
  actions: {
    setSectionVisible(source, key, visible) {
      const section = this[source]?.find(s => s.key === key)
      if (section) section.visible = visible
    },
    applyPreset(preset) {
      const presets = {
        minimal: ['jc_index', 'standings', 'h2h', 'odds_trend'],
        standard: ['jc_index', 'standings', 'data_compare', 'h2h', 'recent_form', 'odds_trend', 'handicap_trend', 'half_full', 'goal_stats', 'briefing'],
        professional: null,
        analyst: null,
      }
      const allowed = presets[preset]
      this.titan.forEach(s => {
        if (preset === 'professional' || preset === 'analyst') {
          s.visible = true
        } else {
          s.visible = allowed ? allowed.includes(s.key) : true
        }
      })
    },
  },
})
