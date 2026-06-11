# Ragas 图解教程 · 从零理解整个项目

[![📖 在线阅读](https://img.shields.io/badge/%F0%9F%93%96%20%E5%9C%A8%E7%BA%BF%E9%98%85%E8%AF%BB-Read%20Online-4f46e5?style=for-the-badge)](https://verdenmax.github.io/ragas-visual-guide/)
[![📄 下载 PDF](https://img.shields.io/badge/%F0%9F%93%84%20%E4%B8%8B%E8%BD%BD%20PDF-Download-7c3aed?style=for-the-badge)](https://github.com/verdenmax/ragas-visual-guide/releases/latest/download/ragas-visual-guide.pdf)

> 🌐 **在线阅读**：<https://verdenmax.github.io/ragas-visual-guide/>　·　📄 **下载 PDF（全 39 课）**：[ragas-visual-guide.pdf](https://github.com/verdenmax/ragas-visual-guide/releases/latest/download/ragas-visual-guide.pdf)

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Lessons](https://img.shields.io/badge/lessons-39-blue.svg)
![Parts](https://img.shields.io/badge/parts-8-9cf.svg)
![Built with](https://img.shields.io/badge/built%20with-Python%203-3776AB.svg?logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![Language](https://img.shields.io/badge/docs-%E4%B8%AD%E6%96%87-orange.svg)

一套面向**完全新手**的可视化（HTML 图解）教程，带你从零理解
[ragas](https://github.com/vibrantlabsai/ragas)——一个用于**评测大语言模型（LLM）应用**的工具包。
既有**宏观全景**，也深入**源码内部**，每一课都对照 ragas 真实源码核实。

> 📌 **版本锚点**：对照 **ragas 当前 `main` 分支**源码讲解，最后核验于 **2026-06**。
> 源码引用以「**文件 + 符号名**」为主（行号会随上游更新而失效，故不写死）。

## 👤 适用人群

- **适用人群**：
  - 完全没接触过 ragas、想从零入门的新手
  - 想先建立宏观认知、再深入内部源码的学习者
  - 准备阅读 / 调试 / 贡献 ragas 源码的开发者
- **你将获得**：从"会用"到"懂原理"的完整路径，以及一份可随时查阅的源码导航地图

## 🚀 如何阅读

直接用浏览器打开 **`index.html`** 即可（双击或拖入浏览器）。页面是自包含的，
导航链接使用相对路径，支持 `file://` 直接打开，也支持任意静态服务器：

```bash
# 可选：用任意静态服务器本地预览
python -m http.server 8000
# 然后访问 http://localhost:8000/
```

## 📚 教程结构（8 部分 · 39 课）

### 第一部分 · 宏观全景（01–03）
1. **Ragas 是什么** — 解决什么问题 · 核心心智模型
2. **项目全景** — 目录分层与各模块职责
3. **一次评测的生命周期** — 从样本到成绩单的完整数据流

### 第二部分 · 数据与入口（04–08）
4. **数据模型①：SingleTurnSample** — 单轮样本字段
5. **数据模型②：MultiTurnSample 与消息** — 多轮对话与消息类型
6. **两个 Dataset 之辨** — 评测 Dataset 与实验 Dataset
7. **经典入口 `evaluate()`** — 一行调用跑完一批指标
8. **现代入口 `@experiment`** — 实验装饰器与新工作流

### 第三部分 · 指标用法（09–12）
9. **内置指标全景** — 都有哪些指标、怎么挑
10. **RAG 四件套用法** — Faithfulness / Context Precision / Recall / Relevancy
11. **自定义指标（Simple 栈）** — 用最少代码写一个指标
12. **传统 / 非 LLM 指标** — BLEU / ROUGE / 精确匹配等

### 第四部分 · 指标内部（13–18）
13. **Metric 基类体系** — `Metric` 抽象与继承关系
14. **MetricResult 双重身份** — 既是数值又是对象
15. **Faithfulness 内部** — 拆句 → 判定 → 打分
16. **Context Precision / Recall 内部** — 检索质量怎么算
17. **Relevancy / Factual / AspectCritic 内部** — 答案侧指标实现
18. **Agent / 多轮指标内部** — 面向 Agent 与对话的指标

### 第五部分 · 引擎与基础设施（19–24）
19. **Prompt 系统：PydanticPrompt** — 结构化提示词的基石
20. **Prompt 进阶：few-shot 与翻译** — 示例注入与多语言
21. **LLM 抽象** — 统一封装各家大模型
22. **Embedding 抽象** — 统一封装各家向量模型
23. **执行引擎 Executor** — 并发调度与限流
24. **Callbacks · 成本 · 缓存** — 追踪、计费与缓存

### 第六部分 · 测试集生成（25–30）
25. **为什么自动造测试集** — 手工标注的痛点
26. **知识图谱** — 文档关系建模
27. **Transforms** — 抽取与变换流水线
28. **Persona 与 Scenario** — 角色与场景设定
29. **Synthesizers** — 由图谱合成问答
30. **TestsetGenerator 端到端** — 一键生成测试集

### 第七部分 · 实验与工程化（31–37）
31. **实验系统深入** — 实验、运行与记录
32. **Backends 可插拔** — CSV / JSONL / 内存 / Google Drive 等存储后端
33. **指标优化与训练** — 提升指标与裁判模型的对齐
34. **集成①：框架** — LangChain / LlamaIndex / LangGraph 等
35. **集成②：观测** — 与可观测性平台对接
36. **读源码 · 调试 · 测试 · 贡献** — 上手开发与贡献规范
37. **CLI** — 命令行用法

### 第八部分 · 实战与速查（38–39）
38. **端到端实战** — 把数据、指标、实验全拼起来
39. **术语表 · 概念索引** — 全书术语一句话查 + 点链接跳到对应课

## 🎨 每页包含

- **宏观理解** — 每课先用大局观讲清「为什么这样设计」，再进入细节
- 🔬 **源码对应** — 指向真实源码文件与符号（如 `metrics/base.py`、`Faithfulness`）
- 🧩 **生活类比** — 用日常事物帮助理解抽象概念
- ✅ **本课要点** — 每课小结
- 💡 **设计亮点** — 该课最精妙的设计思想
- 🧪 **互动自测** — 「想一想为什么这么设计」的折叠式小测验
- 顶部进度条 + 上一课 / 下一课导航 + 可折叠的「深挖」卡片

## 📁 项目结构

```
ragas-visual-guide/
├── index.html              ← 入口（目录页），从这里开始
├── lessons/                ← 39 课图解页面
│   ├── 01-what-is-ragas.html
│   ├── 02-architecture.html
│   └── …  39-glossary.html
├── src/                    ← 无依赖的 Python 生成器（可重建全部 HTML / PDF）
│   ├── shell.py            共享外壳：CSS 设计系统、导航、PAGES 目录、index 页
│   ├── part1.py … part8.py 八个部分的课程内容
│   ├── glossary.py         术语表数据
│   ├── quizzes.py          每课互动自测题
│   ├── registry.py         课程文件 → 内容 的统一映射（CONTENT）
│   ├── build.py            站点构建（→ index.html + lessons/）
│   ├── build_print.py      PDF 构建（→ print.html，折叠全展开）
│   ├── check_links.py      内部链接死链检查
│   └── check_html.py       结构 / 用词一致性检查
├── .github/workflows/
│   ├── deploy.yml          CI：构建 + 生成 PDF + 部署 Pages + tag 发 Release
│   └── ci.yml              CI：无漂移 + 死链 + 结构校验
├── README.md
└── LICENSE
```

## 🛠️ 重新生成

所有 HTML 由 `src/` 下的 Python 生成器产出，无第三方依赖（仅需 Python 3）：

```bash
cd src
python build.py          # 生成 index.html + lessons/（站点）
python build_print.py    # 生成 print.html（用于打 PDF，折叠全部展开）
```

页面之间用相对链接互联，整体可直接拷贝、部署到任意静态服务器或 GitHub Pages。

### 本地导出 PDF

`print.html` 把全部 39 课合成单页文档（折叠卡片全部展开、自动分页）。用任意无头浏览器打 PDF，例如：

```bash
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=ragas-visual-guide.pdf \
  --virtual-time-budget=20000 "file://$PWD/print.html"
```

## 🚀 自动化：GitHub Pages + PDF（CI）

仓库内置 `.github/workflows/deploy.yml`，**推送即自动**：
1. 重新构建站点与 `print.html`；
2. 用无头 Chrome 渲染出 **PDF**（CI 已安装 CJK/emoji 字体，中文正常）；
3. 把 `index.html`、`lessons/`、`ragas-visual-guide.pdf` 部署到 **GitHub Pages**；
4. PDF 同时作为构建产物上传；打 `v*` **标签**时还会自动发布 Release 并附带 PDF。

另有 `.github/workflows/ci.yml`（每次 push / PR 触发）做**防回归**：① 重新运行 `build.py` 并校验提交的 HTML 与 `src/` **没有漂移**；② 运行 `check_links.py` 确保**内部链接无死链**；③ 运行 `check_html.py` 做**结构与用词一致性校验**。

**首次启用（一次性）：**
1. 在 GitHub 新建仓库并推送：
   ```bash
   git remote add origin git@github.com:verdenmax/ragas-visual-guide.git
   git push -u origin master
   ```
2. 仓库 **Settings → Pages → Build and deployment → Source** 选 **GitHub Actions**
   （`deploy.yml` 已带 `enablement: true`，公开仓库首次运行会自动开启，此步为兜底）。
3. 之后每次 `push` 到 `master` 会自动部署，站点地址形如
   `https://verdenmax.github.io/ragas-visual-guide/`，PDF 在
   `https://verdenmax.github.io/ragas-visual-guide/ragas-visual-guide.pdf`。
4. 发布带 PDF 的版本：`git tag v1.0 && git push --tags`。

## 📄 许可

本项目以 [MIT License](./LICENSE) 开源，可自由使用、修改与分发。

ragas 为 VibrantLabs 的项目，相关名称与商标归其所有，详见其
[官方仓库](https://github.com/vibrantlabsai/ragas)与文档。本教程为独立的第三方学习材料，与官方无隶属关系。
