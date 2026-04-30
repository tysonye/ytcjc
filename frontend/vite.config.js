import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: tag => tag === 'font'
        }
      }
    })
  ],
  server: {
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/titan-proxy/jc': {
        target: 'https://jc.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/jc/, ''),
        secure: false,
        headers: { Referer: 'https://jc.titan007.com/' },
      },
      '/titan-proxy/zq': {
        target: 'https://zq.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/zq/, ''),
        secure: false,
        headers: { Referer: 'https://zq.titan007.com/', Origin: 'https://zq.titan007.com' },
      },
      '/titan-proxy/vip': {
        target: 'https://vip.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/vip/, ''),
        secure: false,
        headers: { Referer: 'https://vip.titan007.com/' },
      },
      '/titan-proxy/info': {
        target: 'https://info.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/info/, ''),
        secure: false,
        selfHandleResponse: true,
        headers: {
          Referer: 'https://info.titan007.com/',
          Origin: 'https://info.titan007.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Encoding': 'identity',
        },
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            if ([301, 302, 303, 307, 308].includes(proxyRes.statusCode)) {
              const location = proxyRes.headers.location
              if (location) {
                try {
                  const target = new URL(location, 'https://info.titan007.com')
                  const newLocation = '/titan-proxy/info' + target.pathname + target.search
                  res.writeHead(302, { Location: newLocation })
                  res.end()
                  return
                } catch (e) {}
              }
            }
            let body = []
            proxyRes.on('data', (chunk) => body.push(chunk))
            proxyRes.on('end', () => {
              const headers = { ...proxyRes.headers }
              delete headers['content-encoding']
              delete headers['content-length']
              res.writeHead(proxyRes.statusCode, headers)
              res.end(Buffer.concat(body))
            })
          })
        },
      },
      '/500-proxy': {
        target: 'https://odds.500.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/500-proxy/, ''),
        secure: false,
        headers: {
          Referer: 'https://odds.500.com/',
          Origin: 'https://odds.500.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Encoding': 'identity',
        },
      },
      '/live500-proxy': {
        target: 'https://live.500.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/live500-proxy/, ''),
        secure: false,
        headers: {
          Referer: 'https://live.500.com/',
          Origin: 'https://live.500.com',
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          Accept: 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
          'Accept-Encoding': 'identity',
        },
      },
      '/macau-proxy': {
        target: 'https://www.macauslot.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/macau-proxy/, ''),
        secure: false,
      },
      '/sporttery-proxy': {
        target: 'https://webapi.sporttery.cn',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/sporttery-proxy/, ''),
        secure: false,
        headers: { Referer: 'https://www.sporttery.cn/', Origin: 'https://www.sporttery.cn' },
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
