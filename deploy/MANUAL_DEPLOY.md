# 服务器部署指南

## 方式一：使用 PuTTY（推荐 Windows 用户）

### 1. 下载 PuTTY
- 官网：https://www.putty.org/
- 或使用 Windows 自带的 OpenSSH

### 2. 连接服务器
```
主机：101.35.163.143
端口：22
用户名：ubuntu
密码：Ye292513.
```

### 3. 部署命令

连接成功后，在终端依次执行：

```bash
# 1. 克隆项目（如果服务器上没有）
cd /home/ubuntu
git clone https://github.com/tysonye/ytcjc.git
cd ytcjc

# 2. 安装系统依赖
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip nodejs npm nginx curl git

# 3. 配置后端
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
nano .env
# 编辑内容：
# SECRET_KEY=your-random-secret-key
# AI_BASE_URL=https://gpt.qt.cool/v1
# AI_API_KEY=sk-checkin-6UpGmmzclX7O8CxXWCYmY44O6yZaYaXt

# 5. 初始化数据库
python init_db.py
deactivate

# 6. 构建前端
cd ../frontend
npm install
npm run build

# 7. 配置 Nginx
sudo cp ../deploy/nginx.conf /etc/nginx/sites-available/ytcjc
sudo ln -sf /etc/nginx/sites-available/ytcjc /etc/nginx/sites-enabled/ytcjc
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 8. 配置后端服务
sudo cp ../deploy/ytcjc-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ytcjc-backend
sudo systemctl restart ytcjc-backend
```

## 方式二：使用 Windows OpenSSH（Win10/11）

### 1. 启用 OpenSSH
设置 → 应用 → 可选功能 → 添加 OpenSSH 客户端

### 2. 在 PowerShell 中执行
```powershell
# 连接服务器
ssh ubuntu@101.35.163.143
# 密码输入：Ye292513.

# 之后执行方式一的部署命令
```

## 部署后访问

- **前端访问**：http://101.35.163.143
- **后端 API**：http://101.35.163.143:8000/api/health
- **管理员后台**：http://101.35.163.143/admin
- **管理员账号**：admin / admin123

## 常用维护命令

```bash
# 查看后端日志
sudo journalctl -u ytcjc-backend -f

# 重启后端
sudo systemctl restart ytcjc-backend

# 重启 Nginx
sudo systemctl restart nginx

# 更新部署
cd /home/ubuntu/ytcjc
git pull
cd frontend && npm run build
sudo systemctl restart ytcjc-backend
```
