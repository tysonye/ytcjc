#!/bin/bash
# YTCJC 项目服务器部署脚本
# 使用方法：在服务器终端执行 bash deploy.sh

set -e

APP_DIR="/home/ubuntu/ytcjc"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
DEPLOY_DIR="$APP_DIR/deploy"

echo "========================================="
echo "  竞彩足球数据分析平台 - 服务器部署"
echo "  服务器：腾讯云 上海"
echo "========================================="

# 检查是否在项目目录
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "[错误] 部署目录不存在：$DEPLOY_DIR"
    echo "请先将项目代码上传到 $APP_DIR"
    echo ""
    echo "方法 1: 使用 scp"
    echo "  scp -r ./ytcjc ubuntu@101.35.163.143:/home/ubuntu/"
    echo ""
    echo "方法 2: 使用 git clone"
    echo "  cd /home/ubuntu"
    echo "  git clone https://github.com/tysonye/ytcjc.git"
    exit 1
fi

echo ""
echo "[1/8] 更新系统包..."
sudo apt-get update -y

echo ""
echo "[2/8] 安装系统依赖..."
sudo apt-get install -y python3 python3-venv python3-pip nodejs npm nginx curl git

echo ""
echo "[3/8] 配置后端 Python 环境..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "  ✓ 创建虚拟环境"
else
    echo "  ✓ 虚拟环境已存在"
fi

source venv/bin/activate
pip install --upgrade pip -q
echo "  ✓ 升级 pip"

pip install -r requirements.txt -q
echo "  ✓ 安装后端依赖"

echo ""
echo "[4/8] 配置环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✓ 创建 .env 文件"
    echo ""
    echo "  ⚠️  请编辑 .env 文件配置以下变量："
    echo "     SECRET_KEY  - 设置一个随机密钥"
    echo "     AI_BASE_URL - AI API 地址 (如：https://gpt.qt.cool/v1)"
    echo "     AI_API_KEY  - AI API 密钥"
    echo ""
    echo "  编辑命令：nano .env"
    echo ""
    read -p "是否现在编辑 .env？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        nano .env
    fi
else
    echo "  ✓ .env 已存在"
fi

echo ""
echo "[5/8] 初始化数据库..."
source venv/bin/activate
python init_db.py
echo "  ✓ 数据库初始化完成"

echo ""
echo "[6/8] 构建前端..."
cd "$FRONTEND_DIR"
npm install --silent
npm run build
echo "  ✓ 前端构建完成"

echo ""
echo "[7/8] 配置 Nginx..."
sudo cp "$DEPLOY_DIR/nginx.conf" /etc/nginx/sites-available/ytcjc
sudo ln -sf /etc/nginx/sites-available/ytcjc /etc/nginx/sites-enabled/ytcjc
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx
echo "  ✓ Nginx 配置完成"

echo ""
echo "[8/8] 配置后端服务..."
sudo cp "$DEPLOY_DIR/ytcjc-backend.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ytcjc-backend
sudo systemctl restart ytcjc-backend
echo "  ✓ 后端服务配置完成"

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "  📡 访问地址："
echo "     http://$(curl -s ifconfig.me)"
echo ""
echo "  🔧 后端 API: http://$(curl -s ifconfig.me):8000/api/health"
echo ""
echo "  👤 管理员账号："
echo "     用户名：admin"
echo "     密码：admin123"
echo ""
echo "  📝 常用命令："
echo "     查看后端日志：journalctl -u ytcjc-backend -f"
echo "     重启后端：    sudo systemctl restart ytcjc-backend"
echo "     重启 Nginx：  sudo systemctl restart nginx"
echo "     更新部署：    bash $DEPLOY_DIR/update.sh"
echo ""
echo "  ⚠️  重要：请确保已配置 .env 文件中的 AI API 密钥"
echo ""
