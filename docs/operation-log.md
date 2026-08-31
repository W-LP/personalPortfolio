# 操作日志

按日期记录项目变更，便于追溯。

## 2026-08-27

- [修改] 前端整体风格改造为美剧《绝命毒师》(Breaking Bad) 主题 | `frontend/src/style.css`
  - 配色更换：实验室深黑背景 `#0d0e0b` + 冰毒蓝强调色 `#40c4e8` + 剧标元素绿 `#3e8853` + 新墨西哥沙漠黄 `#d1a54c`
  - body 增加冰蓝雾光与沙漠余晖径向渐变氛围
  - 新增周期表元素方块样式 `.element-box`（左侧原子序数、中间符号、底部元素名），移动端适配
  - 卡片顶部增加冰毒结晶光带 `::before`，hover 泛蓝光；标签改为迷你周期表绿框样式
  - 等宽字体 `'Courier New'` 用于英文点缀，营造实验室报告质感
- [修改] 首页模板融入主题装饰与文案 | `frontend/src/App.vue`
  - Hero 标题改为「你好，我是 K / Fe / Zn」三块绿色元素格（拼音 Kai-Fa-Zhe 致敬 Br Ba 剧标）
  - 副标题加入名言 "Chemistry is the study of change."；提示行加入「作品纯度 99.1%」彩蛋
  - 作品集标题追加 "// Lab Reports"；加载文案 "COOKING…"；链接文案改为「查看实验记录」
  - 页脚加入 "RESPECT THE CHEMISTRY."
- [修改] 网站图标更换为周期表溴元素方格 (Br) | `frontend/public/favicon.svg`
- [配置] 增加 theme-color 元信息跟随暗色底色 | `frontend/index.html`
- [新增] 加入《绝命毒师》主题插画（AI 生成，规避网络抓取版权风险） | `frontend/src/App.vue`
  - Hero 区新增横幅插画：黄昏新墨西哥沙漠中孤独房车（landscape_16_9）
  - 新增「经典意象 // Iconic Scenes」画廊区：防护服实验室、蓝色结晶静物、海森堡剪影海报三张方图（懒加载）
- [修改] 补充插画与画廊样式：横幅暗角蓝光晕、场景卡片 hover 浮起泛光、图注等宽字体 | `frontend/src/style.css`
- [新增] 插画改为本地背景板集成（应用户要求：素材本地化 + 作为背景而非直接展示）
  - 环境限制说明：终端沙箱无法出网（`Invoke-WebRequest` 报代理配置错误、`curl.exe`/Node fetch 均 DNS 失败、`Test-NetConnection` 解析失败），在线下载不可行，临时脚本 `download-art.cjs` 已删除
  - 改为本地手绘原创 SVG 插画三张 | `frontend/public/img/rv-desert.svg`、`crystal-cluster.svg`、`lab-glass.svg`
- [修改] App.vue 移除 hero 内联横幅 `<img>` 与「经典意象」画廊 `<img>` 展示区，回归纯文案结构 | `frontend/src/App.vue`
- [修改] 背景板集成：hero 区挂沙漠房车插画（叠深色遮罩保证可读）、body 固定结晶微纹理 (opacity .05)、状态框右侧结晶点缀、页脚玻璃器皿线稿装饰带 (opacity .26)、移动端 hero 适配 | `frontend/src/style.css`

## 2026-08-31

- [新增] 私厨 Agent 迁移入本项目（源自 D:\tools\hello，接口在 fastapi-master 实现） | `fastapi-master/chief/`
  - `chief/main.py`：FastAPI 入口，端口 8002，路由统一前缀 `/api/chief`，含健康检查
  - `chief/agent.py`：LangGraph Agent（deepseek 多模态 + TavilySearch + SqliteSaver 记忆）；修复两处原项目缺陷：SQLite 由相对路径 `../db` 改为基于 `__file__` 的绝对路径；日志统一用 `chief.logger`（原项目误导入 pip 的 logger 包）
  - `chief/api/chat.py`：流式对话 / 历史查询 / 清空会话三接口
  - `chief/api/oss.py`：OSS 预签名直传；修复三处原项目缺陷：accessUrl 反引号混入 URL（导致图片 404）、函数名 chat_endpoint 与功能不符改为 presign_upload、OSS_ENDPOINT/OSS_REGION 改由 .env 读取
  - `chief/schemas.py`：ChatRequest（message 非空校验）
  - `chief/logger.py`：统一日志配置
  - `chief/.env`：DeepSeek / Tavily / OSS 密钥（gitignore 已忽略）
- [新增] 私厨前端聊天组件 | `frontend/src/components/PersonalChief.vue`
  - SSE 流式对话（fetch + TextDecoder 流式解码防中文乱码，Enter 发送 / Shift+Enter 换行）
  - 图片 OSS 直传（presign → PUT → accessUrl 随消息发送），消息区自动滚底、流式光标动画
  - 历史消息加载、清空会话；thread_id 持久化于 localStorage，刷新不丢记忆
- [修改] 首页新增页签导航「作品集 / AI 私厨」，v-show 切换不销毁组件状态 | `frontend/src/App.vue`
- [修改] 页签样式（冰蓝激活态、hover 微光，移动端适配） | `frontend/src/style.css`
- [修改] Vite 开发代理新增 `/api/chief` → localhost:8002（置于通用 `/api` 规则之前保证优先匹配） | `frontend/vite.config.js`
- [配置] 新增 VITE_CHIEF_TARGET 环境变量 | `frontend/.env.development`、`frontend/.env.production`
- [配置] 忽略私厨密钥与本地数据库 | `fastapi-master/.gitignore`（追加 chief/.env、chief/db/）
- [修改] README 新增「AI 私厨」启动章节与私厨 API 一览 | `README.md`
- [命令] 环境限制说明：沙箱终端无法出网（uv/pip/npm 均 DNS 解析失败，Python `import asyncio` 报 WinError 10038 IOCP 被拦截），依赖安装与服务启动验证需在真实终端执行：
  - `cd fastapi-master && uv pip install --python .venv/Scripts/python.exe langchain langchain-deepseek langchain-tavily langgraph langgraph-checkpoint-sqlite alibabacloud-oss-v2 python-dotenv`
  - `cd fastapi-master && .venv/Scripts/python.exe -m uvicorn chief.main:app --host 127.0.0.1 --port 8002 --reload`

## 2026-08-31（二次迭代：流式与渲染问题修复）

- [修复] 流式输出阻塞问题：`agent.stream`（同步迭代器）在异步生成器中会阻塞事件循环，导致响应攒到生成完毕才一次性下发 | `fastapi-master/chief/agent.py`
  - 改为 `agent.astream` 异步迭代，逐块实时下发
  - 兼容多模态 content 块格式：chunk.content 为列表时提取其中 type=text 的文本块
- [修复] 流式响应防缓冲：StreamingResponse 增加 `Cache-Control: no-cache` 与 `X-Accel-Buffering: no`（Nginx 反代场景禁用缓冲） | `fastapi-master/chief/api/chat.py`
- [新增] 轻量 Markdown 渲染器（无第三方依赖，手写实现） | `frontend/src/md.js`
  - 支持：标题（#~###### 映射 h2~h5）、粗体/斜体/删除线、行内代码、围栏代码块、图片、链接、裸链接（图片后缀自动渲染为 img）、无序/有序列表、引用、分隔线、表格、段落换行
  - 安全：先转义全部 HTML 再生成受控标签，防止 XSS 注入
- [修改] AI 回复改为 markdown 渲染（v-html + :deep 样式）：标题分级配色、食谱图片圆角边框、得分表格（表头冰蓝底/斑马纹/横向滚动）、代码块、引用黄边、列表 | `frontend/src/components/PersonalChief.vue`
  - 用户消息保持纯文本；流式过程中逐块重新渲染 markdown
  - md-body 覆盖 bubble 的 pre-wrap 为 normal，避免双重换行

## 2026-08-31（三次迭代：入口改为作品集卡片）

- [修改] 移除顶部页签导航，恢复单页作品集结构 | `frontend/src/App.vue`
- [修改] 私厨入口改为作品集卡片：前端过滤数据库占位项目「待添加项目二」，同位插入静态「AI 私厨」卡片（标题/简介/技术栈标签 Vue·Python·LangGraph·FastAPI/超链接） | `frontend/src/App.vue`、`sql/init.sql`（数据未改，前端过滤）
- [修改] 点击卡片超链接「进入私厨实验室」跳转私厨功能页：手写 hash 路由（#chief），监听 hashchange 切换视图，支持浏览器前进/后退；私厨页顶部提供「<< 返回作品集」导航；私厨组件改为 v-if 进入页面时才挂载加载历史 | `frontend/src/App.vue`
- [修改] 样式：删除 tabs 相关样式；新增 .chief-back 返回导航；私厨卡片 .chief-card 顶部光带改绿色渐变与普通作品卡区分 | `frontend/src/style.css`

## 2026-08-31（四次迭代：私厨改为全屏独立页面）

- [修改] 视图结构改为互斥双顶层视图：主页（.page 容器，hero+作品集+页脚）与私厨页完全分离，私厨不再嵌套在主页容器内 | `frontend/src/App.vue`
- [修改] 私厨页全屏化：组件根 .chief-page 采用 100vh/100dvh 三段式 flex 布局（顶栏/消息区/输入区），不共享主页 hero 与页脚 | `frontend/src/components/PersonalChief.vue`
  - 顶栏：左侧「<< 作品集」返回按钮（emit back 事件，由 App.vue 处理 hash 路由）、居中标题「私厨实验室」+副标题、右侧会话状态灯与清空按钮
  - 消息区：flex:1 撑满剩余高度自适应滚动（原固定 420px 高度删除），内容 860px 限宽居中
  - 输入区：底部固定、860px 限宽与消息区对齐，带上投影
  - 移动端：顶栏紧凑化、隐藏状态灯，100dvh 适配移动浏览器地址栏
- [修改] 删除 App.vue 中旧的 .chief-back 导航与 style.css 对应样式（返回功能并入私厨页顶栏） | `frontend/src/App.vue`、`frontend/src/style.css`

## 2026-08-31（五次迭代：私厨宝塔部署配置）

- [新增] 私厨 FastAPI systemd 服务模板（沿用 portfolio.service 模式：www 用户、自动重启、日志入 journal；单 worker 兼容 SQLite checkpointer） | `deploy/portfolio-chief.service`
- [修改] Nginx 站点配置新增 /api/chief/ 反代至 8002 端口：proxy_buffering off（SSE 流式关键）、读超时放宽 300s（Agent 检索耗时长）、HTTP/1.1 长连接 | `deploy/portfolio-nginx.conf`
