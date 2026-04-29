import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/titan-proxy/jc': {
        target: 'https://jc.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/jc/, ''),
        secure: false,
        headers: {
          Referer: 'https://jc.titan007.com/',
        },
      },
      '/titan-proxy/zq': {
        target: 'https://zq.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/zq/, ''),
        secure: false,
        headers: {
          Referer: 'https://zq.titan007.com/',
          Origin: 'https://zq.titan007.com',
        },
      },
      '/titan-proxy/vip': {
        target: 'https://vip.titan007.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/titan-proxy\/vip/, ''),
        secure: false,
        headers: {
          Referer: 'https://vip.titan007.com/',
        },
      },
      '/500-proxy': {
        target: 'https://odds.500.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/500-proxy/, ''),
        secure: false,
      },
      '/macau-proxy': {
        target: 'https://www.macauslot.com',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/macau-proxy/, ''),
        secure: false,
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
