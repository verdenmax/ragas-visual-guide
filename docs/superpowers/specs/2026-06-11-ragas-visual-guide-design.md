# Ragas 图解教程（ragas-visual-guide）· 设计文档

- 日期：2026-06-11
- 状态：已批准（待用户复核 spec）
- 参考项目：`/home/verden/course/langchain-visual-guide`（同作者、同形态）
- 目标仓库：`/home/verden/course/ragas-visual-guide`（独立 git 仓库）
- 讲解对象源码：`/home/verden/course/ragas`（`src/ragas/`，导入根 `ragas`）

---

## 1. 目标与定位

做一套面向**完全新手**的可视化（HTML 图解）中文教程，带读者从零理解
[ragas](https://github.com/vibrantlabsai/ragas)（LLM 应用评测工具包）——既有**宏观全景**，
也有**深入真实源码内部**，每课对照 `src/ragas` 真实代码核实。

定位与参考项目**同等深度**：宏观全景 + 用法 + 深入源码内部。**重点强调"设计亮点 / 值得学习的点"**
（用户明确要求"探索亮点、值得学习的点、重点"）。

### 适用人群
- 完全没接触过 ragas、想从零入门的新手
- 想先建立宏观认知、再深入内部源码的学习者
- 准备阅读 / 调试 / 贡献 ragas 源码的开发者

### 成功标准
1. 8 部分 · 约 39 课，全部可用浏览器（含 `file://`）正常打开、互相跳转无死链。
2. 每课源码引用对照 `src/ragas` 真实"文件 + 符号名"，无事实错误。
3. 工具链与参考项目对齐：无依赖 Python 生成器、互动测验、术语表、HTML/链接校验、PDF、CI 自动部署 Pages。
4. `check_html.py` 与 `check_links.py` 全绿；CI 的"无漂移"校验通过。

### 非目标（YAGNI）
- 不做后端服务、不做可编辑/可运行的在线 playground。
- 不引入任何第三方运行时依赖（生成器仅需 Python 3 标准库）。
- 不逐行复制 ragas 源码；只引用"文件 + 符号名"并讲清设计意图。
- 不写死源码行号（会随上游更新失效）。

---

## 2. 仓库与产物结构

```
ragas-visual-guide/
├── index.html              ← 入口（目录页），由 build.py 生成
├── lessons/                ← 约 39 课图解页面，由 build.py 生成
│   ├── 01-what-is-ragas.html
│   └── … 39-glossary.html
├── src/                    ← 无依赖 Python 生成器（可重建全部 HTML / PDF）
│   ├── shell.py            共享外壳：CSS 设计系统 + 顶部进度条 + 导航 + index 目录页 + PAGES/PARTS
│   ├── part1.py … part8.py 各部分课程内容（HTML 字符串常量）
│   ├── registry.py         文件名 → 课程内容 的单一映射（与 shell.PAGES 对齐）
│   ├── quizzes.py          每课互动测验（无依赖，纯 HTML/JS）
│   ├── glossary.py         术语表 · 概念索引
│   ├── build.py            站点构建（→ index.html + lessons/）
│   ├── build_print.py      PDF 构建（→ print.html，折叠全展开、自动分页）
│   ├── check_html.py       HTML 结构自检
│   └── check_links.py      内部链接死链校验
├── .github/workflows/
│   ├── deploy.yml          CI：重建站点 + 无头 Chrome 生成 PDF + 部署 Pages + tag 发 Release
│   └── ci.yml              CI：校验 HTML 与 src 无漂移 + 内部链接无死链
├── .gitignore              （已对齐参考项目：忽略 __pycache__ / *.pdf / print.html / _site 等）
├── README.md               中文说明 + 徽章
└── LICENSE                 MIT
```

提交策略：`index.html` 与 `lessons/` 的**已构建 HTML 一并提交**（CI 校验其与 `src/` 不漂移）；
`*.pdf` / `print.html` 为构建产物，**不提交**（由 CI 生成并部署）。

---

## 3. 生成器架构（数据流）

```
shell.PAGES (有序: 文件名, 短标题, 部分标签)
        │
        ├── registry.CONTENT  (文件名 → partN.LESSON_xx 内容字符串)
        │
build.py:  for each page → shell.page(content + quizzes.render(fname)) → 写 lessons/NN-*.html
           → shell.index_page() → 写 index.html
build_print.py:  拼接全部课程 (折叠全展开) → print.html → 无头浏览器打 PDF
```

- **单一事实源**：课程集合由 `shell.PAGES` 定义，`registry.CONTENT` 负责"文件名 → 内容"映射；
  `build.py` 与 `build_print.py` 都从 `registry` 取内容，保证站点与 PDF 一致。
- **相对链接**：index 链接 `lessons/NN-*.html`；课程页之间用裸文件名互链，返回首页用 `../index.html`。
  整体支持 `file://` 直接打开，也支持任意静态服务器 / GitHub Pages。
- 此架构直接沿用参考项目（已验证可用），仅替换内容、品牌与课程清单。

---

## 4. 视觉设计系统

沿用参考项目的 CSS 设计系统（含**暗色模式自适应** `prefers-color-scheme`）、顶部**进度条**、
sticky 顶栏、卡片/表格/折叠（`<details>`）/代码块等组件。仅做品牌区分：

- **主色**：参考项目为绿色（`#1a7f64`）；本项目改为**靛蓝/紫罗兰**主色（评测/分析气质），
  暗色模式同步给出对应色值。CSS 变量集中在 `:root`，改色为局部改动。
- **favicon / 图标**：用 `📊` 或字母 **R** 的内联 SVG（base64），替换参考项目的 λ。
- **站点名**：`Ragas 图解教程`（用于 `<title>` / OG 元数据）。

### 每页固定元素
- 🌍 **宏观理解** — 大局观，为什么这样设计
- 🔬 **细节 / 源码对应** — 指向真实 `src/ragas/...` 文件 + 符号名
- 🧩 **生活类比** — 用日常事物解释抽象概念
- ✅ **关键要点** — 每课小结
- 💡 **设计亮点 / 值得学习的点** — 该课最精妙的设计思想（**本教程重点**）
- 折叠卡片（示例 / 为什么必要 / ragas 做法 / 其他方案）+ 顶部进度条 + 上一课/下一课导航 + 互动测验

---

## 5. 课程大纲（8 部分 · 39 课）与源码锚点

> 源码引用统一为"文件 + 符号名"，对照当前 `main`，核验日期 2026-06。下列锚点来自对
> `src/ragas` 的源码勘察，用于实现时填充每课的 🔬 源码对应区。

### 第一部分 · 宏观全景
1. **Ragas 是什么** — 从 vibe check 到系统化评测闭环；三大支柱（评测 / 测试生成 / 实验）。锚点：`README.md`、`docs/index.md`。
2. **项目全景** — `src/ragas` 包结构总览。锚点：`ragas/__init__.py`（`__all__` 公开面）、各子包目录。
3. **一次评测的生命周期** — Dataset + metrics → `evaluate/aevaluate` → `Executor` → `EvaluationResult`；并说明"为何官方转向 `@experiment`"。锚点：`ragas/evaluation.py`（`aevaluate`/`evaluate`，含 `DeprecationWarning`）。

### 第二部分 · 数据与入口
4. **数据模型①** — `SingleTurnSample` 字段全解 + `EvaluationDataset`。锚点：`ragas/dataset_schema.py`（`BaseSample`/`SingleTurnSample`/`EvaluationDataset`/`RagasDataset`）。
5. **数据模型②** — `MultiTurnSample` 与 messages（多轮 & Agent 评测的数据基础）。锚点：`ragas/dataset_schema.py`（`MultiTurnSample` 的 `field_validator`/`to_messages`）、`ragas/messages.py`（`HumanMessage`/`AIMessage`/`ToolMessage`/`ToolCall`）。
6. **两个 "Dataset" 之辨**（重点易混淆）— 评测用 `EvaluationDataset` vs 存储型 `Dataset`/`DataTable`。锚点：`ragas/dataset.py`（`DataTable`/`Dataset`、`_resolve_backend`）vs `ragas/dataset_schema.py`（`EvaluationDataset`）。
7. **经典入口** — `evaluate()`/`aevaluate()` 跑通第一个评测 + 结果解读。锚点：`ragas/evaluation.py`、`EvaluationResult`（`to_pandas`/`total_tokens`/`total_cost`）。
8. **现代推荐入口** — `@experiment` 装饰器：为何取代 `evaluate`、怎么用。锚点：`ragas/experiment.py`（`experiment`/`ExperimentWrapper.arun`）。

### 第三部分 · 指标：用法
9. **内置指标全景** — LLM 类 vs 传统类；按 RAG / Agent / 通用 分类。锚点：`ragas/metrics/__init__.py`（导出清单）。
10. **RAG 四件套用法** — Faithfulness / ContextPrecision / ContextRecall / ResponseRelevancy（evaluate 的默认指标）。锚点：`ragas/evaluation.py`（默认 metrics 列表）+ 四个 `metrics/_*.py`。
11. **自定义指标（新 Simple 栈）** — `DiscreteMetric`/`NumericMetric`/`RankingMetric` + `@discrete_metric` 等装饰器（README 快速上手用的就是这套）。锚点：`metrics/discrete.py`/`numeric.py`/`ranking.py`/`decorator.py`。
12. **传统 / 非 LLM 指标** — BLEU / ROUGE / chrF / 字符串距离 / 精确匹配 / SQL 语义等价 / datacompy。锚点：`metrics/_bleu_score.py`/`_rouge_score.py`/`_chrf_score.py`/`_string.py`/`_sql_semantic_equivalence.py`/`_datacompy_score.py`。

### 第四部分 · 指标：源码内部
13. **Metric 基类体系** — 两套栈：经典 `MetricWithLLM` vs 新 `SimpleLLMMetric`；`MetricType`/`MetricOutputType`。锚点：`metrics/base.py`（`Metric`/`MetricWithLLM`/`MetricWithEmbeddings`/`SingleTurnMetric`/`MultiTurnMetric`/`SimpleBaseMetric`/`SimpleLLMMetric`）。
14. 💡 **`MetricResult` 双重身份** — 既是数值又带 reason/traces（pydantic core schema + 运算符重载）。锚点：`metrics/result.py`（`MetricResult.__get_pydantic_core_schema__`/`__float__`）。
15. **指标内部① Faithfulness** — claim 分解 + NLI 两阶段。锚点：`metrics/_faithfulness.py`（`StatementGeneratorPrompt`/`NLIStatementPrompt`/`_compute_score`、`FaithfulnesswithHHEM`）。
16. **指标内部② Context Precision / Recall** — 逐条裁决 + 平均精度 / 归因分类 + `Ensember` 多次投票。锚点：`metrics/_context_precision.py`（`ContextPrecisionPrompt`/`_calculate_average_precision`）、`metrics/_context_recall.py`（`ContextRecallClassificationPrompt`）、`metrics/base.py`（`Ensember`/`ensembler`）。
17. **指标内部③ ResponseRelevancy / FactualCorrectness / AspectCritic** — 反向生成问题、双向 NLI、自然语言自定义裁判。锚点：`metrics/_answer_relevance.py`、`metrics/_factual_correctness.py`（`DecompositionType`/`fbeta_score`）、`metrics/_aspect_critic.py`。
18. **Agent / 多轮指标内部** — ToolCallAccuracy / GoalAccuracy / TopicAdherence。锚点：`metrics/_tool_call_accuracy.py`/`_tool_call_f1.py`/`_goal_accuracy.py`/`_topic_adherence.py`。

### 第五部分 · 引擎与基础设施
19. 💡 **Prompt 系统** — `PydanticPrompt`：JSON-schema 输出签名 + `RagasOutputParser`/`FixOutputFormat` **自我修复** + `PromptMixin` 可发现/可覆盖。锚点：`prompt/pydantic_prompt.py`、`prompt/mixin.py`。
20. **Prompt 进阶** — few-shot（`FewShotPydanticPrompt`/`DynamicFewShotPrompt`/example store）+ `adapt()` 多语言翻译。锚点：`prompt/few_shot_pydantic_prompt.py`/`dynamic_few_shot.py`/`simple_prompt.py`。
21. **LLM 抽象** — 经典 langchain wrapper vs 现代 `instructor`；`llm_factory` 自动选适配器。锚点：`llms/base.py`（`BaseRagasLLM`/`InstructorBaseRagasLLM`/`InstructorLLM`/`LangchainLLMWrapper`）、`llms/__init__.py`（`llm_factory`）、`llms/adapters/`。
22. **Embedding 抽象** — 新旧接口、provider、批处理工具、按 LLM 推断 provider。锚点：`embeddings/base.py`（`BaseRagasEmbedding`/`BaseRagasEmbeddings`/`embedding_factory`/`_infer_embedding_provider_from_llm`）。
23. 💡 **执行引擎** — `Executor`：索引保序并发 + 失败转 `np.nan` 容错 + tenacity 重试 + `RunConfig`。锚点：`executor.py`（`Executor`/`wrap_callable_with_index`）、`run_config.py`（`RunConfig`/`add_retry`）。
24. **Callbacks · 成本 · 缓存** — `RagasTracer`/`new_group`、`CostCallbackHandler`、`cacher`/`DiskCacheBackend`。锚点：`callbacks.py`、`cost.py`、`cache.py`。

### 第六部分 · 测试集生成
25. **为什么自动造测试集** — 全景 + 端到端管道（文档→KG→personas→scenarios→samples→Testset）。锚点：`testset/synthesizers/generate.py`（`TestsetGenerator.generate`）、`docs/concepts/test_data_generation/`。
26. **知识图谱** — `KnowledgeGraph`/`Node`/`Relationship` + 多跳簇查询。锚点：`testset/graph.py`（`NodeType`/`Node`/`Relationship`/`KnowledgeGraph.find_indirect_clusters`）、`testset/graph_queries.py`。
27. **Transforms** — extractors / splitters / relationship builders + `default_transforms` 流水线。锚点：`testset/transforms/base.py`/`engine.py`（`Parallel`/`apply_transforms`）/`extractors/`/`splitters/`/`relationship_builders/`/`default.py`。
28. **Persona 与 Scenario** — `generate_personas_from_kg`、`BaseScenario`、query 风格/长度。锚点：`testset/persona.py`、`testset/synthesizers/base.py`（`BaseScenario`/`QueryLength`/`QueryStyle`/`BaseSynthesizer`）。
29. **Synthesizers** — single-hop / multi-hop（abstract/specific）+ `default_query_distribution`。锚点：`testset/synthesizers/single_hop/`、`multi_hop/`、`synthesizers/__init__.py`（`default_query_distribution`）。
30. **`TestsetGenerator` 端到端** — `from_langchain`/`generate_with_langchain_docs`/`generate`、`Testset.to_evaluation_dataset()`。锚点：`testset/synthesizers/generate.py`、`testset/synthesizers/testset_schema.py`。

### 第七部分 · 实验、优化与工程化
31. **实验系统深入** — `@experiment`/`ExperimentWrapper`/`version_experiment`（git 版本化）。锚点：`experiment.py`。
32. 💡 **Backends** — csv / jsonl / inmemory / gdrive + entry-points **可插拔注册**。锚点：`backends/base.py`（`BaseBackend`）/`registry.py`（`get_registry`/`register_backend`）/具体 backend + `pyproject.toml` 的 `[project.entry-points."ragas.backends"]`。
33. 💡 **指标优化与训练** — `metric.train()`/`MetricAnnotation`/`GeneticOptimizer`/`DSPyOptimizer`/`losses`/对齐。锚点：`metrics/base.py`（`MetricWithLLM.train`、`SimpleLLMMetric.align_and_validate`/`get_correlation`）、`optimizers/`、`losses.py`、`config.py`、`dataset_schema.py`（`MetricAnnotation`）。
34. **集成① 框架** — LangChain / LlamaIndex / LangGraph / 多 Agent（swarm）。锚点：`integrations/langchain.py`/`llama_index.py`/`langgraph.py`/`swarm.py`。
35. **集成② 观测** — Langfuse / MLflow / LangSmith / Helicone / Opik。锚点：`integrations/tracing/`、`integrations/langsmith.py`/`helicone.py`/`opik.py`。
36. **读源码 · 调试 · 测试 · 贡献** — `uv` / `Makefile` / pytest / `fake_llm` fixtures / benchmarks / 贡献规范。锚点：`Makefile`、`tests/conftest.py`、`tests/unit/`、`CONTRIBUTING.md`、`pyproject.toml`。
37. **CLI** — `ragas evals` / `quickstart` / `hello_world`。锚点：`cli.py`（`app = typer.Typer`）、`pyproject.toml` `[project.scripts]`。

### 第八部分 · 实战与速查
38. **端到端实战（capstone）** — 用测试生成 + 指标 + 实验 评测一个 RAG 应用，把全书串起来。锚点：综合前述 + `docs/getstarted/rag_eval.md`/`rag_testset_generation.md`。
39. **术语表 · 概念索引** — 全书术语一句话查 + 点链接跳到对应课。由 `glossary.py` 生成。

> 课程文件名采用 `NN-<slug>.html`（两位序号 + 语义化英文 slug），与 `shell.PAGES` 顺序一致。

---

## 6. 互动测验（quizzes.py）

沿用参考项目形态：每课 2–4 道选择题，纯 HTML/JS（无依赖），点击即时反馈正确/错误 + 解析。
`build.py` 在课程内容尾部 `+ quizzes.render(fname)` 注入。题目以"理解 + 源码认知"为主，
对照真实符号名出题（例如"哪个类负责把响应拆成原子陈述？"→ `StatementGeneratorPrompt`）。

---

## 7. CI / 部署

- `deploy.yml`（push 到默认分支触发）：① 运行 `build.py` + `build_print.py`；② 安装 CJK/emoji 字体后用无头 Chrome 渲染 PDF；③ 部署 `index.html`/`lessons/`/PDF 到 GitHub Pages；④ PDF 作为构建产物上传；打 `v*` tag 时发布 Release 并附 PDF。
- `ci.yml`（push / PR 触发，防回归）：① 重跑 `build.py` 校验提交的 HTML 与 `src/` **无漂移**；② 跑 `check_links.py` 确保内部链接无死链；（可加 `check_html.py`）。
- 首次启用需在 GitHub 仓库 Settings → Pages → Source 选 **GitHub Actions**（owner 一次性手动操作；记忆：configure-pages 无法用默认 token 创建站点，只能部署）。

---

## 8. 源码核实策略

- 引用"**文件 + 符号名**"，不写死行号。
- 每课内容对照 `/home/verden/course/ragas/src/ragas` 真实代码核实；存疑处实际打开源码确认（尤其涉及行为/默认值，如 `evaluate` 默认指标、`RunConfig` 默认值、`ResponseRelevancy` 的 `strictness=3`）。
- 顶部加"版本锚点"：对照当前 `main`，最后核验日期。

---

## 9. 风险与缓解

| 风险 | 缓解 |
|------|------|
| 课程多（39 课），内容易出现事实漂移 | 实现时按部分逐批写 + 逐批对照源码核实；每批跑 `check_links.py`/`check_html.py` |
| 两套指标栈/`evaluate` 废弃等易讲错 | 涉及处直接读 `src/ragas` 源码确认后再下笔 |
| CI 无头 Chrome 中文 PDF 字体缺失 | 照搬参考项目 `deploy.yml` 的字体安装步骤 |
| 站点/HTML 与 `src/` 漂移 | 提交前必跑 `build.py` 重新生成并 `git diff` 校验 |

---

## 10. 里程碑（供 writing-plans 细化）

1. **脚手架**：`shell.py`（设计系统 + PAGES/PARTS + index）+ `build.py`/`build_print.py`/`check_*.py` + 空 `partN.py`/`registry.py`/`quizzes.py`/`glossary.py` 骨架，能构建出空壳站点。
2. **品牌化**：靛蓝/紫主色 + 📊/R favicon + 站点名/OG。
3. **内容**：按第一→第八部分逐批写课程（每批校验源码 + 跑 check）。
4. **测验 + 术语表**：填充 `quizzes.py` 与 `glossary.py`。
5. **CI/部署 + README**：`deploy.yml`/`ci.yml`、中文 README（徽章）、LICENSE。
6. **收尾**：全量构建、`check_html.py`/`check_links.py` 全绿、本地导出 PDF 验证。

---

## 附：关键事实校验清单（实现时逐条确认）
- `evaluate()`/`aevaluate()` 是否发 `DeprecationWarning` 指向 `@experiment`。
- `evaluate` 无 metrics 时的默认指标集合。
- `RunConfig` 默认值（timeout/max_retries/max_workers/seed）。
- 指标失败是否转 `np.nan`（`Executor.wrap_callable_with_index`）。
- `DiscreteMetric` 默认 `allowed_values`（`["pass","fail"]`）。
- backends 通过 `pyproject.toml` entry-points 注册。
- `requires-python`（`>=3.9`）与构建后端（setuptools + setuptools_scm）。
