#!/bin/bash
cd "$(dirname "$0")"
APP_DIR=$(pwd)
VENV_DIR="$APP_DIR/venv"

echo "========================================="
echo "  竞彩足球数据分析平台 - 后端部署"
echo "========================================="
echo "部署目录: $APP_DIR"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "错误：未找到 python3"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "安装依赖..."
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
    echo "创建 .env 配置文件..."
    cat > .env << 'ENVEOF'
SECRET_KEY=CHANGE_THIS_TO_A_RANDOM_SECRET_KEY
AI_BASE_URL=
AI_API_KEY=
ENVEOF
    echo "已创建 .env 文件，请编辑修改 SECRET_KEY！"
fi

echo "初始化数据库..."
python init_db.py

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo "启动: source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "默认管理员: admin / admin123"
echo "========================================="
