# 医疗疾病数据分析大屏可视化系统

一个覆盖 **数据采集 → 数据存储 → 数据分析 → 可视化展示 → 机器学习预测 → AI 对话问答** 全流程的医疗疾病数据分析大屏系统。

基于 Python 爬虫采集好大夫网站真实病例，存入 MySQL，后端 Flask 实时聚合分析，前端 Vue2 + ECharts 搭建数据大屏，并集成了基于 LangGraph + 智谱 GLM 的 NL2SQL 数据分析 Agent，将「静态大屏」升级为「对话式数据分析系统」。

> **数据规模**：835 条真实病例 · 23 类疾病 · 14 个字段

---

## 功能特性

| 模块 | 说明 |
|---|---|
| 🔍 数据采集 | Python `requests` + `lxml`(XPath) + `Selenium` 三级爬虫，列表页 → 详情页两级抓取，详情页复用已登录浏览器会话获取身高/体重/患病时长/过敏史 |
| 💾 数据存储 | MySQL 8.0（`medicalinfo` 库 / `cases` 表），CSV 中转批量入库 |
| 📊 数据分析 | 后端实时聚合 **9 个统计维度**：年龄段分布、疾病类型 Top6、男女患病占比、科室分布、热门医院、各疾病平均身高体重、高频关键词、患病时长分布、过敏史分布 |
| 📈 可视化大屏 | Vue 2 + ECharts 5.4 + data-view + echarts-wordcloud，集成玫瑰图、环形图、词云、水球图、身高体重/患病时长/过敏史柱状图、KPI 指标卡、病例滚动列表 |
| 🔗 图表联动 | 点击关键词云图中的疾病名称，年龄/性别/科室/患病时长/过敏史 5 张图联动筛选为该疾病的数据 |
| 🤖 病情预测 | `jieba` 分词 + TF-IDF + 随机森林，输入病情描述自动分类疾病类型，测试集准确率 **91.6%** |
| 💬 AI 问答 | LangGraph `create_react_agent` + 智谱 GLM，NL2SQL：自然语言提问 → 自动生成只读 SQL → 查询数据库 → 中文回答，内置 SQL 注入拦截 |

---

## 技术栈

- **后端**：Python 3 · Flask · Flask-CORS · PyMySQL · SQLAlchemy
- **前端**：Vue 2 · ECharts 5.4 · @jiaminghi/data-view · echarts-wordcloud · axios
- **数据库**：MySQL 8.0
- **机器学习**：jieba · TF-IDF · scikit-learn（RandomForest）
- **AI Agent**：LangGraph · langchain-openai · 智谱 GLM（glm-4.5-air）

---

## 目录结构

```
├── app.py                  # Flask 后端入口
├── config.py               # 集中配置（数据库 + 大模型）
├── .env.example            # 环境变量模板（复制为 .env 填入真实值）
├── requirements.txt        # Python 依赖
├── medicalinfo.sql         # MySQL 数据（835 条病例）
├── agent/                  # NL2SQL 数据分析 Agent
│   ├── nl2sql.py           #   Agent 主体（模型 + 工具 + prompt + 结果抽取）
│   └── format.py           #   后处理（markdown→HTML / 图表 / 摘要）
├── machine/                # 病情预测模型
│   └── tree.py             #   jieba + TF-IDF + 随机森林
├── spiders/                # 数据采集爬虫
├── utils/                  # 数据处理
│   ├── getAllData.py       #   大屏各图表数据聚合
│   ├── getPublicData.py    #   病例数据读取
│   └── query.py            #   数据库连接与查询
├── static/  templates/     # 静态资源与模板
├── front-end-template-1-master/   # Vue2 前端
│   └── src/views/
│       ├── Index.vue       #   数据大屏
│       ├── Chat.vue        #   智能问答对话页
│       ├── Pred.vue        #   病情预测
│       └── TableData.vue   #   病例表格
├── 项目改进说明.md          # 改进记录（bug 修复 + AI 升级）
└── 简历项目总结-1.md        # 简历写法与量化数据
```

---

## 快速开始

### 1. 环境要求

- Python 3.8+（建议 3.10+）
- Node.js 12+
- MySQL 8.0

### 2. 初始化数据库

```bash
# 创建数据库并导入数据
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS medicalinfo DEFAULT CHARSET utf8mb4;"
mysql -u root -p medicalinfo < medicalinfo.sql
```

### 3. 配置后端

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板并填写
cp .env.example .env
# 编辑 .env：填数据库密码 DB_PASSWORD 和智谱 API Key ZHIPU_API_KEY
```

> `ZHIPU_API_KEY` 用于 `/api/chat` 智能问答，获取地址：https://open.bigmodel.cn → 控制台 → API Keys

### 4. 启动后端

```bash
python app.py        # 监听 5000 端口
```

### 5. 启动前端

```bash
cd front-end-template-1-master
npm install
npm run serve        # 监听 8080 端口，/api 已代理到 5000
```

浏览器打开 **http://localhost:8080/** 查看数据大屏。

---

## API 接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/getHomeData` · `/api/home` | GET/POST | 大屏首页数据（年龄/性别/科室/时长/过敏史等全部图表数据） |
| `/api/chat` · `/chat` | GET/POST | NL2SQL 智能问答（返回 answer/sql/data/chart/summary） |
| `/api/chat/stream` · `/chat/stream` | GET/POST | 智能问答流式输出（SSE） |
| `/submitModel` · `/api/submit` | GET/POST | 病情分类预测 |
| `/tableData` · `/api/table` | GET/POST | 病例表格数据 |

---

## 数据说明

- 病例数据采集自好大夫在线（haodf.com）公开咨询内容，仅用于学习与演示，**请勿用于任何商业用途**。
- 数据包含患者姓名、症状描述、医院科室等公开信息，如涉及隐私请自行脱敏处理。

---

## 安全设计

- **密钥安全**：数据库密码与智谱 API Key 存于 `.env`（已加入 `.gitignore`，不会提交到仓库）。
- **SQL 注入防护**：NL2SQL Agent 只允许 `SELECT`/`WITH` 开头的只读语句，拦截 `insert/update/delete/drop/alter` 等危险关键字，查询结果限量 200 行。

---

## 参考文档

- [`项目改进说明.md`](项目改进说明.md) —— 本次改进的 bug 修复记录与 AI Agent 实现细节
- [`简历项目总结-1.md`](简历项目总结-1.md) —— 简历写法、量化数据与面试讲稿

---

*本项目前端大屏基于开源模板二次开发，数据采集、数据分析、机器学习、后端 API 与 AI Agent 为自主实现。*
