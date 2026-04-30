export default async function handler(req, res) {
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
    return res.status(200).end()
  }

  const targetUrl = req.query.url
  if (!targetUrl) {
    return res.status(400).json({ error: 'Missing url parameter' })
  }

  const allowedHosts = [
    'jc.titan007.com',
    'zq.titan007.com',
    'vip.titan007.com',
    'info.titan007.com',
    'odds.500.com',
    'www.macauslot.com',
    'webapi.sporttery.cn',
  ]

  let parsedUrl
  try {
    parsedUrl = new URL(targetUrl)
  } catch {
    return res.status(400).json({ error: 'Invalid url' })
  }

  if (!allowedHosts.includes(parsedUrl.hostname)) {
    return res.status(403).json({ error: 'Host not allowed' })
  }

  try {
    const qs = parsedUrl.search || ''
    const fetchUrl = parsedUrl.origin + parsedUrl.pathname + qs

    const headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }

    if (parsedUrl.hostname.includes('titan007.com')) {
      headers['Referer'] = parsedUrl.origin + '/'
      headers['Origin'] = parsedUrl.origin
    }

    if (parsedUrl.hostname === 'www.macauslot.com') {
      headers['Referer'] = 'https://www.macauslot.com/sc/soccer/odds_in.html'
      headers['Origin'] = 'https://www.macauslot.com'
      headers['Cookie'] = 'lang=sc'
    }

    const upstream = await fetch(fetchUrl, { headers })

    const contentType = upstream.headers.get('content-type') || 'text/html'
    let body = await upstream.text()

    res.setHeader('Access-Control-Allow-Origin', '*')
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
    res.setHeader('Content-Type', contentType)
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=120')
    res.status(upstream.status).send(body)
  } catch (err) {
    console.error('Proxy error:', err.message)
    res.status(502).json({ error: 'Upstream request failed', detail: err.message })
  }
}
