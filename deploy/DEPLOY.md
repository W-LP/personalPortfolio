# 个人作品集网站 - 宝塔面板部署教程

> 技术栈: Vue 3 (Vite) + Spring Boot 3 (Java 21) + MySQL + Nginx
> 目录结构:
> ```
> /www/wwwroot/portfolio/
> ├── frontend/            # Vue 前端源码，构建产物在 frontend/dist
> ├── backend/             # Spring Boot 后端源码，构建产物 app.jar
> ├── sql/init.sql         # 数据库初始化脚本
> └── deploy/              # 本目录: 部署配置模板
> ```

---

## 一、服务器环境准备（宝塔面板）

在宝塔「软件商店」安装:

| 软件 | 版本建议 | 用途 |
|------|---------|------|
| Nginx | 1.22+ | 静态站点 + API 反向代理 |
| MySQL | 8.0（5.7 亦可） | 数据库 |
| OpenJDK | 21 | 运行后端 jar |

Java 21 安装（宝塔软件商店没有时，用命令行）:

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install -y openjdk-21-jre-headless
# CentOS/Alibaba Cloud Linux
sudo yum install -y java-21-openjdk
java -version   # 确认输出 21.x
```

## 二、上传代码

- 宝塔「文件」-> 进入 `/www/wwwroot/` -> 上传本项目压缩包并解压，目录名改为 `portfolio`；
- 或使用宝塔 Git 功能直接拉取仓库。

最终路径:
- 前端: `/www/wwwroot/portfolio/frontend`
- 后端: `/www/wwwroot/portfolio/backend`
- 数据库脚本: `/www/wwwroot/portfolio/sql/init.sql`

## 三、初始化数据库

1. 宝塔「数据库」->「添加数据库」: 数据库名 `portfolio`，用户名 `portfolio`，密码自定义；
2. 选中该库 ->「导入」-> 选择 `sql/init.sql`（也可在 phpMyAdmin 中执行）；
3. 记住你设置的密码，下一步会用到。

## 四、构建并启动后端

```bash
cd /www/wwwroot/portfolio/backend

# 使用 Maven Wrapper 构建（自动下载 Maven 3.9.x，无需服务器装 Maven）
./mvnw clean package -DskipTests

# 构建产物: target/portfolio-backend-0.0.1-SNAPSHOT.jar
# 拷贝为固定文件名 app.jar（与 systemd 服务配置对应）
cp target/portfolio-backend-0.0.1-SNAPSHOT.jar app.jar
```

安装并启动 systemd 服务:

```bash
# 编辑服务文件，把 DB_PASSWORD 改成你的数据库密码
vim /www/wwwroot/portfolio/deploy/portfolio.service

sudo cp /www/wwwroot/portfolio/deploy/portfolio.service /etc/systemd/system/portfolio.service
sudo systemctl daemon-reload
sudo systemctl enable --now portfolio

# 检查状态与日志
systemctl status portfolio
journalctl -u portfolio -f
```

验证后端:
```bash
curl http://127.0.0.1:9096/api/health              # 应返回 {"code":200,"data":{"status":"UP",...}}
curl -X POST http://127.0.0.1:9096/api/projects/list   # 应返回 {"code":200,"data":[...]}
```

> 提示: `ExecStart` 中的 `java` 路径可能不同，用 `which java` 确认后修改。

## 五、构建前端

```bash
cd /www/wwwroot/portfolio/frontend
npm install
npm run build
# 产物: /www/wwwroot/portfolio/frontend/dist
```

## 六、宝塔添加站点并配置 Nginx

1. 宝塔「网站」->「添加站点」: 域名填你的域名或服务器 IP（如 `www.example.com`），
   「根目录」选择 `/www/wwwroot/portfolio/frontend/dist`；
2. 进入站点「设置」->「配置文件」，用 `deploy/portfolio-nginx.conf` 的内容
   替换其中 `server { ... }` 部分，并把 `server_name` 改成你的域名；
3. 如已申请 SSL，宝塔会自动管理证书，无需改 nginx 配置；
4. 「网站」-> 站点「设置」->「伪静态」-> 选择 `laravel5` 或直接按配置文件中的
   `try_files` 规则（SPA history 路由回退）。

## 七、监控（部署后的日常运维）

| 监控项 | 方式 |
|--------|------|
| 服务器资源 | 宝塔面板首页仪表盘（CPU/内存/磁盘/带宽） |
| 后端存活 | `curl http://127.0.0.1:9096/actuator/health`，可接入监控工具定时探测 |
| 后端日志 | `journalctl -u portfolio -f`（或宝塔「日志」-> 网站日志） |
| 告警 | 宝塔「监控」->「告警通知」绑定邮箱/微信，设置 CPU、内存阈值 |

## 八、常见问题

- **502 Bad Gateway**: 后端没起来 -> `systemctl status portfolio` 看日志，确认后端端口（application.yml 中 `server.port`，默认 9096）与 nginx `proxy_pass` 一致、端口未被占用、Java 版本正确；
- **数据库连接失败**: 确认 MySQL 已启动、账号密码与 `portfolio.service` 中 `DB_PASSWORD` 一致，
  并允许 `portfolio` 用户从 `localhost` 访问（`sql/init.sql` 已含授权语句）；
- **前端页面空白 / 404**: 确认 nginx `root` 指向 `frontend/dist`，且 `try_files` 回退已配置；
- **API 跨域报错**: 生产环境由 nginx 同源代理，不应出现跨域；本地开发由 Vite 代理转发。
