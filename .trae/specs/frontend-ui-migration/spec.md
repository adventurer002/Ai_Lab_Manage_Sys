# 前端 UI 迁移至 Art Design Pro - Product Requirements Document

## Overview
- **Summary**: 将现有 `frontend/`（Vue3 + JS + 简易 Element Plus 布局）整体替换为 `exampleui/art-design-pro` 模板骨架，保留模板全部能力（主题切换、多布局、工作标签、暗色模式、i18n、设置面板、art-table/art-form 等），并将实验室预约系统的业务页面以 TypeScript 形式迁入，对接现有后端 API。
- **Purpose**: 提升前端 UI 视觉品质与交互体验，获得企业级后台管理系统的观感。
- **Target Users**: 实验室管理员、教师、学生。

## Goals
- 前端整体视觉与交互达到 Art Design Pro 模板的水准。
- 所有现有业务功能（登录/注册/实验室/设备/用户/预约/审核/AI 对话/个人中心/改密）在新框架下完整可用。
- 保留模板的主题切换、暗色模式、工作标签、面包屑、设置面板等全部能力。
- 业务页面使用 TypeScript 编写。

## Non-Goals
- 不修改后端接口与数据结构。
- 不引入后端菜单接口（使用前端模式 `VITE_ACCESS_MODE=frontend` 控制菜单权限）。
- 不重构后端业务逻辑。
- 不删除模板的基础设施能力（仅替换 demo 业务路由为实验室业务路由）。

## Background & Context
- 现有 `frontend/` 为 Vue3 + JS + Element Plus，布局简单，UI 较为朴素。
- `exampleui/art-design-pro` 为成熟的 Vue3 + TS + Element Plus + Tailwind 模板，具备完整的布局/主题/权限/组件体系。
- 后端 API 统一前缀 `/v1`，响应格式 `{code, message, data}`，JWT 头需 `Bearer {token}`。
- 后端角色为中文：`学生` / `教师` / `管理员`。

## Functional Requirements
- **FR-1**: 前端以 Art Design Pro 模板为骨架启动，保留其布局、主题、设置、工作标签等能力。
- **FR-2**: 登录页对接 `/v1/auth/login`（username/password），成功后保存 token 与用户信息并进入主页。
- **FR-3**: 注册页对接 `/v1/auth/register`。
- **FR-4**: 用户信息接口 `/v1/user/info` 返回数据适配模板 UserInfo 结构（id→userId、role→roles 数组）。
- **FR-5**: 菜单按角色（学生/教师/管理员）前端过滤展示。
- **FR-6**: 实验室列表、实验室管理（增删改查）页面可用。
- **FR-7**: 设备列表管理页面可用。
- **FR-8**: 用户管理页面（管理员）可用。
- **FR-9**: 我的预约（学生）、预约审核（管理员）页面可用。
- **FR-10**: AI 智能助手页面以 SSE 流式方式工作，支持工具过程展示。
- **FR-11**: 个人信息、修改密码页面可用。
- **FR-12**: 实验室列表页可进入设备查看与预约（LabEquipment + ReserveDialog）。
- **FR-13**: 文件上传接口 `/v1/file/upload` 可用（头像/封面图）。

## Non-Functional Requirements
- **NFR-1**: `pnpm dev` 可正常启动，无编译错误。
- **NFR-2**: 所有业务页面可正常访问并与后端通信。
- **NFR-3**: 暗色/亮色主题切换正常。
- **NFR-4**: 工作标签（多页签）功能正常。
- **NFR-5**: 构建 `pnpm build` 无 TypeScript 报错。

## Constraints
- **Technical**: 必须使用 TypeScript；保留模板完整能力；使用模板的 `art-*` 组件体系与 Pinia。
- **Business**: 后端接口不变；角色取值为中文。
- **Dependencies**: 后端服务运行于 `127.0.0.1:8000`；前端代理需将 `/api` 重写为 `/v1`。

## Assumptions
- 模板的 `pnpm install` 在当前环境可成功。
- 后端响应 `message` 字段（非 `msg`）需在 HTTP 层兼容。
- 后端无菜单接口，使用前端模式控制菜单。

## Acceptance Criteria

### AC-1: 模板骨架启动
- **Type**: `rule`
- **Given**: 已用模板替换 `frontend/` 并安装依赖
- **When**: 执行 `pnpm dev`
- **Then**: 服务正常启动，浏览器访问可看到 Art Design Pro 登录页
- **Pass Condition**: 启动无报错，登录页渲染正常
- **Evidence**: 终端输出 + 浏览器截图

### AC-2: 登录与鉴权闭环
- **Type**: `rule`
- **Given**: 后端在线
- **When**: 使用合法账号登录
- **Then**: 成功进入主页，token 持久化，刷新页面保持登录态
- **Pass Condition**: 登录成功跳转主页，刷新不丢失登录态
- **Evidence**: 浏览器操作录屏/截图

### AC-3: 角色菜单过滤
- **Type**: `rule`
- **Given**: 分别以学生、管理员账号登录
- **When**: 查看侧边栏菜单
- **Then**: 学生看到「实验室列表/我的预约/AI助手」等，管理员额外看到「实验室管理/设备管理/用户管理/预约审核」
- **Pass Condition**: 菜单按角色正确显示/隐藏
- **Evidence**: 两种角色截图对比

### AC-4: 业务页面功能完整
- **Type**: `rule`
- **Given**: 已登录对应角色
- **When**: 访问实验室列表、设备管理、用户管理、预约、AI 对话、个人中心、改密页面
- **Then**: 各页面数据加载正常，CRUD/提交操作可成功与后端交互
- **Pass Condition**: 所有页面无功能性错误
- **Evidence**: 逐页面操作验证

### AC-5: AI 对话 SSE 流式
- **Type**: `rule`
- **Given**: 已登录
- **When**: 在 AI 助手发送消息
- **Then**: 以流式方式逐字显示回复，工具调用过程可见
- **Pass Condition**: 流式输出正常，无报错
- **Evidence**: 对话截图

### AC-6: 主题与工作标签
- **Type**: `rule`
- **Given**: 已登录
- **When**: 切换暗色/亮色主题、打开多个页面
- **Then**: 主题切换生效，工作标签可切换/关闭
- **Pass Condition**: 主题与标签功能正常
- **Evidence**: 截图

### AC-7: 构建无错
- **Type**: `rule`
- **Given**: 代码完成
- **When**: 执行 `pnpm build`
- **Then**: 构建成功，无 TS 报错
- **Pass Condition**: build exit code 0
- **Evidence**: 终端输出

### AC-8: UI 视觉品质
- **Type**: `rubric`
- **Dimension**: 整体视觉与 Art Design Pro 模板的一致性与完成度
- **Scale**: 1-5
- **Anchors**: 1 = 基本无模板风格；3 = 部分页面套用但不统一；5 = 全部页面统一呈现模板视觉与交互
- **Pass Threshold**: >= 4
- **Evidence**: 全页面截图审查

## Open Questions
- 无（迁移范围与取舍已与用户确认）
