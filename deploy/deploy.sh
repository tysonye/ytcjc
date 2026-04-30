#!/bin/bash
set -e

APP_DIR="/opt/ytcjc"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

echo "========================================="
echo "  竞彩足球数据分析平台 - 一键部署脚本"
echo "========================================="

if [ ! -d "$APP_DIR" ]; then
    echo "[错误] 项目目录 $APP_DIR 不存在"
    echo "请先将项目代码上传到 $APP_DIR"
    echo "  scp -r ./ytcjc root@your-server:/opt/"
    exit 1
fi

echo ""
echo "[1/7] 安装系统依赖..."
apt-get update
apt-get install -y python3 python3-venv python3-pip nodejs npm nginx

echo ""
echo "[2/7] 配置后端 Python 环境..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "[3/7] 配置后端环境变量..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "[提示] 已创建 .env 文件，请编辑配置："
    echo "  nano $BACKEND_DIR/.env"
    echo ""
    echo "  必须修改："
    echo "    SECRET_KEY  - 设置一个随机密钥"
    echo "    AI_BASE_URL - AI API 地址"
    echo "    AI_API_KEY  - AI API 密钥"
    echo ""
    read -p "是否现在编辑 .env？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ${EDITOR:-nano} .env
    fi
else
    echo "  .env 已存在，跳过"
fi

echo ""
echo "[4/7] 初始化数据库..."
source venv/bin/activate
python init_db.py

echo ""
echo "[5/7] 构建前端..."
cd "$FRONTEND_DIR"
npm install
npm run build

echo ""
echo "[6/7] 配置 Nginx..."
cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/ytcjc
ln -sf /etc/nginx/sites-available/ytcjc /etc/nginx/sites-enabled/ytcjc
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
systemctl enable nginx

echo ""
echo "[7/7] 配置后端服务..."
cp "$APP_DIR/deploy/ytcjc-backend.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable ytcjc-backend
systemctl restart ytcjc-backend

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "  前端访问: http://$(hostname -I | awk '{print $1}')"
echo "  后端 API: http://$(hostname -I | awk '{print $1}'):8000/api/health"
echo "  管理员: admin / admin123"
echo ""
echo "  常用命令："
echo "    查看后端日志: journalctl -u ytcjc-backend -f"
echo "    重启后端:     systemctl restart ytcjc-backend"
echo "    重启 Nginx:   systemctl restart nginx"
echo "    更新部署:     bash $APP_DIR/deploy/update.sh"
echo ""
