# Zili Nutrition — 外贸独立站（Sample 概念站）

英文 B2B 膳食补充剂批发 / OEM / ODM 代工企业展示站，面向欧洲、美国、东南亚市场。

## 最终交付物

- **`website.html`** — 单文件自包含站点（所有 CSS/JS/图标内联，无网络依赖，直接用浏览器打开即可），含五个区块：
  Home（Hero + 三市场覆盖 + 服务线）/ About / Products（Capsules · Tablets · Powders · Gummies · Softgels）/ OEM-ODM（编号流程链 + 范围边界）/ Contact（询盘表单，带校验与隐私声明）。

## 真实信息已填入（v2，2026-09-05）

公司名与联系方式已替换为真实信息，其余业务事实仍为占位（见下方清单）：

- 公司名：**Zili Nutrition**（中文主体：郑州植力科技）
- 邮箱：**zvitahealth@outlook.com**
- WhatsApp：**+86 177 0069 9079**
- 地址：**Zhengzhou, Henan, China**
- 官网：**www.zvitahealth.com**

## 目录结构

- `src/` — 可维护源码（index.html / styles/main.css / scripts/main.js）
- `dist/` — 与 src 同步的构建目录
- `.design-suite/` — 设计契约与验证证据链（route/contract/icon 契约、浏览器六档证据、布局几何探针、单文件导出证据、执行收据）
- `website.html` — 导出后的最终单文件交付物
- `index.html` — **线上部署的正式单文件**（GitHub Pages 分支构建，main 根目录；由模板 + 内容构建生成）
- `templates/index.html` — 可编辑文本已替换为 `{{...}}` 占位符的模板（视觉/结构不变）
- `content/*.json` — 全部可编辑内容数据（联系方式、产品、区块文案等）
- `tools/extract.py` — 一次性抽取脚本（模板 + 初始 content 的生成器）
- `tools/build.py` — 构建脚本：占位符 → 渲染 index.html，支持 `--check` 字节级校验
- `admin/` — Decap CMS 可视化后台（index.html + config.yml + 本地 vendor decap-cms.js）
- `.github/workflows/build.yml` — 内容变更时自动重建 index.html 并提交回 main

## 内容管理（两种方式）

### 方式一：可视化后台（推荐，配置完成后）

1. 在 Netlify 免费注册并授权本 GitHub 仓库（步骤见下节「后台登录配置」）。
2. 访问 `https://zvitahealth.com/admin/`，用 Netlify Identity 登录，直接在后台编辑全部可编辑字段。
3. 保存后自动提交 `content/*.json` 到 main，GitHub Actions 自动重建 index.html，Pages 自动发布。

### 方式二：直接改内容文件（无需后台）

1. 编辑 `content/*.json` 中的文本值（保持 JSON 格式合法）。
2. 本地验证：`python3 tools/build.py --check`（应与当前 index.html 完全一致）；
   改动后执行 `python3 tools/build.py` 重新生成 index.html。
3. git add/commit/push 到 main，Actions 与 Pages 自动完成后续发布。

### 后台登录配置（最后一步，需用户操作）

`admin/config.yml` 中已预留 Netlify 认证参数（`base_url` / `auth_endpoint`，当前为注释状态）。
完成以下步骤后正式启用登录：

1. 注册免费 Netlify 账号：https://app.netlify.com/signup
2. 将 GitHub 仓库 `zilinutrition-arch/zili-nutrition-site` 接入 Netlify（New site from Git；由于 Pages 已承担托管，也可只做 OAuth 授权，不启用 Netlify 部署）。
3. 在 Netlify Site settings 中打开 Identity 服务、启用 Git Gateway。
4. 将 `admin/config.yml` 中 `base_url: https://api.netlify.com` 与 `auth_endpoint: auth` 两行的注释取消并提交。
5. 访问 `https://zvitahealth.com/admin/` 验证登录、编辑与保存。

## 上线前必改（仍为 Sample 占位事实）

以下内容仍是占位示例，正式上线前必须替换为真实内容：

- 认证与合规声明（FDA / GMP / HACCP / 欧盟 Novel Foods 等具体证书编号）
- 产能、MOQ、交期、价格等数值
- 产品目录与配方细节、公司历史/团队介绍文案、隐私条款

## 质量验证记录（已验证通过）

- 浏览器六档证据（320/390/768/1440/1920/2560）：console / resources / keyboard / responsive / states 全 passed，无横向溢出、无控制台错误
- 布局几何探针：6 viewports、3 probe invariants PASS（contact-form、nav-brand、product-grid 移动端不破版）
- 单文件 static-export：结构 / 离线 / 渲染 / 控制台 / 响应式 全 passed，沙箱 API 零使用
- 设计套件执行收据：`export-approved`（receipt_id 见 `.design-suite/execution-receipt.json`）

生成时间：2026-09-05（v2 真实公司信息版）