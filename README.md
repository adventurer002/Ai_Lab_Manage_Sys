<div align="center">

# Ed Lab Agent · 智能实验室预约系统

基于 **FastAPI + Vue 3 + LangGraph** 的前后端分离实验室预约管理系统

支持用自然语言与 AI 助手对话，一句话完成实验室 / 设备预约
</div>

## 项目简介

面向高校 / 科研实验室场景的一站式预约管理平台，提供实验室与设备管理、预约审核、数据看板等完整业务闭环，并内置基于 LangGraph 的 AI 智能助手：

- 用户可在对话中直接描述预约需求（如「帮我预约明天上午 10 点到下午 2 点的化学实验室」），Agent 自动查询数据库核对信息、复述确认，并在用户确认后提交预约；
- 规则类问题（预约规则、开放时间、设备使用、安全规范）通过向量知识库语义检索回答，不凭空编造。

## 界面预览

| 登录页 | 系统首页 |
| :---: | :---: |
| ![登录页](docs/images/login.png) | ![系统首页](docs/images/dashboard.png) |
| 账号密码登录 + 滑块验证 | 数据统计卡片 / 实验室概览 / 设备数量分布 |

| 实验室列表 | 设备管理 |
| :---: | :---: |
| ![实验室列表](docs/images/lab-list.png) | ![设备管理](docs/images/equipment-manage.png) |
| 卡片式展示，支持筛选与一键预约 | 设备增删改查、规格与状态维护 |

| 预约审核 | 个人中心 |
| :---: | :---: |
| ![预约审核](docs/images/reservation-audit.png) | ![个人中心](docs/images/profile.png) |
| 管理员按状态筛选，通过 / 拒绝 | 资料编辑与头像上传 |

<p align="center">
  <img src="docs/images/ai-chat.png" width="380" alt="AI 智能助手" />
  <br />
  <sub>AI 智能助手：自然语言对话完成预约（复述确认 → 提交 → 待审核）</sub>
</p>

## 功能特性

### 业务功能

- **登录注册**：账号密码登录 + 滑块验证 + 记住密码；JWT 认证，Token 过期前端自动登出
- **系统首页**：实验室总数、设备总数、角色与用户信息统计卡片；实验室概览表格；实验室设备数量分布图表
- **实验室列表**：卡片式展示（封面图、位置、容量、开放时段、简介、开放状态），支持关键字 / 状态筛选；开放中的实验室可一键预约
- **实验室预约**：支持「预约整间实验室」或「指定设备预约」；提交时校验实验室开放时间、设备状态与时段冲突；预约指定设备的入口同时内嵌在实验室设备页
- **实验室管理**：管理员维护实验室信息（名称、位置、容量、开放时段、封面图上传、开放 / 关闭状态）
- **设备管理**：管理员维护设备（归属实验室、型号规格、数量、正常 / 维修中状态），支持关键字与所属实验室筛选
- **用户管理**：管理员维护用户，支持学生 / 教师 / 管理员三种角色与启用 / 禁用状态
- **预约审核**：管理员按状态筛选预约记录，执行通过 / 拒绝
- **我的预约**：查看个人预约记录；待审核 / 已通过的预约可取消；已取消 / 已过期的记录可删除
- **自动过期**：后台任务每 60 秒扫描一次，超时的「待审核」自动变更为「已取消」，超时的「已通过」自动变更为「已过期」
- **时段冲突检测**：同一实验室或同一设备在时间重叠时拦截重复预约
- **个人中心**：修改姓名、邮箱、手机号，上传头像（顶栏、AI 聊天窗口、锁屏头像同步更新）
- **文件上传**：统一上传接口，扩展名白名单 + 单文件 100MB 限制

### AI 智能助手

- **自然语言预约**：对话中直接描述需求，Agent 解析「今天 / 明天」等相对日期，自动查询实验室与设备信息，复述预约内容并获得用户确认后提交
- **LangGraph Agent 工作流**：基于 StateGraph 实现 LLM ⇄ 工具调用闭环，最多 10 轮交互，防止空转
- **SSE 流式输出**：逐字推送回答，同时展示工具调用过程（中文过程文案）
- **向量知识库**：ChromaDB 持久化 + bge-small-zh-v1.5 中文嵌入模型，覆盖「预约规则 / 开放时间 / 设备使用 / 安全规范」四类文档，支持语义检索
- **安全约束**：不编造数据库中不存在的实验室与设备；预约前必须复述信息并等待用户确认；规则类问题优先检索知识库

## 技术栈

### 后端

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn（全异步） |
| ORM | SQLAlchemy 2.0 AsyncSession + aiomysql |
| 数据库 | MySQL |
| 认证 | PyJWT + bcrypt |
| AI Agent | LangGraph + LangChain（langchain-openai） |
| 大模型 | OpenAI 兼容 API（AsyncOpenAI） |
| 向量检索 | ChromaDB + sentence-transformers（bge-small-zh-v1.5） |
| 配置管理 | pydantic-settings |
| 包管理 | uv（Python 3.13） |

### 前端

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3.5（Composition API + `<script setup>` + TypeScript） |
| 构建工具 | Vite 7 |
| UI 组件 | Element Plus 2 + @element-plus/icons-vue |
| 状态管理 | Pinia 3（持久化插件） |
| 路由 | Vue Router 4（动态路由 + 角色菜单权限） |
| 样式 | Tailwind CSS 4 + SCSS |
| 图表 | ECharts 6 |
| HTTP | Axios（统一封装：Token 注入、错误提示、401 登出） |
| Markdown 渲染 | marked + DOMPurify（防 XSS） |
| 国际化 | vue-i18n |
| 包管理 | pnpm（Node >= 20.19） |
| 布局基础 | Art Design Pro 模板 |

## 系统架构

```
浏览器（Vue 3 SPA + Element Plus）
   │  Axios 请求 / SSE 流式响应
   ▼
Vite 开发代理（生产环境为 Nginx）
   │  /api → /v1、/uploads → 后端静态目录
   ▼
FastAPI 应用
   ├── 路由层 app/v1/ ：参数接收、鉴权、转发（薄）
   ├── 业务层 app/server/ ：预约校验、Agent 编排、向量检索（厚）
   └── 数据层：SQLAlchemy AsyncSession
          ├── MySQL：用户 / 实验室 / 设备 / 预约
          ├── ChromaDB：知识库向量索引
          └── 文件系统：上传的图片与附件（uploads/）
```

启动阶段（lifespan）自动完成：建表 → 向量模型预热（约 30 秒）→ 启动预约过期后台任务。

## AI Agent 工作流

```
用户提问
   │
   ▼
LangGraph Agent（System Prompt + 历史消息）
   │
   ▼
LLM 判断是否需要调用工具
   ├── 不需要 ──► 直接生成回答（流式输出）
   │
   └── 需要 ──► ToolNode 执行工具 ──► 结果回喂 LLM ──► 继续判断
                （LLM ⇄ 工具回路最多 10 轮）
   │
   ▼
SSE 逐字推送前端（工具调用过程 + 回答内容）
```

内置 5 个工具：

| 工具 | 说明 |
|------|------|
| `search_lab_docs` | 检索知识库（预约规则 / 开放时间 / 设备使用 / 安全规范） |
| `list_open_labs` | 按关键词查询开放中的实验室，获取 `lab_id` |
| `list_lab_equipments` | 查询指定实验室的设备列表，获取 `equipment_id` |
| `create_lab_reservation` | 创建预约（需用户确认后调用） |
| `get_today` | 获取当前日期，用于换算「今天 / 明天 / 后天」 |

系统提示词关键约束：

- 预约前必须向用户复述预约信息并获得确认，才可调用 `create_lab_reservation`
- 缺少 `lab_id` / `equipment_id` 时必须先查询获取，不能编造
- 规则 / 开放时间类问题优先调用 `search_lab_docs`，不凭空回答
- 预约提交后状态为「待审核」，需管理员确认后生效

## 项目结构

```
lab_agent/
├── backend/                          # 后端服务（FastAPI）
│   ├── app/
│   │   ├── main.py                   # 应用入口：lifespan、CORS、全局异常、静态文件挂载
│   │   ├── config.py                 # 配置管理：.env 加载、上传大小 / 扩展名白名单
│   │   ├── database.py               # 异步引擎、AsyncSession、Base、建表
│   │   ├── common/                   # 统一响应结构（Response / QueryResponse）与异常处理
│   │   ├── model/                    # ORM 模型：user / lab / equipment / reservation
│   │   ├── schemas/                  # Pydantic 请求 / 响应模型
│   │   ├── v1/                       # 路由层（薄）：auth / user / lab / equipment / reservation / chat / file
│   │   ├── server/                   # 业务层（厚）
│   │   │   ├── auth.py               # 登录注册、JWT 签发
│   │   │   ├── user_service.py       # 用户管理、密码修改
│   │   │   ├── lab_service.py        # 实验室管理
│   │   │   ├── equipment_service.py  # 设备管理
│   │   │   ├── reservation_service.py # 预约创建 / 冲突检测 / 审核 / 取消 / 删除 / 自动过期
│   │   │   ├── agent_service.py      # LangGraph Agent 对话与 SSE 流式输出
│   │   │   ├── agent_tools.py        # Agent 工具集（5 个工具）
│   │   │   └── kb_service.py         # 向量知识库（懒加载 + 启动预热）
│   │   ├── dependencies/auth.py      # JWT 解析、当前用户、管理员校验依赖
│   │   └── utils/                    # JWT / 密码哈希工具
│   ├── data/
│   │   ├── kb/                       # 知识库 Markdown 源文档（预约规则 / 开放时间 / 设备使用 / 安全规范）
│   │   └── chroma/                   # ChromaDB 向量索引持久化目录
│   └── uploads/                      # 上传文件存放目录（头像、实验室封面图等）
│
├── frontend/                         # 前端应用（Vue 3，基于 Art Design Pro 模板）
│   ├── src/
│   │   ├── api/                      # 接口封装：auth / lab / equipment / reservation / user / ai / file
│   │   ├── views/lab/                # 业务页面
│   │   │   ├── home/                 # 系统首页：统计卡片 + 实验室概览 + 设备分布图
│   │   │   ├── lab-list/             # 实验室列表 + 预约弹窗（ReserveDialog）
│   │   │   ├── lab-equipment/        # 实验室设备页（行内设备预约入口）
│   │   │   ├── lab-manage/           # 实验室管理（管理员）
│   │   │   ├── equipment/            # 设备管理（管理员）
│   │   │   ├── user-manage/          # 用户管理（管理员）
│   │   │   ├── my-reservation/       # 我的预约（取消 / 删除）
│   │   │   ├── audit-reservation/    # 预约审核（管理员）
│   │   │   ├── ai-chat/              # AI 智能助手
│   │   │   ├── profile/              # 个人中心（资料 + 头像上传）
│   │   │   └── password/             # 修改密码
│   │   ├── components/core/          # 布局与通用组件（侧边栏、顶栏、AI 聊天抽屉、锁屏等）
│   │   ├── router/modules/lab.ts     # 业务路由与菜单配置（含角色权限 roles）
│   │   ├── store/modules/            # Pinia：user / menu / setting / table / worktab
│   │   ├── hooks/                    # 组合式函数（useTable 分页表格等）
│   │   ├── utils/http/               # Axios 封装：Token 注入、统一错误、401 登出
│   │   └── config/                   # 全局配置（快速入口、主题等）
│   ├── vite.config.ts                # 开发代理：/api → 后端 /v1，/uploads → 后端静态资源
│   └── .env.development              # 开发环境变量（API 前缀、代理目标）
│
└── docs/images/                      # README 截图资源
```

结构分析：

- **后端「路由层薄、业务层厚」**：`v1/` 只负责参数接收、鉴权与转发；全部业务逻辑集中在 `server/`，因此 Agent 工具能直接复用预约校验逻辑，Web 接口与 AI 对话共享同一套业务规则。
- **统一响应与异常**：除 SSE 流式接口外，所有接口返回 `{ code, message, data }` 结构，业务异常 `BusinessException` 由全局处理器统一转换为 JSON，前端只需要一套错误处理。
- **前端按页面组织**：业务页面集中在 `views/lab/`，布局与通用能力来自 `components/core/`（Art Design Pro 骨架）；路由 `meta.roles` 驱动侧边栏菜单的角色可见性。
- **前后端接口约定**：分页请求使用 `page` / `page_size`，响应使用 `items` / `total`；角色取值统一为中文「学生 / 教师 / 管理员」。

## 数据库设计

```
user ──< reservations >── labs
               │
               └── equipments（可选，为空表示预约整间实验室）
```

| 表 | 说明 |
|----|------|
| `user` | 用户（用户名、密码哈希、姓名、角色、联系方式、头像、状态） |
| `labs` | 实验室（名称、位置、容量、开放时段、封面图、开放 / 关闭状态） |
| `equipments` | 设备（所属实验室、名称、规格、数量、正常 / 维修中状态） |
| `reservations` | 预约（用户、实验室、设备、日期、起止时间、备注、状态） |

- **预约状态**：`0` 待审核 / `1` 已通过 / `2` 已拒绝 / `3` 已取消 / `4` 已过期
- **角色取值**：`学生` / `教师` / `管理员`（统一使用中文，前后端一致）

## 快速开始

### 环境要求

- Python **3.13**（建议，更高版本可能导致科学计算类依赖异常）
- Node.js **>= 20.19.0**，pnpm **>= 8.8.0**
- MySQL **5.7+ / 8.0+**

### 1. 启动后端

```bash
cd backend

# 安装依赖（uv 自动创建虚拟环境）
uv sync

# 复制环境变量模板并填写配置（数据库、JWT、大模型）
cp .env.example .env

# 创建数据库（表结构会在服务启动时自动创建）
mysql -uroot -p -e "CREATE DATABASE lab_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 启动服务（必须在 backend/ 目录下运行）
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 地址：`http://127.0.0.1:8000`
- 接口文档（Swagger）：`http://127.0.0.1:8000/docs`

首次启动时会在 lifespan 阶段完成向量模型预热（约 20 ~ 30 秒，首次需下载 bge-small-zh-v1.5 模型）；代码中已配置 Hugging Face 国内镜像，无代理环境可直接使用。

### 2. 启动前端

```bash
cd frontend

# 安装依赖（必须使用 pnpm）
pnpm install

# 启动开发服务器
pnpm dev
```

- 前端地址：`http://localhost:5173`

开发时需要同时运行前后端：前端通过 Vite 代理将 `/api` 转发到后端 `/v1`（解决跨域），`/uploads` 转发到后端静态资源目录。生产部署时需在 Nginx 中配置同样的反向代理。

## 环境变量说明

### 后端 `backend/.env`

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | MySQL 异步连接串 | `mysql+aiomysql://root:password@127.0.0.1:3306/lab_agent` |
| `JWT_SECRET_KEY` | JWT 签名密钥 | 随机长字符串 |
| `JWT_EXPIRE_HOURS` | Token 有效时长（小时） | `24` |
| `JWT_ALGORITHM` | JWT 签名算法 | `HS256` |
| `LLM_API_KEY` | 大模型 API Key | `sk-xxxx` |
| `LLM_BASE_URL` | OpenAI 兼容接口地址 | `https://api.openai.com/v1` |
| `LLM_MODEL` | 模型名称 | `gpt-4o-mini` |

### 前端 `frontend/.env.development`

| 变量 | 说明 | 示例 |
|------|------|------|
| `VITE_BASE_URL` | 应用部署基础路径 | `/` |
| `VITE_API_URL` | API 请求前缀（开发环境用 `/` 走代理） | `/` |
| `VITE_API_PROXY_URL` | 开发代理目标（后端地址） | `http://127.0.0.1:8000` |
| `VITE_DROP_CONSOLE` | 构建时是否移除 console | `false` |

## 安全设计

- 密码使用 bcrypt 哈希存储，不落明文
- JWT 认证 + 过期自动失效，401 前端自动登出（带防抖）
- 管理接口通过 `judge_manager` 依赖统一校验管理员角色
- 删除预约双重限制：仅「已取消 / 已过期」状态可删，且仅本人或管理员可操作
- 前端 Markdown 渲染经 DOMPurify 过滤，防 XSS
- 文件上传校验扩展名白名单 + 大小限制

## 开发约定

- 后端「路由层薄、业务层厚」：路由只做转发，业务逻辑集中在 `server/`
- 数据库访问统一使用 SQLAlchemy 2.0 异步 `select()` 风格，禁用旧版 `query()`
- 角色取值统一使用中文：`学生` / `教师` / `管理员`
- 前端接口字段约定：分页请求 `page` / `page_size`，响应 `items` / `total`
- 阻塞操作（向量检索、文件写盘）通过 `asyncio.to_thread()` 包装，避免阻塞事件循环