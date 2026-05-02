function toSimplified(str) {
  if (!str) return str
  const t2s = {
    '聯': '联', '賽': '赛', '盃': '杯', '亞': '亚', '歐': '欧', '國': '国',
    '會': '会', '隊': '队', '級': '级', '區': '区', '東': '东', '風': '风',
    '場': '场', '進': '进', '勝': '胜', '負': '负', '時': '时', '間': '间',
    '員': '员', '門': '门', '開': '开', '關': '关', '後': '后', '來': '来',
    '個': '个', '們': '们', '這': '这', '說': '说', '話': '话', '對': '对',
    '錯': '错', '長': '长', '頭': '头', '發': '发', '現': '现', '見': '见',
    '馬': '马', '鳥': '鸟', '魚': '鱼', '龍': '龙', '車': '车', '電': '电',
    '機': '机', '線': '线', '網': '网', '紙': '纸', '鐵': '铁', '銅': '铜',
    '錢': '钱', '銀': '银', '問': '问', '聞': '闻', '聲': '声',
    '聽': '听', '讀': '读', '寫': '写', '書': '书', '畫': '画', '紅': '红',
    '綠': '绿', '藍': '蓝', '黃': '黄', '難': '难',
    '過': '过', '還': '还', '讓': '让', '給': '给', '請': '请', '謝': '谢',
    '點': '点', '數': '数', '學': '学', '愛': '爱', '親': '亲', '認': '认',
    '識': '识', '語': '语', '論': '论', '課': '课', '題': '题', '義': '义',
    '務': '务', '總': '总', '統': '统', '計': '计', '劃': '划', '則': '则',
    '創': '创', '製': '制',
  }
  return str.split('').map(c => t2s[c] || c).join('')
}

export function parseShujuPage(html) {
  if (!html) return null

  const result = {
    basicInfo: { homeTeam: '', awayTeam: '', league: '', matchTime: '', weather: '', venue: '' },
    recentForm: {
      home: { formSeq: '', panSeq: '' },
      away: { formSeq: '', panSeq: '' }
    },
    h2hRecord: {
      summary: '',
      homeWins: 0,
      draws: 0,
      awayWins: 0,
      matches: []
    },
    recommendation: {
      result: '',
      analysis: ''
    }
  }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')

    const titleEl = doc.querySelector('title')
    if (titleEl) {
      const titleText = titleEl.textContent || ''
      const vsMatch = titleText.match(/(.+?)\s*(?:vs|VS|对阵|對陣)\s*(.+?)(?:\(|$)/i)
      if (vsMatch) {
        result.basicInfo.homeTeam = toSimplified(vsMatch[1].trim())
        result.basicInfo.awayTeam = toSimplified(vsMatch[2].trim())
      }
      const leagueMatch = titleText.match(/\((\d{4}\/?\d*)([\u4e00-\u9fa5]+)\)/)
      if (leagueMatch) {
        result.basicInfo.league = toSimplified(leagueMatch[2])
      }
    }

    const gameTimeEl = doc.querySelector('.game_time')
    if (gameTimeEl) {
      const timeText = gameTimeEl.textContent || ''
      const timeMatch = timeText.match(/(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})/)
      if (timeMatch) {
        result.basicInfo.matchTime = timeMatch[1]
      }
    }

    const leagueEl = doc.querySelector('.odds_hd_ls .hd_name')
    if (leagueEl && !result.basicInfo.league) {
      const leagueText = (leagueEl.textContent || '').trim()
      const leagueM = leagueText.match(/(\d{2}\/?\d{0,2})([\u4e00-\u9fa5]+)/)
      if (leagueM) {
        result.basicInfo.league = toSimplified(leagueM[2])
      } else if (leagueText) {
        result.basicInfo.league = toSimplified(leagueText)
      }
    }

    const hisInfoEl = doc.querySelector('.his_info')
    if (hisInfoEl) {
      const hisText = hisInfoEl.textContent || ''
      const h2hMatch = hisText.match(/(\d+)胜(\d+)平(\d+)负/)
      if (h2hMatch) {
        result.h2hRecord.homeWins = parseInt(h2hMatch[1], 10) || 0
        result.h2hRecord.draws = parseInt(h2hMatch[2], 10) || 0
        result.h2hRecord.awayWins = parseInt(h2hMatch[3], 10) || 0
        result.h2hRecord.summary = `${h2hMatch[1]}胜${h2hMatch[2]}平${h2hMatch[3]}负`
      }
      if (!result.h2hRecord.summary && hisText) {
        result.h2hRecord.summary = hisText.trim()
      }
    }

    const bottomInfos = doc.querySelectorAll('.bottom_info')
    bottomInfos.forEach((infoEl, idx) => {
      const pEl = infoEl.querySelector('p')
      if (!pEl) return
      const pText = pEl.textContent || ''
      const formMatch = pText.match(/(\d+)胜(\d+)平(\d+)负/)
      if (!formMatch) return
      const formSeq = formMatch[0]
      if (idx === 0) {
        result.recentForm.home.formSeq = formSeq
      } else if (idx === 1) {
        result.recentForm.away.formSeq = formSeq
      }
    })

    const formImgs = doc.querySelectorAll('.record .chart img')
    const homeImgs = []
    const awayImgs = []
    let currentTeam = 'home'
    for (const img of formImgs) {
      const alt = (img.getAttribute('alt') || '').trim()
      if (alt === '胜' || alt === '负' || alt === '平') {
        if (currentTeam === 'home') {
          homeImgs.push(alt === '胜' ? 'W' : alt === '平' ? 'D' : 'L')
        } else {
          awayImgs.push(alt === '胜' ? 'W' : alt === '平' ? 'D' : 'L')
        }
      }
      if (homeImgs.length >= 10 && currentTeam === 'home') {
        currentTeam = 'away'
      }
    }
    if (homeImgs.length > 0 && !result.recentForm.home.formSeq) {
      result.recentForm.home.formSeq = homeImgs.join('')
    }
    if (awayImgs.length > 0 && !result.recentForm.away.formSeq) {
      result.recentForm.away.formSeq = awayImgs.join('')
    }

    const hasData = result.basicInfo.homeTeam ||
      result.recentForm.home.formSeq ||
      result.h2hRecord.summary

    if (!hasData) return null
  } catch (e) {
    console.warn('解析shuju页面失败:', e)
    return null
  }

  return result
}

export function parseOuzhiPage(html) {
  if (!html) return { europeanOdds: [], kellyIndex: [], basicInfo: null }
  const result = { europeanOdds: [], kellyIndex: [], basicInfo: null }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')

    const titleEl = doc.querySelector('title')
    if (titleEl) {
      const titleText = titleEl.textContent || ''
      const vsMatch = titleText.match(/(.+?)\s*(?:vs|VS|对阵|對陣)\s*(.+?)(?:\(|-)/i)
      if (vsMatch) {
        result.basicInfo = {
          homeTeam: toSimplified(vsMatch[1].trim()),
          awayTeam: toSimplified(vsMatch[2].trim()),
          league: '',
          matchTime: '',
        }
      }
      if (result.basicInfo) {
        const leagueMatch = titleText.match(/\((\d{4}\/?\d*)([\u4e00-\u9fa5]+)\)/)
        if (leagueMatch) {
          result.basicInfo.league = toSimplified(leagueMatch[2])
        }
      }
    }

    const gameTimeEl = doc.querySelector('.game_time')
    if (gameTimeEl && result.basicInfo) {
      const timeText = gameTimeEl.textContent || ''
      const timeMatch = timeText.match(/(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})/)
      if (timeMatch) {
        result.basicInfo.matchTime = timeMatch[1]
      }
    }

    const datatb = doc.getElementById('datatb')
    if (!datatb) return result

    const rows = datatb.querySelectorAll('tr[class^="tr"]')
    rows.forEach(row => {
      const plgsTd = row.querySelector('.tb_plgs')
      if (!plgsTd) return
      const company = plgsTd.getAttribute('title') || plgsTd.querySelector('a')?.getAttribute('title') || plgsTd.querySelector('.quancheng')?.textContent?.trim() || plgsTd.textContent?.trim() || ''
      if (!company) return

      const plTables = row.querySelectorAll('table.pl_table_data')
      if (plTables.length < 1) return

      const initOdds = []
      const currOdds = []
      const initKelly = []
      const currKelly = []

      if (plTables.length >= 1) {
        const oddsTable = plTables[0]
        const trs = oddsTable.querySelectorAll('tr')
        if (trs.length >= 1) {
          const initTds = trs[0].querySelectorAll('td')
          for (const td of initTds) {
            const val = td.textContent?.trim()
            if (val && /^\d+\.\d+$/.test(val)) initOdds.push(val)
            const klfc = td.getAttribute('klfc')
            if (klfc) initKelly.push(klfc)
          }
        }
        if (trs.length >= 2) {
          const currTds = trs[1].querySelectorAll('td')
          for (const td of currTds) {
            const val = td.textContent?.trim()
            if (val && /^\d+\.\d+$/.test(val)) currOdds.push(val)
            const klfc = td.getAttribute('klfc')
            if (klfc) currKelly.push(klfc)
          }
        }
      }

      if (initOdds.length >= 3 || currOdds.length >= 3) {
        result.europeanOdds.push({
          company,
          initHome: initOdds[0] || '',
          initDraw: initOdds[1] || '',
          initAway: initOdds[2] || '',
          currHome: currOdds[0] || initOdds[0] || '',
          currDraw: currOdds[1] || initOdds[1] || '',
          currAway: currOdds[2] || initOdds[2] || '',
        })
      }

      if (currKelly.length >= 3) {
        result.kellyIndex.push({
          company,
          home: currKelly[0],
          draw: currKelly[1],
          away: currKelly[2],
          returnRate: ''
        })
      } else if (initKelly.length >= 3) {
        result.kellyIndex.push({
          company,
          home: initKelly[0],
          draw: initKelly[1],
          away: initKelly[2],
          returnRate: ''
        })
      }
    })
  } catch (e) {
    console.warn('解析ouzhi页面失败:', e)
  }

  return result
}

export function parseYazhiPage(html) {
  if (!html) return { asianOdds: [] }
  const result = { asianOdds: [] }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const datatb = doc.getElementById('datatb')
    if (!datatb) return result

    const rows = datatb.querySelectorAll('tr[class^="tr"]')
    rows.forEach(row => {
      const plgsTd = row.querySelector('.tb_plgs')
      if (!plgsTd) return
      const company = plgsTd.getAttribute('title') || plgsTd.querySelector('a')?.getAttribute('title') || plgsTd.querySelector('.quancheng')?.textContent?.trim() || plgsTd.textContent?.trim() || ''
      if (!company) return

      const plTables = row.querySelectorAll('table.pl_table_data')
      if (plTables.length < 2) return

      const currVals = []
      const currTable = plTables[0]
      const currTds = currTable.querySelectorAll('td')
      for (const td of currTds) {
        const text = td.textContent?.trim().replace(/[↑↓]/g, '') || ''
        if (text && /^-?\d+\.\d+$/.test(text)) currVals.push(text)
        else if (text && /平手|半球|一球|球半|两球|受/.test(text)) currVals.push(text)
      }

      const initVals = []
      const initTable = plTables[1]
      const initTds = initTable.querySelectorAll('td')
      for (const td of initTds) {
        const text = td.textContent?.trim().replace(/[↑↓]/g, '') || ''
        if (text && /^-?\d+\.\d+$/.test(text)) initVals.push(text)
        else if (text && /平手|半球|一球|球半|两球|受/.test(text)) initVals.push(text)
      }

      if (initVals.length >= 3 || currVals.length >= 3) {
        result.asianOdds.push({
          company,
          initHome: initVals[0] || '',
          initHandicap: initVals[1] || '',
          initAway: initVals[2] || '',
          currHome: currVals[0] || initVals[0] || '',
          currHandicap: currVals[1] || initVals[1] || '',
          currAway: currVals[2] || initVals[2] || '',
        })
      }
    })
  } catch (e) {
    console.warn('解析yazhi页面失败:', e)
  }

  return result
}

export function parseDaxiaoPage(html) {
  if (!html) return { overunderOdds: [] }
  const result = { overunderOdds: [] }

  try {
    const parser = new DOMParser()
    const doc = parser.parseFromString(html, 'text/html')
    const datatb = doc.getElementById('datatb')
    if (!datatb) return result

    const rows = datatb.querySelectorAll('tr[class^="tr"]')
    rows.forEach(row => {
      const plgsTd = row.querySelector('.tb_plgs')
      if (!plgsTd) return
      const company = plgsTd.getAttribute('title') || plgsTd.querySelector('a')?.getAttribute('title') || plgsTd.querySelector('.quancheng')?.textContent?.trim() || plgsTd.textContent?.trim() || ''
      if (!company) return

      const plTables = row.querySelectorAll('table.pl_table_data')
      if (plTables.length < 2) return

      const currVals = []
      const currTable = plTables[0]
      const currTds = currTable.querySelectorAll('td')
      for (const td of currTds) {
        const text = td.textContent?.trim().replace(/[↑↓]/g, '') || ''
        if (text && /^-?\d+\.\d+$/.test(text)) currVals.push(text)
        else if (text && /^\d/.test(text) && /\d$/.test(text)) currVals.push(text)
      }

      const initVals = []
      const initTable = plTables[1]
      const initTds = initTable.querySelectorAll('td')
      for (const td of initTds) {
        const text = td.textContent?.trim().replace(/[↑↓]/g, '') || ''
        if (text && /^-?\d+\.\d+$/.test(text)) initVals.push(text)
        else if (text && /^\d/.test(text) && /\d$/.test(text)) initVals.push(text)
      }

      if (initVals.length >= 3 || currVals.length >= 3) {
        result.overunderOdds.push({
          company,
          initBig: initVals[0] || '',
          initLine: initVals[1] || '',
          initSmall: initVals[2] || '',
          currBig: currVals[0] || initVals[0] || '',
          currLine: currVals[1] || initVals[1] || '',
          currSmall: currVals[2] || initVals[2] || '',
        })
      }
    })
  } catch (e) {
    console.warn('解析daxiao页面失败:', e)
  }

  return result
}
