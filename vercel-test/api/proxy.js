// Vercel Edge Function - 代理请求
export const config = {
  runtime: 'edge',
}

export default async function handler(request) {
  // 处理 CORS 预检请求
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '86400',
      },
    })
  }

  try {
    const url = new URL(request.url)
    const targetUrl = url.searchParams.get('url')

    if (!targetUrl) {
      return new Response(JSON.stringify({
        error: 'Missing url parameter',
        message: 'Please provide target URL',
      }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      })
    }

    console.log('Proxying to:', targetUrl)

    // 检测目标 URL 是否为 API 端点
    const isApiEndpoint = targetUrl.includes('/default/') || targetUrl.includes('.json') || targetUrl.includes('getAnalyData')
    
    // 构建基础 headers
    const proxyHeaders = {
      'Host': new URL(targetUrl).host,
      'Referer': new URL(targetUrl).origin + '/',
      'Origin': new URL(targetUrl).origin,
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Accept-Language': 'zh-CN,zh;q=0.9',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Cache-Control': 'no-cache',
      'Pragma': 'no-cache',
    }
    
    // 根据请求类型设置 Accept 和 X-Requested-With
    if (isApiEndpoint) {
      proxyHeaders['Accept'] = 'application/json, text/javascript, */*; q=0.01'
      proxyHeaders['X-Requested-With'] = 'XMLHttpRequest'
    } else {
      proxyHeaders['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
    }
    
    // 转发请求到目标网站
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: proxyHeaders,
      // 添加超时
      signal: AbortSignal.timeout(30000)
    })

    console.log('Response status:', response.status)

    // 复制响应头并添加 CORS
    const headers = new Headers(response.headers)
    headers.set('Access-Control-Allow-Origin', '*')
    headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    headers.set('Access-Control-Allow-Headers', 'Content-Type')

    // 移除可能引起问题的头
    headers.delete('Content-Length')
    headers.delete('Transfer-Encoding')

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers,
    })

  } catch (error) {
    console.error('Proxy error:', error)

    if (error.name === 'AbortError') {
      return new Response(JSON.stringify({
        error: 'Timeout',
        message: 'Request to target timed out',
      }), {
        status: 504,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
      })
    }

    return new Response(JSON.stringify({
      error: 'Proxy error',
      message: error.message,
    }), {
      status: 502,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
      },
    })
  }
}
