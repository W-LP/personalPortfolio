# 后端开发规范文档

> 本文档整理自参考项目 `syncplant-business-tms`（`D:\syncplant-business-tms\src\backend\syncplant-tms`）的架构与官方《目录结构》说明，作为本仓库后端开发的统一规范。
>
> 参考项目技术栈为 **Spring Cloud + MyBatis-Plus + Nacos（Java 8）**，依赖公司自研 `com.springsciyon.core` 框架；本仓库（personalPortfolio）为 **Spring Boot 3 + MyBatis-Plus + MySQL（Java 21）** 的轻量实现，规范中涉及公司框架的部分做了等价适配，见文末「适配说明」。

---

## 一、总体架构

```
┌─────────────────────────────────────────────────────────┐
│  前端 (Vue)          ──HTTP──►   Nginx 反代 /api          │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────┐
│  后端服务 (Spring Boot + MyBatis-Plus + MySQL)            │
│  ┌────────────────────────────────────────────────────┐  │
│  │ controller  (接收请求, 参数校验, 统一 R 返回)          │  │
│  │      ↓                                              │  │
│  │ service 接口 (I 前缀) ──► service/impl (业务逻辑)     │  │
│  │      ↓                                              │  │
│  │ mapper (数据访问, BaseMapper + 自定义 SQL)            │  │
│  │      ↓                                              │  │
│  │ MySQL                                               │  │
│  └────────────────────────────────────────────────────┘  │
│  basic 基础包: config / constant / enums / utils         │
└─────────────────────────────────────────────────────────┘
```

## 二、包结构规范（核心，来自官方《目录结构》）

```
com.portfolio.business
├── PortfolioApplication.java      # 启动类
├── basic                          # 整个项目基础包
│   ├── api                        # 统一返回体 R / 异常定义
│   ├── config                     # 全局配置：跨域、全局异常处理、MyBatis-Plus 等
│   ├── constant                   # 常量定义，禁止出现魔法值
│   │   ├── TableConstants         # 表名常量统一编写地方
│   │   └── TipConstants           # 一些公用提示信息
│   ├── enums                      # 枚举包，解决魔法值（字典值统一在此定义）
│   ├── controller                 # 基础能力接口（健康检查等）
│   └── utils                      # 自定义工具类
└── project                        # 业务模块（后续有其它业务继续追加模块）
    ├── controller                 # 控制器
    ├── entity                     # 实体
    │   ├── vo                     # 返回参数的实体类，禁止用 Map
    │   └── dto                    # 接收参数用的实体类，禁止用 Map
    ├── mapper                     # 数据访问层；所有自定义 SQL 方法一律以 xxxSql 结尾
    ├── service
    │   └── impl                   # 接口实现层；无特殊情况每个方法只干一件事，不超过 80 行
    └── (可选) xxljob              # 定时任务（参考项目约定）
```

**规则要点：**
1. 业务模块按领域划分，新增业务直接追加同级模块（如 `order`、`user`），**禁止把业务代码写进 basic**；
2. `basic` 只放跨模块复用的基础能力；
3. 空目录不需要创建，用到才建；
4. 接口请求/响应对象必须用 **DTO/VO**，**禁止用 `Map` 直接传参和返回**。

## 三、分层职责与命名规范

| 层 | 命名 | 继承/注解 | 职责 |
|----|------|-----------|------|
| 启动类 | `XxxApplication` | `@SpringBootApplication` + `@MapperScan("...mapper")` | 装配与扫描 |
| Controller | `ProjectController` | `@RestController` + `@RequestMapping("/api/projects")` + `@AllArgsConstructor` | 参数校验、路由、统一返回 |
| Service 接口 | `IProjectService` | `extends IService<Project>` | 业务方法声明 |
| Service 实现 | `ProjectServiceImpl` | `extends ServiceImpl<ProjectMapper, Project> implements IProjectService` + `@Service` | 业务逻辑 |
| Mapper | `ProjectMapper` | `extends BaseMapper<Project>`（自定义方法以 `xxxSql` 结尾） | 数据访问 |
| Entity | `Project` | `@Data @TableName(...)` | 表映射 |
| DTO | `XxxDto` | `@Data implements Serializable` | 接收参数 |
| VO | `XxxVo` | `@Data implements Serializable` | 返回参数 |

**类名前缀规则：** 参考项目业务模块类统一带模块前缀（如 tms 模块 → `TmsBaseAddress`）。本仓库模块与实体同名（project 模块 → `Project`），模块内命名自然唯一即可；**多模块共存时必须在实体/控制器前加模块前缀**，避免冲突。

## 四、代码规范

### 4.1 统一返回体 `R<T>`
所有 Controller 方法**必须**返回 `R<T>`（`com.portfolio.business.basic.api.R`）：
```java
R.data(obj)          // 成功，携带数据
R.status(boolean)    // 成功/失败，无数据
R.fail(msg)          // 失败，携带提示信息
```
禁止直接返回裸对象或裸集合。

### 4.2 接口风格（参考项目约定：全 POST）
| 语义 | 约定 |
|------|------|
| 列表/分页查询 | `POST /xxx/list` |
| 新增/修改 | `POST /xxx/saveOrUpdate`（`@RequestBody` 实体或 DTO） |
| 删除 | `POST /xxx/remove`（`@RequestParam String ids`，逗号分隔，Service 内拆分） |
| 其它业务动作 | `POST /xxx/动作名` |

> 适配说明：参考项目经网关剥离 `/api` 前缀，路径为 `/tms/baseAddress`；本仓库 nginx 反代 `/api/`，故统一以 `/api/projects` 为模块根路径。

### 4.3 禁止魔法值
- 枚举、字典、状态、提示语等一律抽到 `basic.constant` / `basic.enums`；
- 表名统一放 `TableConstants`，提示语统一放 `TipConstants`；
- 枚举格式（参考 `TmsSfRulesTypeEnum`）：`@Getter @AllArgsConstructor`，字段 `code/text/remark`，提供 `fromCode()`。

### 4.4 实体规范（参考 `TmsBaseAddress`）
```java
@Data
@TableName("project")
public class Project implements Serializable {
    private static final long serialVersionUID = 1L;

    /** 主键 */
    @TableId(type = IdType.AUTO)
    private Long id;

    /** 项目标题 */
    @NotBlank(message = "项目标题不能为空")
    @Size(max = 100, message = "项目标题长度不能超过100个字符")
    @TableField("title")
    private String title;
}
```
- `@TableName` 表名、`@TableId` 主键、`@TableField("列名")` 列映射（下划线 ↔ 驼峰）；
- 每个字段必须有 Javadoc 注释；JSR-303 校验注解必须带**中文** message；
- 类注释模板：`/** Xxx对象 表名 @author 作者 @date 日期 */`。

### 4.5 Service 规范
- 接口 `I 前缀`，实现类 `ServiceImpl` 后缀，放在 `service/impl`；
- **无特殊情况每个方法只干一件事，不超过 80 行**；
- 复杂逻辑拆分私有方法。

### 4.6 注释规范
- 类/方法/字段必须写 Javadoc，注明作者、日期；
- 方法注释说明：做什么、参数、返回值。

## 五、数据访问规范（MyBatis-Plus）

1. Mapper 接口 `extends BaseMapper<Entity>`，单表 CRUD 直接用框架方法，不写 SQL；
2. 自定义 SQL：Mapper 接口声明方法（**以 `xxxSql` 结尾**）+ `resources/mapper/XxxMapper.xml` 实现；
3. XML 约定：
   - `namespace` 写 Mapper 接口全限定名；
   - 提供 `BaseResultMap`（列 → 属性映射）与 `Base_Column_List`（通用查询列）；
   - 列名大写（`ID`、`CREATOR`），业务下划线列（`type_dic`）照原样；
4. 复杂 SQL 用 XML，禁止在 Java 里拼接 SQL 字符串。

## 六、工程与部署规范

### 6.1 启动类注解（参考 `TmsApplication`）
```java
@SpringBootApplication
@MapperScan({"com.portfolio.business.project.mapper"})   // 有多个模块就列多个包
@EnableScheduling                                        // 有定时任务时开启
public class PortfolioApplication { ... }
```

### 6.2 配置管理
- 数据库连接、中间件配置统一放 `src/main/resources/application.yml`，**敏感信息用环境变量占位**（`${DB_USER:root}`），部署时由环境变量/面板注入；
- 全局配置类放 `basic/config`（跨域、全局异常处理等）。

### 6.3 打包与部署
- `mvnw clean package -DskipTests` 产出可执行 jar；
- 生产建议开启 Spring Boot 分层打包（参考项目 `layers.xml` 按 dependencies → loader → application 分层，配合 Docker 多阶段构建）；
- 部署由 systemd / 容器托管，健康检查走 `/actuator/health`。

## 七、开发流程规范（参考《合并分支.txt》）

以 devlop 分支合并到 master 为例：
1. 先保证 devlop 分支代码已 push；
2. 切换到 master 分支并 pull 最新；
3. IDE 右下角 Git → Remote → origin → devlop → `Merge devlop into master`。

补充约定：
- 开发分支命名：`feature/功能`、`fix/缺陷`；
- 合并前必须本地构建通过，禁止把编译不过的代码合并到 master。

## 八、本仓库适配说明

| 参考项目 | 本仓库（personalPortfolio） | 说明 |
|----------|------------------------------|------|
| Spring Cloud + Nacos | Spring Boot 单体 | 规模小，暂不引入注册中心；后续微服务化时按参考项目补 Nacos |
| 公司 core 框架（SyncplantController/BaseService/R 等） | 自实现等价物（basic.api.R、IService、Service 层） | 保持分层与命名一致 |
| `@ApiInfo/@ApiLog/@ApiOperation` 接口文档注解 | 未引入 Swagger/日志注解 | 需要时接入 springdoc/knife4j，注解规则不变 |
| 分页 `Condition.getPage(Query)` | 暂不分页，返回全量列表 | 数据量大时引入 MyBatis-Plus 分页插件，接口保持 `/list` |
| `BaseEntity`（创建人/修改人/删除标记） | 暂未引入审计字段 | 需要时抽 `basic` 公共基类，实体继承之 |

## 九、改造对照（本次重构清单）

- ✅ 后端包结构：`com.portfolio.business` + `basic` 基础包 + `project` 业务模块
- ✅ 数据访问层：JPA Repository → **MyBatis-Plus Mapper**（`ProjectMapper extends BaseMapper<Project>`）
- ✅ 业务分层：Controller 直连 Repository → **Controller → IProjectService → ProjectServiceImpl → Mapper**
- ✅ 统一返回：裸 JSON → **R&lt;T&gt;**（code/data/msg）
- ✅ 接口风格：GET/DELETE 混合 → **全 POST**（`/list`、`/saveOrUpdate`、`/remove`）
- ✅ 常量与提示：魔法字符串 → **TableConstants / TipConstants**
- ✅ 实体规范：Lombok `@Data`、`@TableName/@TableId/@TableField`、字段 Javadoc、中文校验消息
- ✅ 全局异常处理：500 裸错误 → **GlobalExceptionHandler 统一返回 R**
