# Ragas 图解教程（ragas-visual-guide）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在独立仓库 `/home/verden/course/ragas-visual-guide` 里，用无依赖 Python 生成器产出一套 8 部分 · 39 课的中文可视化（HTML）教程，讲清 ragas（LLM 评测工具包）的宏观全景、用法与真实源码内部，并带互动测验、术语表、PDF 与 CI 自动部署。

**Architecture:** 完全仿照参考项目 `/home/verden/course/langchain-visual-guide` 的成熟架构：`src/shell.py` 提供 CSS 设计系统 + 导航 + 目录页；`src/part1.py … part8.py` 以 HTML 字符串常量承载课程内容；`src/registry.py` 把"文件名 → 内容"统一映射；`build.py` 生成站点（`index.html` + `lessons/NN-*.html`），`build_print.py` 生成可打 PDF 的 `print.html`；`check_html.py` / `check_links.py` 做结构与死链校验。内容对照 `/home/verden/course/ragas/src/ragas` 真实代码核实，引用"文件 + 符号名"不写死行号。

**Tech Stack:** Python 3（仅标准库，无第三方运行时依赖）；纯静态 HTML/CSS/JS；GitHub Actions（Pages 部署 + 无头 Chrome 生成 PDF）。讲解对象源码：ragas（`src/ragas/`，导入根 `ragas`，`requires-python >=3.9`）。

---

## 设计文档（spec）

本计划实现的设计见：`docs/superpowers/specs/2026-06-11-ragas-visual-guide-design.md`（同仓库）。课程大纲、每课源码锚点、品牌、CI 策略均以该 spec 为准。

## 验证策略（本项目的"测试"）

本项目没有 pytest 单元测试；与参考项目一致，**验证 = 构建成功 + 两个校验脚本通过 + 无漂移**。每个任务完成后运行（在 `src/` 目录）：

```bash
cd /home/verden/course/ragas-visual-guide/src
python build.py            # 生成 index.html + lessons/
python check_html.py       # 结构/一致性校验：ERR 必须为 0
python check_links.py      # 内部链接无死链
```

- `check_html.py` 检查：标签平衡（div/details/table/pre/summary）、details↔summary 配对、恰好一个 `<h1>`、有 `<title>` 与 meta description、`<pre>` 内无未转义 `<`、"第 N 课"引用不越界、上一/下一课导航链与 `shell.PAGES` 顺序一致、index 目录列出每一课且"共 N 课 · N 个部分"计数正确、（WARN）每课含"本课要点"与"card analogy"。
- 提交前务必重跑 `build.py` 并 `git diff --exit-code -- index.html lessons/` 确认无漂移（CI 会卡这一点）。

> **源码核实纪律**：写任何"🔬 源码对应 / 行为 / 默认值"前，实际打开 `/home/verden/course/ragas/src/ragas/...` 对应文件确认符号名与行为。见每课锚点与文末"事实校验清单"。

---

## 文件结构（File Structure）

| 文件 | 职责 | 来源 |
|------|------|------|
| `src/shell.py` | CSS 设计系统 + `head_meta()` + `PAGES`（39 课有序表）+ `page()` 课页外壳 + `index_page()` 目录页 + 搜索 JS | 移植参考项目并改品牌/PAGES |
| `src/build.py` | 读 `shell.PAGES` + `registry.CONTENT` + `quizzes.render()` → 写 `index.html` 与 `lessons/NN-*.html` | 移植，改产物名 |
| `src/build_print.py` | 拼全部课程（折叠全展开）→ `print.html`（封面 + 目录 + 正文）供打 PDF | 移植，改标题/产物名 |
| `src/check_html.py` | 结构/一致性回归校验（ERR 非零则失败） | 移植，改 STALE 文案 |
| `src/check_links.py` | 内部相对链接死链校验 | 移植，改 ALLOW_MISSING 的 PDF 名 |
| `src/registry.py` | `CONTENT`：文件名 → `partN.LESSON_xx` 内容字符串（与 `shell.PAGES` 对齐） | 新建 |
| `src/part1.py … part8.py` | 各部分课程内容（HTML 字符串常量） | 新建（内容） |
| `src/quizzes.py` | `QUIZZES` 数据 + `render(fname)`（确定性打乱选项） | 移植骨架 + 新建题目 |
| `src/glossary.py` | `LESSON_GLOSSARY`：术语表/概念索引（第 39 课） | 新建（内容） |
| `index.html`, `lessons/*.html` | 构建产物，随源码一并提交（CI 校验无漂移） | 由 `build.py` 生成 |
| `.github/workflows/deploy.yml` | 构建站点 + 生成 PDF + 部署 Pages + tag 发 Release | 移植，改名 |
| `.github/workflows/ci.yml` | 无漂移校验 + check_links + check_html | 移植 |
| `README.md`, `LICENSE` | 中文说明（徽章）+ MIT | 新建 |

> 课页文件名采用 `NN-<slug>.html`（两位序号 + 语义化英文 slug），完整清单见 Task 1 的 `PAGES`。

---

## 第一阶段 · 脚手架（移植生成器 + 品牌化）

### Task 1: 移植 `shell.py`（设计系统 + 品牌 + 39 课 PAGES）

**Files:**
- Create: `src/shell.py`
- Reference: `/home/verden/course/langchain-visual-guide/src/shell.py`

- [ ] **Step 1: 复制参考 shell.py 作为起点**

```bash
cp /home/verden/course/langchain-visual-guide/src/shell.py \
   /home/verden/course/ragas-visual-guide/src/shell.py
```

- [ ] **Step 2: 改品牌主色（`:root` 与暗色模式）**

在 `CSS` 字符串里，浅色 `:root` 把绿色强调色替换为靛蓝/紫罗兰：

```css
--accent: #5b54e0; --accent-soft: #eceafb; --accent-ink: #3d36b0;
```

暗色模式 `@media (prefers-color-scheme: dark)` 的 `:root` 改为：

```css
--accent: #9b8cff; --accent-soft: #241f4d; --accent-ink: #c4baff;
```

`head_meta()` 里的 `theme-color` 改为 `#5b54e0`（原 `#1a7f64`）。其余 CSS（布局/卡片/表格/折叠/代码/进度条）**原样保留**。

- [ ] **Step 3: 换 favicon**

把 `_FAVICON_SVG` 替换为靛蓝底白色字母 R：

```python
_FAVICON_SVG = (
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'>"
    "<rect width='32' height='32' rx='7' fill='#5b54e0'/>"
    "<text x='16' y='23' font-family='system-ui,sans-serif' font-size='19'"
    " font-weight='700' fill='#fff' text-anchor='middle'>R</text></svg>"
)
```

- [ ] **Step 4: 替换 `PAGES` 为 39 课（文件名, 短标题, 部分标签）**

```python
PAGES = [
    ("01-what-is-ragas.html", "Ragas 是什么", "第一部分 · 宏观全景"),
    ("02-architecture.html", "项目全景", "第一部分 · 宏观全景"),
    ("03-evaluation-lifecycle.html", "一次评测的生命周期", "第一部分 · 宏观全景"),
    ("04-single-turn-sample.html", "数据模型①：SingleTurnSample", "第二部分 · 数据与入口"),
    ("05-multi-turn-sample.html", "数据模型②：MultiTurnSample 与消息", "第二部分 · 数据与入口"),
    ("06-two-datasets.html", "两个 Dataset 之辨", "第二部分 · 数据与入口"),
    ("07-evaluate.html", "经典入口 evaluate()", "第二部分 · 数据与入口"),
    ("08-experiment.html", "现代入口 @experiment", "第二部分 · 数据与入口"),
    ("09-metrics-overview.html", "内置指标全景", "第三部分 · 指标用法"),
    ("10-rag-metrics.html", "RAG 四件套用法", "第三部分 · 指标用法"),
    ("11-custom-metrics.html", "自定义指标（Simple 栈）", "第三部分 · 指标用法"),
    ("12-traditional-metrics.html", "传统 / 非 LLM 指标", "第三部分 · 指标用法"),
    ("13-metric-base.html", "Metric 基类体系", "第四部分 · 指标内部"),
    ("14-metric-result.html", "MetricResult 双重身份", "第四部分 · 指标内部"),
    ("15-faithfulness-internals.html", "Faithfulness 内部", "第四部分 · 指标内部"),
    ("16-context-metrics-internals.html", "Context Precision / Recall 内部", "第四部分 · 指标内部"),
    ("17-answer-metrics-internals.html", "Relevancy / Factual / AspectCritic 内部", "第四部分 · 指标内部"),
    ("18-agent-metrics-internals.html", "Agent / 多轮指标内部", "第四部分 · 指标内部"),
    ("19-prompt-system.html", "Prompt 系统：PydanticPrompt", "第五部分 · 引擎与基础设施"),
    ("20-prompt-advanced.html", "Prompt 进阶：few-shot 与翻译", "第五部分 · 引擎与基础设施"),
    ("21-llm-abstraction.html", "LLM 抽象", "第五部分 · 引擎与基础设施"),
    ("22-embedding-abstraction.html", "Embedding 抽象", "第五部分 · 引擎与基础设施"),
    ("23-executor.html", "执行引擎 Executor", "第五部分 · 引擎与基础设施"),
    ("24-callbacks-cost-cache.html", "Callbacks · 成本 · 缓存", "第五部分 · 引擎与基础设施"),
    ("25-testgen-overview.html", "为什么自动造测试集", "第六部分 · 测试集生成"),
    ("26-knowledge-graph.html", "知识图谱", "第六部分 · 测试集生成"),
    ("27-transforms.html", "Transforms", "第六部分 · 测试集生成"),
    ("28-persona-scenario.html", "Persona 与 Scenario", "第六部分 · 测试集生成"),
    ("29-synthesizers.html", "Synthesizers", "第六部分 · 测试集生成"),
    ("30-testset-generator.html", "TestsetGenerator 端到端", "第六部分 · 测试集生成"),
    ("31-experiments-deep.html", "实验系统深入", "第七部分 · 实验与工程化"),
    ("32-backends.html", "Backends 可插拔", "第七部分 · 实验与工程化"),
    ("33-optimization-training.html", "指标优化与训练", "第七部分 · 实验与工程化"),
    ("34-integrations-frameworks.html", "集成①：框架", "第七部分 · 实验与工程化"),
    ("35-integrations-observability.html", "集成②：观测", "第七部分 · 实验与工程化"),
    ("36-source-debug-contribute.html", "读源码 · 调试 · 测试 · 贡献", "第七部分 · 实验与工程化"),
    ("37-cli.html", "CLI", "第七部分 · 实验与工程化"),
    ("38-capstone.html", "端到端实战", "第八部分 · 实战与速查"),
    ("39-glossary.html", "术语表 · 概念索引", "第八部分 · 实战与速查"),
]
```

- [ ] **Step 5: 全局替换站点名 + 文案**

把所有 `LangChain 图解教程` → `Ragas 图解教程`；topbar/home 的 `📘` → `📊`；`og:site_name` 同改。`page()` 的 `<title>` 模板 `… — LangChain 图解教程` → `… — Ragas 图解教程`。`index_page()` 的 `<title>`、hero `<h1>`、`lead`、`legend`（保留四项：宏观理解/细节·源码/生活类比/关键要点）、PDF 按钮文案、版本锚点段落改写为 ragas 版本（见下 Step 6）。`page()` 的 `head_meta` description 改为 ragas 语境。

- [ ] **Step 6: 改 `index_page()` 的版本锚点与 PDF 链接**

PDF 按钮 `href` 改为 `ragas-visual-guide.pdf`、文案 `📄 下载完整 PDF（全 {len(PAGES)} 课）`（用动态计数，勿写死 39）；版本锚点段落改为：

```html
📌 对照 ragas 当前 <strong>main</strong> 源码讲解 · 最后核验 2026-06 · 源码引用以"文件 + 符号名"为主（行号会随上游更新而变）
```

- [ ] **Step 7: 替换 `index_page()` 的 `subtitles` 字典为 39 条 ragas 副标题**

key 用上面 39 个文件名，value 为一句话副标题，例如 `"01-what-is-ragas.html": "从 vibe check 到系统化评测闭环"`、`"15-faithfulness-internals.html": "claim 分解 + NLI 两阶段"` 等（逐条对应 spec 第 5 节的课程描述）。

- [ ] **Step 8: 语法 + 数量自检**

Run:
```bash
cd /home/verden/course/ragas-visual-guide/src && \
python -c "import shell; print(len(shell.PAGES), len({p[2] for p in shell.PAGES}))"
```
Expected: `39 8`

### Task 2: 移植 `build.py` / `build_print.py` / `check_html.py` / `check_links.py`

**Files:**
- Create: `src/build.py`, `src/build_print.py`, `src/check_html.py`, `src/check_links.py`
- Reference: 同名文件位于 `/home/verden/course/langchain-visual-guide/src/`

- [ ] **Step 1: 原样复制四个脚本**

```bash
cd /home/verden/course/langchain-visual-guide/src
cp build.py build_print.py check_html.py check_links.py \
   /home/verden/course/ragas-visual-guide/src/
```

- [ ] **Step 2: `build.py` 无需改动**

`build.py` 不含 langchain 专有字符串（只用 `shell.PAGES`/`shell.INDEX_FILE`/`registry.CONTENT`/`quizzes.render`）。保持原样。

- [ ] **Step 3: `build_print.py` 改标题/封面/PDF 名**

把封面 `<h1>LangChain 图解教程</h1>` → `<h1>Ragas 图解教程</h1>`；封面 emoji `📘` → `📊`（与站点品牌一致）；封面 `sub` 改为 `从零理解整个 ragas · 宏观 → 用法 → 源码内部 → 测试生成 → 实战`；`<title>` 与 docstring 里的 `langchain-visual-guide.pdf` → `ragas-visual-guide.pdf`；封面 `meta` 的"每课配真实代码对应与设计亮点"保留。

- [ ] **Step 4: `check_links.py` 改放行的 PDF 名**

```python
ALLOW_MISSING = {"ragas-visual-guide.pdf"}
```

- [ ] **Step 5: `check_html.py` 改 STALE 与 SOFT_EXEMPT**

```python
STALE = [
    "LangChain 图解教程",   # 站点名漏替换
    "全 27 课", "共 27 课", "27 课 · 8 个部分",
]
SOFT_EXEMPT = {"39-glossary.html"}
```

> 注意：`STALE` 只放整句站点名"LangChain 图解教程"，**不要**放裸词 "LangChain"（第 34 课讲集成时会合法提到 LangChain）。

- [ ] **Step 6: 语法自检（暂不构建，registry/parts 尚未就绪）**

Run:
```bash
cd /home/verden/course/ragas-visual-guide/src && \
python -c "import ast; [ast.parse(open(f).read()) for f in ('build.py','build_print.py','check_html.py','check_links.py')]; print('syntax ok')"
```
Expected: `syntax ok`

### Task 3: 创建 `registry.py` + 8 个 part 桩 + `quizzes.py` + `glossary.py` 桩（空壳可构建）

**Files:**
- Create: `src/registry.py`, `src/part1.py … src/part8.py`, `src/glossary.py`, `src/quizzes.py`

- [ ] **Step 1: 写 `registry.py`（39 条映射）**

```python
"""Single source of truth: ordered map of output filename -> lesson HTML.

Imported by both build.py and build_print.py so the lesson set stays in sync.
"""
import part1, part2, part3, part4, part5, part6, part7, part8
import glossary

CONTENT = {
    "01-what-is-ragas.html": part1.LESSON_01,
    "02-architecture.html": part1.LESSON_02,
    "03-evaluation-lifecycle.html": part1.LESSON_03,
    "04-single-turn-sample.html": part2.LESSON_04,
    "05-multi-turn-sample.html": part2.LESSON_05,
    "06-two-datasets.html": part2.LESSON_06,
    "07-evaluate.html": part2.LESSON_07,
    "08-experiment.html": part2.LESSON_08,
    "09-metrics-overview.html": part3.LESSON_09,
    "10-rag-metrics.html": part3.LESSON_10,
    "11-custom-metrics.html": part3.LESSON_11,
    "12-traditional-metrics.html": part3.LESSON_12,
    "13-metric-base.html": part4.LESSON_13,
    "14-metric-result.html": part4.LESSON_14,
    "15-faithfulness-internals.html": part4.LESSON_15,
    "16-context-metrics-internals.html": part4.LESSON_16,
    "17-answer-metrics-internals.html": part4.LESSON_17,
    "18-agent-metrics-internals.html": part4.LESSON_18,
    "19-prompt-system.html": part5.LESSON_19,
    "20-prompt-advanced.html": part5.LESSON_20,
    "21-llm-abstraction.html": part5.LESSON_21,
    "22-embedding-abstraction.html": part5.LESSON_22,
    "23-executor.html": part5.LESSON_23,
    "24-callbacks-cost-cache.html": part5.LESSON_24,
    "25-testgen-overview.html": part6.LESSON_25,
    "26-knowledge-graph.html": part6.LESSON_26,
    "27-transforms.html": part6.LESSON_27,
    "28-persona-scenario.html": part6.LESSON_28,
    "29-synthesizers.html": part6.LESSON_29,
    "30-testset-generator.html": part6.LESSON_30,
    "31-experiments-deep.html": part7.LESSON_31,
    "32-backends.html": part7.LESSON_32,
    "33-optimization-training.html": part7.LESSON_33,
    "34-integrations-frameworks.html": part7.LESSON_34,
    "35-integrations-observability.html": part7.LESSON_35,
    "36-source-debug-contribute.html": part7.LESSON_36,
    "37-cli.html": part7.LESSON_37,
    "38-capstone.html": part8.LESSON_38,
    "39-glossary.html": glossary.LESSON_GLOSSARY,
}
```

- [ ] **Step 2: 生成 8 个 part 桩 + glossary 桩（每个 LESSON 常量给最小合法内容）**

用下面脚本一次性生成（桩内容稍后由各内容任务替换）：

```bash
cd /home/verden/course/ragas-visual-guide/src
python - <<'PY'
ranges = {
    "part1": [1, 2, 3], "part2": [4, 5, 6, 7, 8],
    "part3": [9, 10, 11, 12], "part4": [13, 14, 15, 16, 17, 18],
    "part5": [19, 20, 21, 22, 23, 24], "part6": [25, 26, 27, 28, 29, 30],
    "part7": [31, 32, 33, 34, 35, 36, 37], "part8": [38],
}
stub = '''<p class="lead">（建设中）本课内容稍后填充。</p>
<div class="card analogy"><div class="tag">🧩 生活类比</div>占位。</div>
<div class="card key"><div class="tag">✅ 本课要点</div><ul><li>占位。</li></ul></div>'''
for mod, nums in ranges.items():
    lines = [f'"""Content for {mod} (stub)."""', ""]
    for n in nums:
        lines.append(f'LESSON_{n:02d} = r"""\n{stub}\n"""')
        lines.append("")
    open(f"{mod}.py", "w", encoding="utf-8").write("\n".join(lines))
open("glossary.py", "w", encoding="utf-8").write(
    '"""Glossary / concept index (lesson 39, stub)."""\n\n'
    'LESSON_GLOSSARY = r"""\n' + stub + '\n"""\n'
)
print("stubs written")
PY
```

- [ ] **Step 3: 移植 `quizzes.py`，清空题库**

```bash
cp /home/verden/course/langchain-visual-guide/src/quizzes.py \
   /home/verden/course/ragas-visual-guide/src/quizzes.py
```
然后把 `QUIZZES = { … }` 整个字典替换为 `QUIZZES = {}`（保留 `_shuffle` 与 `render`；`render` 已对缺失 key 返回 `""`）。

- [ ] **Step 4: 构建空壳站点**

Run:
```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py
```
Expected: `Wrote 40 files under …`（39 课 + index.html）

- [ ] **Step 5: 跑校验（ERR 必须 0；WARN 允许）**

Run:
```bash
cd /home/verden/course/ragas-visual-guide/src && python check_html.py && python check_links.py
```
Expected: `check_html.py` 末行 `✓ structural check passed`（会有"no 本课要点 / analogy"之外的 WARN，但 0 error）；`check_links.py` 输出 `✓ all N internal links resolve`。

- [ ] **Step 6: Commit（含首次生成的 HTML 产物）**

```bash
cd /home/verden/course/ragas-visual-guide
git add -A
git commit -m "feat: scaffold registry + part stubs + quizzes; green empty-shell build"
```

---

## 第二阶段 · 内容编写

### 内容编写规范（所有课程任务共用）

**每课 HTML 骨架（按此顺序）：**

1. `<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem"> … </p>` — 一句话点题（🌍 宏观理解）
2. `<div class="card analogy"><div class="tag">🧩 生活类比</div> … </div>` — 生活类比（**必有**，否则 check_html WARN）
3. 若干 `<h2>` 小节 + `<table class="t">` 对比表 + `<details class="accordion">` 折叠深挖
4. `<div class="card detail"><div class="tag">🔬 源码对应</div> … </div>` — 指向真实 `ragas/...` 文件 + 符号名
5. `<div class="card spark"><div class="tag">💡 设计亮点</div><ul> … </ul></div>` — 值得学习的点（**本教程重点**）
6. `<div class="card key"><div class="tag">✅ 本课要点</div><ul> … </ul></div>` — 小结（**必有**）

**组件速查（均为参考项目已有的 CSS 类，shell.py 原样保留）：**

- 卡片：`card macro`(🌍)、`card detail`(🔬)、`card analogy`(🧩)、`card key`(✅)、`card spark`(💡)、`card warn`(⚠️)
- 折叠：`<details class="accordion"><summary><span class="badge-num">1</span> 标题 <span class="hint">点击展开详解</span></summary><div class="acc-body"><div class="qa"><div class="q">🧪 示例</div><div class="a"> … </div></div></div></details>`
- 代码块：`<pre class="code"><span class="cm"># 注释</span>\n<span class="kw">from</span> ragas <span class="kw">import</span> evaluate</pre>`；行内代码二选一并保持一致：`<span class="inline">x</span>` 用于**正文里强调符号/标识符**（chip 样式），`<span class="mono">x</span>` 用于**文件路径、源码对应卡片、表格里的符号**（等宽）。
- 表格：`<table class="t"><tr><th>…</th></tr><tr><td>…</td></tr></table>`

**编写纪律（硬性）：**

- **先读源码再下笔**：写每课前打开 spec 第 5 节列出的 `/home/verden/course/ragas/src/ragas/...` 锚点文件，确认符号名与行为。
- `<pre>` 内的 `<`、`>` 必须转义为 `&lt;`/`&gt;`，或仅用 `PRE_INLINE` 允许的标签（span/strong/b/em/u/a）——否则 check_html 报 ERR。
- 引用源码用"文件 + 符号名"，**不写行号**。
- 跨课引用写"第 N 课"且 N≤39；不要出现 langchain 旧文案或错误课数。
- 中文正文；代码/标识符保留英文原名。

**每课验证（统一）：** 写完该批次后在 `src/` 跑 `python build.py && python check_html.py && python check_links.py`，确保 0 ERR、无死链，再提交。

---

### Task 4: 第 1 课「Ragas 是什么」— 完整范例（其余课照此模板）

**Files:**
- Modify: `src/part1.py`（替换 `LESSON_01` 桩为下方完整内容）
- 阅读核实：`/home/verden/course/ragas/README.md`、`docs/index.md`、`src/ragas/__init__.py`

- [ ] **Step 1: 把 `part1.py` 的 `LESSON_01` 替换为完整内容**

```python
LESSON_01 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Ragas 是一个用 Python 写的<strong>开源工具包</strong>，专门帮你<strong>评测</strong>大语言模型（LLM）应用。
它的核心主张是：把你对 AI 应用"<strong>感觉还行</strong>"（vibe check）的主观判断，升级成
<strong>可量化、可复现、可迭代的系统化评测闭环</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  没有 ragas 时，判断 AI 应用好不好像<strong>用手背试体温</strong>——主观、说不清、换个人结论就变。
  ragas 给你一套<strong>体检仪器 + 指标 + 病历本</strong>：用客观分数量体温，用测试集做标准化体检，
  用实验记录每次"用药"前后的变化。从"我觉得还行"变成"数据说它从 0.72 涨到 0.81"。
</div>

<h2>它到底解决什么问题？</h2>
<p>直接拿 LLM 拼个应用很容易，但"它到底好不好、改完是变好还是变差"却很难回答。ragas 要抹平的正是这几类麻烦：</p>

<table class="t">
  <tr><th>痛点</th><th>没有 ragas 时</th><th>ragas 的做法</th></tr>
  <tr><td><strong>主观</strong></td><td>"读几条输出感觉还行"</td><td>用<strong>客观指标</strong>打分（LLM 类 + 传统类）</td></tr>
  <tr><td><strong>不可复现</strong></td><td>换个人 / 换一天结论就变</td><td>固定<strong>数据集 + 指标</strong>，分数可重跑</td></tr>
  <tr><td><strong>没有测试集</strong></td><td>靠手写几条样例</td><td><strong>自动生成</strong>覆盖多场景的测试集</td></tr>
  <tr><td><strong>不知改动好坏</strong></td><td>改完凭感觉"应该更好了"</td><td>用 <span class="mono">experiment</span> 跑前后对比</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 三大支柱：评测 · 测试生成 · 实验 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一个最小评测</div>
      <div class="a">用 <span class="inline">DiscreteMetric</span> 自定义一个"准确/不准确"的裁判（取自官方快速上手）：
<pre class="code"><span class="kw">from</span> ragas.metrics <span class="kw">import</span> DiscreteMetric
<span class="kw">from</span> ragas.llms <span class="kw">import</span> llm_factory

metric = DiscreteMetric(
    name=<span class="st">"summary_accuracy"</span>,
    allowed_values=[<span class="st">"accurate"</span>, <span class="st">"inaccurate"</span>],
    prompt=<span class="st">"判断摘要是否准确：\nResponse: {response}"</span>,
)
score = <span class="kw">await</span> metric.ascore(llm=llm, response=<span class="st">"……"</span>)
print(score.value, score.reason)  <span class="cm"># 'accurate' + 给分理由</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ 三大支柱怎么配合</div>
      <div class="a"><strong>① 评测</strong>（metrics + <span class="inline">evaluate</span>/<span class="inline">experiment</span>）给输出打分；
        <strong>② 测试生成</strong>（<span class="inline">TestsetGenerator</span>）从你的文档自动造测试集；
        <strong>③ 实验</strong>（<span class="inline">@experiment</span>）把"改动 → 跑分 → 对比"固化成闭环。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  公开入口集中在 <span class="mono">src/ragas/__init__.py</span>：评测用 <span class="mono">evaluate</span>/<span class="mono">aevaluate</span>，
  实验用 <span class="mono">experiment</span>/<span class="mono">Experiment</span>，数据用 <span class="mono">Dataset</span>/<span class="mono">EvaluationDataset</span>。
  指标从子模块导入（如 <span class="mono">from ragas.metrics import Faithfulness</span>）。介绍见 <span class="mono">README.md</span> 与 <span class="mono">docs/index.md</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>experiments-first</strong>：ragas 把"评测"重塑成"做实验"——每次改动都能跑一遍、留下可对比的记录，而不是一次性打个分。</li>
    <li><strong>LLM 类 + 传统类指标并存</strong>：既能用 LLM 当裁判（语义层面），也能用 BLEU/ROUGE 等确定性指标，按场景取舍。</li>
    <li><strong>自定义指标只需一个装饰器或一个类</strong>：把"评测标准"也变成可版本化的代码。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>ragas = LLM 应用的<strong>系统化评测工具包</strong>：从 vibe check 升级到可量化、可复现、可迭代。</li>
    <li>记住三大支柱：<strong>评测 → 测试生成 → 实验</strong>，这是整套教程的骨架。</li>
    <li>下一课拉远镜头，看看这些能力散落在 <span class="mono">src/ragas</span> 的哪些子包里。</li>
  </ul>
</div>
"""
```

- [ ] **Step 2: 构建 + 校验**

Run:
```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
```
Expected: 0 ERR；`01-what-is-ragas.html` 不再触发 analogy/key 的 WARN。

- [ ] **Step 3: Commit**

```bash
cd /home/verden/course/ragas-visual-guide
git add -A && git commit -m "content: lesson 01 (what is ragas) as canonical template"
```

---

### Task 5: 第一部分剩余 · 第 2–3 课

**Files:** Modify `src/part1.py`（`LESSON_02`、`LESSON_03`）。按 Task 4 模板写，写前阅读锚点源码。

- [ ] **Step 1: 第 2 课「项目全景」(`LESSON_02`, `02-architecture.html`)**
  - 锚点：`src/ragas/`（目录结构）、`ragas/__init__.py`（`__all__`、`__getattr__("experimental")`）、子包 `metrics/`/`testset/`/`llms/`/`embeddings/`/`prompt/`/`backends/`/`integrations/`/`optimizers/`、`evaluation.py`、`experiment.py`、`executor.py`。
  - 类比：把 ragas 想成一座"评测工厂"——原料(`Dataset`)、质检线(metrics)、自动出题车间(testset)、实验台(experiment)、水电基建(llms/embeddings/executor)。
  - 小节：① 顶层公开 API（`__init__.py` 导出了什么 / 没导出什么）；② 一张"子包地图"表（每个子包一句话职责）；③ 两条主线预告：评测线 vs 测试生成线。
  - 💡 设计亮点：公开面**小而稳**（`__all__` 只导核心，metrics/llms 等从子模块按需导入，降低耦合）；`experimental` 用惰性 `__getattr__` 按需加载，缺依赖时给清晰报错。
  - ✅ 要点：记住子包地图；分清两条主线；后续课程都按这张图展开。
  - 测验点：为什么 metrics 不在顶层 `__all__`？惰性 `__getattr__` 解决了什么？

- [ ] **Step 2: 第 3 课「一次评测的生命周期」(`LESSON_03`, `03-evaluation-lifecycle.html`)**
  - 锚点：`evaluation.py`（`aevaluate`/`evaluate`、无指标时的默认集合 `[answer_relevancy, context_precision, faithfulness, context_recall]`、`DeprecationWarning`、`return_executor`）、`executor.py`（`Executor`）、`dataset_schema.py`（`EvaluationResult.__post_init__`）、`callbacks.py`（`new_group`/`RAGAS_EVALUATION_CHAIN_NAME`）。
  - 类比：像考试阅卷——试卷(samples) × 评分标准(metrics) → 多人并发阅卷(`Executor`) → 汇总成绩单(`EvaluationResult`)。
  - 小节：数据流 6 步（默认指标 → 规范化数据集 → 注入 LLM/embeddings + `metric.init` → `Executor` 按 (sample × metric) 提交 `single_turn_ascore`/`multi_turn_ascore` → `aresults()` 按 `results[len(metrics)*i+j]` 重排 → `EvaluationResult`）；为何官方转向 `@experiment`。
  - 💡 设计亮点：**async-first**（`aevaluate` 是真实现，`evaluate` 是同步包装）；每个 (sample,metric) 是独立任务 → 天然并发；失败转 `np.nan` 不中断整轮。
  - ✅ 要点：记住生命周期 6 步；`evaluate` 已废弃、指向 `@experiment`；下一部分深入"数据与入口"。
  - 测验点：默认四指标是哪四个？为什么 evaluate 发 DeprecationWarning？结果如何从扁平列表重排回每行？

- [ ] **Step 3: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 1 lessons 02-03 (architecture, eval lifecycle)"
```

---

### Task 6: 第二部分 · 第 4–8 课（数据与入口）

**Files:** Modify `src/part2.py`（`LESSON_04`…`LESSON_08`）。按模板写，写前读锚点。

- [ ] **Step 1: 第 4 课「数据模型① SingleTurnSample」(`04-single-turn-sample.html`)**
  - 锚点：`dataset_schema.py`（`BaseSample.to_dict`/`get_features`/`to_string`、`SingleTurnSample` 全字段、`RagasDataset` 转换器、`EvaluationDataset`）。
  - 类比：一行样本像一张"考卷"——问题(`user_input`)、参考资料(`retrieved_contexts`)、标准答案(`reference`)、考生作答(`response`)。
  - 小节：`SingleTurnSample` 全字段表（`user_input`/`retrieved_contexts`/`reference_contexts`/`response`/`multi_responses`/`reference`/`rubrics`/`persona_name` 等，均 Optional）；`EvaluationDataset` 容器 + `to_pandas`/`from_hf_dataset`/`to_csv`/`to_jsonl`；哪些字段被哪些指标要求。
  - 💡 设计亮点：`to_dict` 丢弃 `None` → 样本"按需带字段"；统一的 `RagasDataset` 转换层让 pandas/HF/csv/jsonl 互转。
  - ✅ 要点：记住核心字段语义；样本 → `EvaluationDataset` → 喂给评测。
  - 测验点：`retrieved_contexts` vs `reference_contexts` 区别？为什么字段大多 Optional？

- [ ] **Step 2: 第 5 课「数据模型② MultiTurnSample 与消息」(`05-multi-turn-sample.html`)**
  - 锚点：`dataset_schema.py`（`MultiTurnSample` 的 `field_validator`、`to_messages`、`pretty_repr`、`reference_tool_calls`/`reference_topics`）、`messages.py`（`Message`/`HumanMessage`/`AIMessage`/`ToolMessage`/`ToolCall`）。
  - 类比：多轮样本像"一段聊天记录 + 工具调用小票"。
  - 小节：五类消息；`MultiTurnSample.user_input` 是消息列表；`field_validator` 强制 tool-call/message 合法顺序；这是 Agent/多轮评测的数据基础（呼应第 18 课）。
  - 💡 设计亮点：结构化消息（`AIMessage.tool_calls` 里的 `ToolCall` 与随后的 `ToolMessage` 按**顺序**配对，ragas 消息无 `tool_call_id` 字段）；在**数据层**就用 validator 保证消息序合法，错误前移。
  - ✅ 要点：单轮 vs 多轮样本的差异；消息是 Agent 评测的载体。
  - 测验点：`field_validator` 防止了什么非法数据？`ToolMessage` 如何与 `AIMessage` 的工具调用配对（按顺序）？

- [ ] **Step 3: 第 6 课「两个 Dataset 之辨」(`06-two-datasets.html`)**
  - 锚点：`dataset.py`（`DataTable`、`Dataset`、`_resolve_backend`、`DATATABLE_TYPE`）对比 `dataset_schema.py`（`EvaluationDataset`、`RagasDataset`）。
  - 类比：`EvaluationDataset` 是"待阅的一叠考卷"（评测输入）；`Dataset`/`DataTable` 是"带存储的台账"（可 `load`/`save` 到 backend）。
  - 小节：两者来历与用途区别（评测输入 vs 存储型 list-like + backend）；何时用哪个；`Experiment` 也建在 `DataTable` 上。
  - 💡 设计亮点：同名易混 → 讲清边界；`DataTable` 泛型基类被 `Dataset` 与 `Experiment` 共用（DRY）；backend 用字符串 `"local/csv"` 解析。
  - ✅ 要点：分清两个"Dataset"；存储型走 backend。
  - 测验点：哪个 Dataset 喂给 `evaluate`？哪个能存到 csv backend？

- [ ] **Step 4: 第 7 课「经典入口 evaluate()」(`07-evaluate.html`)**
  - 锚点：`evaluation.py`（`evaluate`/`aevaluate` 参数：metrics/llm/embeddings/run_config/callbacks）、`dataset_schema.py`（`EvaluationResult.to_pandas`/`total_tokens`/`total_cost`/`__repr__`）、`validation.py`（`remap_column_names`）。
  - 类比：像"一键阅卷"。
  - 小节：最小可跑示例（`EvaluationDataset` + metrics → `evaluate` → result）；结果解读（`to_pandas`、均值分、token/cost）；列名 remap。
  - 💡 设计亮点：缺 LLM 时自动建默认 `llm_factory("gpt-4o-mini", client=OpenAI())`；结果对象自带成本统计。
  - ✅ 要点：会跑会读结果；它已废弃 → 第 8 课的 `@experiment`。
  - 测验点：不传 metrics 会发生什么？结果里的均值怎么来的（`safe_nanmean`）？

- [ ] **Step 5: 第 8 课「现代入口 @experiment」(`08-experiment.html`)**
  - 锚点：`experiment.py`（`experiment` 装饰器、`ExperimentWrapper.__call__`/`arun`、`version_experiment`）；对照 `evaluation.py` 的 `DeprecationWarning`。
  - 类比：把"评测"写成一个"实验函数"——对每行数据跑一遍并自动存结果。
  - 小节：为何取代 `evaluate`（experiments-first）；最小示例（`@experiment` 装饰函数 → `dataset.arun`）；命名 + backend 解析 + `asyncio.as_completed` 并发 + 存盘；`version_experiment`（git 版本化）。
  - 💡 设计亮点：**实验即函数 + 自动留痕**（可对比迭代）；`arun` 并发跑全行 + tqdm；结果落 backend 可复查。
  - ✅ 要点：现代推荐路径；改动 → 跑实验 → 对比。
  - 测验点：`@experiment` 相比 `evaluate` 多了什么能力？`arun` 如何并发？

- [ ] **Step 6: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 2 lessons 04-08 (data model & entry points)"
```

---

### Task 7: 第三部分 · 第 9–12 课（指标用法）

**Files:** Modify `src/part3.py`（`LESSON_09`…`LESSON_12`）。按模板写，写前读锚点。

> **⚠️ 重要（两代指标，务必讲清）**：ragas 指标正在迁移——具名指标（Faithfulness/ContextPrecision/AnswerRelevancy/AspectCritic/FactualCorrectness/BLEU/ROUGE/ToolCallAccuracy…）的**规范位置是 `ragas.metrics.collections`**；从 `ragas.metrics` 导入它们会触发 `DeprecationWarning`（v1.0 移除）。而 `DiscreteMetric`/`NumericMetric`/`RankingMetric` 及基类原语仍规范地留在 `ragas.metrics`。现代用法：`metric = Faithfulness(llm=...)` 然后 `await metric.ascore(user_input=..., response=..., retrieved_contexts=[...])` → 返回 `MetricResult`。经典 `evaluate()` 的默认指标仍用旧版单例（`_*.py`）。**本部分一律以 `ragas.metrics.collections` 为推荐导入，并点明旧导入已废弃。**（来源：`metrics/__init__.py` 的 `__all__`/`_DEPRECATED_METRICS`/`__getattr__`；`metrics/collections/__init__.py`）

- [ ] **Step 1: 第 9 课「内置指标全景」(`09-metrics-overview.html`)**
  - 锚点：`metrics/__init__.py`（`__all__` 只剩基类原语 + Simple 栈；`_DEPRECATED_METRICS` + `__getattr__` 把具名指标转向 collections）、`metrics/collections/__init__.py`（具名指标规范清单）、`metrics/base.py`（`MetricType`）、`README.md` Key Features。
  - 类比：指标像"体检套餐目录"——按器官（场景）分类挑选。
  - 小节：**两代指标 + 导入位置**（collections 具名 vs ragas.metrics 原语/Simple 栈，旧导入废弃）；LLM 类 vs 传统类；按场景分（RAG / Agent / 通用 / 字符串）；一张大表（指标 → 类型 → 用途 → 对应课程链接）。
  - 💡 设计亮点：指标库分两代但**算法一致**；现代 collections 指标统一 `ascore(**kwargs)→MetricResult`，可自由混用、组合。
  - ✅ 要点：建立指标地图；具名指标从 `ragas.metrics.collections` 导入。
  - 测验点：具名指标的规范导入位置？为何从 `ragas.metrics` 导入会告警？

- [ ] **Step 2: 第 10 课「RAG 四件套用法」(`10-rag-metrics.html`)**
  - 锚点：`metrics/collections/faithfulness/`、`collections/context_precision/`、`collections/context_recall/`、`collections/answer_relevancy/`（现代规范实现）；旧版默认指标见 `evaluation.py` + `_faithfulness.py` 等。
  - 类比：RAG 像"开卷考试"——四件套分别查"有没有照着资料答 / 资料相不相关 / 资料够不够 / 答没答到点"。
  - 小节：四个指标各衡量什么 + 各需哪些字段（Faithfulness 需 `response`+`retrieved_contexts`；ContextRecall 需 `reference`；AnswerRelevancy 需 embeddings）；用 `from ragas.metrics.collections import Faithfulness, ...` + `await metric.ascore(...)` 的最小组合示例；提一句经典 `evaluate()` 默认就是这四个（旧版单例）。
  - 💡 设计亮点：四件套覆盖 RAG 的**检索质量 + 生成质量**两端，互补成闭环。
  - ✅ 要点：记住四件套各管一段；现代从 collections 导入、`ascore` 调用。
  - 测验点：哪两个查"检索"、哪两个查"生成"？AnswerRelevancy 为何还要 embeddings？

- [ ] **Step 3: 第 11 课「自定义指标（Simple 栈）」(`11-custom-metrics.html`)**
  - 锚点：`metrics/discrete.py`（`DiscreteMetric`、默认 `allowed_values=["pass","fail"]`、`create_auto_response_model`）、`numeric.py`（`NumericMetric`、`range`）、`ranking.py`（`RankingMetric`）、`decorator.py`（`discrete_metric`/`numeric_metric`/`ranking_metric`、`CustomMetric`、`score` 强制 keyword-only）。
  - 类比：自己定一份"评分细则"，让 LLM 照着打分。
  - 小节：三种新指标类（离散/数值/排序）+ 三个装饰器；`DiscreteMetric` 示例；装饰器把普通函数变指标。
  - 💡 设计亮点：`__post_init__` 用 `Literal[...]` **自动生成 pydantic 响应模型**，把 LLM 输出强约束到 `allowed_values`；类 / 装饰器两种风格按口味选。
  - ✅ 要点：评测标准也能写成可版本化的代码；优先用 Simple 栈做自定义。
  - 测验点：`Literal` 自动响应模型解决了什么？装饰器为何要求 `score` 关键字参数？

- [ ] **Step 4: 第 12 课「传统 / 非 LLM 指标」(`12-traditional-metrics.html`)**
  - 锚点：现代规范实现 `metrics/collections/_bleu_score.py`、`_rouge_score.py`、`chrf_score`、`_string.py`（`ExactMatch`/`StringPresence`/`NonLLMStringSimilarity`/`DistanceMeasure`）、`sql_semantic_equivalence`、`datacompy_score`、`context_*`（`NonLLM*`/ID-based 变体）；旧版镜像在 `metrics/_bleu_score.py`/`_rouge_score.py`/`_string.py` 等（已废弃导出）。
  - 类比：不请"考官"(LLM)，改用"尺子"(确定性算法)量。
  - 小节：何时用传统指标（便宜 / 可复现 / 无需 LLM）；各指标一句话；非 LLM 的 context precision/recall 变体（字符串距离 / ID 匹配）。
  - 💡 设计亮点：同一概念常有 **LLM 版 + Non-LLM 版**（成本/精度权衡）；传统指标确定性、零 token 成本。
  - ✅ 要点：能用尺子就别请考官；混合使用更划算。
  - 测验点：传统指标相比 LLM 指标的两大优势？什么时候它们不够用？

- [ ] **Step 5: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 3 lessons 09-12 (metrics usage)"
```

---

### Task 8: 第四部分 · 第 13–18 课（指标源码内部）

**Files:** Modify `src/part4.py`（`LESSON_13`…`LESSON_18`）。按模板写。**两代实现**：算法的规范实现现在在 `metrics/collections/<name>/metric.py` + `util.py`（基于 `SimpleBaseMetric`→`collections/base.py:BaseMetric` + instructor LLM + `ragas.prompt.metrics.base_prompt.BasePrompt`，`ascore(**kwargs)`），旧版镜像在 `metrics/_*.py`（基于 `MetricWithLLM`+`PydanticPrompt`，已废弃）。**每课先打开 collections 的规范实现读懂 Prompt 输入/输出模型与聚合逻辑再下笔**；两代算法一致，讲算法即可，并点明"规范实现在 collections、旧版已废弃"。若某指标的 collections 实现与旧版细节不同，以 **collections 实际代码**为准。

- [ ] **Step 1: 第 13 课「Metric 基类体系」(`13-metric-base.html`)**
  - 锚点：`metrics/base.py`（`Metric`、`MetricType`、`MetricOutputType`、`MetricWithLLM`、`MetricWithEmbeddings`、`SingleTurnMetric`、`MultiTurnMetric`、`SimpleBaseMetric`、`SimpleLLMMetric`、`ModeMetric`）、`metrics/collections/base.py`（`BaseMetric(SimpleBaseMetric, NumericValidator)`）、`metrics/__init__.py`（`__all__` vs `_DEPRECATED_METRICS`）。
  - 类比：指标的"族谱"——两代血脉（经典 `MetricWithLLM` vs 现代 `SimpleBaseMetric`/collections `BaseMetric`）。
  - 小节：经典栈（`Metric` → `MetricWithLLM`/`MetricWithEmbeddings` → `SingleTurnMetric`/`MultiTurnMetric`，`single_turn_ascore(sample)`，已废弃导出）；现代栈（`SimpleBaseMetric` → `SimpleLLMMetric`/collections `BaseMetric` → Discrete/Numeric/Ranking 与 collections 具名指标，`ascore(**kwargs)→MetricResult`）；`MetricType`/`MetricOutputType`；`required_columns` 的 `:optional`/`:ignored` 后缀（经典栈）。
  - 💡 设计亮点：**一次架构迁移**——把指标从"绑定 SingleTurnSample 的经典栈"迁到"组件化、用 instructor 结构化输出的现代栈"，新旧并存、算法不变（值得学习的演进案例）。
  - ✅ 要点：看懂两代族谱再读具体指标；规范实现走 collections。
  - 测验点：`MetricWithLLM` 与 collections `BaseMetric` 各属哪代？两代调用接口有何不同（`single_turn_ascore(sample)` vs `ascore(**kwargs)`）？

- [ ] **Step 2: 第 14 课「MetricResult 双重身份」(`14-metric-result.html`)**
  - 锚点：`metrics/result.py`（`MetricResult`、`__get_pydantic_core_schema__`、`__float__`/`__int__`、算术/比较 dunders、`to_dict`）。
  - 类比：一张既写着"分数"又写着"评语"的成绩条。
  - 小节：`MetricResult` 包 `value` + reason/traces；运算符重载让它能直接当数字参与计算/比较；pydantic core schema 让它能嵌进模型并序列化。
  - 💡 设计亮点：**一个对象同时是"可运算的数值"和"可解释的理由"**——靠 `__float__` 与 `__get_pydantic_core_schema__` 实现双重身份，既好用又可追溯。
  - ✅ 要点：分数不只是数字，还带 why；这是 ragas 可解释性的关键。
  - 测验点：为什么 `MetricResult` 要重载 `__float__`？core schema 解决了什么？

- [ ] **Step 3: 第 15 课「Faithfulness 内部」(`15-faithfulness-internals.html`)**
  - 锚点（规范）：`metrics/collections/faithfulness/metric.py`（`Faithfulness(BaseMetric)`、`ascore`、`_create_statements`/`_create_verdicts`/`_compute_score`）+ `faithfulness/util.py`（`StatementGeneratorPrompt`/`StatementGeneratorInput`/`Output`、`NLIStatementPrompt`/`NLIStatementInput`/`Output`、`StatementFaithfulnessAnswer`(verdict 0/1)）；旧版镜像 `metrics/_faithfulness.py`（含 `FaithfulnesswithHHEM`）。
  - 类比：两步判"作弊"——先把答案拆成一句句"主张"，再逐句去资料里查"有没有依据"。
  - 小节：阶段① claim 分解（`StatementGeneratorPrompt`）；阶段② NLI 逐句裁决（`NLIStatementPrompt` → verdict 0/1）；得分 = 有据数 / 总数；HHEM 变体（旧版）用 cross-encoder 替代 NLI LLM。
  - 💡 设计亮点：**claim 分解 + NLI** 是可复用范式（第 17 课 FactualCorrectness 复用 `NLIStatementPrompt`）；现代实现用 instructor `agenerate(prompt_str, OutputModel)` 直接拿结构化结果。
  - ✅ 要点：忠实度 = 拆句 + 逐句查证；规范实现在 collections。
  - 测验点：两个阶段分别用哪个 Prompt？得分公式是什么？

- [ ] **Step 4: 第 16 课「Context Precision / Recall 内部」(`16-context-metrics-internals.html`)**
  - 锚点（规范）：`metrics/collections/context_precision/`（`metric.py`+`util.py`：逐条裁决 + 平均精度；`ContextPrecisionWithReference`/`WithoutReference`/`ContextUtilization`）、`metrics/collections/context_recall/`（按句归因 attributed 0/1）；旧版镜像 `_context_precision.py`/`_context_recall.py`（`ContextPrecisionPrompt`/`QAC`/`Verification`/`_calculate_average_precision`、`ContextRecallClassificationPrompt`、`NonLLM*`/`IDBased*` 变体）、`base.py`（`Ensember`/`ensembler` 多次投票）。**写前在源码确认 collections 版是否仍用 `Ensember`/`generate_multiple`，以实际为准。**
  - 类比：precision 像"检索排序质量"（有用的是否排前面）；recall 像"标准答案每句能否在资料里找到出处"。
  - 小节：precision 逐条裁决 + 平均精度(MAP)；recall 把 `reference` 按句归因；（若源码可见）`Ensember` 多次投票提稳。
  - 💡 设计亮点：平均精度复用排序检索经典指标；如有 `Ensember` 多数表决则讲"多次采样对抗 LLM 随机性"。
  - ✅ 要点：precision 看排序、recall 看覆盖。
  - 测验点：precision 为什么要算"平均精度"而非简单比例？recall 如何按句归因？

- [ ] **Step 5: 第 17 课「Relevancy / Factual / AspectCritic 内部」(`17-answer-metrics-internals.html`)**
  - 锚点（规范，写前在源码确认实际字段/算法）：`metrics/collections/answer_relevancy/`（反向生成问题 + cosine + `noncommittal`；确认默认 strictness 值）、`metrics/collections/factual_correctness/`（claim 分解 + 双向 NLI、`mode∈{precision,recall,f1}`+`beta`+`fbeta_score`）；**AspectCritic 未迁移到 collections**，用旧版 `metrics/_aspect_critic.py`（`AspectCritic`、自然语言 `definition`、`SingleTurn`/`MultiTurnAspectCriticPrompt`、`AspectCriticOutput`(verdict)、`ensembler`）并点明"该指标仍是经典栈"。
  - 类比：relevancy 反向出题（从答案倒推问题再比相似度）；factual 双向对照；aspect critic 用一句话定义裁判。
  - 小节：relevancy = 反向生成若干问题 + cosine + `noncommittal` 惩罚；factual = 双向 NLI → TP/FP/FN → `fbeta_score`；aspect critic = 自然语言 `definition` 的 0/1 裁判。
  - 💡 设计亮点：ResponseRelevancy 的"**反向生成问题**"巧思；FactualCorrectness 用**双向 NLI** 统一 precision/recall/f1；AspectCritic 让你"**一句话造一个指标**"。
  - ✅ 要点：三种思路各有巧妙；体会"把主观判断算法化"。
  - 测验点：relevancy 为什么要反向生成问题？factual 的 TP/FP/FN 怎么来的？

- [ ] **Step 6: 第 18 课「Agent / 多轮指标内部」(`18-agent-metrics-internals.html`)**
  - 锚点（规范）：`metrics/collections/tool_call_accuracy/`、`tool_call_f1/`、`agent_goal_accuracy/`（`AgentGoalAccuracy`/`WithReference`/`WithoutReference`）、`topic_adherence/`；旧版镜像 `_tool_call_accuracy.py`/`_tool_call_f1.py`/`_goal_accuracy.py`/`_topic_adherence.py`；数据基础见 `dataset_schema.py` 的 `MultiTurnSample`（呼应第 5 课）。
  - 类比：评 Agent 像评"实习生干活"——工具用对没(tool call)、最终目标达成没(goal)、有没有跑题(topic)。
  - 小节：`ToolCallAccuracy`（对比 `reference_tool_calls`）；`ToolCallF1`；`AgentGoalAccuracy`（有/无 reference）；`TopicAdherence`；均吃多轮消息。
  - 💡 设计亮点：把"Agent 好不好"拆成**工具 / 目标 / 话题**多个可测维度；复用多轮消息结构。
  - ✅ 要点：Agent 评测靠多轮样本 + 多维度指标。
  - 测验点：评 Agent 用单轮还是多轮样本？三个维度各测什么？

- [ ] **Step 7: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 4 lessons 13-18 (metrics internals)"
```

---

### Task 9: 第五部分 · 第 19–24 课（引擎与基础设施）

**Files:** Modify `src/part5.py`（`LESSON_19`…`LESSON_24`）。按模板写，写前读锚点。

- [ ] **Step 1: 第 19 课「Prompt 系统：PydanticPrompt」(`19-prompt-system.html`)**
  - 锚点：`prompt/pydantic_prompt.py`（`PydanticPrompt`、`input_model`/`output_model`/`instruction`/`examples`、`to_string`、`_generate_output_signature`、`generate`/`generate_multiple`、`RagasOutputParser`、`FixOutputFormat`、`process_input`/`process_output`、`adapt`）、`prompt/mixin.py`（`PromptMixin`）、`prompt/base.py`（`BasePrompt`/`StringPrompt`/`StringIO`/`BoolIO`）。**另**：现代 collections 指标用更轻量的 `prompt/metrics/base_prompt.py`（`BasePrompt[InputModel, OutputModel]`，`to_string` + instructor `agenerate(prompt_str, OutputModel)`）——读一下做对比。
  - 类比：给 LLM 一张"带标准答题格式的考卷"，并附带"答错格式就退回重填"。
  - 小节：`PydanticPrompt` 如何把 instruction + JSON-schema 输出签名 + few-shot + input 拼成 prompt；`generate` → LLM → `RagasOutputParser` 解析校验进 `OutputModel`；`FixOutputFormat` 自我修复（JSON 坏了重试）；`PromptMixin` 让经典指标的 prompt 可发现/可覆盖/可翻译；**对比**现代 `prompt/metrics/base_prompt.py` 的 `BasePrompt`（collections 指标用它 + instructor 直接产结构化输出，更薄）。
  - 💡 设计亮点：输出签名来自 `output_model.model_json_schema()`（强约束）；解析失败用 **`FixOutputFormat` 自动修复**（健壮）；`PromptMixin` 把 prompt 变成一等公民（可 get/set/save/load/adapt）；现代栈把"解析/修复"交给 instructor，prompt 更薄。
  - ✅ 要点：经典指标站在 `PydanticPrompt`（自带解析+修复），现代 collections 站在 `prompt/metrics/base_prompt.py` 的 `BasePrompt`（靠 instructor）；都在做"约束输出"。
  - 测验点：`PydanticPrompt` 输出签名怎么来的？JSON 解析失败时发生什么？现代 `BasePrompt` 把解析交给了谁？

- [ ] **Step 2: 第 20 课「Prompt 进阶：few-shot 与翻译」(`20-prompt-advanced.html`)**
  - 锚点：`prompt/few_shot_pydantic_prompt.py`（`FewShotPydanticPrompt`、`ExampleStore`/`InMemoryExampleStore`）、`prompt/dynamic_few_shot.py`（`DynamicFewShotPrompt`、`SimpleInMemoryExampleStore` 基于 embedding）、`prompt/simple_prompt.py`（`Prompt`：`format`/`add_example`）、`pydantic_prompt.py` 的 `adapt`（`TranslateStatements`）、`multi_modal_prompt.py`（`ImageTextPrompt`）。
  - 类比：给考生"看几道例题"(few-shot)，还能"把考卷翻译成另一种语言"(adapt)。
  - 小节：静态 few-shot vs 动态（按相似度选例子）；example store；`adapt()` 多语言翻译；新栈用的轻量 `Prompt`。
  - 💡 设计亮点：**动态 few-shot 用 embedding 选最相关示例**；`adapt` 让 prompt 跨语言迁移而不重写。
  - ✅ 要点：例子能动态选、prompt 能翻译；都为复用与质量服务。
  - 测验点：动态 few-shot 靠什么挑示例？`adapt` 解决了什么痛点？

- [ ] **Step 3: 第 21 课「LLM 抽象」(`21-llm-abstraction.html`)**
  - 锚点：`llms/base.py`（`BaseRagasLLM`、`LangchainLLMWrapper`、`InstructorBaseRagasLLM`、`InstructorLLM`、`_map_openai_params`/`_map_google_params`、`DeprecationHelper`）、`llms/__init__.py`（`llm_factory`）、`llms/adapters/`。
  - 类比："万能转接头"——底下插 OpenAI/Google/本地，上面统一插口；现代版还自带"结构化输出"。
  - 小节：经典 langchain wrapper vs 现代 `instructor` 路径；`llm_factory(model, provider, client, adapter="auto")` 自动选适配器（Google→LiteLLM，否则 Instructor）；为何用 instructor。
  - 💡 设计亮点：**instructor 让 LLM 直接吐 pydantic 对象**（免手写解析）；`llm_factory` 自动选适配器隐藏差异；旧 wrapper 用 `DeprecationHelper` 平滑迁移。
  - ✅ 要点：优先 `llm_factory`；理解新旧两条路径。
  - 测验点：`adapter="auto"` 如何决定用哪个适配器？instructor 相比手写解析省了什么？

- [ ] **Step 4: 第 22 课「Embedding 抽象」(`22-embedding-abstraction.html`)**
  - 锚点：`embeddings/base.py`（`BaseRagasEmbeddings` 旧 / `BaseRagasEmbedding` 新：`embed_text`/`aembed_text`、providers `OpenAI`/`Google`/`HuggingFace`/`LiteLLM`、`embedding_factory`/`modern_embedding_factory`、`_infer_embedding_provider_from_llm`、`validate_texts`/`batch_texts`/`get_optimal_batch_size`）。
  - 类比：把文本变成向量的"翻译机"，新旧两套插口。
  - 小节：新旧接口；provider；批处理工具（最优 batch size）；`evaluate` 如何按所选 LLM 推断 embedding provider。
  - 💡 设计亮点：`_infer_embedding_provider_from_llm` 让用户少配一次；批处理工具优化吞吐。
  - ✅ 要点：embedding 也有新旧栈；相似度类指标依赖它。
  - 测验点：哪些指标需要 embedding？provider 能怎样自动推断？

- [ ] **Step 5: 第 23 课「执行引擎 Executor」(`23-executor.html`)**
  - 锚点：`executor.py`（`Executor`、`submit`、`wrap_callable_with_index`、`_process_jobs`、`results`/`aresults`、`cancel`/`_cancel_event`、`run_async_batch`）、`run_config.py`（`RunConfig`：`timeout=180`/`max_retries=10`/`max_wait=60`/`max_workers=16`/`seed=42`、`add_retry`/`add_async_retry`(tenacity)）。
  - 类比："阅卷调度中心"——多人并发、谁卡住超时跳过、出错记零分不拖累整体、还能中途叫停。
  - 小节：索引保序并发；失败 → `np.nan`（`wrap_callable_with_index`）；`RunConfig` 控并发/超时/重试(tenacity)；`cancel`。
  - 💡 设计亮点：**包装时捕获索引 → 结果可按原序重排**；**单任务失败转 `nan` 不拖垮整轮**（鲁棒）；`RunConfig` 把并发/重试/超时收敛成一个配置对象。
  - ✅ 要点：评测的并发与容错都在这；`RunConfig` 是总开关。
  - 测验点：为什么要 `wrap_callable_with_index`？某个 (sample,metric) 抛异常会怎样？

- [ ] **Step 6: 第 24 课「Callbacks · 成本 · 缓存」(`24-callbacks-cost-cache.html`)**
  - 锚点：`callbacks.py`（`new_group`、`ChainType`、`ChainRun`、`RagasTracer`、`parse_run_traces`）、`cost.py`（`TokenUsage`、`CostCallbackHandler`、`get_token_usage_for_openai`/`anthropic`/`bedrock`）、`cache.py`（`CacheInterface`、`DiskCacheBackend`、`cacher`、缓存键哈希）。
  - 类比：追踪=行车记录仪；成本=油表；缓存=记住走过的路别重跑。
  - 小节：`new_group`/`RagasTracer` 把一次评测组织成 run 树；`CostCallbackHandler` 统计 token/成本（各厂商解析）；`cacher` 装饰器 + `DiskCacheBackend` 缓存 LLM/embedding 调用。
  - 💡 设计亮点：回调把**可观测性做成可挂载层**；缓存用**内容哈希做 key** 复用结果省钱；成本对各厂商统一抽象。
  - ✅ 要点：可观测、可算钱、可缓存——工程化三件套。
  - 测验点：缓存键怎么算？成本统计如何兼容多厂商？

- [ ] **Step 7: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 5 lessons 19-24 (engine & infrastructure)"
```

---

### Task 10: 第六部分 · 第 25–30 课（测试集生成）

**Files:** Modify `src/part6.py`（`LESSON_25`…`LESSON_30`）。按模板写，写前读 `testset/` 锚点。

- [ ] **Step 1: 第 25 课「为什么自动造测试集」(`25-testgen-overview.html`)**
  - 锚点：`testset/synthesizers/generate.py`（`TestsetGenerator.generate` 端到端）、`docs/concepts/test_data_generation/`。
  - 类比：与其人肉出几道题，不如让机器读完资料"自动出一套覆盖全面的卷子"。
  - 小节：手写测试集的痛（少/偏/慢）；端到端管道总览（docs → KG → personas → scenarios → samples → `Testset`）；一张流程图。
  - 💡 设计亮点：把"造测试集"也做成**可复现流水线**；从你的真实文档生成 → 贴近生产分布。
  - ✅ 要点：建立测试生成的整体心智图；这是 ragas 第二大支柱。
  - 测验点：自动测试集解决了手写的哪些问题？管道有哪几步？

- [ ] **Step 2: 第 26 课「知识图谱」(`26-knowledge-graph.html`)**
  - 锚点：`testset/graph.py`（`NodeType`(DOCUMENT/CHUNK)、`Node`(properties)、`Relationship`(bidirectional)、`KnowledgeGraph`(`add`/`save`/`load`)、`find_indirect_clusters`/`find_n_indirect_clusters`/`find_two_nodes_single_rel`）、`graph_queries.py`。
  - 类比：把文档拆成节点、节点间连边，组成一张"知识地图"。
  - 小节：`Node`/`Relationship`/`NodeType`；`KnowledgeGraph` 存取；多跳簇查询（为 multi-hop 出题做准备）。
  - 💡 设计亮点：用**图结构承载文档关系** → 支持单跳/多跳问题生成；簇查询找"能跨多个节点出题"的组合。
  - ✅ 要点：KG 是测试生成的中枢数据结构。
  - 测验点：为什么测试生成要先建图？簇查询为多跳出题准备了什么？

- [ ] **Step 3: 第 27 课「Transforms」(`27-transforms.html`)**
  - 锚点：`testset/transforms/base.py`（`BaseGraphTransformation`、`Extractor`、`LLMBasedExtractor`、`Splitter`、`RelationshipBuilder`、`NodeFilter`）、`engine.py`（`Parallel`、`apply_transforms`、`rollback_transforms`）、`extractors/`（`Summary`/`Keyphrases`/`Title`/`Headlines`/`NER`/`Themes`/`TopicDescription`、`EmbeddingExtractor`、regex `emails`/`links`/`markdown_headings`）、`splitters/`（`HeadlineSplitter`）、`relationship_builders/`（`CosineSimilarity`/`Jaccard`/`OverlapScore`）、`default.py`（`default_transforms`）。
  - 类比：一条"文档加工流水线"——切块、抽摘要/关键词/实体、按相似度连边。
  - 小节：四类 transform（extractor/splitter/relationship builder/filter）；`Parallel` 分组；`default_transforms` 标准管道。
  - 💡 设计亮点：transform **可组合 + `Parallel` 并行 + 可 rollback**；默认管道开箱即用又可定制。
  - ✅ 要点：图是被 transforms 一步步"加工"出来的。
  - 测验点：`Parallel` 有什么用？默认管道大致做了哪几类加工？

- [ ] **Step 4: 第 28 课「Persona 与 Scenario」(`28-persona-scenario.html`)**
  - 锚点：`testset/persona.py`（`Persona`(name/role_description)、`PersonaGenerationPrompt`、`generate_personas_from_kg`）、`synthesizers/base.py`（`BaseScenario`(nodes/style/length/persona)、`QueryLength`、`QueryStyle`、`BaseSynthesizer`）。
  - 类比：先设定几个"虚拟提问者"(persona)，再决定"用什么风格/长度问"(scenario)。
  - 小节：persona 从 KG 自动生成；scenario = nodes + style + length + persona；组合产生多样问题。
  - 💡 设计亮点：**persona × style × length 的组合**让测试集多样性可控；从 KG 自动产 persona 贴合内容。
  - ✅ 要点：多样性 = persona + 风格 + 长度的笛卡尔组合。
  - 测验点：persona 从哪来？scenario 由哪几个要素构成？

- [ ] **Step 5: 第 29 课「Synthesizers」(`29-synthesizers.html`)**
  - 锚点：`synthesizers/single_hop/`（`SingleHopScenario`、`SingleHopQuerySynthesizer` → `SingleHopSpecificQuerySynthesizer`、`_extract_themes_from_items`、`get_node_clusters`）、`multi_hop/`（`MultiHopScenario`、`MultiHopQuerySynthesizer` → `Abstract`/`Specific`）、`synthesizers/__init__.py`（`default_query_distribution`）。
  - 类比：出题机——单跳题(一个节点)和多跳题(跨节点推理)两种出题官，按比例分配。
  - 小节：single-hop vs multi-hop(abstract/specific)；`generate_scenarios` → `generate_sample` 两步；`default_query_distribution` 按概率配比 + 过滤无效簇。
  - 💡 设计亮点：出题分"**场景生成**"和"**样本生成**"两步（解耦）；`default_query_distribution` 自动按图能力配题型。
  - ✅ 要点：题型由 synthesizer 决定；配比可控。
  - 测验点：单跳与多跳的区别？两步生成各产出什么？

- [ ] **Step 6: 第 30 课「TestsetGenerator 端到端」(`30-testset-generator.html`)**
  - 锚点：`synthesizers/generate.py`（`TestsetGenerator`、`from_langchain`/`from_llama_index`、`generate_with_langchain_docs`、`generate`、`num_personas`、`calculate_split_values`、`Executor`、`new_group` 的 "Scenario Generation"/"Sample Generation"）、`testset_schema.py`（`TestsetSample`、`Testset`、`to_evaluation_dataset`、`from_annotated`）。
  - 类比：把前面所有零件串起来——投入文档，产出一套可直接评测的测试集。
  - 小节：`generate_with_langchain_docs`/`generate` 全流程（transforms → KG → personas → 分配 → 并发出题 → `Testset`）；`Testset.to_evaluation_dataset()` 接回评测线。
  - 💡 设计亮点：端到端用 `Executor` 并发 + `new_group` 分阶段追踪；**`Testset` → `EvaluationDataset` 无缝衔接两条主线**。
  - ✅ 要点：一行 `generate_with_langchain_docs` 背后是整条流水线；产物可直接评测。
  - 测验点：`to_evaluation_dataset` 把测试生成线接到了哪？端到端分哪两个追踪阶段？

- [ ] **Step 7: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 6 lessons 25-30 (test data generation)"
```

---

### Task 11: 第七部分 · 第 31–37 课（实验、优化与工程化）

**Files:** Modify `src/part7.py`（`LESSON_31`…`LESSON_37`）。按模板写，写前读锚点。

- [ ] **Step 1: 第 31 课「实验系统深入」(`31-experiments-deep.html`)**
  - 锚点：`experiment.py`（`Experiment(DataTable)`、`experiment` 装饰器、`ExperimentWrapper.__call__`/`arun`、`version_experiment`）。
  - 类比：实验台——每次改动跑一轮、自动命名、自动存档、可 git 版本化对比。
  - 小节：`Experiment` 是存储型表；`@experiment` 全流程（`__call__` 跑一行、`arun` 并发跑全 dataset + 存盘）；命名 + backend fallback；`version_experiment`(GitPython)。
  - 💡 设计亮点：**结果落 backend + git 版本化** → 真正的"评测闭环"；`arun` 用 `asyncio.as_completed` 并发。
  - ✅ 要点：实验 = 跑一轮 + 存档 + 可对比；承接第 8 课。
  - 测验点：`version_experiment` 解决了什么？`arun` 与 `__call__` 分工？

- [ ] **Step 2: 第 32 课「Backends 可插拔」(`32-backends.html`)**
  - 锚点：`backends/base.py`（`BaseBackend`：`load_dataset`/`save_dataset`/`load_experiment`/`save_experiment`/`list_*`）、`local_csv.py`/`local_jsonl.py`/`inmemory.py`/`gdrive_backend.py`、`registry.py`（`BackendRegistry`、`get_registry`、`register_backend`、`print_available_backends`）、`pyproject.toml` 的 `[project.entry-points."ragas.backends"]`。
  - 类比：存储插槽——csv/jsonl/内存/网盘随意换，靠"注册表 + 字符串名"选。
  - 小节：`BaseBackend` 接口；四种内置 backend；`get_registry` + 字符串 `"local/csv"`；entry-points 注册第三方 backend。
  - 💡 设计亮点：**entry-points 让第三方 backend 即插即用**（无需改 ragas）；统一 load/save 接口屏蔽存储差异。
  - ✅ 要点：存储是可插拔的；记住注册机制。
  - 测验点：`"local/csv"` 字符串如何变成一个 backend？怎样加一个自定义 backend？

- [ ] **Step 3: 第 33 课「指标优化与训练」(`33-optimization-training.html`)**
  - 锚点：`metrics/base.py`（`MetricWithLLM.train`、`_optimize_instruction`/`_optimize_demonstration`；`SimpleLLMMetric.align_and_validate`/`get_correlation`）、`optimizers/`（`Optimizer`、`GeneticOptimizer`、`DSPyOptimizer`）、`losses.py`（`Loss`、`MSELoss`、`BinaryMetricLoss`）、`config.py`（`InstructionConfig`/`DemonstrationConfig`）、`dataset_schema.py`（`MetricAnnotation`、`SingleMetricAnnotation`）。
  - 类比：给指标"上课培训"——用标注数据让 LLM 裁判更准（调指令 + 选示例）。
  - 小节：为什么训练指标（对齐人类标注）；`MetricWithLLM.train`（从 `MetricAnnotation` 学，优化指令 + few-shot）；`GeneticOptimizer`/DSPy；Simple 栈的 `align_and_validate`/`get_correlation`。
  - 💡 设计亮点：把"**prompt 工程变成可优化问题**"（遗传/DSPy）；用**与人类标注的相关性**(`get_correlation`)衡量指标好坏。
  - ✅ 要点：指标不仅能用，还能被"训练"到更准。
  - 测验点：训练指标优化的是什么（指令/示例）？怎么判断指标变好了？

- [ ] **Step 4: 第 34 课「集成①：框架」(`34-integrations-frameworks.html`)**
  - 锚点：`integrations/langchain.py`、`llama_index.py`、`langgraph.py`、`swarm.py`、`griptape.py`、`amazon_bedrock.py`、`r2r.py`、`integrations/__init__.py`（lazy import）。
  - 类比：各种"适配插头"——把别的框架的对象接进 ragas 评测/测试生成。
  - 小节：主要框架集成各一句；`TestsetGenerator.from_langchain`/`from_llama_index`；lazy import 容忍可选依赖。
  - 💡 设计亮点：集成模块 **lazy import**（缺依赖不炸整包）；与主流框架双向打通。
  - ✅ 要点：ragas 不孤立，能接进现有技术栈。
  - 测验点：为什么集成要 lazy import？测试生成怎么吃 LangChain 文档？
  - 注意：本课会合法提到 "LangChain"/"LlamaIndex" 等裸词（不是 stale）。

- [ ] **Step 5: 第 35 课「集成②：观测」(`35-integrations-observability.html`)**
  - 锚点：`integrations/tracing/`（Langfuse、MLflow、`observe`、`LangfuseTrace`、`MLflowTrace`）、`langsmith.py`、`helicone.py`（`helicone_config`，被 `evaluation.py` 引用）、`opik.py`、`ag_ui.py`。
  - 类比：把评测过程接到"监控大盘"，可视化、可回溯。
  - 小节：各观测平台集成一句；`observe` 追踪；`helicone_config` 在评测里的作用。
  - 💡 设计亮点：评测可上报多家观测平台 → **生产级可视化与回溯**。
  - ✅ 要点：评测结果能进监控体系，闭环到生产。
  - 测验点：观测集成给评测带来什么？`observe` 大致做什么？

- [ ] **Step 6: 第 36 课「读源码 · 调试 · 测试 · 贡献」(`36-source-debug-contribute.html`)**
  - 锚点：`Makefile`（`install-minimal`/`install`/`format`/`type`/`test`/`run-ci`）、`pyproject.toml`（uv workspace、ruff、pyright、pytest、`requires-python>=3.9`）、`tests/conftest.py`（`fake_llm`/`fake_embedding`/`mock_llm`）、`tests/unit/`、`tests/benchmarks/`、`CONTRIBUTING.md`。
  - 类比：给想下场改 ragas 的人的"工地安全须知 + 工具说明书"。
  - 小节：用 `uv` 管环境（`make install-minimal`）；`make format`/`type`/`test`；`fake_llm` fixtures 如何免真调 LLM 测指标；benchmarks；贡献流程。
  - 💡 设计亮点：**`fake_llm`/`fake_embedding` 让指标测试确定、零成本**；`Makefile` 把 CI 一键化；uv workspace 管多包。
  - ✅ 要点：上手开发就用这套工具链。
  - 测验点：为什么测试要用 fake LLM？`make install-minimal` 与 `make install` 区别？

- [ ] **Step 7: 第 37 课「CLI」(`37-cli.html`)**
  - 锚点：`cli.py`（`app = typer.Typer`、`ragas evals`/`quickstart`/`hello_world`、`create_numerical_metrics_table`/`display_metrics_tables`）、`pyproject.toml` `[project.scripts]`（`ragas = "ragas.cli:app"`）、`sdk.py`（当前为空占位）。
  - 类比：命令行遥控器——不写代码也能跑评测 / 拉模板。
  - 小节：`ragas quickstart`（拉 `rag_eval` 模板）；`ragas evals`（对数据集跑评测文件 + rich 表格）；`ragas hello_world`；`sdk.py` 目前为空。
  - 💡 设计亮点：**typer + rich** 让 CLI 体验好；`quickstart` 模板降低上手门槛。
  - ✅ 要点：CLI 是另一条上手路径。
  - 测验点：`ragas quickstart` 做什么？CLI 入口在 pyproject 哪里声明？

- [ ] **Step 8: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: part 7 lessons 31-37 (experiments, optimization, engineering)"
```

---

### Task 12: 第八部分 · 第 38 课（端到端实战 capstone）

**Files:** Modify `src/part8.py`（`LESSON_38`）。综合全书，串起两条主线。

- [ ] **Step 1: 写第 38 课「端到端实战」(`38-capstone.html`)**
  - 锚点：综合前述课程 + `docs/getstarted/rag_eval.md`、`rag_testset_generation.md`、`evals.md`。
  - 类比：毕业设计——把测试生成 + 指标 + 实验拼成一个完整的 RAG 评测流程。
  - 小节：① 场景设定（评一个 RAG 问答应用）；② 用 `TestsetGenerator.generate_with_langchain_docs` 从文档造测试集（→ 第 30 课）；③ `Testset.to_evaluation_dataset()` 转评测集（→ 第 6/30 课）；④ 选 RAG 四件套指标（→ 第 10 课）；⑤ 用 `@experiment` 跑评测并对比（→ 第 8/31 课）；⑥ 读结果迭代。每一步用 `<a href="NN-….html">第 N 课</a>` 链回对应课。
  - 💡 设计亮点：**两条主线（测试生成 + 评测）通过 `to_evaluation_dataset` 汇流**；`@experiment` 把"改 → 跑 → 比"闭环。
  - ✅ 要点：全书知识在此合流；评测是可持续迭代的工程闭环。结尾加一句"结业"寄语（注意：check_html 对含"全书结业"或"本课要点"的页面放行 key-card 软检查，但仍建议保留 `card key`）。
  - 测验点：两条主线在哪一步汇合？为什么用 experiment 而非一次性 evaluate？

- [ ] **Step 2: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: lesson 38 capstone (end-to-end RAG evaluation)"
```

---

### Task 13: 第 39 课「术语表 · 概念索引」(`glossary.py`)

**Files:** Modify `src/glossary.py`（`LESSON_GLOSSARY`）。
**Reference 格式：** `/home/verden/course/langchain-visual-guide/src/glossary.py`（lead + `card detail` 用法说明 + 多张 `table.t`，每行 `术语 / 一句话 / 见课`）。

- [ ] **Step 1: 按三组写术语表**

结构：`<p class="lead">…</p>` + `<div class="card detail"><div class="tag">🔎 用法</div> Ctrl/⌘+F 搜索，点"见课"跳转，术语分三组 …</div>` + 三个 `<h2>` 分组表。每行格式：

```html
<tr><td class="mono">Faithfulness</td><td>把答案拆成原子陈述、逐句对照检索资料判忠实度</td><td><a href="15-faithfulness-internals.html">第 15 课</a></td></tr>
```

- 组 ①「评测核心」：`Dataset`/`EvaluationDataset`/`SingleTurnSample`/`MultiTurnSample`/`evaluate`/`@experiment`/`Metric`/`MetricResult`/`MetricType`/`Faithfulness`/`ContextPrecision`/`ContextRecall`/`ResponseRelevancy`/`FactualCorrectness`/`AspectCritic`/`DiscreteMetric`/`NumericMetric`/`Ensember` 等 → 链到第 3–18 课对应页。
- 组 ②「测试集生成」：`KnowledgeGraph`/`Node`/`Relationship`/`Transform`/`Extractor`/`Splitter`/`Persona`/`Scenario`/`Synthesizer`/`single-hop`/`multi-hop`/`TestsetGenerator`/`Testset`/`default_query_distribution` 等 → 链到第 25–30 课。
- 组 ③「引擎 · 工程 · 生态」：`PydanticPrompt`/`PromptMixin`/`RagasOutputParser`/`llm_factory`/`instructor`/`embedding_factory`/`Executor`/`RunConfig`/`Backend`/`get_registry`/`Optimizer`/`RagasTracer`/`CostCallbackHandler`/`cacher`/`CLI` 等 → 链到第 19–24、31–37 课。

- [ ] **Step 2: 链接正确性自检（每个 href 必须命中存在的课页）**

写完后构建并跑 `check_links.py`（死链会让它退出 1）。注意所有 `href` 用裸文件名（如 `15-faithfulness-internals.html`），与 `shell.PAGES` 文件名完全一致。

- [ ] **Step 3: 构建 + 校验 + 提交**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: lesson 39 glossary / concept index"
```

---

## 第三阶段 · 测验

### Task 14: 填充 `quizzes.py`（39 课自测题）

**Files:** Modify `src/quizzes.py`（`QUIZZES` 字典）。

**Schema（沿用参考项目，`render` 会确定性打乱选项）：**

```python
"NN-file.html": {
    "mcq": [
        {"q": "题干", "opts": ["选项A", "选项B", "选项C", "选项D"],
         "answer": 1, "why": "解析：为什么是这个答案"},
    ],
    "open": ["发散题 1（无标准答案）"],   # 可选
}
```

> `answer` 是**正确项在 `opts` 中的 0-based 下标**。题目聚焦"**为什么这么设计**"（呼应每课的 💡 设计亮点），用前面各内容任务里标注的"测验点"。行内代码用 `<code>…</code>`，里面用单引号避免转义。

- [ ] **Step 1: 用一个完整范例起步（第 1 课）**

```python
QUIZZES = {
    "01-what-is-ragas.html": {
        "mcq": [
            {"q": "ragas 的核心主张是把对 AI 应用的判断从“vibe check”升级成什么？",
             "opts": ["更快的推理", "可量化、可复现、可迭代的系统化评测闭环",
                      "更便宜的 API", "更大的上下文窗口"],
             "answer": 1,
             "why": "ragas 解决的是“好不好、改完是变好还是变差”这类问题——靠客观指标 + 固定数据集 + 实验闭环，而非主观感受。"},
            {"q": "教程把 ragas 概括为哪三大支柱？",
             "opts": ["训练 / 推理 / 部署", "评测 / 测试生成 / 实验",
                      "前端 / 后端 / 数据库", "采集 / 清洗 / 标注"],
             "answer": 1,
             "why": "评测(metrics+evaluate/experiment)、测试生成(TestsetGenerator)、实验(@experiment)是贯穿全书的骨架。"},
        ],
        "open": ["回想你做过的一个 LLM 应用：哪些“感觉还行”的判断可以换成 ragas 指标？"],
    },
    # … 其余 38 课同结构
}
```

- [ ] **Step 2: 为第 2–39 课各加一条 `QUIZZES` 条目**

每课 2–4 道 mcq（+可选 open），题点取自各内容任务标注的"测验点"。例如：
  - `15-faithfulness-internals.html`：两阶段分别用哪个 Prompt？得分公式？
  - `23-executor.html`：单任务抛异常会怎样（转 `np.nan`）？为何要 `wrap_callable_with_index`？
  - `32-backends.html`：`"local/csv"` 字符串如何解析成 backend？怎么加自定义 backend（entry-points）？

确保每个 key 与 `shell.PAGES` 文件名一致；`opts` 中如含 `<`/`>` 用 `<code>` 包裹或转义。

- [ ] **Step 3: 构建 + 校验（测验注入后 details/summary 仍需平衡）**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build.py && python check_html.py && python check_links.py
```
Expected: 0 ERR（`render` 每题生成一对 `<details>`/`<summary>`，自动平衡）。

- [ ] **Step 4: Commit**

```bash
cd /home/verden/course/ragas-visual-guide && git add -A && git commit -m "content: per-lesson quizzes for all 39 lessons"
```

---

## 第四阶段 · CI、README 与收尾

### Task 15: CI 工作流 + README + LICENSE

**Files:** Create `.github/workflows/deploy.yml`、`.github/workflows/ci.yml`、`README.md`、`LICENSE`。

- [ ] **Step 1: 移植两个工作流**

```bash
cp /home/verden/course/langchain-visual-guide/.github/workflows/deploy.yml \
   /home/verden/course/ragas-visual-guide/.github/workflows/deploy.yml
cp /home/verden/course/langchain-visual-guide/.github/workflows/ci.yml \
   /home/verden/course/ragas-visual-guide/.github/workflows/ci.yml
```

- [ ] **Step 2: 改 `deploy.yml` 的 PDF 名与 artifact 名**

把所有 `langchain-visual-guide.pdf` → `ragas-visual-guide.pdf`（"Render PDF" 步骤的 `--print-to-pdf=` 与 `ls`、"Upload PDF artifact" 的 `path`、"Assemble _site" 的 `cp`、release job 的 `files`）；artifact `name: langchain-visual-guide-pdf` → `ragas-visual-guide-pdf`（upload 与 download 两处）。其余（fonts 安装、setup-chrome、Pages 步骤）保持不变。`ci.yml` 无 langchain 专有串，原样即可。

- [ ] **Step 3: 写 `README.md`（中文 + 徽章）**

参照 `/home/verden/course/langchain-visual-guide/README.md` 结构改写为 ragas 版：标题「Ragas 图解教程 · 从零理解整个项目」；在线阅读 `https://verdenmax.github.io/ragas-visual-guide/`、PDF 链接 `ragas-visual-guide.pdf`；徽章（lessons-39、parts-8、dependencies-none、Python 3、docs 中文）；适用人群；如何阅读（浏览器开 `index.html` 或 `python -m http.server`）；教程结构（8 部分 39 课列表，可精简）；重新生成（`cd src && python build.py` / `python build_print.py`）；本地导出 PDF（headless chromium 命令，产物名 `ragas-visual-guide.pdf`）；CI 说明；首次启用 Pages（Settings→Pages→Source: GitHub Actions）；MIT 许可 + 免责声明（"ragas 为 VibrantLabs 的项目，相关名称与商标归其所有……本教程为独立第三方学习材料，与官方无隶属关系"，链 `https://github.com/vibrantlabsai/ragas`）。

- [ ] **Step 4: 写 `LICENSE`（MIT）**

```bash
cp /home/verden/course/langchain-visual-guide/LICENSE \
   /home/verden/course/ragas-visual-guide/LICENSE
```
确认是 MIT 文本（如含年份/作者占位，按需保留作者署名）。

- [ ] **Step 5: 校验 README 里的内部命令/链接无误（人工）**

确认 README 中提及的课数（39）、部分数（8）、PDF 名（`ragas-visual-guide.pdf`）、Pages URL 与实际一致；不残留 "LangChain 图解教程" 字样。

- [ ] **Step 6: Commit**

```bash
cd /home/verden/course/ragas-visual-guide
git add -A && git commit -m "ci: add deploy + ci workflows; add README and LICENSE"
```

---

### Task 16: 收尾 — 全量构建、校验、PDF 与事实核查

**Files:** 无新增；最终验证与修正。

- [ ] **Step 1: 全量重建 + 校验（必须全绿）**

```bash
cd /home/verden/course/ragas-visual-guide/src
python build.py && python check_html.py && python check_links.py
```
Expected: `check_html.py` → `✓ structural check passed`、`0 error(s)`、`0 warning(s)`（39 课均应已有 analogy + key，故 WARN 也应为 0）；`check_links.py` → `✓ all N internal links resolve`。

- [ ] **Step 2: 无漂移自检（CI 会卡这一点）**

```bash
cd /home/verden/course/ragas-visual-guide
python src/build.py >/dev/null && git diff --exit-code -- index.html lessons/ && echo "no drift ✓"
```
Expected: `no drift ✓`（若有 diff，说明有未提交的构建产物，`git add` 后重试）。

- [ ] **Step 3: 本地生成 PDF 验证（需要 chromium/chrome）**

```bash
cd /home/verden/course/ragas-visual-guide/src && python build_print.py
cd /home/verden/course/ragas-visual-guide
chromium --headless=new --no-pdf-header-footer \
  --print-to-pdf=ragas-visual-guide.pdf \
  --virtual-time-budget=30000 "file://$PWD/print.html" && ls -la ragas-visual-guide.pdf
```
Expected: 生成非空 `ragas-visual-guide.pdf`（被 `.gitignore` 忽略，不提交）。如本机无 chromium，跳过此步（CI 会生成）。

- [ ] **Step 4: 事实核查（对照 spec 第 11 节"关键事实校验清单"逐条确认）**

打开 `/home/verden/course/ragas/src/ragas/...` 逐条核对并修正任何偏差：
  - `evaluate`/`aevaluate` 发 `DeprecationWarning` 指向 `@experiment`（`evaluation.py`）。
  - 默认四指标 `[answer_relevancy, context_precision, faithfulness, context_recall]`（`evaluation.py`）。
  - `RunConfig` 默认值 timeout=180 / max_retries=10 / max_workers=16 / seed=42（`run_config.py`）。
  - 失败转 `np.nan`（`executor.py` 的 `wrap_callable_with_index`）。
  - `DiscreteMetric` 默认 `allowed_values=["pass","fail"]`（`metrics/discrete.py`）。
  - backends 经 `pyproject.toml` entry-points 注册（`[project.entry-points."ragas.backends"]`）。
  - `requires-python >= 3.9`、setuptools + setuptools_scm（`pyproject.toml`）。

  若任一条与课程内容不符，回到对应 `partN.py` 修正、重建、重跑校验。

- [ ] **Step 5: 最终提交（如有修正）**

```bash
cd /home/verden/course/ragas-visual-guide
git add -A && git commit -m "fix: source-grounding corrections after final fact-check" || echo "nothing to fix ✓"
```

- [ ] **Step 6: （可选）推送与启用 Pages**

```bash
cd /home/verden/course/ragas-visual-guide
git remote add origin git@github.com:verdenmax/ragas-visual-guide.git
git push -u origin master
```
随后在 GitHub 仓库 **Settings → Pages → Source** 选 **GitHub Actions**（owner 一次性手动操作；记忆：configure-pages 的 `enablement:true` 无法用默认 token 创建站点，需手动开启一次）。

---

## Self-Review（计划自检）

- **Spec 覆盖**：spec 第 5 节 39 课 → Task 4（第 1 课）/ 5（2–3）/ 6（4–8）/ 7（9–12）/ 8（13–18）/ 9（19–24）/ 10（25–30）/ 11（31–37）/ 12（38）/ 13（39）全覆盖；工具链（shell/build/print/check）→ Task 1–2；测验 → Task 14；术语表 → Task 13；CI/README/LICENSE → Task 15；PDF/事实核查 → Task 16。无遗漏。
- **占位符扫描**：无 "TBD/TODO/稍后补"。各内容任务以"锚点 + 类比 + 小节 + 设计亮点 + 要点 + 测验点"形式给出可执行的写作规格（先读源码后下笔），非空泛占位。
- **类型/命名一致性**：`shell.PAGES` 文件名、`registry.CONTENT` 的 `partN.LESSON_xx` 常量名、各 Task 的 `LESSON_xx` 区间、`quizzes`/`glossary` 的 key 全程一致（01→39）。CSS 类名（`card macro/detail/analogy/key/spark/warn`、`accordion`、`t`）取自参考项目实测。
- **风险**：内容量大 → 已按部分分批、每批构建+校验+提交；事实漂移 → Task 16 设事实核查关卡。

---

## Execution Handoff

计划已保存到 `docs/superpowers/plans/2026-06-11-ragas-visual-guide.md`。两种执行方式：

1. **Subagent-Driven（推荐）** — 每个 Task 派一个全新子代理实现，任务间双重审查（spec 符合 + 代码质量），快速迭代。
2. **Inline Execution** — 在本会话内按 executing-plans 批量执行，设检查点复核。

选哪种？
