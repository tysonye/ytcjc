#!/bin/bash
set -e

APP_DIR="/opt/ytcjc"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

echo "========================================="
echo "  竞彩足球数据分析平台 - 增量更新"
echo "========================================="

echo ""
echo "[1/4] 更新后端依赖..."
cd "$BACKEND_DIR"
source venv/bin/activate
pip install -r requirements.txt -q

echo ""
echo "[2/4] 重新构建前端..."
cd "$FRONTEND_DIR"
npm install --silent
npm run build

echo ""
echo "[3/4] 重启后端服务..."
systemctl restart ytcjc-backend

echo ""
echo "[4/4] 重载 Nginx..."
systemctl reload nginx

echo ""
echo "更新完成！"
echo "  后端状态: systemctl status ytcjc-backend"
echo "  后端日志: journalctl -u ytcjc-backend -f --no-pager -n 20"
