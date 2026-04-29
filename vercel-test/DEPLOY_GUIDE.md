# 🚀 Vercel 部署完整指南

## 📋 部署步骤

### 第 1 步：打开 PowerShell 管理员模式

**重要：** 需要管理员权限

1. 按 `Win + X`
2. 选择"Windows PowerShell (管理员)"

### 第 2 步：切换到项目目录

```powershell
cd d:\BackUp\internet\jc_temp\vercel-test
```

### 第 3 步：登录 Vercel

```powershell
vercel login
```

会自动打开浏览器，使用以下方式之一登录：
- GitHub（推荐）
- GitLab
- Bitbucket
- 邮箱

### 第 4 步：部署到生产环境

```powershell
vercel --prod
```

**部署过程：**
1. 第一次会问一些问题，全部按回车使用默认值
2. 等待上传（几秒钟）
3. 部署成功后会显示 URL

**示例输出：**
```
🔍  Inspect: https://vercel.com/your-account/jc-proxy-vercel/xxx
✅  Production: https://jc-proxy-vercel.vercel.app
```

**复制这个 URL：** `https://jc-proxy-vercel.vercel.app`

### 第 5 步：测试是否被屏蔽

#### 方法 A：使用测试页面

1. 访问：`https://jc-proxy-vercel.vercel.app/test.html`
2. 点击"测试所有数据源"
3. 查看结果

#### 方法 B：手动测试

访问以下 URL：

**测试 1：根路径**
```
https://jc-proxy-vercel.vercel.app/api/proxy?url=https://jc.titan007.com/
```

**测试 2：Titan 竞彩**
```
https://jc-proxy-vercel.vercel.app/titan-proxy/jc/
```

**测试 3：500 彩票**
```
https://jc-proxy-vercel.vercel.app/500-proxy/
```

**预期结果：**
- ✅ 看到 HTML 内容（可能乱码）→ 成功！
- ❌ 522 错误 → Vercel IP 也被屏蔽

### 第 6 步：根据结果决定方案

#### 如果测试通过（✅）

**恭喜！可以免费使用了！**

1. **修改前端代码**
   
   打开 `frontend/src/views/MatchDetail.vue`
   
   ```javascript
   // 修改为 Vercel URL
   const WORKERS_URL = 'https://jc-proxy-vercel.vercel.app'
   ```

2. **重启前端**
   ```bash
   cd frontend
   # Ctrl+C 停止
   npm run dev
   ```

3. **测试数据加载**
   - 访问 `http://localhost:3001/`
   - 选择比赛
   - 查看数据

#### 如果测试失败（❌）

**Vercel IP 也被屏蔽，只能使用国内服务器方案**

1. **参考文档：** `CLOUDFLARE_BLOCKED_SOLUTION.md`
2. **购买国内服务器**
3. **部署 Nginx 反向代理**

---

## 💰 成本说明

### Vercel 免费额度

- **带宽：** 100GB/月
- **请求数：** 100 万次/月
- **Serverless 执行时间：** 100 万小时/月

**个人使用：** 完全免费！

**如果超出：**
- $20/月（Pro 计划）
- 或按量付费

### 国内服务器方案

- **服务器：** ¥30-50/月
- **域名：** 已有
- **流量：** 通常包含或按量付费

---

## ⚠️ 注意事项

### 1. 部署域名

- 默认使用 `vercel.app` 域名
- 可以绑定自定义域名（免费）

### 2. 访问速度

- Vercel 边缘节点主要在国外
- 国内访问延迟约 100-200ms
- 但比经过后端服务器快

### 3. 稳定性

- Vercel 是全球最大的前端云平台
- 稳定性极高
- 不会被轻易屏蔽（IP 段经常更换）

### 4. 限制

- 免费版有带宽和请求数限制
- 但对于个人使用完全够用
- 超出后会自动升级或按量付费

---

## 🔧 故障排查

### 问题 1：部署失败

**可能原因：**
- 未登录 Vercel
- 网络连接问题

**解决：**
```bash
vercel login
vercel --prod
```

### 问题 2：访问 404

**可能原因：**
- 路由配置错误
- 部署未完成

**解决：**
- 等待 1-2 分钟
- 检查 `vercel.json` 配置

### 问题 3：522 错误

**原因：** Vercel IP 也被屏蔽

**解决：** 使用国内服务器方案

---

## 📊 对比总结

| 方案 | 成本 | 速度 | 稳定性 | 推荐度 |
|------|------|------|--------|--------|
| **Vercel** | 免费 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **国内服务器** | ¥30-50/月 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Cloudflare Workers** | 免费 | ⭐⭐⭐⭐ | ❌ 被屏蔽 | ❌ |
| **后端 API** | 流量费 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🎯 立即行动

### 快速部署命令

```powershell
# 1. 切换到项目目录
cd d:\BackUp\internet\jc_temp\vercel-test

# 2. 登录 Vercel
vercel login

# 3. 部署
vercel --prod

# 4. 复制输出的 URL
# 例如：https://jc-proxy-vercel.vercel.app
```

### 部署完成后

1. **复制 Vercel URL**
2. **访问测试页面**
3. **告诉我测试结果**

**如果 Vercel 可用，我们就省了一个月服务器钱！💰**

---

**准备好了吗？开始部署吧！** 🚀
