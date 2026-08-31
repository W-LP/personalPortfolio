# 个人作品集网站

个人作品集网站的最简可运行框架：**Vue 3 + Spring Boot 3 (Java 21) + MySQL**，配套**宝塔面板**部署与监控配置。
后端架构遵循 **[docs/DEVELOPMENT-STANDARDS.md](docs/DEVELOPMENT-STANDARDS.md)**（整理自 syncplant-tms 开发规范）。

## 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 前端 | Vue 3 + Vite | 单页应用，SPA history 路由预留，页面请求 `/api/projects/list` |
| 后端 | Java 21 + Spring Boot 3.4 | REST API + MyBatis-Plus，统一返回 `R<T>`，内置 Actuator 健康检查 |
| 数据库 | MySQL 8.0 | 结构由 `sql/init.sql` 建表（见下方初始化步骤） |
| 部署 | Nginx + systemd + 宝塔 | 前端静态托管 + `/api` 反向代理；后端 systemd 守护 |

## 目录结构

```
personalPortfolio/
├── frontend/                  # Vue 3 前端
│   ├── src/App.vue            # 作品集首页（展示后端返回的项目列表）
│   ├── src/style.css          # 全局样式
│   └── vite.config.js         # 开发代理: /api -> localhost:9096
├── backend/                   # Spring Boot 后端（遵循 syncplant-tms 分层规范）
│   ├── pom.xml                # Spring Boot 3.4.5, MyBatis-Plus, Java 21
│   └── src/main/
│       ├── java/com/portfolio/
│       │   ├── PortfolioApplication.java          # 启动类 (@MapperScan)
│       │   └── business/
│       │       ├── basic/                         # 基础包
│       │       │   ├── api/                       # 统一返回体 R<T>
│       │       │   ├── config/                    # 跨域、全局异常处理
│       │       │   ├── constant/                  # TableConstants / TipConstants
│       │       │   └── controller/                # 健康检查
│       │       └── project/                       # 业务模块
│       │           ├── controller/ProjectController.java
│       │           ├── entity/Project.java
│       │           ├── mapper/ProjectMapper.java  # MyBatis-Plus Mapper
│       │           └── service/
│       │               ├── IProjectService.java
│       │               └── impl/ProjectServiceImpl.java
│       └── resources/application.yml   # 数据源（环境变量可覆盖）+ MyBatis-Plus 配置
├── sql/init.sql               # 建库 + 建表 + 示例数据
├── deploy/
│   ├── portfolio.service      # 后端 systemd 服务模板
│   ├── portfolio-nginx.conf   # 宝塔 nginx 站点配置模板
│   └── DEPLOY.md              # 宝塔部署 + 监控教程（从零到上线）
└── README.md
```

## 本地开发

### 1. 启动 MySQL 并初始化

```bash
mysql -uroot -p < sql/init.sql   # 创建 portfolio 库 + 账号 + 示例数据
```

默认账号 `portfolio / portfolio123`（见 `sql/init.sql`，可修改）。

### 2. 启动后端（9096 端口）

```bash
cd backend
./mvnw spring-boot:run          # Windows: mvnw.cmd spring-boot:run
```

验证: `curl http://localhost:9096/api/health` → `{"code":200,"data":{"status":"UP",...}}`
`curl -X POST http://localhost:9096/api/projects/list` → `{"code":200,"data":[...]}`

> 数据库连接可用环境变量覆盖: `DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD`。

### 3. 启动前端（5173 端口）

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

开发模式下 `/api` 请求由 Vite 代理转发到 9096，无需处理跨域。

### 4. 后端打包

```bash
cd backend
./mvnw clean package -DskipTests
# 产物: target/portfolio-backend-0.0.1-SNAPSHOT.jar
```

## AI 私厨（Personal Chief）

基于 **LangGraph + FastAPI** 的多模态 Agent：上传食材照片 → 识别食材 → web 搜索食谱 → 按
营养/难度打分输出推荐报告。前端入口在首页页签「AI 私厨」，后端代码位于 `fastapi-master/chief/`。

### 1. 安装依赖（首次，在 fastapi-master 目录）

```bash
cd fastapi-master
uv pip install --python .venv/Scripts/python.exe langchain langchain-deepseek langchain-tavily langgraph langgraph-checkpoint-sqlite alibabacloud-oss-v2 python-dotenv
```

> 密钥配置见 `fastapi-master/chief/.env`（DeepSeek / Tavily / OSS，已加入 .gitignore 不入库）。

### 2. 启动私厨服务（8002 端口）

```bash
cd fastapi-master
.venv/Scripts/python.exe -m uvicorn chief.main:app --host 127.0.0.1 --port 8002 --reload
```

### 3. 前端访问

启动 `npm run dev` 后打开 http://localhost:5173 ，切换页签到「AI 私厨」即可对话。
开发模式下 Vite 已将 `/api/chief` 代理到 8002 端口，无需处理跨域。

> 注意：图片直传 OSS 需在阿里云 bucket 控制台配置 CORS 规则（允许 PUT 与对应来源）。

## API 一览

> 统一返回体 `R<T>`：`{"code":200,"msg":"操作成功","data":...}`；`code=500` 表示失败。

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| POST | `/api/projects/list` | 项目列表（按 sortOrder 升序） |
| POST | `/api/projects/saveOrUpdate` | 新增/修改项目（body: 项目 JSON） |
| POST | `/api/projects/remove?ids=1,2` | 删除项目（逗号分隔 id） |
| GET | `/actuator/health` | Spring Boot 原生健康检查 |

私厨（FastAPI，8002 端口，前缀 `/api/chief`）：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/chief/health` | 私厨健康检查 |
| POST | `/api/chief/chat/stream` | 流式对话（SSE，body: message/image_url/thread_id） |
| GET | `/api/chief/chat/messages?thread_id=` | 查询会话历史 |
| DELETE | `/api/chief/chat/messages?thread_id=` | 清空会话 |
| GET | `/api/chief/oss/presign?filename=` | 申请 OSS 直传预签名 URL |

## 宝塔部署

完整图文步骤见 **[deploy/DEPLOY.md](deploy/DEPLOY.md)**，核心三步：

1. 宝塔安装 Nginx / MySQL / OpenJDK 21，导入 `sql/init.sql`；
2. 后端 `./mvnw package` 后以 systemd 服务运行（`deploy/portfolio.service`）；
3. 前端 `npm run build`，宝塔添加站点指向 `frontend/dist`，套用 `deploy/portfolio-nginx.conf`。

监控: 宝塔仪表盘看资源；`/actuator/health` 供存活探测；`journalctl -u portfolio` 看后端日志。

## 后续可以扩展的方向

- 前端: vue-router 多页面（首页 / 关于 / 项目详情）、TypeScript、组件库（Element Plus / Naive UI）；
- 后端: 登录鉴权（Spring Security + JWT）、文件上传、接口分页（MyBatis-Plus 分页插件）、审计字段基类；
- 部署: HTTPS 证书、CDN、CI/CD（宝塔 WebHook 自动构建）。
