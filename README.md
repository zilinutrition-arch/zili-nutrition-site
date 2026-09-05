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