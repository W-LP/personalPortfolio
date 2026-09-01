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

## 2026-09-01

- [修复] 私厨流式对话假性阻塞：AI 回复内容到达后不逐字显示、流结束时一次性出现 | `frontend/src/components/PersonalChief.vue`
  - 根因：sendMessage 中先创建普通对象 reply 再 push 进 messages 数组，流式追加时仍持有原始对象引用修改 content，Vue 3 中直接改原始对象不触发视图更新，直到 finally 中 sending=false 才触发一次重渲染
  - 修复：push 后从响应式数组取回 Proxy 引用（`messages.value[messages.value.length - 1]`）再追加流式内容
  - 后端 `/api/chief/chat/stream`（agent.astream 逐 token yield）与前端 fetch reader 读取链路本身均为真流式，无需改动
- [修复] AI 回复中的食谱参考图破图无法展示 | `frontend/src/md.js`
  - 根因：图床（百度百科 bkimg.cdn.bcebos.com、下厨房 i2.chuimg.com、百度图片 t13/t14.baidu.com 等）均有 Referer 防盗链，浏览器从 localhost:5174 引用被 403 拒绝
  - 修复：img 标签增加 `referrerpolicy="no-referrer"` 去掉 Referer 绕过防盗链；http 图片升级为 https（避免部署 HTTPS 后被混合内容拦截）；增加 onerror 兜底隐藏破图
  - 定位方式：终端网络受限无法调接口，改从 SQLite checkpoint 原始字节提取真实图片 URL 确认图床域名；node 本地验证渲染输出（markdown 图片/裸链接两种路径）
  - 清理临时调试脚本 check_imgs.py、check_imgs_db.py、test-md.mjs
- [新增] AI 学管功能：教师通过 Word/Excel/图片/文字指令管理学生信息与成绩（Vue + Spring Boot + FastAPI 三端） | `sql/student.sql`、`backend/.../student/**`、`fastapi-master/students/**`、`frontend/src/components/StudentManager.vue`、`frontend/src/App.vue`、`frontend/vite.config.js`
  - 建表 SQL：student（studentname/gender/age/height/weight/personality，列名纯小写无下划线）与 studentscore（studentid/examname/examdate/subject/scorevalue） | `sql/student.sql`
  - Spring Boot 学生模块（com.portfolio.business.student）：entity/mapper/dto/vo/service/controller 全套；StudentController 提供 /students/list、/students/listByNames、/students/saveOrUpdateBatch（按姓名自动判断新增/更新，空字段不覆盖）、/students/remove；ScoreController 提供 /scores/saveOrUpdateBatch（按 学生+考试+科目 判断增改，未匹配学生记入 missingStudents 不中断）与 /scores/list；批量查询后内存匹配避免循环查库；事务 rollbackFor=Exception.class | `StudentController.java`、`ScoreController.java`、`StudentServiceImpl.java`、`StudentScoreServiceImpl.java` 等
  - Spring Boot 基础设施：新增 IResultCode/ServiceException（业务异常统一枚举构造，错误码 STU+4位数字）与 StudentResultCodeEnum；GlobalExceptionHandler 增加 ServiceException 处理；TableConstants 增加 STUDENT/STUDENT_SCORE；启动类 MapperScan 扩展 student.mapper | `IResultCode.java`、`ServiceException.java`、`StudentResultCodeEnum.java`、`GlobalExceptionHandler.java`、`PortfolioApplication.java`
  - FastAPI 学管 Agent（students 包）：office_parser.py 以标准库 zipfile+xml 解析 xlsx/docx（零新增依赖，沙箱无法联网装 openpyxl/python-docx）；parser.py 图片走 DeepSeek 多模态提取表格；agent.py LangGraph create_agent 挂 6 个工具（query_students/list_students/save_students/remove_students/save_scores/list_scores）经 httpx 调 Spring Boot /api 下接口（地址 STUDENT_API_BASE 环境变量可配，默认 http://127.0.0.1:9096/api）；api.py 暴露 POST /api/student-agent/agent（multipart：file+text）| `students/office_parser.py`、`students/parser.py`、`students/agent.py`、`students/api.py`、`chief/main.py`
  - 前端：新增 StudentManager.vue 全屏页（#students hash 路由）：📎 上传 word/excel/图片/csv 即时交 Agent、文字指令对话、Agent 回复 markdown 渲染、右侧学生名单面板（Agent 修改数据后自动刷新，直连 Spring Boot）；App.vue 增加首页「AI 学管」卡片与 #students 路由分支；vite.config.js 增加 '/api/student-agent' → 8002 代理（置于 '/api' 之前，Spring Boot 的 /api/students 走通用 /api → 9096，二者不冲突）| `StudentManager.vue`、`App.vue`、`vite.config.js`
  - 验证：Spring Boot `mvn -o compile` BUILD SUCCESS（JAVA_HOME 用 jdk-21）；office_parser 用标准库构造最小 xlsx/docx 解析验证通过；py_compile 语法检查通过；`npm run build` 构建通过；FastAPI/MySQL 服务需重启后生效
- [修改] AI 学管接口改为流式输出并增加会话记忆 | `fastapi-master/students/agent.py`、`fastapi-master/students/api.py`、`fastapi-master/chief/main.py`、`frontend/src/components/StudentManager.vue`
  - 流式：students/api.py 端点由 POST /agent（一次性 JSON）改为 POST /stream（StreamingResponse，media_type=text/event-stream，X-Accel-Buffering: no），新增必填 Form 参数 thread_id；agent.py 新增 stream_student_agent 异步生成器，agent.astream(stream_mode="messages") 逐 token yield
  - 记忆：create_agent 挂 AsyncSqliteSaver checkpointer（独立库 chief/db/student_manager.db，绝对路径），按 thread_id 持久化多轮对话；main.py lifespan 增加 init_student_checkpointer()
  - 前端：StudentManager.vue 改用 fetch reader.read() 流式追加渲染；thread_id 持久化到 localStorage（刷新页面记忆不丢）；顶栏新增「新对话」按钮（重置 thread_id 清空记忆）
  - 验证：py_compile 语法检查通过、`npm run build` 构建通过；需重启 FastAPI 服务生效
- [新增] AI 学管教师注册/登录功能（角色：教师） | `sql/student.sql`、`backend/.../student/**`、`backend/.../basic/util/**`、`frontend/src/components/StudentManager.vue`
  - 建表：teacher（username 唯一索引、password 存 SHA-256 加盐摘要、realname） | `sql/student.sql`
  - Spring Boot：TeacherController 提供 /teacher/register（注册即登录）、/teacher/login、/teacher/check（token 校验）；密码摘要 PasswordUtil（SHA-256：账号+密码+pepper）；JWT 签发/校验 JwtUtil（手写 HMAC-SHA256，JDK 标准库零新增依赖，secret 可用环境变量 JWT_SECRET 覆盖）；错误码 STU2001/2002/2003；登录失败统一提示避免账号枚举 | `TeacherController.java`、`TeacherServiceImpl.java`、`JwtUtil.java`、`PasswordUtil.java`、`StudentResultCodeEnum.java`
  - 前端：StudentManager.vue 未登录显示登录/注册卡片（tab 切换），登录态持久化 localStorage（刷新自动恢复）；Agent 会话线程按教师隔离（thread_id 键 = student_thread_id_{teacherId}），退出登录清除该教师记忆；顶栏显示教师名 + 退出按钮 | `StudentManager.vue`
  - 验证：`mvn -o compile` BUILD SUCCESS、`npm run build` 构建通过；需执行 teacher 建表 SQL 并重启 Spring Boot 生效
- [修复] 访问 #students 页面全空白 | `frontend/src/components/StudentManager.vue`
  - 根因：未登录时 teacher.value 为 null，setup 初始化无条件调用 threadKey()（内部读取 teacher.value.id）抛出 TypeError，组件渲染失败导致页面空白
  - 修复：线程 ID 初始化增加判空，仅已登录时读取/生成
  - 验证：`npm run build` 构建通过
