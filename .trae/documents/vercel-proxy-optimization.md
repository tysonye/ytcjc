# Vercel 代理优化方案

## 当前问题

1. **访问速度慢** - Vercel Function 转发延迟 + 无 CDN 缓存
2. **带宽消耗** - 每次请求都实时转发到球探/500
3. **可能被反爬** - 频繁请求目标站点

## 优化方案

### 方案一：Vercel + 边缘缓存（推荐）

利用 Vercel 的 **Edge Config** + **CDN 缓存**，减少实时请求：

#### 1. 优化 `api/proxy.js`
- 添加响应缓存（Redis/Upstash）
- 对静态数据（联赛列表、球队信息）缓存 5-10 分钟
- 对动态数据（比分、赔率）缓存 30-60 秒
- 启用 gzip 压缩传输

#### 2. 使用 Vercel Edge Function
- 从 Node.js Function 改为 Edge Function（更快）
- 利用 Vercel 全球边缘节点缓存

#### 3. 添加缓存层
```javascript
// 使用 Upstash Redis (免费 10000 次/天)
import { Redis } from '@upstash/redis'

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL,
  token: process.env.UPSTASH_REDIS_REST_TOKEN,
})

// 缓存逻辑
const cached = await redis.get(cacheKey)
if (cached) return cached

const response = await fetch(targetUrl)
await redis.setex(cacheKey, ttl, response)
```

#### 4. 优化 `vercel.json`
```json
{
  "functions": {
    "api/proxy.js": {
      "maxDuration": 10,
      "memory": 1024
    }
  },
  "headers": [
    {
      "source": "/api/proxy",
      "headers": [
        { "key": "Cache-Control", "value": "public, s-maxage=60, stale-while-revalidate=300" }
      ]
    }
  ]
}
```

### 方案二：混合架构（最佳性能）

```
用户请求
  ├── 静态数据 → Vercel + CDN 缓存（缓存 5 分钟）
  ├── 动态数据 → 你的服务器 Nginx 代理（实时）
  └── AI 预测 → 你的服务器后端 API
```

#### 实现步骤：

1. **前端配置分离**
   - 静态数据（联赛列表、球队名）：走 Vercel 代理
   - 动态数据（实时比分、赔率变化）：走服务器代理
   - API 接口（用户认证、AI 聊天）：走服务器后端

2. **修改 `vite.config.js`**
```javascript
proxy: {
  // 静态数据 - Vercel
  '/titan-proxy/jc': {
    target: 'https://jc.titan007.com',
    // ... 添加缓存头
  },
  // 动态数据 - 本地服务器
  '/live-data/': {
    target: 'http://your-server-ip:8000/proxy/',
    // 实时转发，不缓存
  }
}
```

3. **Nginx 配置动态/静态分离**
```nginx
# 静态数据 - 开启缓存
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    proxy_cache_valid 200 10m;
    proxy_cache_use_stale error timeout updating;
}

# 动态数据 - 不缓存
location /api/live/ {
    proxy_cache off;
    proxy_buffering off;
}
```

### 方案三：定时任务预抓取（最省流量）

使用 **GitHub Actions** 或 **Vercel Cron** 定时抓取数据：

```yaml
# .github/workflows/fetch-data.yml
name: Fetch Match Data
on:
  schedule:
    - cron: '*/5 * * * *'  # 每 5 分钟

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Fetch data
        run: |
          curl https://jc.titan007.com/xxx > data/matches.json
      - name: Deploy to Vercel
        run: vercel --prod
```

前端直接读取静态 JSON 文件，完全不消耗服务器流量。

## 推荐实施步骤

### 第一步：优化当前 Vercel 代理（立即执行）
1. 更新 `api/proxy.js` 添加缓存逻辑
2. 配置 Upstash Redis（免费）
3. 设置不同数据的 TTL

### 第二步：混合架构（可选）
1. 区分静态/动态数据路由
2. 静态走 Vercel CDN
3. 动态走服务器 Nginx

### 第三步：定时预抓取（可选）
1. 配置 GitHub Actions 定时任务
2. 抓取结果存为静态 JSON
3. 前端直接读取

## 成本对比

| 方案 | 服务器流量 | Vercel 带宽 | 延迟 | 复杂度 |
|------|-----------|-----------|------|--------|
| 当前（纯服务器） | 高 | 0 | 低 | 低 |
| 当前（纯 Vercel） | 0 | 高 | 中 | 低 |
| **优化后（Vercel+ 缓存）** | **0** | **中（减少 80%）** | **低** | **中** |
| 混合架构 | 中 | 中 | 低 | 高 |
| 定时预抓取 | 0 | 低 | 中 | 中 |

## 立即执行：方案一

优化 `api/proxy.js`，添加 Redis 缓存层，预计减少 80% 的 Vercel 请求次数和外部站点请求次数。
