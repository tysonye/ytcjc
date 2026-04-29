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
