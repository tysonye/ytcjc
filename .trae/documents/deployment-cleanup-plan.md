# 竞彩足球数据平台 - 部署前代码审查与清理计划

## 项目概述
- **项目名称**: 竞彩足球比赛数据获取与盘口分析系统
- **技术栈**: Vue 3 + Vite + FastAPI + SQLAlchemy + SQLite
- **部署目标**: 生产环境

---

## 一、无效/无用文件清理

### 1.1 测试文件（根目录）
以下文件为开发测试遗留，生产环境不需要：

| 文件路径 | 说明 | 操作 |
|---------|------|------|
| `test_fetch_data.py` | 数据获取测试脚本 | 删除 |
| `test_jczq.html` | 竞彩足球测试页面 | 删除 |
| `test_live2.html` | 实时数据测试页面 | 删除 |
| `test_live3.html` | 实时数据测试页面 | 删除 |
| `test_live_debug.html` | 调试测试页面 | 删除 |
| `test_macau.py` | 澳门数据测试脚本 | 删除 |
| `test_macau_api.py` | 澳门API测试脚本 | 删除 |
| `test_macau_api2.py` | 澳门API测试脚本 | 删除 |
| `test_macau_api3.py` | 澳门API测试脚本 | 删除 |
| `test_macau_waf.py` | WAF测试脚本 | 删除 |
| `test_macau_waf2.py` | WAF测试脚本 | 删除 |
| `test_macau_waf3.py` | WAF测试脚本 | 删除 |
| `test_macau_waf4.py` | WAF测试脚本 | 删除 |
| `test_match.js` | 比赛数据测试脚本 | 删除 |
| `test_near6.py` | 近6场数据测试脚本 | 删除 |
| `analysis_1398725.html` | 单场比赛分析页面快照 | 删除 |
| `analysis_page.html` | 分析页面快照 | 删除 |
| `analysis_section.txt` | 分析片段文本 | 删除 |

### 1.2 前端测试/调试文件

| 文件路径 | 说明 | 操作 |
|---------|------|------|
| `frontend/src/views/TestPage.vue` | Vercel代理测试工具页面 | 删除 |
| `frontend/src/views/ProxyDebug.vue` | 代理配置诊断页面 | 删除 |
| `frontend/public/proxy-test.html` | 代理快速验证页面 | 删除 |
| `frontend/public/quick-test.html` | 快速测试页面 | 删除 |

**关联清理**: 删除上述文件后，需同步清理路由配置：
- `frontend/src/router/index.js` 中移除 `/test` 和 `/proxy-debug` 路由

### 1.3 废弃项目目录

| 目录路径 | 说明 | 操作 |
|---------|------|------|
| `vercel-test/` | Vercel测试项目（独立目录） | 删除整个目录 |

---

## 二、代码冗余与遗留代码清理

### 2.1 后端冗余代码

#### `backend/app/routers/proxy.py`
- **问题**: 包含已废弃的注释代码（第74-77行）
- **操作**: 删除注释掉的废弃路由代码

#### `backend/app/config.py`
- **问题**: 
  - `SECRET_KEY` 使用硬编码默认值，生产环境必须修改
  - 会员价格配置硬编码
- **操作**: 
  - 确保生产环境 `.env` 中设置强密钥
  - 添加生产环境配置检查

### 2.2 前端冗余代码

#### `frontend/src/views/MatchDetail.vue`
- **问题**: `parseStandingsJs` 函数在HTML解析成功后不再使用，但作为降级方案保留
- **评估**: 可保留作为后备方案，但需标记为 `@deprecated`

#### `frontend/src/router/index.js`
- **问题**: 测试路由 `/test` 和 `/proxy-debug` 需要移除
- **操作**: 删除相关路由定义

#### `frontend/vite.config.js`
- **问题**: 开发服务器代理配置中包含大量硬编码的User-Agent和Header
- **评估**: 开发配置，不影响生产，但可优化

---

## 三、安全风险评估与修复

### 3.1 🔴 高危安全问题

#### 1. CORS 配置过于宽松
**位置**: `backend/app/main.py` 第12-18行
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
**风险**: 允许任意域名的跨域请求，存在CSRF攻击风险
**修复**: 限制为生产域名
```python
allow_origins=["https://your-domain.com", "https://admin.your-domain.com"]
```

#### 2. 密钥硬编码
**位置**: `backend/app/config.py` 第7行
```python
SECRET_KEY = os.getenv("SECRET_KEY", "ytcjc-secret-key-change-in-production-2026")
```
**风险**: 如果未设置环境变量，使用可预测的默认密钥
**修复**: 生产环境强制检查
```python
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")
```

#### 3. 代理接口无认证
**位置**: `backend/app/routers/proxy.py`
**风险**: `/api/proxy/` 端点允许匿名访问外部资源
**评估**: 当前有域名白名单限制，但建议增加速率限制

#### 4. AI代理接口SSL验证关闭
**位置**: `backend/app/routers/proxy.py` 第141行
```python
async with httpx.AsyncClient(timeout=60.0, verify=False) as client:
```
**风险**: `verify=False` 关闭SSL证书验证，存在中间人攻击风险
**修复**: 移除 `verify=False` 或配置正确的CA证书

#### 5. 管理员认证仅依赖localStorage
**位置**: `frontend/src/router/index.js` 第63-69行
```javascript
if (to.meta.requiresAdmin) {
    const adminToken = localStorage.getItem('adminToken')
    if (!adminToken) {
      next({ name: 'AdminLogin' })
      return
    }
}
```
**风险**: 仅检查token存在性，不验证有效性，易被伪造
**修复**: 添加后端token验证中间件

### 3.2 🟡 中危安全问题

#### 6. 数据库使用SQLite
**位置**: `backend/app/config.py`
**风险**: SQLite不适合高并发生产环境，文件权限问题
**建议**: 生产环境迁移到PostgreSQL或MySQL

#### 7. 密码哈希强度未配置
**位置**: `backend/app/services/auth_service.py`
**评估**: 使用bcrypt默认配置，需确认rounds参数

#### 8. 前端代理配置暴露内部URL
**位置**: `frontend/vite.config.js`
**风险**: 开发配置中包含大量外部API的代理规则
**评估**: 仅影响开发环境，生产使用Vercel配置

### 3.3 🟢 低危安全问题

#### 9. 错误信息泄露
**位置**: 多处 `except Exception as e` 返回详细错误
**建议**: 生产环境返回通用错误信息，详细日志记录到文件

#### 10. 缺少请求速率限制
**位置**: 所有API路由
**建议**: 添加慢速攻击防护和速率限制

---

## 四、生产环境配置检查清单

### 4.1 环境变量
- [ ] `DATABASE_URL` - 设置为生产数据库
- [ ] `SECRET_KEY` - 设置为强随机密钥（至少32字节）
- [ ] `AI_BASE_URL` - AI服务地址
- [ ] `AI_API_KEY` - AI服务密钥

### 4.2 后端配置
- [ ] CORS origins 限制为生产域名
- [ ] 关闭SQLAlchemy echo（如果开启）
- [ ] 配置日志级别为 WARNING/ERROR
- [ ] 启用HTTPS强制跳转

### 4.3 前端配置
- [ ] API baseURL 指向生产后端
- [ ] 移除所有调试代码和console.log
- [ ] 启用构建优化和代码压缩

---

## 五、实施步骤

### 阶段1: 文件清理（预计30分钟）
1. 删除根目录测试文件（17个）
2. 删除前端测试/调试文件（4个）
3. 删除 `vercel-test/` 目录
4. 更新路由配置，移除测试路由

### 阶段2: 安全修复（预计1小时）
1. 修复CORS配置
2. 强制检查SECRET_KEY
3. 修复SSL验证问题
4. 添加管理员token验证

### 阶段3: 代码优化（预计30分钟）
1. 删除注释掉的废弃代码
2. 清理未使用的导入
3. 添加错误处理规范化

### 阶段4: 生产配置（预计30分钟）
1. 创建生产环境 `.env` 文件
2. 配置数据库连接
3. 设置域名白名单
4. 配置日志和监控

---

## 六、验证清单

- [ ] 项目可正常构建
- [ ] 所有测试文件已删除
- [ ] 路由配置已更新
- [ ] CORS配置已限制
- [ ] SECRET_KEY已设置为强密钥
- [ ] SSL验证已启用
- [ ] 管理员认证已加固
- [ ] 生产环境变量已配置
- [ ] 无console.log调试代码
- [ ] 错误处理不泄露敏感信息
