# 前端 UI 迁移至 Art Design Pro - Implementation Plan

## Task 1: 用模板骨架替换 frontend 并调整环境配置
- **Status**: `completed`
- **Completion Evidence**:
  - 模板已复制到 frontend/，pnpm install 成功（allowBuilds 配置解决 pnpm11 构建脚本忽略问题）
  - vite 启动成功：`VITE v7.1.7 ready in 2795 ms`，http://localhost:5173/ 返回 Art Design Pro 页面 HTML
  - 代理已配置：`/api` 重写为 `/v1`，`/uploads` 指向后端，SSE 关闭缓冲
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 将 `exampleui/art-design-pro` 的全部内容复制到 `frontend/`（覆盖现有文件）。
  - 修改 `.env`/`.env.development`：`VITE_API_PROXY_URL=http://127.0.0.1:8000`，`VITE_PORT=5173`，保留 `VITE_ACCESS_MODE=frontend`。
  - 修改 `vite.config.ts` 代理：`/api` → `http://127.0.0.1:8000` 并 `rewrite /api → /v1`；新增 `/uploads` 代理到后端；SSE 流式响应关闭缓冲。
  - 运行 `pnpm install` 确认依赖可安装。
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `rule` TR-1.1: `pnpm install` 退出码 0；`pnpm dev` 可启动并访问到登录页
  - `rule` TR-1.2: 代理配置中 `/api` 重写为 `/v1`，`/uploads` 指向后端

## Task 2: 适配 HTTP 层（响应字段、鉴权头）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 修改 `src/utils/http/index.ts` 响应拦截器：兼容 `msg` 与 `message` 字段（取 `data.message ?? data.msg`）。
  - 修改请求拦截器：`Authorization` 头改为 `Bearer ${accessToken}`。
  - 确认 `BaseResponse` 类型 `src/types/common/response.ts` 的字段命名兼容。
- **Acceptance Criteria Addressed**: AC-2, AC-4
- **Test Requirements**:
  - `rule` TR-2.1: 请求头为 `Bearer <token>` 格式
  - `rule` TR-2.2: 后端 `{code, message, data}` 响应可被正确解析，错误时弹出 message

## Task 3: 适配认证 API 与用户信息映射
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 修改 `src/api/auth.ts`：`fetchLogin` 参数改为 `{username, password}`，url `/api/auth/login`；`fetchGetUserInfo` url `/api/user/info`。
  - 修改 `src/types/api/api.d.ts`：`LoginParams` 用 `username`；`UserInfo` 增加 `name`、`phone`、`role`、`status` 字段，`roles` 由 `role` 派生。
  - 在 `fetchGetUserInfo` 或 user store 中做映射：`id→userId`、`username→userName`、`role→roles:[role]`。
  - 修改 `src/store/modules/user.ts`：`logOut` 与 `setToken` 适配单 token（无 refreshToken）；`setUserInfo` 正确处理 lab_agent 字段。
- **Acceptance Criteria Addressed**: AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-3.1: 登录请求体为 `{username, password}`，响应 token 存入 store
  - `rule` TR-3.2: 用户信息中 `roles` 数组包含后端返回的 `role` 中文值

## Task 4: 创建实验室业务路由模块并注册
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 新建 `src/router/modules/lab.ts`，定义实验室系统全部路由：首页、实验室列表、实验室管理、设备管理、用户管理、我的预约、预约审核、AI 助手、个人中心、修改密码、实验室设备。
  - 为每个路由设置 `meta.roles`（管理员可见管理类；学生可见预约/列表类；教师可见列表+预约）。
  - 修改 `src/router/modules/index.ts`：移除 demo 模块（dashboard/template/widgets/examples/article/result/safeguard/help），保留 `exception`，加入 `labRoutes`。
  - 设置 `HOME_PAGE_PATH` 为首页路径。
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `rule` TR-4.1: 路由模块注册成功，菜单按 `roles` 过滤
  - `rule` TR-4.2: 学生看不到管理菜单，管理员可看到全部

## Task 5: 登录页与注册页适配
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**:
  - 修改 `src/views/auth/login/index.vue`：字段改为 `username`（去掉账号选择下拉的 demo 逻辑，保留拖拽验证可选）；登录成功调用 `userStore.setToken` + `setUserInfo` + `setLoginStatus(true)`，跳转首页。
  - 修改 `src/views/auth/register/index.vue`：对接 `/api/auth/register`，字段 username/password/name。
  - 适配 `src/locales/langs/zh.json` 与 `en.json` 中 login/register 文案（可选，确保不报错即可）。
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `rule` TR-5.1: 登录成功进入主页，注册成功跳转登录页
  - `rule` TR-5.2: 错误密码提示后端 message

## Task 6: 首页 + 实验室列表页
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 新建 `src/views/lab/home/index.vue`：系统首页，展示欢迎信息与快捷入口。
  - 新建 `src/views/lab/lab-list/index.vue`：对接 `GET /api/lab/list`，使用 `art-table` 展示开放实验室，可进入查看设备/预约。
  - 新建 `src/api/lab.ts`（TS 版）封装实验室接口。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-6.1: 实验室列表数据加载并展示
  - `rule` TR-6.2: 分页/关键字搜索正常

## Task 7: 实验室管理页（管理员 CRUD）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 新建 `src/views/lab/lab-manage/index.vue`：实验室增删改查，使用 `art-search-bar` + `art-table` + 表单弹窗。
  - 包含封面图上传（`/api/file/upload`）、开放时段选择、状态开关。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-7.1: 新增/编辑/删除实验室成功并刷新列表
  - `rule` TR-7.2: 表单校验生效

## Task 8: 设备管理页
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 新建 `src/views/lab/equipment/index.vue`：设备 CRUD，关联实验室，`art-table` 展示，状态显示。
  - 新建 `src/api/equipment.ts`。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-8.1: 设备列表/新增/编辑/删除正常
  - `rule` TR-8.2: 设备归属实验室字段正确

## Task 9: 用户管理页
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 新建 `src/views/lab/user-manage/index.vue`：管理员用户 CRUD，角色选择（学生/教师/管理员），状态开关，头像上传。
  - 新建 `src/api/user.ts`。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-9.1: 用户列表/新增/编辑/删除正常
  - `rule` TR-9.2: 不能删除自己、不能删除管理员的后端校验提示正常显示

## Task 10: 我的预约 + 预约审核页
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 新建 `src/views/lab/my-reservation/index.vue`：学生查看自己的预约，可取消待审核预约。
  - 新建 `src/views/lab/audit-reservation/index.vue`：管理员审核预约（通过/拒绝）。
  - 新建 `src/api/reservation.ts`。
  - 复用 `src/components/ReserveDialog.vue`（转 TS）用于实验室列表预约。
- **Acceptance Criteria Addressed**: AC-4, AC-9
- **Test Requirements**:
  - `rule` TR-10.1: 预约列表按角色正确过滤
  - `rule` TR-10.2: 取消/审核操作成功并刷新

## Task 11: AI 智能助手页（SSE 流式）
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 新建 `src/views/lab/ai-chat/index.vue`：基于模板布局实现对话 UI，使用 fetch + ReadableStream 调用 `POST /api/ai/chat/stream`。
  - 解析 SSE 事件（status/tool_start/tool_end/token/error/done），逐字追加回复，展示工具过程。
  - Markdown 渲染用 marked + DOMPurify。
  - 新建 `src/api/ai.ts`。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `rule` TR-11.1: 发送消息后流式输出正常
  - `rule` TR-11.2: 工具调用过程文案可见
  - `rule` TR-11.3: 错误事件正确提示

## Task 12: 个人中心 + 修改密码 + 实验室设备页
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 新建 `src/views/lab/profile/index.vue`：展示并编辑个人信息（`PUT /api/user/update`）。
  - 新建 `src/views/lab/password/index.vue`：修改密码（`PUT /api/user/password`）。
  - 新建 `src/views/lab/lab-equipment/index.vue`：查看某实验室设备并发起预约。
- **Acceptance Criteria Addressed**: AC-4, AC-11
- **Test Requirements**:
  - `rule` TR-12.1: 个人信息编辑保存成功
  - `rule` TR-12.2: 密码修改校验（原密码错误/新旧相同）提示正常
  - `rule` TR-12.3: 实验室设备页可提交预约

## Task 13: 清理 demo 资源并修复类型/构建
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 5-12
- **Description**:
  - 清理不再使用的 demo 视图/API/mock 引用（保留异常页等基础设施）。
  - 修复 `pnpm build` 的 TypeScript 报错（类型不匹配、未使用变量、缺失导入等）。
  - 确认 `src/locales` 中业务页面用到的 `$t` key 存在（或改为硬编码中文避免缺 key）。
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-13.1: `pnpm build` 退出码 0，无 TS 错误
  - `rule` TR-13.2: `pnpm dev` 运行无控制台报错

## Task 14: 全功能联调与主题/标签验证
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 启动后端与前端，逐角色（学生/管理员）走通全部页面。
  - 验证暗色/亮色主题切换、工作标签切换/关闭、面包屑。
  - 验证退出登录清理状态并跳转登录页。
- **Acceptance Criteria Addressed**: AC-6, AC-8
- **Test Requirements**:
  - `rule` TR-14.1: 主题切换实时生效
  - `rule` TR-14.2: 工作标签多开/切换/关闭正常
  - `rubric` TR-14.3: 全页面视觉一致性；scale 1-5；anchors 1=风格割裂 3=大体统一 5=高度统一；threshold >=4；evidence 截图
