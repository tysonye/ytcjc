# 竞彩足球比赛数据获取与盘口分析系统

实时获取竞彩足球比赛数据、赔率指数和 AI 预测分析的工具，支持大屏图形界面展示。

## 功能特性

- ✅ 实时获取比赛场次信息
- ✅ 提取赔率指数（主胜、平局、客胜）
- ✅ 获取 AI 预测数据
- ✅ 盘口分析（让球分析、价值投注计算）
- ✅ 实时监控赔率变化
- ✅ 数据导出为 JSON 格式
- ✅ 支持自定义刷新间隔
- ✅ 🖥️ 大屏图形界面展示（新增）
- ✅ 📊 可视化盘口分析面板
- ✅ 🔍 联赛和状态筛选功能

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 🖥️ 图形界面模式（推荐）

```bash
python gui_main.py
```

**界面功能：**
- 大屏展示所有比赛信息
- 左侧显示比赛列表，右侧显示比赛详情
- 点击比赛卡片查看详细对阵信息
- 点击"查看盘口分析"按钮查看分析结果
- 支持按联赛和状态筛选比赛
- 实时刷新数据（点击刷新按钮）

### 1. 单次获取比赛数据

```bash
python main.py
```

执行后会：
- 获取当前所有比赛数据
- 显示比赛详情（联赛、时间、对阵、赔率等）
- 进行盘口分析
- 保存数据到 `matches_data.json`

### 2. 实时监控模式

```bash
python realtime_monitor.py --interval 60
```

参数说明：
- `--interval`: 刷新间隔（秒），默认 60 秒
- `--duration`: 监控时长（分钟），不指定则持续监控
- `--url`: 目标网址，默认为 https://jc.titan007.com/index.aspx

示例：
```bash
# 每 30 秒刷新一次，监控 10 分钟
python realtime_monitor.py --interval 30 --duration 10

# 每 2 分钟刷新一次，持续监控
python realtime_monitor.py --interval 120
```

## 输出数据说明

### 比赛数据字段

- `match_id`: 比赛编号（如：周五 001）
- `league`: 联赛名称
- `match_time`: 比赛时间
- `status`: 比赛状态
- `home_team`: 主队名称
- `away_team`: 客队名称
- `score`: 比分
- `odds`: 赔率指数
  - `home`: 主胜赔率
  - `draw`: 平局赔率
  - `away`: 客胜赔率
- `analysis`: 分析数据
  - `ai_prediction`: AI 预测信息

### 盘口分析内容

- **让球分析**: 判断让球方及盘口深浅
- **赔付率**: 计算隐含概率
- **庄家优势**: 计算庄家利润率
- **公平价值**: 计算各结果的公平价值

## 数据文件

- `matches_data.json`: 单次获取的比赛数据和分析结果
- `historical_data.json`: 实时监控的历史数据记录（保留最近 100 条）

## 注意事项

1. 请确保网络连接正常
2. 建议设置合理的刷新间隔，避免频繁请求（建议≥30 秒）
3. 数据仅供参考，请理性看待

## 技术栈

- Python 3.7+
- requests: HTTP 请求
- beautifulsoup4: HTML 解析
- colorama: 彩色输出
- lxml: XML/HTML 解析器
