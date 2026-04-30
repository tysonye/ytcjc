# Vercel 代理方案分析

## 文章核心内容

该博客介绍了使用 Vercel 进行反向代理并加速的方法：

1. **反代原理**：通过 Vercel 的 Edge Network 边缘节点转发请求
2. **加速方式**：
   - Vercel 在全球有多个边缘节点（台湾、韩国、日本、新加坡等）
   - 通过修改 CNAME 解析到优选 IP，绕过 `cname.vercel-dns.com` 的慢速香港节点
   - 使用 `vercel.cdn.yt-blog.top` 这样的优选解析服务自动选择附近优质节点

## 当前项目架构分析

### 现有代理方式
```
用户浏览器 → Vite dev server 代理 → 外部站点（球探/500/竞彩）
```

开发环境使用 Vite 的 `proxy` 配置直接转发请求到目标站点。

### 生产环境（已部署）
```
用户浏览器 → Nginx 反向代理 → 外部站点
```

使用 Nginx 在服务器端进行反向代理。

## Vercel 方案是否适合？

### ❌ 不适合的原因

1. **代理类型不同**
   - 文章中的 `oichat-proxy` 是反代**自己的私有 VPS 服务器**
   - 你的需求是代理访问**第三方公开网站**（球探/500/竞彩）
   - Vercel 会禁止代理他人网站的行为（违反 ToS）

2. **技术实现冲突**
   - 当前项目前端直连外部站点（通过浏览器 CORS 或 Vite/Nginx 代理）
   - Vercel Function 有 10 秒超时限制，而球探/500 页面加载通常超过 10 秒
   - Vercel 免费额度有限（100GB 带宽/月），代理大量外部资源会快速耗尽

3. **已有更优方案**
   - 生产环境使用 Nginx 反向代理，直接部署在自己的服务器上
   - 服务器带宽充足，无超时限制
   - 完全控制，不会被封禁

4. **法律风险**
   - Vercel 明确禁止使用其服务代理非自己拥有的网站
   - 球探/500 等网站可能投诉导致 Vercel 账户被封

### ✅ 唯一适用场景

如果你使用 Vercel **仅部署前端静态文件**，后端 API 和反向代理都在自己的服务器：

```
用户 → Vercel（前端静态文件） → 你的服务器 Nginx（API + 代理） → 外部站点
```

这种情况下：
- Vercel 只托管 HTML/CSS/JS，不直接代理外部站点
- 所有代理请求通过你的服务器中转
- 符合 Vercel ToS

## 结论

**Vercel 代理方案不适合你的项目。**

### 推荐方案

1. **开发环境**：继续使用 Vite dev server 的 proxy 配置（已配置完成）

2. **生产环境**：使用已创建的 Nginx 反向代理配置（`deploy/nginx.conf`）
   - 部署在自己的服务器（1 核 2G 即可）
   - 所有外部站点代理通过 Nginx 转发
   - 前端静态文件也通过 Nginx 托管
   - 后端 FastAPI 通过 systemd 守护

3. **如果必须使用 Vercel**（例如没有服务器）：
   - 仅部署前端静态文件（`vercel-test` 方案）
   - 后端 API 需要找其他免费托管（如 Render、Railway）
   - 代理功能由后端 API 完成（但会消耗后端服务的带宽）

## 已准备的部署文件

- `deploy/nginx.conf` - 完整的 Nginx 反向代理配置
- `deploy/deploy.sh` - 一键部署脚本
- `deploy/update.sh` - 增量更新脚本
- `deploy/ytcjc-backend.service` - systemd 服务配置

使用这些文件，在自己的服务器上部署即可，无需依赖 Vercel 代理。
