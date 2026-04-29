# 🚀 Vercel 部署指南

## 📋 快速部署步骤

### 第 1 步：安装 Vercel CLI

```bash
npm install -g vercel
```

### 第 2 步：登录 Vercel

```bash
vercel login
```

会打开浏览器，使用 GitHub/GitLab/Bitbucket 登录。

### 第 3 步：部署到 Vercel

```bash
cd vercel-test
vercel --prod
```

### 第 4 步：获取部署 URL

部署成功后会显示：
```
🔍  Inspect: https://vercel.com/your-account/jc-proxy-vercel/xxx
✅  Production: https://jc-proxy-vercel.vercel.app
```

### 第 5 步：测试是否被屏蔽

访问：
```
https://jc-proxy-vercel.vercel.app/titan-proxy/jc/
```

**如果看到内容（即使乱码），说明 Vercel IP 未被屏蔽！✅**

**如果还是 522 错误，说明 Vercel IP 也被屏蔽了 ❌**

---

##  测试工具

部署完成后，访问测试页面：
```
https://jc-proxy-vercel.vercel.app/test.html
```

会自动测试所有数据源。

---

## 💰 成本

- **免费额度：** 每月 100GB 带宽，10 万次请求
- **个人使用：** 完全免费
- **超出后：** $20/月

---

## ⚠️ 注意事项

1. **域名：** 默认使用 `vercel.app` 域名
2. **备案：** 不需要（服务器在国外）
3. **速度：** 边缘节点主要在国外，国内访问稍慢
4. **限制：** 免费版有带宽和请求数限制

---

## 🎯 下一步

如果 Vercel IP 未被屏蔽：
1. ✅ 直接使用（免费！）
2. ✅ 修改前端代码配置 Vercel URL
3. ✅ 完成！

如果 Vercel IP 也被屏蔽：
1. ❌ 只能使用国内服务器方案
2. 📋 参考 `CLOUDFLARE_BLOCKED_SOLUTION.md`
