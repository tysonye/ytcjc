# 竞彩足球比赛数据获取与盘口分析系统

实时获取竞彩足球比赛数据、赔率指数和分析数据的 Web 应用，支持多数据源对比和 AI 分析。

## 功能特性

- 实时获取比赛场次信息
- 即时走势对比（多公司赔率比较：欧洲指数、欧转亚盘、实际亚盘、进球数）
- 竞彩指数数据（胜平负、亚让、进球数、比分、半全场）
- 球队积分排名（总/主/客）
- 对赛往绩和近期战绩
- 半全场/进球数统计
- 盘路走势和相同让球
- 阵容情况
- AI 智能分析
- 会员系统与权限管理

## 技术栈

**后端：** Python 3.7+ / FastAPI / SQLAlchemy / httpx

**前端：** Vue 3 / Vite / Element Plus / ECharts / Pinia

## 项目结构

```
ytcjc/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI 入口
│   │   ├── config.py         # 配置（数据库、密钥、代理域名白名单）
│   │   ├── database.py       # 数据库连接
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── routers/          # API 路由（代理、用户、认证、订单等）
│   │   ├── schemas/          # Pydantic 数据校验
│   │   └── services/         # 业务逻辑
│   ├── init_db.py            # 初始化数据库
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── titan/        # Titan 数据组件（走势、积分、往绩等）
│   │   │   ├── five/         # 500 数据组件
│   │   │   └── macau/        # 澳门数据组件
│   │   ├── views/            # 页面（首页、详情、登录、管理后台）
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── router/           # 路由配置
│   │   ├── styles/           # 全局样式
│   │   └── utils/            # 工具函数
│   ├── vite.config.js        # Vite 配置（含代理规则）
│   └── package.json
└── README.md
```

## 快速开始

### 1. 安装依赖

```bash
# 后端
cd backend
pip install -r requirements.txt

# 前端
cd frontend
npm install
```

### 2. 配置环境变量

在 `backend/` 目录创建 `.env` 文件：

```
DATABASE_URL=sqlite:///./ytcjc.db
SECRET_KEY=your-secret-key
AI_BASE_URL=https://api.example.com/v1
AI_API_KEY=your-api-key
```

### 3. 初始化数据库

```bash
cd backend
python init_db.py
```

### 4. 启动服务

```bash
# 后端（默认 8000 端口）
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（默认 3000 端口）
cd frontend
npm run dev
```

访问 http://localhost:3000

### 5. 构建生产版本

```bash
cd frontend
npm run build
```

## 数据源

- 比赛列表与竞彩指数：jc.titan007.com
- 赔率分析与走势：zq.titan007.com
- 赔率对比：odds.500.com
- 澳门盘口：macauslot.com

## 注意事项

1. 需要稳定的网络连接
2. 数据仅供参考
3. 生产环境请修改 `SECRET_KEY`
4. AI 功能需配置 `AI_BASE_URL` 和 `AI_API_KEY`

## 生产部署改造建议

> 当前架构为开发模式，仅适合 10~30 并发。主体功能完成后，按以下阶段改造：

### 第一阶段：基础生产化（支撑 100~500 并发）

| 改造项 | 现状 | 目标 |
|--------|------|------|
| 数据库 | SQLite（单文件，写锁阻塞） | PostgreSQL / MySQL（支持并发读写） |
| 后端进程 | uvicorn 单 worker | uvicorn 4~8 workers + Gunicorn 管理 |
| 前端部署 | Vite 开发服务器 | `npm run build` + Nginx 托管静态资源 |
| 反向代理 | 无 | Nginx 反代前端静态 + 后端 API |
| 数据库连接 | 每请求创建连接 | 连接池（SQLAlchemy pool） |

### 第二阶段：缓存与性能优化（支撑 500~2000 并发）

| 改造项 | 说明 |
|--------|------|
| Redis 缓存层 | 赔率数据缓存 1~3 分钟，同一场比赛 100 个用户只请求外部 1 次 |
| 前端 CDN | 静态资源部署 CDN，减少服务器带宽压力 |
| 代理请求限流 | 对外部数据源的请求做队列和限流，防止被 WAF 封禁 |
| 数据预加载 | 比赛列表定时预取热门比赛的赔率数据到缓存 |

### 第三阶段：高可用扩展（支撑 2000+ 并发）

| 改造项 | 说明 |
|--------|------|
| 多实例负载均衡 | 多台后端服务器 + Nginx 负载均衡 |
| 代理服务独立部署 | 将数据代理服务从主应用拆分，独立扩缩容 |
| 数据库读写分离 | 主库写入，从库读取 |
| 监控与告警 | 请求量、响应时间、错误率监控 |

### 当前架构瓶颈速查

| 组件 | 现状 | 瓶颈 |
|------|------|------|
| 数据库 | SQLite | 写入并发仅 1 连接 |
| 后端 | uvicorn 单进程 | 仅用 1 个 CPU 核心 |
| 前端 | Vite 开发服务器 | 不能用于生产 |
| 数据请求 | 每用户穿透到外部 | 外部网站限流/封 IP |
| 缓存 | 无 | 相同数据重复请求 |
