"""Content for part3 (stub)."""

LESSON_09 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
ragas 内置了几十个指标，但它们正处在<strong>两代并存</strong>的迁移期。本课先给你一张<strong>指标地图</strong>：
讲清两代指标各自<strong>从哪里导入</strong>、谁已被废弃，再按 LLM 类 / 传统类 / Agent 类把常用指标排成一张可检索的总表。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  内置指标就像一份<strong>体检套餐目录</strong>：有"抽血化验"（LLM 当裁判、看语义），也有"量身高体重"（传统算法、确定性测量）。
  你不必每项都做——<strong>按场景（RAG / Agent / 文本相似）挑选</strong>需要的几项，组合成自己的套餐即可。
</div>

<h2>两代指标：从哪里导入</h2>
<p>ragas 的具名指标正在从老模块 <span class="inline">ragas.metrics</span> 搬到新模块 <span class="inline">ragas.metrics.collections</span>。记住一条规矩就够了：</p>
<ul>
  <li><strong>具名指标</strong>（Faithfulness、ContextPrecision、ToolCallAccuracy…）的"正门"是 <span class="mono">ragas.metrics.collections</span>。</li>
  <li><strong>基类与 Simple 栈</strong>（<span class="mono">Metric</span> / <span class="mono">MetricWithLLM</span> / <span class="mono">DiscreteMetric</span> / <span class="mono">NumericMetric</span> / <span class="mono">RankingMetric</span> / <span class="mono">MetricResult</span> 等）仍留在 <span class="mono">ragas.metrics</span>，<strong>未废弃</strong>。</li>
  <li>从 <span class="mono">ragas.metrics</span> 导入<strong>具名指标</strong>会触发 <span class="mono">DeprecationWarning</span>，并在 <strong>v1.0 移除</strong>。</li>
</ul>

<pre class="code"><span class="cm"># ✅ 具名指标：从 collections 导入（现代规范）</span>
<span class="kw">from</span> ragas.metrics.collections <span class="kw">import</span> Faithfulness, ContextPrecision

<span class="cm"># ✅ 基类与 Simple 栈：仍在 ragas.metrics（未废弃）</span>
<span class="kw">from</span> ragas.metrics <span class="kw">import</span> DiscreteMetric, NumericMetric, MetricResult

<span class="cm"># ⚠️ 旧写法：从 ragas.metrics 导入具名指标 → DeprecationWarning，v1.0 移除</span>
<span class="kw">from</span> ragas.metrics <span class="kw">import</span> Faithfulness   <span class="cm"># 触发告警</span></pre>

<h2>LLM 类 vs 传统类（外加：单轮 / 多轮）</h2>
<p>按"要不要请裁判模型"分两大类，是挑指标时最实用的切法：</p>
<ul>
  <li><strong>LLM 类</strong>：拿一个 LLM 当裁判，从语义层面打分（如 Faithfulness）。现代 collections 版只接受<strong>现代 LLM</strong>（<span class="inline">llm_factory</span> 的产物），构造时注入。</li>
  <li><strong>传统类</strong>：用确定性算法直接算（如 BLEU / ROUGE / 字符串距离），<strong>不需要模型</strong>、零 token（<a href="12-traditional-metrics.html">第 12 课</a>）。</li>
</ul>
<p>另有一条正交的分法——<strong>单轮 vs 多轮</strong>：由 <span class="inline">MetricType</span> 区分（<span class="mono">SINGLE_TURN</span> / <span class="mono">MULTI_TURN</span>）。Agent 类指标多是多轮的，吃一整段带工具调用的对话（<a href="18-agent-metrics-internals.html">第 18 课</a>）。</p>

<h2>指标地图：常用内置指标总表</h2>
<table class="t">
  <tr><th>指标</th><th>类型</th><th>一句话用途</th><th>深入课程</th></tr>
  <tr><td class="mono">Faithfulness</td><td>LLM 类</td><td>答案是否全部有检索资料支撑（查幻觉）</td><td><a href="10-rag-metrics.html">第 10 课</a> · <a href="15-faithfulness-internals.html">第 15 课</a></td></tr>
  <tr><td class="mono">ContextPrecision</td><td>LLM 类</td><td>检索到的资料是否相关、且相关的排在前面</td><td><a href="10-rag-metrics.html">第 10 课</a> · <a href="16-context-metrics-internals.html">第 16 课</a></td></tr>
  <tr><td class="mono">ContextRecall</td><td>LLM 类</td><td>该检索到的资料是否都召回了</td><td><a href="10-rag-metrics.html">第 10 课</a> · <a href="16-context-metrics-internals.html">第 16 课</a></td></tr>
  <tr><td class="mono">AnswerRelevancy</td><td>LLM + Embedding</td><td>回答是否切题、不跑偏</td><td><a href="10-rag-metrics.html">第 10 课</a> · <a href="17-answer-metrics-internals.html">第 17 课</a></td></tr>
  <tr><td class="mono">FactualCorrectness</td><td>LLM 类</td><td>回答与标准答案的事实一致度（claim 分解 + F1）</td><td><a href="17-answer-metrics-internals.html">第 17 课</a></td></tr>
  <tr><td class="mono">AspectCritic</td><td>LLM 类</td><td>自定义"是 / 否"断言式评判（如"是否有害"）</td><td><a href="17-answer-metrics-internals.html">第 17 课</a></td></tr>
  <tr><td class="mono">ToolCallAccuracy</td><td>Agent 类</td><td>Agent 的工具调用是否正确</td><td><a href="18-agent-metrics-internals.html">第 18 课</a></td></tr>
  <tr><td class="mono">AgentGoalAccuracy</td><td>Agent 类</td><td>多轮对话是否达成用户目标</td><td><a href="18-agent-metrics-internals.html">第 18 课</a></td></tr>
  <tr><td class="mono">TopicAdherence</td><td>Agent 类</td><td>对话是否守在允许的话题范围内</td><td><a href="18-agent-metrics-internals.html">第 18 课</a></td></tr>
  <tr><td class="mono">BleuScore / RougeScore</td><td>传统类</td><td>n-gram / LCS 文本重叠（翻译、摘要）</td><td><a href="12-traditional-metrics.html">第 12 课</a></td></tr>
  <tr><td class="mono">ExactMatch / StringPresence</td><td>传统类</td><td>字符串精确相等 / 是否包含 / 编辑距离</td><td><a href="12-traditional-metrics.html">第 12 课</a></td></tr>
  <tr><td class="mono">DiscreteMetric / NumericMetric / RankingMetric</td><td>自定义</td><td>自己写离散 / 数值 / 排序评分标准</td><td><a href="11-custom-metrics.html">第 11 课</a></td></tr>
</table>

<p><strong>两个例外要记住</strong>：<span class="inline">AspectCritic</span> 目前<strong>只有</strong> legacy 版（<span class="mono">from ragas.metrics import AspectCritic</span>，会告警），collections 暂未提供；检索类还有<strong>非 LLM 版</strong>（按字符串距离 / ID 比对），同样只在 <span class="mono">ragas.metrics</span>（<a href="12-traditional-metrics.html">第 12 课</a>）。其余具名指标都已在 collections 落地。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> "导入即告警"是怎么实现的 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 模块级 __getattr__ + 废弃名单</div>
      <div class="a"><span class="mono">ragas/metrics/__init__.py</span> 的 <span class="inline">__all__</span> 只列基类与 Simple 栈；具名指标改放进一个 <span class="inline">_DEPRECATED_METRICS</span> 字典，再用模块级 <span class="inline">__getattr__</span> 拦截访问、发出告警后才返回实现：
<pre class="code"><span class="kw">def</span> <span class="fn">__getattr__</span>(name):
    <span class="kw">if</span> name <span class="kw">in</span> _DEPRECATED_METRICS:
        warnings.warn(
            _DEPRECATION_MESSAGE.format(name=name),
            DeprecationWarning, stacklevel=<span class="st">2</span>,
        )
        <span class="kw">return</span> _DEPRECATED_METRICS[name]
    <span class="kw">raise</span> AttributeError(...)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ 告警文案直接告诉你怎么改</div>
      <div class="a">告警模板是："<span class="mono">Importing {name} from 'ragas.metrics' is deprecated and will be removed in v1.0. Please use 'ragas.metrics.collections' instead.</span>"——还附上正确写法 <span class="mono">from ragas.metrics.collections import {name}</span>。照着改导入路径即可，分数口径不变。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  两代指标的"门牌"都在 <span class="mono">src/ragas/metrics/__init__.py</span>：<span class="mono">__all__</span> 只导出基类与 Simple 栈（<span class="mono">Metric</span> / <span class="mono">MetricWithLLM</span> / <span class="mono">DiscreteMetric</span> / <span class="mono">NumericMetric</span> / <span class="mono">RankingMetric</span> / <span class="mono">MetricResult</span> …），具名指标进 <span class="mono">_DEPRECATED_METRICS</span> 字典，由模块级 <span class="mono">__getattr__</span> 拦截并发 <span class="mono">DeprecationWarning</span>（文案 <span class="mono">_DEPRECATION_MESSAGE</span>）。
  现代具名指标的"正门"是 <span class="mono">src/ragas/metrics/collections/__init__.py</span>（其 <span class="mono">__all__</span> 列出 Faithfulness、ContextPrecision、ToolCallAccuracy… ，但<strong>不含</strong> AspectCritic）。单轮 / 多轮之分见 <span class="mono">metrics/base.py</span> 的 <span class="mono">MetricType</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>两代指标但算法一致</strong>：collections 是同一套打分逻辑的"现代封装"，迁移只换导入路径，<strong>分数口径不变</strong>。</li>
    <li><strong>接口统一、可混用组合</strong>：collections 指标都是"构造注入依赖 → <span class="inline">await ascore(**kwargs)</span> 返回 <span class="inline">MetricResult</span>"，不同指标能拼成自己的套餐。</li>
    <li><strong>公开面小而稳</strong>：<span class="inline">__all__</span> 只留基类与 Simple 栈，具名指标集中到 collections，旧路径用 <span class="inline">__getattr__</span> 平滑过渡到 v1.0。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>一张<strong>指标地图</strong>：LLM 类（裁判模型）/ 传统类（确定性算法）/ Agent 类（多轮 + 工具）/ 自定义（Simple 栈）。</li>
    <li><strong>具名指标从 <span class="mono">ragas.metrics.collections</span> 导入</strong>；从 <span class="mono">ragas.metrics</span> 导入它们会告警、v1.0 移除。</li>
    <li>基类与 <span class="mono">DiscreteMetric</span> / <span class="mono">NumericMetric</span> / <span class="mono">RankingMetric</span> 仍留在 <span class="mono">ragas.metrics</span>（未废弃）。</li>
    <li>接下来三课细讲：RAG 四件套（<a href="10-rag-metrics.html">第 10 课</a>）、自定义 Simple 栈（<a href="11-custom-metrics.html">第 11 课</a>）、传统指标（<a href="12-traditional-metrics.html">第 12 课</a>）。</li>
  </ul>
</div>
"""

LESSON_10 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
RAG 应用要同时管好<strong>检索</strong>和<strong>生成</strong>两端。ragas 的 <strong>RAG 四件套</strong>——Faithfulness、ContextPrecision、ContextRecall、AnswerRelevancy——正好各盯一段。
本课讲清每个指标<strong>量什么、需要哪些字段</strong>，并给出现代 collections 的最小组合用法。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  RAG 像一场<strong>开卷考试</strong>：考生（LLM）答题前先翻资料（检索）。四件套分别问四个问题——
  <strong>答案有没有照着资料写</strong>（Faithfulness）、<strong>翻到的资料相不相关</strong>（ContextPrecision）、
  <strong>该翻的资料翻全了没</strong>（ContextRecall）、<strong>有没有答到点子上</strong>（AnswerRelevancy）。
</div>

<h2>四件套：各盯一段</h2>
<p>每个指标只挑自己要的字段（回顾样本字段见 <a href="04-single-turn-sample.html">第 4 课</a>）。注意 <span class="inline">ascore</span> 的<strong>必需字段</strong>各不相同：</p>

<table class="t">
  <tr><th>指标</th><th>量什么</th><th><span class="mono">ascore</span> 必需字段</th></tr>
  <tr><td class="mono">Faithfulness</td><td>生成端：答案是否全部有检索资料支撑（查幻觉）</td><td class="mono">user_input + response + retrieved_contexts</td></tr>
  <tr><td class="mono">ContextPrecision</td><td>检索端：相关资料是否排在前面（平均精度）</td><td class="mono">user_input + reference + retrieved_contexts</td></tr>
  <tr><td class="mono">ContextRecall</td><td>检索端：reference 的内容是否都被检索覆盖</td><td class="mono">user_input + retrieved_contexts + reference</td></tr>
  <tr><td class="mono">AnswerRelevancy</td><td>生成端：回答是否切题（反推问题再比相似度）</td><td class="mono">user_input + response（构造时另需 embeddings）</td></tr>
</table>

<p><span class="inline">ContextPrecision</span> 默认等于 <span class="inline">ContextPrecisionWithReference</span>（拿 <span class="inline">reference</span> 比对）；没有标准答案时改用 <span class="inline">ContextPrecisionWithoutReference</span>（别名 <span class="inline">ContextUtilization</span>，改拿 <span class="inline">response</span> 比对）。
<span class="inline">AnswerRelevancy</span> 要把"从回答反推出来的问题"与原问题算<strong>余弦相似度</strong>，所以构造时必须给 <span class="inline">embeddings</span>。</p>

<h2>最小组合示例</h2>
<pre class="code"><span class="kw">from</span> ragas.metrics.collections <span class="kw">import</span> (
    Faithfulness, ContextPrecision, ContextRecall, AnswerRelevancy,
)
<span class="kw">from</span> ragas.llms <span class="kw">import</span> llm_factory
<span class="kw">from</span> ragas.embeddings.base <span class="kw">import</span> embedding_factory
<span class="kw">from</span> openai <span class="kw">import</span> AsyncOpenAI

client = AsyncOpenAI()                       <span class="cm"># 需要 OPENAI_API_KEY</span>
llm = llm_factory(<span class="st">"gpt-4o-mini"</span>, client=client)
emb = embedding_factory(<span class="st">"openai"</span>, model=<span class="st">"text-embedding-3-small"</span>, client=client)

q   = <span class="st">"谁写了《哈姆雷特》？"</span>
ctx = [<span class="st">"《哈姆雷特》是莎士比亚的剧作。"</span>]
ans = <span class="st">"莎士比亚。"</span>
ref = <span class="st">"威廉·莎士比亚"</span>

faith = Faithfulness(llm=llm)                <span class="cm"># 只需 llm</span>
cprec = ContextPrecision(llm=llm)            <span class="cm"># = ContextPrecisionWithReference</span>
crec  = ContextRecall(llm=llm)
arel  = AnswerRelevancy(llm=llm, embeddings=emb)   <span class="cm"># 另需 embeddings</span>

r_faith = <span class="kw">await</span> faith.ascore(user_input=q, response=ans, retrieved_contexts=ctx)
r_prec  = <span class="kw">await</span> cprec.ascore(user_input=q, reference=ref, retrieved_contexts=ctx)
r_rec   = <span class="kw">await</span> crec.ascore(user_input=q, retrieved_contexts=ctx, reference=ref)
r_rel   = <span class="kw">await</span> arel.ascore(user_input=q, response=ans)
print(r_faith.value, r_prec.value, r_rec.value, r_rel.value)  <span class="cm"># 四个 0~1 分数</span></pre>

<p>四个指标都返回 <span class="inline">MetricResult</span>，取 <span class="inline">.value</span> 拿分数（<a href="14-metric-result.html">第 14 课</a>）。
注意 embedding 工厂从 <span class="mono">ragas.embeddings.base</span> 导入——从 <span class="mono">ragas.embeddings</span> 导 <span class="inline">embedding_factory</span> 已被标记废弃。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 字段不齐会怎样？和 evaluate() 默认指标的关系 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 缺字段立即报错</div>
      <div class="a">每个 <span class="inline">ascore</span> 开头都会校验必需字段，缺了就直接抛 <span class="mono">ValueError</span>（如 <span class="mono">"retrieved_contexts is missing…"</span>）。所以传错字段会<strong>当场暴露</strong>，而不是默默给个错分。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 正是 evaluate() 的默认四件套</div>
      <div class="a"><span class="inline">evaluate()</span> 不传 <span class="inline">metrics</span> 时，默认就是这四个（<a href="07-evaluate.html">第 7 课</a>）——只不过用的是 <strong>legacy 单例</strong>（<span class="mono">answer_relevancy</span> / <span class="mono">context_precision</span> / <span class="mono">faithfulness</span> / <span class="mono">context_recall</span>，定义在 <span class="mono">_answer_relevance.py</span> 等）。本课教的是同一算法的现代 collections 版，推荐自己组合。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  四件套现代实现各在 <span class="mono">src/ragas/metrics/collections/</span> 下的 <span class="mono">&lt;name&gt;/metric.py</span>：
  <span class="mono">faithfulness/metric.py</span>（<span class="mono">Faithfulness.ascore(user_input, response, retrieved_contexts)</span>，先把回答拆成原子陈述、再逐条 NLI 核对，分数 = 被支撑陈述占比）；
  <span class="mono">context_precision/metric.py</span>（<span class="mono">ContextPrecision</span> 即 <span class="mono">ContextPrecisionWithReference</span>，算 average precision）；
  <span class="mono">context_recall/metric.py</span>（<span class="mono">ContextRecall.ascore(user_input, retrieved_contexts, reference)</span>）；
  <span class="mono">answer_relevancy/metric.py</span>（构造需 <span class="mono">llm</span> + <span class="mono">embeddings</span>，<span class="mono">strictness</span> 默认 3）。
  它们都继承 <span class="mono">collections/base.py</span> 的 <span class="mono">BaseMetric</span>，只接受现代 <span class="mono">InstructorBaseRagasLLM</span>（<span class="mono">llm_factory</span> 产物，否则报错）。<span class="mono">evaluate()</span> 的默认四件套见 <span class="mono">evaluation.py</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>两端覆盖</strong>：ContextPrecision / Recall 管"检索质量"，Faithfulness / AnswerRelevancy 管"生成质量"，合起来给 RAG 做体检。</li>
    <li><strong>接口统一</strong>：都是 <span class="inline">await metric.ascore(**kwargs)</span> → <span class="inline">MetricResult</span>，按需取 <span class="inline">.value</span> / <span class="inline">.reason</span>。</li>
    <li><strong>缺字段立即报错</strong>：每个 <span class="inline">ascore</span> 开头校验必需字段，为空就抛 <span class="mono">ValueError</span>，问题早暴露。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>四件套各管一段：Faithfulness（无幻觉）· ContextPrecision（相关靠前）· ContextRecall（召回全）· AnswerRelevancy（切题）。</li>
    <li>记住<strong>必需字段</strong>差异：Faithfulness 要 <span class="mono">retrieved_contexts</span>，ContextRecall 还要 <span class="mono">reference</span>，AnswerRelevancy 另需 <span class="mono">embeddings</span>。</li>
    <li>现代用法：<span class="mono">from ragas.metrics.collections import …</span> → 构造注入 <span class="mono">llm</span> / <span class="mono">embeddings</span> → <span class="mono">await ascore(...)</span>；<span class="mono">evaluate()</span> 不传 metrics 时默认就是这四个（legacy 版）。</li>
  </ul>
</div>
"""

LESSON_11 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
内置指标不够用时，ragas 让你<strong>自己写指标</strong>。最轻量的是 <strong>Simple 栈</strong>：三种指标类（离散 / 数值 / 排序）加三个同名装饰器，
几行就能把"评分标准"变成可调用、可版本化的代码。它们都住在 <span class="inline">ragas.metrics</span>，<strong>不在</strong>废弃之列。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  自定义指标就像给裁判写一份<strong>评分细则</strong>：你规定"只能打这几个等级 / 这个分数区间 / 排出前几名"，再写一句 prompt 让 LLM 照章打分。
  ragas 负责把 LLM 的输出<strong>卡死在你允许的取值</strong>里，不会冒出意料之外的答案。
</div>

<h2>三类指标 + 三装饰器</h2>
<p>按"输出长什么样"分三种，每种都有"类"和"装饰器"两副面孔：</p>

<table class="t">
  <tr><th>类</th><th>装饰器</th><th><span class="mono">allowed_values</span> 默认</th><th>输出</th></tr>
  <tr><td class="mono">DiscreteMetric</td><td class="mono">@discrete_metric</td><td class="mono">["pass", "fail"]</td><td>离散类别（str，限定在 allowed_values）</td></tr>
  <tr><td class="mono">NumericMetric</td><td class="mono">@numeric_metric</td><td class="mono">(0.0, 1.0)</td><td>连续数值（float，限定在区间）</td></tr>
  <tr><td class="mono">RankingMetric</td><td class="mono">@ranking_metric</td><td class="mono">2</td><td>排序列表（List[str]，长度为 allowed_values）</td></tr>
</table>

<p>三者都继承 <span class="inline">SimpleLLMMetric</span>（再上层是 <span class="inline">SimpleBaseMetric</span>）。<strong>类</strong>适合需要复用 / 保存（<span class="inline">load</span>）的指标，<strong>装饰器</strong>适合把一个现成函数快速变成指标。</p>

<h2>类风格：一个 DiscreteMetric</h2>
<pre class="code"><span class="kw">from</span> ragas.metrics <span class="kw">import</span> DiscreteMetric
<span class="kw">from</span> ragas.llms <span class="kw">import</span> llm_factory
<span class="kw">from</span> openai <span class="kw">import</span> OpenAI

llm = llm_factory(<span class="st">"gpt-4o-mini"</span>, client=OpenAI())

metric = DiscreteMetric(
    name=<span class="st">"summary_accuracy"</span>,
    allowed_values=[<span class="st">"accurate"</span>, <span class="st">"inaccurate"</span>],
    prompt=<span class="st">"判断摘要是否准确：\nResponse: {response}"</span>,
)
result = metric.score(llm=llm, response=<span class="st">"……"</span>)
print(result.value, result.reason)  <span class="cm"># 'accurate' / 'inaccurate' + 给分理由</span></pre>

<p>注意 <span class="inline">llm</span> 在<strong>打分时</strong>传入（<span class="inline">score</span> / <span class="inline">ascore</span> 内部 <span class="mono">kwargs.pop("llm")</span>），其余关键字（这里是 <span class="inline">response</span>）用来填 prompt 里的占位符。</p>

<h2>装饰器风格：把函数变成指标</h2>
<pre class="code"><span class="kw">from</span> ragas.metrics <span class="kw">import</span> discrete_metric

<span class="kw">@</span><span class="fn">discrete_metric</span>(name=<span class="st">"sentiment"</span>, allowed_values=[<span class="st">"positive"</span>, <span class="st">"neutral"</span>, <span class="st">"negative"</span>])
<span class="kw">def</span> <span class="fn">sentiment</span>(user_input: str, response: str) -> str:
    <span class="st">'''按关键词判断回答情绪（纯规则，无需 LLM）。'''</span>
    text = response.lower()
    <span class="kw">if</span> <span class="st">"great"</span> <span class="kw">in</span> text <span class="kw">or</span> <span class="st">"good"</span> <span class="kw">in</span> text:
        <span class="kw">return</span> <span class="st">"positive"</span>
    <span class="kw">if</span> <span class="st">"bad"</span> <span class="kw">in</span> text <span class="kw">or</span> <span class="st">"poor"</span> <span class="kw">in</span> text:
        <span class="kw">return</span> <span class="st">"negative"</span>
    <span class="kw">return</span> <span class="st">"neutral"</span>

result = sentiment.score(user_input=<span class="st">"今天如何？"</span>, response=<span class="st">"It was great!"</span>)
print(result.value)  <span class="cm"># "positive"</span></pre>

<p>装饰器会按 <span class="inline">allowed_values</span> 的类型<strong>自动选指标种类</strong>（list → 离散、tuple → 数值、int → 排序）。函数返回的普通值会被自动包成 <span class="inline">MetricResult</span> 并按 allowed_values 校验。
<span class="inline">score()</span> / <span class="inline">ascore()</span> <strong>只接受关键字参数</strong>——传位置参数会抛出一条带纠正提示的 <span class="mono">TypeError</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 怎么把 LLM 输出"卡死"在 allowed_values <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 __post_init__ + Literal + 自动响应模型</div>
      <div class="a"><span class="inline">DiscreteMetric.__post_init__</span> 把 <span class="inline">allowed_values</span> 转成 <span class="inline">Literal[...]</span>，再用 <span class="inline">create_auto_response_model</span> 动态造一个 pydantic 响应模型：
<pre class="code">self._response_model = create_auto_response_model(
    <span class="st">"DiscreteResponseModel"</span>,
    reason=(str, Field(..., description=<span class="st">"Reasoning for the value"</span>)),
    value=(Literal[values], Field(..., description=<span class="st">"The value predicted"</span>)),
)</pre>
        于是 LLM 必须返回 <span class="mono">{reason, value}</span>，且 <span class="mono">value</span> 只能是允许值之一——从源头杜绝"答非所选"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 三种栈的响应模型差异</div>
      <div class="a"><span class="inline">NumericMetric</span> 的 <span class="mono">value</span> 是 <span class="mono">float</span>、<span class="inline">RankingMetric</span> 是 <span class="mono">List[str]</span>；校验分别交给 <span class="mono">DiscreteValidator</span> / <span class="mono">NumericValidator</span> / <span class="mono">RankingValidator</span>（装饰器用 <span class="inline">get_validator_for_allowed_values</span> 按类型自动挑）。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  Simple 栈定义在 <span class="mono">src/ragas/metrics/</span>：<span class="mono">discrete.py</span>（<span class="mono">DiscreteMetric</span>，默认 <span class="mono">allowed_values=["pass", "fail"]</span>）、<span class="mono">numeric.py</span>（<span class="mono">NumericMetric</span>，默认 <span class="mono">(0.0, 1.0)</span>）、<span class="mono">ranking.py</span>（<span class="mono">RankingMetric</span>，默认 <span class="mono">2</span>）；
  三个装饰器在 <span class="mono">decorator.py</span> 的 <span class="mono">create_metric_decorator</span>（<span class="mono">score</span> 强制关键字、按 <span class="mono">allowed_values</span> 类型选 validator）。
  基类 <span class="mono">SimpleLLMMetric</span> / <span class="mono">SimpleBaseMetric</span> 与 <span class="mono">create_auto_response_model</span> 在 <span class="mono">base.py</span>（<span class="mono">score</span> 内 <span class="mono">kwargs.pop("llm")</span> 后用 <span class="mono">self.prompt.format(**kwargs)</span> 调 LLM）。它们都在 <span class="mono">ragas.metrics</span> 的 <span class="mono">__all__</span> 里——<strong>未废弃</strong>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>用 <span class="inline">Literal</span> 强约束输出</strong>：<span class="inline">__post_init__</span> 自动按 allowed_values 生成 pydantic 响应模型，LLM 只能吐出合法取值，省掉解析与兜底。</li>
    <li><strong>类 / 装饰器两种风格</strong>：要复用、保存就用类；把现成函数一键变指标就用装饰器。</li>
    <li><strong>评分标准即代码</strong>：自定义指标能进版本库、随实验一起 <span class="inline">version_experiment</span> 回溯（<a href="08-experiment.html">第 8 课</a>）。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Simple 栈 = 三类（<span class="mono">DiscreteMetric</span> / <span class="mono">NumericMetric</span> / <span class="mono">RankingMetric</span>）+ 三装饰器，都在 <span class="mono">ragas.metrics</span>（未废弃）。</li>
    <li>默认 <span class="inline">allowed_values</span>：离散 <span class="mono">["pass", "fail"]</span>、数值 <span class="mono">(0.0, 1.0)</span>、排序 <span class="mono">2</span>。</li>
    <li><span class="inline">__post_init__</span> 用 <span class="inline">Literal[...]</span> + <span class="inline">create_auto_response_model</span> 把输出卡进 allowed_values；<span class="inline">score()</span> 只收关键字、<span class="inline">llm</span> 在打分时传。</li>
    <li>想深入打分背后的基类与结果对象，看 <span class="mono">Metric</span> 基类（<a href="13-metric-base.html">第 13 课</a>）与 <span class="mono">MetricResult</span>（<a href="14-metric-result.html">第 14 课</a>）。</li>
  </ul>
</div>
"""

LESSON_12 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
不是每个指标都要请 LLM 当裁判。<strong>传统 / 非 LLM 指标</strong>用确定性算法直接"量"——便宜、可复现、零 token，
放进 CI 里反复跑也不心疼。本课讲清它们各量什么、何时该用，以及检索指标的非 LLM 版本。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  LLM 类指标像请<strong>考官</strong>主观评判；传统指标像拿<strong>尺子</strong>量——尺子量出来的数永远一致、不要钱、瞬间出结果。
  能用尺子说清的，就别为它单独请一位考官。
</div>

<h2>何时用传统指标</h2>
<ul>
  <li>有<strong>标准答案</strong>可逐字 / 逐词比对时；</li>
  <li>要<strong>可复现</strong>——跨次、跨人结果一致时；</li>
  <li>要<strong>省成本</strong>——零 token、无 API、毫秒级，特别适合放进 CI 回归。</li>
</ul>
<p>代价是它们<strong>不懂语义</strong>：换种说法但意思相同，分数也可能偏低。所以传统指标常和 LLM 指标<strong>混用</strong>。</p>

<h2>一句话清单</h2>
<table class="t">
  <tr><th>指标</th><th>量什么</th><th>依赖</th><th>必需字段</th></tr>
  <tr><td class="mono">BleuScore</td><td>n-gram 重叠（机器翻译 / 生成）</td><td class="mono">sacrebleu</td><td class="mono">reference + response</td></tr>
  <tr><td class="mono">RougeScore</td><td>n-gram / 最长公共子序列重叠（摘要）</td><td class="mono">rouge_score</td><td class="mono">reference + response</td></tr>
  <tr><td class="mono">CHRFScore</td><td>字符级 n-gram F 值（形态丰富的语言更稳）</td><td class="mono">sacrebleu</td><td class="mono">reference + response</td></tr>
  <tr><td class="mono">ExactMatch</td><td>是否完全相等（1.0 / 0.0）</td><td class="mono">—</td><td class="mono">reference + response</td></tr>
  <tr><td class="mono">StringPresence</td><td>reference 是否作为子串出现在 response 中</td><td class="mono">—</td><td class="mono">reference + response</td></tr>
  <tr><td class="mono">NonLLMStringSimilarity</td><td>编辑距离相似度（Levenshtein / Hamming / Jaro / JaroWinkler）</td><td class="mono">rapidfuzz</td><td class="mono">reference + response</td></tr>
  <tr><td class="mono">DataCompyScore</td><td>两份 CSV 的行 / 列比对（precision / recall / f1）</td><td class="mono">datacompy + pandas</td><td class="mono">reference + response</td></tr>
</table>

<p>这些现代版都在 <span class="inline">ragas.metrics.collections</span>：构造即用、<span class="inline">await ascore(reference=..., response=...)</span>，<strong>无需 llm / embeddings</strong>。
注意类名在 collections 里是 <span class="mono">CHRFScore</span>（legacy 旧名 <span class="mono">ChrfScore</span>）。</p>

<pre class="code"><span class="kw">from</span> ragas.metrics.collections <span class="kw">import</span> BleuScore, ExactMatch, RougeScore

bleu  = BleuScore()
em    = ExactMatch()
rouge = RougeScore(rouge_type=<span class="st">"rougeL"</span>, mode=<span class="st">"fmeasure"</span>)

<span class="cm"># 传统指标无需 llm / embeddings，零 token、毫秒级</span>
r1 = <span class="kw">await</span> bleu.ascore(reference=<span class="st">"巴黎是法国的首都。"</span>, response=<span class="st">"法国的首都是巴黎。"</span>)
r2 = <span class="kw">await</span> em.ascore(reference=<span class="st">"Paris"</span>, response=<span class="st">"Paris"</span>)
print(r1.value, r2.value)  <span class="cm"># 0.xx  1.0</span></pre>

<h2>非 LLM 的检索指标（暂只在 legacy）</h2>
<p>检索质量也有不花钱的算法版，但<strong>目前只在 <span class="inline">ragas.metrics</span></strong>（collections 暂未提供）：</p>

<table class="t">
  <tr><th>指标</th><th>怎么算</th><th>必需字段</th></tr>
  <tr><td class="mono">NonLLMContextPrecisionWithReference<br>NonLLMContextRecall</td><td>用<strong>字符串距离</strong>（默认 Levenshtein）+ 阈值 0.5，比对 retrieved_contexts 与 reference_contexts</td><td class="mono">retrieved_contexts + reference_contexts</td></tr>
  <tr><td class="mono">IDBasedContextPrecision<br>IDBasedContextRecall</td><td>直接按 <strong>ID</strong> 比对（支持 str / int），看检索到的 ID 与参考 ID 的交集</td><td class="mono">retrieved_context_ids + reference_context_ids</td></tr>
</table>

<p>它们是 <a href="16-context-metrics-internals.html">第 16 课</a> LLM 版 ContextPrecision / Recall 的"省钱版"——同一概念、确定性算法实现。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> LLM 版 vs 非 LLM 版，怎么选？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 同一概念常有两个版本</div>
      <div class="a">很多概念都有"考官版"和"尺子版"：SQL 等价判断有 <span class="inline">SQLSemanticEquivalence</span>（<strong>LLM</strong> 判语义等价，构造需 <span class="inline">llm</span>）和确定性的 <span class="inline">DataCompyScore</span>（直接比表格数据）；检索精度有 LLM 版 <span class="inline">ContextPrecision</span> 与非 LLM 版 <span class="inline">NonLLMContextPrecisionWithReference</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 取舍原则</div>
      <div class="a">要"懂语义、容忍换种说法"→ 花钱请 LLM；要"快、稳、可复现、能进 CI"→ 用传统指标。实战常<strong>两者混用</strong>：先用传统指标快速回归初筛，再用 LLM 指标抓语义问题。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  传统指标的现代实现集中在 <span class="mono">src/ragas/metrics/collections/</span>：<span class="mono">_bleu_score.py</span>（<span class="mono">BleuScore</span>，sacrebleu）、<span class="mono">_rouge_score.py</span>（<span class="mono">RougeScore</span>，rouge_score）、<span class="mono">chrf_score/metric.py</span>（<span class="mono">CHRFScore</span>，sacrebleu）、<span class="mono">_string.py</span>（<span class="mono">ExactMatch</span> / <span class="mono">StringPresence</span> / <span class="mono">NonLLMStringSimilarity</span> + <span class="mono">DistanceMeasure</span> 枚举）、<span class="mono">datacompy_score/metric.py</span>（<span class="mono">DataCompyScore</span>，datacompy + pandas）；它们的 <span class="mono">ascore(reference, response)</span> 不碰 llm。
  对照之下，<span class="mono">sql_semantic_equivalence/metric.py</span> 的 <span class="mono">SQLSemanticEquivalence</span> <strong>需要</strong> llm（判语义）。非 LLM / ID 版检索指标在 legacy 的 <span class="mono">_context_precision.py</span> / <span class="mono">_context_recall.py</span>（<span class="mono">NonLLMContext…</span> / <span class="mono">IDBasedContext…</span>，均 <span class="mono">SingleTurnMetric</span>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li>同一概念常<strong>LLM 版 + 非 LLM 版并存</strong>：在"懂语义"与"成本 / 可复现"之间按需取舍。</li>
    <li>传统指标<strong>确定、零 token</strong>：同样输入永远同样输出，特别适合 CI 回归与大批量初筛。</li>
    <li>现代传统指标<strong>构造即用</strong>：不定义 llm / embeddings 字段，<span class="inline">BaseMetric</span> 就跳过模型校验。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>能用尺子（确定性算法）说清的，就别请考官（LLM）：传统指标便宜、可复现、零 token。</li>
    <li>现代版在 <span class="mono">ragas.metrics.collections</span>：<span class="mono">BleuScore</span> / <span class="mono">RougeScore</span> / <span class="mono">CHRFScore</span> / <span class="mono">ExactMatch</span> / <span class="mono">StringPresence</span> / <span class="mono">NonLLMStringSimilarity</span> / <span class="mono">DataCompyScore</span>，<span class="mono">ascore(reference, response)</span> 无需模型。</li>
    <li>检索指标的非 LLM / ID 版<strong>暂只在 <span class="mono">ragas.metrics</span></strong>（legacy）。</li>
    <li>实战<strong>混用</strong>最划算：传统指标快筛 + LLM 指标抓语义（对照 <a href="10-rag-metrics.html">第 10 课</a> / <a href="16-context-metrics-internals.html">第 16 课</a> 的 LLM 版）。</li>
  </ul>
</div>
"""
