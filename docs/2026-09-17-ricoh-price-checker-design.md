# 理光相机比价网站 — 设计文档

- 日期：2026-09-17
- 状态：待评审

## 1. 目标

做一个网页，展示理光 **GR IIIx HDF** 和 **GR IV HDF** 在澳洲多家零售商的当前价格，按机型分组并高亮每款最低价。最终部署到公网，可分享给他人访问。

## 2. 技术栈

| 层 | 选择 | 说明 |
|---|---|---|
| 后端 | Python 3 + Flask | 本地小服务器；部署到 Render 后成为公网服务 |
| 抓取 | requests + BeautifulSoup4 | Shopify 店用公开 JSON 接口（最稳）；非 Shopify 店解析 HTML |
| 前端 | 单页 HTML + 原生 JS | 表格 + 「刷新」按钮，无框架，简单可教 |
| 部署 | GitHub（托管代码）→ Render（免费云托管）| 两阶段：本地开发 → 公网部署 |

## 3. 架构与组件

```
浏览器（别人的电脑，打开公开网址）
   │  点「刷新」
   ▼
Flask 服务器（部署在 Render 上）
   │  遍历目标清单，逐个抓取
   ├─ digiDirect（Shopify JSON）
   ├─ Camera Electronic（Shopify JSON）
   ├─ Pentax 澳洲官方（解析 HTML）
   └─ CameraPro（解析 HTML）
   ▼
返回 JSON 价格列表 → 网页渲染表格，按机型分组，高亮最低价
```

组件与职责：

| 文件 | 职责 |
|---|---|
| `app.py` | Flask 入口；两个路由：`GET /`（页面）、`GET /api/prices`（返回价格 JSON）|
| `scrapers.py` | 每家店一个抓取函数，统一返回 `{店名, 价格, 现货, 链接}` |
| `targets.py` | 「机型 × 零售商 × 链接」清单，抓取遍历的依据 |
| `templates/index.html` | 前端页面：表格 + 刷新按钮 + 最低价高亮 |
| `requirements.txt` | 依赖：flask、requests、beautifulsoup4 |

## 4. 数据流

点「刷新」→ 请求 `/api/prices` → Flask 按 `targets.py` 清单逐个抓取 → 每家返回 `{店名, 价格, 现货, 链接}` → 汇总为 JSON → 前端按机型分组渲染表格，绿色高亮每款最低价，抓失败的店显示「抓取失败」而非崩溃。

## 5. 目标清单

### GR IV HDF（已实测验证 Shopify 接口可用）

| 零售商 | 类型 | 链接 | 参考价 |
|---|---|---|---|
| digiDirect | Shopify | https://www.digidirect.com.au/products/ricoh-gr-iv-hdf | $2,389 |
| Camera Electronic | Shopify | https://www.cameraelectronic.com.au/products/ricoh-gr-iv-hdf-edition | $2,379 |
| Pentax 澳洲官方 | 非 Shopify | https://pentax.com.au/products/1573/ricoh-gr-iv-hdf-edition-camera | $2,395 |
| CameraPro | 非 Shopify | https://www.camerapro.com.au/15312-ricoh-gr-iv-hdf-edition-compact-camera.html | $2,395 |

### GR IIIx HDF（链接在实施第 1 步收集）

同上四家店，具体商品链接在实施阶段抓取搜索页确定。

> 首版只做 4 家店跑通教学，后续可任意增加零售商（Double Bay Camera Shop、Diamonds、ShopValet 等）。

## 6. 错误处理

- 每个抓取函数用 `try/except` 包裹，一家失败不影响其他家。
- 请求带浏览器 User-Agent 头、设超时、请求间加小延迟（礼貌抓取）。
- Shopify 接口有两种返回格式（带/不带 `"product"` 外层包装），代码需兼容——实测发现的坑。
- 抓取失败在页面上显示「抓取失败」占位，不整体崩溃。

## 7. 部署方案（两阶段）

1. **阶段 1 本地开发**：在本地跑 `python app.py`，浏览器打开 `localhost:5000` 开发调试。
2. **阶段 2 公网部署**：代码推到 GitHub → 在 Render 建免费 Web Service 指向该仓库 → 得到公开网址 `https://<应用名>.onrender.com`，分享给他人。

注意：Render 免费档有「休眠」机制，长时间无人访问后首次打开需约 30 秒冷启动。抓取发生在服务器端（Render 的海外节点），需在部署后实测澳洲零售商是否可访问。

## 8. 实施步骤（教学节奏）

1. 骨架跑通：1 家 Shopify 店 + 1 个机型（Flask + 网页 + 一个抓取器）
2. 扩清单：2 个机型 × 4 家店，学会怎么加目标
3. 前端增强：最低价高亮 + 按价格排序 + 现货标记
4. 非 Shopify 店：Pentax 官方 / CameraPro 的 HTML 解析
5. 部署：git 推送 GitHub → Render 上线 → 拿到公开网址

## 9. 成功标准

- 打开公开网址，点「刷新」，看到 GR IIIx HDF 和 GR IV HDF 在 4 家店的价格。
- 每款最低价被高亮；抓失败的店有提示。
- 别人用手机/电脑都能访问同一个网址看到价格。

## 10. 用户需准备

- GitHub 账号：已有 ✅
- Render 账号：免费，需注册（部署阶段再注册即可）
