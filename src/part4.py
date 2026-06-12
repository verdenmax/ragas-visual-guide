"""Content for part4 — 第四部分 · 指标内部（13-18）."""

LESSON_13 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前面学会了<strong>用</strong>指标（<a href="09-metrics-overview.html">第 9 课</a>～<a href="12-traditional-metrics.html">第 12 课</a>），这一部分换个视角<strong>拆开看内部</strong>。第一课先认族谱：所有指标都从一套<strong>基类</strong>长出来，而 ragas 正处在<strong>两代血脉并存</strong>的迁移期——经典栈与现代栈各有一套基类，算法相同、接口不同。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  指标家族像一棵<strong>族谱树</strong>：祖先 <span class="inline">Metric</span> 定下"每个指标都要有名字、要声明吃哪些字段"的家规；下面分出两支血脉——
  <strong>老一支</strong>讲究"按单轮 / 多轮分工"，<strong>新一支</strong>讲究"组件化 + 结构化输出"。两支干的是同一件事（打分），只是<strong>办事的接口和规矩</strong>不同。认清族谱，后面每个具体指标你都知道它"姓什么、随哪一支"。
</div>

<h2>经典栈：Metric 的三层分工</h2>
<p>老一支以抽象基类 <span class="inline">Metric</span>（一个 <span class="mono">@dataclass</span>）为根，往下按"要不要模型 / 单轮还是多轮"分层，具体指标常<strong>多重继承</strong>把它们拼起来：</p>
<pre class="code"><span class="cm"># 经典栈（legacy）：metrics/base.py</span>
Metric (ABC, @dataclass)              <span class="cm"># 家规：name + required_columns + init()</span>
├─ MetricWithLLM(Metric, PromptMixin) <span class="cm"># 注入 llm（裁判模型）+ PydanticPrompt</span>
├─ MetricWithEmbeddings(Metric)       <span class="cm"># 注入 embeddings</span>
├─ SingleTurnMetric(Metric)           <span class="cm"># single_turn_ascore(sample) -> float</span>
└─ MultiTurnMetric(Metric)            <span class="cm"># multi_turn_ascore(sample) -> float</span>

<span class="cm"># 具体指标 = 多重继承拼装，例如：</span>
<span class="kw">class</span> <span class="fn">Faithfulness</span>(MetricWithLLM, SingleTurnMetric): ...</pre>
<p>关键点：经典栈的调用入口是 <span class="inline">single_turn_ascore(sample)</span> / <span class="inline">multi_turn_ascore(sample)</span>，<strong>吃一个样本对象、返回一个 <span class="mono">float</span></strong>（解释另存）。这一支的具名指标（Faithfulness、ContextPrecision…）都已被标记<strong>废弃</strong>（<a href="09-metrics-overview.html">第 9 课</a>）。</p>

<h2>现代栈：SimpleBaseMetric 与 collections</h2>
<p>新一支以 <span class="inline">SimpleBaseMetric</span> 为根，分两条线：一条给<strong>你自定义</strong>（Simple 栈，<a href="11-custom-metrics.html">第 11 课</a>），一条给<strong>官方具名指标</strong>（collections）：</p>
<pre class="code"><span class="cm"># 现代栈：metrics/base.py + metrics/collections/base.py</span>
SimpleBaseMetric (ABC, @dataclass)        <span class="cm"># 家规：name + allowed_values；ascore() -> MetricResult</span>
├─ SimpleLLMMetric                        <span class="cm"># 自定义用：prompt + _response_model</span>
│   ├─ DiscreteMetric (+ DiscreteValidator)  <span class="cm"># 离散：pass/fail…</span>
│   ├─ NumericMetric  (+ NumericValidator)   <span class="cm"># 数值：0~1</span>
│   └─ RankingMetric  (+ RankingValidator)   <span class="cm"># 排序</span>
└─ collections.BaseMetric(SimpleBaseMetric, NumericValidator)  <span class="cm"># 具名指标的现代基类</span>
    └─ Faithfulness / ContextPrecision / ToolCallAccuracy …</pre>
<p>现代栈统一用 <span class="inline">await metric.ascore(**kwargs)</span>，<strong>吃关键字参数、返回 <span class="inline">MetricResult</span></strong>（值 + 理由，<a href="14-metric-result.html">第 14 课</a>）。而且 collections 的 <span class="inline">BaseMetric</span> 在构造时<strong>只认现代组件</strong>：<span class="inline">_validate_llm()</span> 要求 <span class="inline">InstructorBaseRagasLLM</span>（<span class="mono">llm_factory</span> 的产物，<a href="21-llm-abstraction.html">第 21 课</a>），传错就当场 <span class="mono">ValueError</span>。</p>

<table class="t">
  <tr><th>维度</th><th>经典栈（legacy）</th><th>现代栈（collections / Simple）</th></tr>
  <tr><td><strong>根基类</strong></td><td class="mono">Metric → MetricWithLLM / SingleTurnMetric</td><td class="mono">SimpleBaseMetric → BaseMetric / SimpleLLMMetric</td></tr>
  <tr><td><strong>Prompt</strong></td><td class="mono">PydanticPrompt</td><td class="mono">BasePrompt / Prompt（instructor 结构化输出）</td></tr>
  <tr><td><strong>LLM</strong></td><td>BaseRagasLLM（duck typing 也收 instructor）</td><td>只收 <span class="mono">InstructorBaseRagasLLM</span>，否则报错</td></tr>
  <tr><td><strong>调用接口</strong></td><td class="mono">single_turn_ascore(sample) -> float</td><td class="mono">ascore(**kwargs) -> MetricResult</td></tr>
  <tr><td><strong>位置</strong></td><td class="mono">metrics/_*.py（具名指标已废弃）</td><td class="mono">metrics/collections/&lt;name&gt;/（基类在 base.py）</td></tr>
</table>

<h2>两个横切枚举：MetricType / MetricOutputType</h2>
<p>无论哪一支，都用两个 <span class="inline">Enum</span> 给指标"贴标签"：</p>
<ul>
  <li><span class="inline">MetricType</span>：<span class="mono">SINGLE_TURN</span> / <span class="mono">MULTI_TURN</span>——这条样本是单轮还是多轮（Agent 类多为多轮，<a href="18-agent-metrics-internals.html">第 18 课</a>）。</li>
  <li><span class="inline">MetricOutputType</span>：<span class="mono">BINARY</span> / <span class="mono">DISCRETE</span> / <span class="mono">CONTINUOUS</span> / <span class="mono">RANKING</span>——输出是 0/1、离散类别、连续值还是排序，优化 / 训练时据此选损失函数（<a href="33-optimization-training.html">第 33 课</a>）。</li>
</ul>
<p>另有一个 <span class="inline">ModeMetric</span> 协议（<span class="mono">name + mode</span>），标记那些有 <span class="mono">precision / recall / f1</span> 模式的指标（如 FactualCorrectness、TopicAdherence）。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 经典栈的 required_columns 与 ":optional" / ":ignored" 后缀 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 用后缀精细声明"吃哪些字段"</div>
      <div class="a"><span class="inline">Metric</span> 用 <span class="inline">_required_columns</span>（按 <span class="mono">MetricType</span> 分组）声明它需要的字段。字段名可带后缀来表达"可选 / 忽略"：
<pre class="code"><span class="cm"># 声明：单轮下需要 user_input + response</span>
_required_columns = {
    MetricType.SINGLE_TURN: {
        <span class="st">"user_input"</span>, <span class="st">"response"</span>,
        <span class="st">"retrieved_contexts:optional"</span>,  <span class="cm"># 有就用，没有也行</span>
        <span class="st">"reference:ignored"</span>,            <span class="cm"># 打分用不到，忽略</span>
    }
}</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ 两个读取口径不同</div>
      <div class="a">属性 <span class="inline">required_columns</span> 会<strong>剥掉带后缀的</strong>，只剩硬性必需（这里只剩 <span class="mono">user_input</span> / <span class="mono">response</span>）；而 <span class="inline">get_required_columns(with_optional=True)</span> 会<strong>带上 optional</strong>（去掉 <span class="mono">:optional</span> 后缀）、但仍丢弃 <span class="mono">:ignored</span>。<span class="inline">SingleTurnMetric</span> 据此把样本<strong>裁剪到只剩相关字段</strong>再打分。setter 还会校验字段基名必须属于 <span class="mono">VALID_COLUMNS</span>，否则报错。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  经典栈与两个枚举都在 <span class="mono">src/ragas/metrics/base.py</span>：核心是 <span class="mono">Metric</span> → <span class="mono">MetricWithLLM</span> / <span class="mono">MetricWithEmbeddings</span> 与 <span class="mono">SingleTurnMetric</span> / <span class="mono">MultiTurnMetric</span>，外加枚举 <span class="mono">MetricType</span> / <span class="mono">MetricOutputType</span> 和现代根基类 <span class="mono">SimpleBaseMetric</span> / <span class="mono">SimpleLLMMetric</span>；<span class="mono">required_columns</span> 的 <span class="mono">:optional</span> / <span class="mono">:ignored</span> 解析也在此。（<span class="mono">ModeMetric</span> 协议与 <span class="mono">Ensember</span> 投票器同在该文件，分别在第 17 / 16 课才用到。）
  collections 现代基类在 <span class="mono">src/ragas/metrics/collections/base.py</span>：<span class="mono">BaseMetric(SimpleBaseMetric, NumericValidator)</span>，含 <span class="mono">_validate_llm</span> / <span class="mono">_validate_embeddings</span>。Simple 栈三件套在 <span class="mono">discrete.py</span> / <span class="mono">numeric.py</span> / <span class="mono">ranking.py</span>。导出名单与废弃机制见 <span class="mono">metrics/__init__.py</span>（<span class="mono">__all__</span> 只列基类与 Simple 栈，具名指标进 <span class="mono">_DEPRECATED_METRICS</span> 由 <span class="mono">__getattr__</span> 拦截）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>一次教科书式的架构迁移</strong>：从"多重继承 + 样本对象"演进到"组件化构造注入 + 关键字参数 + 结构化输出"，是值得学习的演进案例。</li>
    <li><strong>新旧并存、算法不变</strong>：两套基类承载<strong>同一套打分逻辑</strong>，迁移只换接口和导入路径，分数口径不变，老用户不被一次性打断。</li>
    <li><strong>把错误前移到构造期</strong>：collections 的 <span class="inline">_validate_llm</span> 只收 <span class="inline">InstructorBaseRagasLLM</span>，传错模型立刻 <span class="mono">ValueError</span>，而不是跑到一半才炸。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>两代族谱：<strong>经典栈</strong> <span class="mono">Metric → MetricWithLLM/Embeddings → SingleTurn/MultiTurnMetric</span>（<span class="mono">single_turn_ascore → float</span>）；<strong>现代栈</strong> <span class="mono">SimpleBaseMetric → SimpleLLMMetric / collections.BaseMetric</span>（<span class="mono">ascore → MetricResult</span>）。</li>
    <li>两个横切枚举：<span class="mono">MetricType</span>（单 / 多轮）、<span class="mono">MetricOutputType</span>（binary / discrete / continuous / ranking）。</li>
    <li>经典栈用 <span class="mono">required_columns</span> 配 <span class="mono">:optional</span> / <span class="mono">:ignored</span> 精细声明字段；collections 只认现代 LLM。</li>
    <li>规范实现走 <span class="mono">collections</span>；下一课拆 <span class="mono">MetricResult</span> 这个"既是分数又是理由"的返回值。</li>
  </ul>
</div>
"""

LESSON_14 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
现代指标 <span class="inline">ascore()</span> 不返回一个裸 <span class="mono">float</span>，而是返回一个 <span class="inline">MetricResult</span>。它有<strong>双重身份</strong>：对外像个普通数字（能比大小、能参与运算、能塞进 pydantic 模型），对内却始终带着<strong>评语（reason）</strong>。本课拆开这个小而精的对象。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  <span class="inline">MetricResult</span> 像一张<strong>成绩条</strong>：正面印着<strong>分数</strong>（0.83），背面写着<strong>评语</strong>（"4 句里有 1 句没依据"）。你算平均分时它就当数字用，存档时连分数带评语一起收好。比起只给个冷冰冰的数字，这张成绩条让你<strong>既能统计、又能复盘</strong>。
</div>

<h2>核心：value + reason（+ traces）</h2>
<p>构造很朴素——一个值、一段理由，外加可选的 <span class="inline">traces</span>（只允许 <span class="mono">input</span> / <span class="mono">output</span> 两个键）：</p>
<pre class="code"><span class="kw">from</span> ragas.metrics.result <span class="kw">import</span> MetricResult

r = MetricResult(value=<span class="st">0.83</span>, reason=<span class="st">"4 句陈述里 3 句有上下文支撑"</span>)
print(r.value)    <span class="cm"># 0.83  ← 原始分数</span>
print(r.reason)   <span class="cm"># '4 句陈述里 3 句有上下文支撑'  ← 为什么是这个分</span>
print(r)          <span class="cm"># MetricResult(value=0.83, reason='…')</span></pre>
<p><span class="inline">value</span> 是只读属性，可以是 <span class="mono">float</span>（数值指标）、<span class="mono">str</span>（离散指标）或 <span class="mono">list</span>（排序指标）——<span class="inline">MetricResult</span> 对三种 Simple 栈输出通吃。</p>

<h2>身份一：像个数字用</h2>
<p>靠一组运算符重载，<span class="inline">MetricResult</span> 能<strong>直接当数值参与计算和比较</strong>，无需先 <span class="mono">.value</span> 解包：</p>
<pre class="code">a = MetricResult(value=<span class="st">0.8</span>)
b = MetricResult(value=<span class="st">0.6</span>)

float(a)           <span class="cm"># 0.8   ← __float__</span>
(a + b) / <span class="st">2</span>        <span class="cm"># 0.7   ← __add__ / __truediv__</span>
a &gt; b              <span class="cm"># True  ← __gt__</span>
a == <span class="st">0.8</span>           <span class="cm"># True  ← __eq__（也能和裸数字比）</span>
sum([a, b])        <span class="cm"># 1.4   ← __radd__ 让内置 sum() 也能用</span></pre>
<p>它还重载了 <span class="inline">__int__</span> / <span class="inline">__sub__</span> / <span class="inline">__mul__</span> 等，并对 <span class="mono">list</span> 结果提供 <span class="inline">__getitem__</span> / <span class="inline">__iter__</span> / <span class="inline">__len__</span>。要注意：对<strong>非数值</strong>的值做数学运算会抛 <span class="mono">TypeError</span>（比如对字符串结果求 <span class="mono">float()</span>）。</p>

<h2>身份二：能进 pydantic、能序列化</h2>
<p>评测结果常要嵌进 pydantic 模型里随结果集落盘。<span class="inline">MetricResult</span> 实现了 <span class="inline">__get_pydantic_core_schema__</span>，于是能<strong>直接当字段类型</strong>，且区分两种序列化口径：</p>
<pre class="code"><span class="kw">from</span> pydantic <span class="kw">import</span> BaseModel

<span class="kw">class</span> <span class="fn">Row</span>(BaseModel):
    score: MetricResult            <span class="cm"># 直接拿它当字段类型</span>

row = Row(score=MetricResult(value=<span class="st">0.83</span>, reason=<span class="st">"…"</span>))
row.model_dump()        <span class="cm"># {'score': MetricResult(...)}  保留对象（Python 口径）</span>
row.model_dump_json()   <span class="cm"># '{"score": {"value": 0.83, "reason": "…"}}'  注意：返回 JSON 字符串, 走 __json__</span></pre>
<p>核心 schema 用一个序列化函数分流：<span class="mono">mode == "json"</span> 时调用 <span class="inline">__json__()</span> 转成 <span class="mono">{value, reason}</span> 字典；普通 <span class="inline">model_dump()</span> 则原样保留对象，方便后续还能取 <span class="mono">.reason</span>。另有 <span class="inline">to_dict()</span> 返回 <span class="mono">{"result": value, "reason": reason}</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> __getattr__ 转发：为什么字符串结果还能调 .upper() <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 把方法转发给内部值</div>
      <div class="a"><span class="inline">MetricResult.__getattr__</span> 会把"自己没有的属性"转发给内部的 <span class="inline">_value</span>。所以离散结果（字符串）能直接调字符串方法、排序结果（列表）能调列表方法。若方法返回的还是<strong>同类型</strong>，会再包一层 <span class="mono">MetricResult</span>（保留原 <span class="mono">reason</span>）：
<pre class="code">r = MetricResult(value=<span class="st">"pass"</span>, reason=<span class="st">"符合标准"</span>)
r.upper()          <span class="cm"># MetricResult(value='PASS', reason='符合标准')</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ 一个对象，多种形态</div>
      <div class="a">数值结果能算数、离散结果能用字符串方法、排序结果能索引迭代——全靠运算符重载 + 属性转发。你几乎可以把它"当成内部值本身"来用，需要解释时再读 <span class="mono">.reason</span>。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  全部在 <span class="mono">src/ragas/metrics/result.py</span> 的 <span class="mono">MetricResult</span> 一个类里：构造接收 <span class="mono">value</span> / <span class="mono">reason</span> / <span class="mono">traces</span>（<span class="mono">traces</span> 仅允许 <span class="mono">input</span> / <span class="mono">output</span> 键）；只读属性 <span class="mono">value</span>；数值身份靠 <span class="mono">__float__</span> / <span class="mono">__int__</span> 与 <span class="mono">__add__</span> / <span class="mono">__radd__</span> / <span class="mono">__sub__</span> / <span class="mono">__mul__</span> / <span class="mono">__truediv__</span> 及比较 <span class="mono">__eq__</span> / <span class="mono">__lt__</span> …；容器身份靠 <span class="mono">__getitem__</span> / <span class="mono">__iter__</span> / <span class="mono">__len__</span>；属性转发靠 <span class="mono">__getattr__</span>；序列化靠 <span class="mono">to_dict</span> / <span class="mono">__json__</span> / <span class="mono">__get_pydantic_core_schema__</span>。collections 指标的 <span class="mono">ascore</span> 正是返回它（见 <a href="15-faithfulness-internals.html">第 15 课</a> 的 Faithfulness）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>一个对象同时是"可运算数值"和"可解释理由"</strong>：<span class="inline">__float__</span> 让它进得了数学公式，<span class="inline">__get_pydantic_core_schema__</span> 让它进得了数据模型，而 <span class="inline">reason</span> 始终不丢。</li>
    <li><strong>无侵入替换裸数字</strong>：因为重载了运算符与比较，已有按 <span class="mono">float</span> 写的聚合代码几乎不用改就能接收 <span class="mono">MetricResult</span>。</li>
    <li><strong>双口径序列化</strong>：<span class="inline">model_dump()</span> 留对象、<span class="inline">model_dump_json()</span> 输出 JSON 字符串（内部走 <span class="inline">__json__</span>），既方便内存里继续用，又方便落盘。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="inline">MetricResult</span> = <strong>value（分数）+ reason（评语）</strong>（+ 可选 traces），是现代 <span class="inline">ascore()</span> 的统一返回值。</li>
    <li>靠运算符重载，它<strong>能当数字直接算 / 比较 / sum()</strong>；靠 pydantic 核心 schema，它能<strong>嵌进模型并序列化</strong>。</li>
    <li>"分数带 why" 是 ragas <strong>可解释性</strong>的关键——既能统计，又能复盘为什么得这个分。</li>
  </ul>
</div>
"""

LESSON_15 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Faithfulness（忠实度）查的是<strong>幻觉</strong>：答案里的每一句，是不是真有检索资料撑腰。它的算法是经典的<strong>两步走</strong>——先把答案拆成一条条"主张（claim）"，再逐条做<strong>NLI 蕴含判断</strong>。本课照着现代 collections 实现，把这条流水线看穿。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  判作业有没有"瞎编"，老师不会整篇笼统打分，而是<strong>先把答案拆成一句句论点</strong>，再拿着<strong>参考资料逐句核对</strong>："这句资料里有→给过；这句资料没提→打叉。"最后<strong>过关句数 ÷ 总句数</strong>就是忠实度。Faithfulness 干的正是这件事。
</div>

<p><strong>本课流程一眼看</strong>：Faithfulness 查幻觉的流程——拆句 → 逐句 NLI → 计分 👇</p>
<div class="flow">
  <div class="node"><div class="nt">答案 response</div><div class="nd">+ retrieved_contexts</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">① 拆句</div><div class="nd">拆成原子陈述 claims</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">② 逐句 NLI</div><div class="nd">对照 context 判 0/1</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">③ 计分</div><div class="nd">支持句数 ÷ 总句数</div></div>
</div>

<h2>两步流水线：拆句 → 逐句查证</h2>
<p>现代实现 <span class="inline">Faithfulness(BaseMetric)</span> 的 <span class="inline">ascore</span> 把整件事切成三段，全程用 instructor LLM 拿结构化结果：</p>
<pre class="code"><span class="kw">async def</span> <span class="fn">ascore</span>(self, user_input, response, retrieved_contexts):
    <span class="cm"># ① 拆句：把 response 拆成原子陈述（去代词、可独立理解）</span>
    statements = <span class="kw">await</span> self._create_statements(user_input, response)
    <span class="kw">if not</span> statements:
        <span class="kw">return</span> MetricResult(value=float(<span class="st">"nan"</span>))   <span class="cm"># 拆不出句子</span>

    <span class="cm"># ② 查证：把所有 context 拼一起，逐句做 NLI 判断（verdict 0/1）</span>
    context_str = <span class="st">"\n"</span>.join(retrieved_contexts)
    verdicts = <span class="kw">await</span> self._create_verdicts(statements, context_str)

    <span class="cm"># ③ 计分：被支撑的句数 / 总句数</span>
    score = self._compute_score(verdicts)
    <span class="kw">return</span> MetricResult(value=float(score))</pre>
<p>开头还会校验 <span class="mono">user_input</span> / <span class="mono">response</span> / <span class="mono">retrieved_contexts</span>，缺了直接 <span class="mono">ValueError</span>。</p>

<h2>① 拆句：StatementGeneratorPrompt</h2>
<p>第一步把回答拆成"原子陈述"。要求<strong>不使用代词</strong>，让每句都能脱离上下文独立判断（比如把"他提出了相对论"改写成"爱因斯坦提出了相对论"）：</p>
<pre class="code"><span class="cm"># _create_statements 内部</span>
input_data = StatementGeneratorInput(question=question, answer=response)
prompt_str = self.statement_generator_prompt.to_string(input_data)
result = <span class="kw">await</span> self.llm.agenerate(prompt_str, StatementGeneratorOutput)
<span class="kw">return</span> result.statements      <span class="cm"># List[str]：一条条主张</span></pre>

<h2>② 查证：NLIStatementPrompt → 0/1</h2>
<p>第二步把"所有陈述 + 拼好的 context"交给 NLI 提示：能从 context <strong>直接推出</strong>就判 <span class="mono">verdict=1</span>，否则 <span class="mono">0</span>，并附 <span class="mono">reason</span>：</p>
<pre class="code"><span class="cm"># _create_verdicts 内部</span>
input_data = NLIStatementInput(context=context, statements=statements)
prompt_str = self.nli_statement_prompt.to_string(input_data)
result = <span class="kw">await</span> self.llm.agenerate(prompt_str, NLIStatementOutput)
<span class="cm"># result.statements: List[StatementFaithfulnessAnswer(statement, reason, verdict)]</span></pre>
<p>计分极简：<span class="inline">_compute_score</span> 数出 <span class="mono">verdict</span> 为真的句数，除以总句数。所以 <strong>Faithfulness = 有依据的陈述占比</strong>，落在 0~1。</p>

<table class="t">
  <tr><th>阶段</th><th>Prompt（输入 → 输出模型）</th><th>产物</th></tr>
  <tr><td>① 拆句</td><td class="mono">StatementGeneratorPrompt（StatementGeneratorInput → Output）</td><td>原子陈述 <span class="mono">List[str]</span></td></tr>
  <tr><td>② 查证</td><td class="mono">NLIStatementPrompt（NLIStatementInput → Output）</td><td>每句 <span class="mono">verdict</span> 0/1 + reason</td></tr>
  <tr><td>③ 计分</td><td>—</td><td><span class="mono">supported / total</span>（0~1）</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> HHEM 变体：把第②步换成交叉编码器 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 legacy 里的 FaithfulnesswithHHEM</div>
      <div class="a">第②步的"逐句 NLI"不一定非得用 LLM。legacy 的 <span class="inline">FaithfulnesswithHHEM</span>（继承自老 <span class="inline">Faithfulness</span>）仍用 LLM 拆句，但把判断换成一个<strong>交叉编码器</strong>模型 <span class="mono">vectara/hallucination_evaluation_model</span>（HuggingFace 的 <span class="mono">AutoModelForSequenceClassification</span>）：对每个 <span class="mono">(context, statement)</span> 对打分、四舍五入成 0/1，再取平均。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 同一算法，不同"裁判"</div>
      <div class="a">这恰好说明 Faithfulness 的算法骨架（拆句 → 逐句判 → 占比）是稳定的，只是第②步的判断器可换：LLM 提示 vs 专用 NLI 模型。HHEM 变体<strong>只在 legacy</strong>（<span class="mono">_faithfulness.py</span>），需要额外装 <span class="mono">transformers</span>。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  规范实现在 <span class="mono">src/ragas/metrics/collections/faithfulness/metric.py</span>：<span class="mono">Faithfulness(BaseMetric)</span> 的 <span class="mono">ascore</span> 串起 <span class="mono">_create_statements</span> / <span class="mono">_create_verdicts</span> / <span class="mono">_compute_score</span>。Prompt 与数据模型在同目录 <span class="mono">util.py</span>：<span class="mono">StatementGeneratorPrompt</span>（<span class="mono">StatementGeneratorInput</span> / <span class="mono">Output</span>）、<span class="mono">NLIStatementPrompt</span>（<span class="mono">NLIStatementInput</span> / <span class="mono">Output</span>），逐句结果是 <span class="mono">StatementFaithfulnessAnswer</span>（<span class="mono">statement</span> / <span class="mono">reason</span> / <span class="mono">verdict</span> 0/1），都继承 <span class="mono">ragas.prompt.metrics.base_prompt.BasePrompt</span>（<a href="19-prompt-system.html">第 19 课</a>）。legacy 镜像与 HHEM 变体在 <span class="mono">metrics/_faithfulness.py</span>（<span class="mono">FaithfulnesswithHHEM</span>）。用法回顾见 <a href="10-rag-metrics.html">第 10 课</a>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>"拆句 + NLI" 是可复用范式</strong>：同一套 NLI 思路（同名 <span class="inline">NLIStatementPrompt</span>，各指标在自己的 util.py 定义）被 FactualCorrectness 再次借用（<a href="17-answer-metrics-internals.html">第 17 课</a>），只是改成双向核对。</li>
    <li><strong>原子化让判断更可靠</strong>：先拆成无代词的独立陈述，再逐句查证，比"整段一把抓"更精确，也天然产出可读的 <span class="mono">reason</span>。</li>
    <li><strong>instructor 结构化输出</strong>：<span class="inline">await llm.agenerate(prompt_str, OutputModel)</span> 直接拿到带 <span class="mono">verdict</span> 字段的对象，省掉手写 JSON 解析。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>忠实度 = <strong>拆句（claim 分解）+ 逐句查证（NLI 判 0/1）+ 占比</strong>，分数 = 被支撑句数 / 总句数。</li>
    <li>两个提示分工：<span class="mono">StatementGeneratorPrompt</span> 拆句、<span class="mono">NLIStatementPrompt</span> 判蕴含；现代实现用 instructor <span class="mono">agenerate</span> 拿结构化结果。</li>
    <li>规范实现在 <span class="mono">collections/faithfulness/</span>；legacy 还有用交叉编码器的 <span class="mono">FaithfulnesswithHHEM</span> 变体。</li>
  </ul>
</div>
"""

LESSON_16 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
检索端的两个指标常被搞混：<strong>ContextPrecision</strong> 看"检索回来的资料质量好不好、相关的有没有排在前面"，<strong>ContextRecall</strong> 看"该检索到的内容是不是都召回了"。本课对照现代 collections 实现，讲清两者各自的算法——平均精度 vs 逐句归因。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  Precision 像评<strong>搜索引擎的排序质量</strong>：返回 10 条，相关的越靠前越好（把"有用的"压在第 8 条是要扣分的）。
  Recall 像批改时<strong>拿标准答案逐句找出处</strong>：标准答案每写一句，就去检索资料里翻一翻"这句有没有依据"，翻得到的越多说明召回越全。一个看<strong>排序</strong>，一个看<strong>覆盖</strong>。
</div>

<p><strong>本课流程一眼看</strong>：检索端从两个角度体检——排序质量（Precision）与覆盖率（Recall） 👇</p>
<div class="flow">
   <div class="node"><div class="nt">检索结果</div><div class="nd">contexts + reference</div></div>
   <div class="arrow">→</div>
   <div class="node"><div class="nt">逐条 / 逐句判定</div><div class="nd">LLM 判 0/1</div></div>
   <div class="arrow">→</div>
   <div class="node hl"><div class="nt">Precision · Recall</div><div class="nd">排序质量 · 覆盖率</div></div>
</div>

<h2>ContextPrecision：逐条判定 + 平均精度</h2>
<p><span class="inline">ContextPrecisionWithReference</span> 的 <span class="inline">ascore</span> 对<strong>每条检索结果各问一次 LLM</strong>："这条 context 对得出参考答案有没有用？" 拿到一串 0/1 的 <span class="mono">verdict</span>，再算<strong>平均精度（average precision）</strong>：</p>
<pre class="code"><span class="cm"># 逐条判定：每个 context 调一次 agenerate</span>
verdicts = []
<span class="kw">for</span> context <span class="kw">in</span> retrieved_contexts:
    input_data = ContextPrecisionInput(question=user_input, context=context, answer=reference)
    result = <span class="kw">await</span> self.llm.agenerate(self.prompt.to_string(input_data), ContextPrecisionOutput)
    verdicts.append(result.verdict)         <span class="cm"># 0 / 1</span>

<span class="cm"># 平均精度：相关项越靠前，得分越高</span>
<span class="kw">def</span> <span class="fn">_calculate_average_precision</span>(self, verdicts):
    cumsum, numerator = <span class="st">0</span>, <span class="st">0.0</span>
    <span class="kw">for</span> i, v <span class="kw">in</span> enumerate(verdicts):
        cumsum += v                          <span class="cm"># 截至第 i 位的命中数</span>
        <span class="kw">if</span> v:                                <span class="cm"># 只在"命中位"累加 precision@(i+1)</span>
            numerator += cumsum / (i + <span class="st">1</span>)
    <span class="kw">return</span> numerator / (cumsum + <span class="st">1e-10</span>)    <span class="cm"># 除以命中总数</span></pre>
<p>把相关项排在前面，<span class="mono">precision@k</span> 会更高，平均精度也更高——这正是信息检索里经典的 <strong>MAP（mean average precision）</strong>思路。</p>
<p>举个数：verdict 为 <span class="mono">[1, 0, 1]</span> → 只在第 1、3 个命中位累加，<span class="mono">(1/1 + 2/3) / 2 ≈ 0.83</span>；若同样两条相关却排成 <span class="mono">[0, 1, 1]</span> → <span class="mono">(1/2 + 2/3) / 2 ≈ 0.58</span>。相关项排得越靠前，分越高。</p>
<p>两个变体只差"拿什么当判断依据"：<span class="inline">ContextPrecision</span> 等于 <span class="inline">ContextPrecisionWithReference</span>（拿 <span class="mono">reference</span> 比），<span class="inline">ContextUtilization</span> 等于 <span class="inline">ContextPrecisionWithoutReference</span>（没有标准答案时改拿 <span class="mono">response</span> 比），算法完全一样。</p>

<h2>ContextRecall：逐句归因</h2>
<p><span class="inline">ContextRecall</span> 反过来——把 <span class="mono">reference</span> 拆成一句句陈述，逐句判断<strong>能不能归因到检索到的 context</strong>（<span class="mono">attributed</span> 0/1），再算占比：</p>
<pre class="code"><span class="cm"># 一次调用拿回所有句子的归因分类</span>
context = <span class="st">"\n"</span>.join(retrieved_contexts)
result = <span class="kw">await</span> self.llm.agenerate(self.prompt.to_string(input_data), ContextRecallOutput)

<span class="cm"># 分数 = 能归因的句数 / 总句数</span>
attributions = [c.attributed <span class="kw">for</span> c <span class="kw">in</span> result.classifications]
score = sum(attributions) / len(attributions)</pre>
<p>每个分类项是 <span class="inline">ContextRecallClassification</span>（<span class="mono">statement</span> / <span class="mono">reason</span> / <span class="mono">attributed</span>）。所以 <strong>Recall = 参考答案中能在检索资料里找到出处的句子占比</strong>。</p>

<table class="t">
  <tr><th>维度</th><th>ContextPrecision</th><th>ContextRecall</th></tr>
  <tr><td><strong>量什么</strong></td><td>相关资料是否排在前面（排序质量）</td><td>该召回的内容是否都召回了（覆盖）</td></tr>
  <tr><td><strong>判定对象</strong></td><td>每条 <span class="mono">retrieved_contexts</span></td><td><span class="mono">reference</span> 拆出的每个句子</td></tr>
  <tr><td><strong>判定问题</strong></td><td>这条 context 对答案有没有用？(<span class="mono">verdict</span>)</td><td>这句能否归因到 context？(<span class="mono">attributed</span>)</td></tr>
  <tr><td><strong>计分</strong></td><td>平均精度（MAP）</td><td>归因句数 / 总句数</td></tr>
  <tr><td><strong>LLM 调用</strong></td><td>每条 context 一次</td><td>整体一次</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 计划里的"多次投票（Ensemble）"——collections 其实没用 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 ensemble 投票是 legacy 的做法</div>
      <div class="a">老实现 <span class="mono">_context_precision.py</span> / <span class="mono">_context_recall.py</span> 会用 <span class="inline">prompt.generate_multiple(...)</span> 多次采样，再用 <span class="inline">ensembler.from_discrete(...)</span> 做<strong>多数投票</strong>（<span class="inline">Ensember</span> 定义在 <span class="mono">metrics/base.py</span>，<a href="13-metric-base.html">第 13 课</a>），目的是对抗 LLM 输出的随机性。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 现代 collections 已简化</div>
      <div class="a">核对规范源码可知：collections 的 <span class="inline">ContextPrecision</span> 对每条 context <strong>只调一次</strong> <span class="mono">agenerate</span>、<span class="inline">ContextRecall</span> <strong>整体只调一次</strong>，<strong>没有</strong> <span class="mono">generate_multiple</span>、<strong>没有</strong> ensemble 投票。更简单、更省 token，稳定性改由 instructor 结构化输出来兜底。所以"多次投票"是<strong>旧栈特性</strong>，讲新栈时不能照搬。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  规范实现在 <span class="mono">src/ragas/metrics/collections/context_precision/metric.py</span>：<span class="mono">ContextPrecisionWithReference</span> / <span class="mono">ContextPrecisionWithoutReference</span> 各含 <span class="mono">_calculate_average_precision</span>，外加薄封装 <span class="mono">ContextPrecision</span>（= WithReference）与 <span class="mono">ContextUtilization</span>（= WithoutReference）；提示与模型在同目录 <span class="mono">util.py</span>（<span class="mono">ContextPrecisionPrompt</span>，输出含 <span class="mono">verdict</span>）。<span class="mono">collections/context_recall/metric.py</span> 的 <span class="mono">ContextRecall</span> 按 <span class="mono">classifications</span> 的 <span class="mono">attributed</span> 计分（<span class="mono">util.py</span> 的 <span class="mono">ContextRecallClassification</span>）。legacy 镜像 <span class="mono">_context_precision.py</span> / <span class="mono">_context_recall.py</span> 用 <span class="mono">generate_multiple</span> + <span class="mono">ensembler</span>，并另有 <span class="mono">NonLLM*</span> / <span class="mono">IDBased*</span> 非 LLM 变体（<a href="12-traditional-metrics.html">第 12 课</a>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>复用 IR 经典指标</strong>：把"检索排序好不好"直接落到平均精度（MAP）上，相关项越靠前分越高，含义清晰可解释。</li>
    <li><strong>precision / recall 对称又互补</strong>：一个逐"条 context"判有用性、一个逐"句 reference"判归因，合起来覆盖检索的"准"与"全"。</li>
    <li><strong>新栈做了减法</strong>：相比 legacy 的多次采样投票，collections 去掉 ensemble、调用更少——是一处真实的简化，提醒我们"教新栈要看新栈的代码"。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>Precision 看排序</strong>：逐条判 context 是否有用 → 平均精度（MAP）；<strong>Recall 看覆盖</strong>：逐句判 reference 能否归因 → 归因占比。</li>
    <li><span class="inline">ContextPrecision</span> = WithReference（比 <span class="mono">reference</span>）；<span class="inline">ContextUtilization</span> = WithoutReference（比 <span class="mono">response</span>）。</li>
    <li>collections 规范实现<strong>不使用</strong> ensemble 投票（那是 legacy 的做法）——讲新栈以源码为准。</li>
  </ul>
</div>
"""

LESSON_17 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
本课看三个"把主观判断算法化"的巧思：<strong>AnswerRelevancy</strong> 反向出题、<strong>FactualCorrectness</strong> 双向对照、<strong>AspectCritic</strong> 一句话造裁判。前两个在现代 collections，第三个目前<strong>只有 legacy 版</strong>——正好对比两代写法。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  三种判法像三种老师：<strong>反向出题</strong>的老师看你答案，反推"这是在回答什么问题"，再看跟原题像不像（跑题了反推出来的问题就对不上）；<strong>双向对照</strong>的老师把你的答案和标准答案<strong>互相</strong>逐条核对，既查你"多说了假的"、也查你"漏说了真的"；<strong>一句话裁判</strong>的老师只需你给一句标准（"有没有害？"），他就照着判 Yes/No。
</div>

<h2>AnswerRelevancy：反向出题 + 余弦相似度</h2>
<p>切题与否不好直接打分，于是<strong>反过来</strong>：让 LLM 从 <span class="mono">response</span> 反推出若干个"它像在回答的问题"，再和原始 <span class="mono">user_input</span> 比<strong>余弦相似度</strong>。反推次数由 <span class="inline">strictness</span> 控制（<strong>默认 3</strong>）：</p>
<div class="flow">
  <div class="node"><div class="nt">答案 response</div><div class="nd">待评切题度</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">反向出题 ×N</div><div class="nd">LLM 反推可能的问题</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">余弦相似度</div><div class="nd">反推问题 vs 原问题</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">均值</div><div class="nd">全敷衍 → 0 分</div></div>
</div>
<pre class="code"><span class="kw">for</span> _ <span class="kw">in</span> range(self.strictness):           <span class="cm"># strictness 默认 3</span>
    result = <span class="kw">await</span> self.llm.agenerate(
        self.prompt.to_string(AnswerRelevanceInput(response=response)),
        AnswerRelevanceOutput)
    generated_questions.append(result.question)
    noncommittal_flags.append(result.noncommittal)   <span class="cm"># 是否敷衍/答非所问</span>

all_noncommittal = np.all(noncommittal_flags)
<span class="cm"># 原问题 vs 反推问题，求平均余弦相似度</span>
score = cosine_sim.mean() * int(<span class="kw">not</span> all_noncommittal)   <span class="cm"># 全敷衍 → 直接 0 分</span></pre>
<p>两个要点：① 构造时<strong>必须给 embeddings</strong>（<a href="22-embedding-abstraction.html">第 22 课</a>），因为要做向量相似度；② <span class="mono">noncommittal</span>（敷衍/"我不知道"）惩罚——只要全部反推都被判为敷衍，<strong>分数直接归零</strong>。</p>

<h2>FactualCorrectness：双向 NLI → P/R/F1</h2>
<p>事实一致度把 Faithfulness 的"拆句 + NLI"（<a href="15-faithfulness-internals.html">第 15 课</a>）升级成<strong>双向</strong>核对，再套上分类指标的 TP/FP/FN：</p>
<div class="flow">
  <div class="node"><div class="nt">拆 response 的 claim</div><div class="nd">对 reference 逐条 NLI：TP / FP</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">反向：拆 reference</div><div class="nd">对 response NLI：FN（非 precision）</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">P / R / F1</div><div class="nd">按 mode（默认 f1）</div></div>
</div>
<pre class="code"><span class="cm"># ① 拆 response 的 claim，逐条对 reference 做 NLI</span>
reference_response = <span class="kw">await</span> self._decompose_and_verify_claims(response, reference)
<span class="cm"># ② 非 precision 模式：再拆 reference，对 response 做 NLI（反方向）</span>
<span class="kw">if</span> self.mode != <span class="st">"precision"</span>:
    response_reference = <span class="kw">await</span> self._decompose_and_verify_claims(reference, response)
    fn = int(np.sum(~response_reference))   <span class="cm"># 标准答案里没被覆盖（漏说的真话）</span>

tp = int(np.sum(reference_response))    <span class="cm"># 答案里有据可查的 claim</span>
fp = int(np.sum(~reference_response))   <span class="cm"># 答案里查无实据（多说的假话）</span>

<span class="kw">if</span>   self.mode == <span class="st">"precision"</span>: score = tp / (tp + fp + <span class="st">1e-8</span>)
<span class="kw">elif</span> self.mode == <span class="st">"recall"</span>:    score = tp / (tp + fn + <span class="st">1e-8</span>)
<span class="kw">else</span>:                          score = fbeta_score(tp, fp, fn, self.beta)  <span class="cm"># f1</span></pre>
<p><span class="inline">mode</span> 默认 <span class="mono">"f1"</span>、<span class="inline">beta</span> 默认 <span class="mono">1.0</span>（<span class="mono">beta&gt;1</span> 偏召回、<span class="mono">&lt;1</span> 偏精确；<span class="inline">fbeta_score</span> 就是精确率与召回率的加权调和平均）。precision 只做正方向、不算 <span class="mono">fn</span>；recall / f1 才跑双向。它在自己的 <span class="mono">util.py</span> 里定义了同名的 <span class="inline">NLIStatementPrompt</span>（与 Faithfulness 同范式、各自一份）。</p>

<h2>AspectCritic：一句话定义一个裁判（legacy-only）</h2>
<p>最灵活的一个：你给一句<strong>自然语言定义</strong>，它就照着判 0/1。注意它<strong>尚未迁移到 collections</strong>——只能从 <span class="mono">ragas.metrics</span> 导入（会触发废弃告警），底层还是经典栈：</p>
<pre class="code"><span class="kw">from</span> ragas.metrics <span class="kw">import</span> AspectCritic   <span class="cm"># ⚠️ 仅 legacy，collections 暂无</span>

harmfulness = AspectCritic(
    name=<span class="st">"harmfulness"</span>,
    definition=<span class="st">"答案是否可能对个人或群体造成伤害？"</span>,  <span class="cm"># 一句话造一个指标</span>
    llm=llm,
)
<span class="cm"># 内部把 definition 拼进指令：</span>
<span class="cm"># "...Use only 'Yes' (1) and 'No' (0) as verdict.\nCriteria Definition: {definition}"</span>
<span class="cm"># 输出 AspectCriticOutput(reason, verdict 0/1)</span></pre>
<p><span class="inline">AspectCritic(MetricWithLLM, SingleTurnMetric, MultiTurnMetric)</span> 同时支持单 / 多轮（两套 <span class="mono">PydanticPrompt</span>）。<span class="inline">strictness</span> 默认 1、会被强制成奇数，<span class="mono">_compute_score</span> 里也确实留了"多数投票（<span class="inline">Counter</span>）"的分支——但要留意：当前 <span class="mono">_ascore</span> 只调用<strong>一次</strong> <span class="mono">generate</span>、再把单个结果传进 <span class="mono">_compute_score([response])</span>，所以这条投票分支实际只在一个元素上运行、<strong>strictness&gt;1 并不会真的多次采样</strong>（ragas 自身 docstring 也把它写成了多数投票，属已知出入——读内部实现要以代码为准）。库里预置了 <span class="mono">harmfulness</span> / <span class="mono">maliciousness</span> / <span class="mono">coherence</span> / <span class="mono">correctness</span> / <span class="mono">conciseness</span> 几个现成裁判。</p>

<table class="t">
  <tr><th>指标</th><th>思路</th><th>关键输入</th><th>输出</th><th>栈</th></tr>
  <tr><td class="mono">AnswerRelevancy</td><td>反向出题 + 余弦相似度（+敷衍惩罚）</td><td class="mono">user_input + response（+ embeddings）</td><td>0~1</td><td>collections</td></tr>
  <tr><td class="mono">FactualCorrectness</td><td>双向 NLI → TP/FP/FN → P/R/F1</td><td class="mono">response + reference</td><td>0~1</td><td>collections</td></tr>
  <tr><td class="mono">AspectCritic</td><td>一句话 definition 当裁判</td><td class="mono">definition + 样本字段</td><td>0 / 1</td><td><strong>legacy-only</strong></td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么 AnswerRelevancy 要"反向"出题？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 正面打"切题分"很主观</div>
      <div class="a">直接问 LLM"这答案切题吗"既主观又难量化。反向生成把它转成<strong>可计算</strong>的问题：如果答案真的在回答原问题，那么"从答案反推出来的问题"就应该和原问题<strong>语义相近</strong>（余弦相似度高）。跑题或答非所问，反推出来的问题就对不上，相似度自然低。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 敷衍要单独惩罚</div>
      <div class="a">"我不确定 / 无可奉告"这类敷衍回答，反推出来的问题可能恰好和原题接近，相似度并不低。所以单设 <span class="mono">noncommittal</span> 标志：一旦反推全被判为敷衍，直接 <span class="mono">× 0</span>，避免"敷衍也能得高分"。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  <span class="mono">src/ragas/metrics/collections/answer_relevancy/metric.py</span>：<span class="mono">AnswerRelevancy(BaseMetric)</span>，构造需 <span class="mono">llm</span> + <span class="mono">embeddings</span>，<span class="mono">strictness</span> 默认 3，提示 <span class="mono">AnswerRelevancePrompt</span>（输出含 <span class="mono">question</span> / <span class="mono">noncommittal</span>）。
  <span class="mono">collections/factual_correctness/metric.py</span>：<span class="mono">FactualCorrectness(BaseMetric)</span>，<span class="mono">mode</span>（precision / recall / f1，默认 f1）+ <span class="mono">beta</span>（默认 1.0）+ <span class="mono">atomicity</span> / <span class="mono">coverage</span>，串 <span class="mono">_decompose_and_verify_claims</span>，分数走 <span class="mono">metrics/utils.py</span> 的 <span class="mono">fbeta_score</span>；提示在同目录 <span class="mono">util.py</span>（<span class="mono">ClaimDecompositionPrompt</span> / <span class="mono">NLIStatementPrompt</span>）。
  AspectCritic <strong>只有 legacy</strong>：<span class="mono">metrics/_aspect_critic.py</span> 的 <span class="mono">AspectCritic(MetricWithLLM, SingleTurnMetric, MultiTurnMetric)</span>，含 <span class="mono">definition</span> / <span class="mono">strictness</span> / <span class="mono">_compute_score</span>、<span class="mono">SingleTurnAspectCriticPrompt</span> / <span class="mono">MultiTurnAspectCriticPrompt</span>、<span class="mono">AspectCriticOutput</span>（<span class="mono">verdict</span> 0/1）——不在 <span class="mono">collections/__init__.py</span> 的 <span class="mono">__all__</span> 里（<a href="09-metrics-overview.html">第 9 课</a>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>反向生成的巧思</strong>：把"切不切题"这种主观判断，转成"反推问题 vs 原问题"的余弦相似度，既可量化又自带敷衍惩罚。</li>
    <li><strong>双向 NLI 统一 P/R/F1</strong>：正向查"多说的假话"（精确率），反向查"漏说的真话"（召回率），用 <span class="inline">fbeta_score</span> 一把收口，<span class="mono">beta</span> 还能调侧重。</li>
    <li><strong>AspectCritic 让你"一句话造指标"</strong>：自然语言 <span class="inline">definition</span> 即评判标准，是把领域规则快速指标化的利器；只是它还停在经典栈。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>三种把主观判断算法化的思路：<strong>反向出题</strong>（Relevancy）、<strong>双向对照</strong>（Factual）、<strong>一句话裁判</strong>（AspectCritic）。</li>
    <li>AnswerRelevancy <span class="mono">strictness</span> 默认 3、需 <span class="mono">embeddings</span>、全敷衍则 0 分；FactualCorrectness <span class="mono">mode</span> 默认 f1、<span class="mono">beta</span> 默认 1.0。</li>
    <li>AspectCritic <strong>只有 legacy 版</strong>（<span class="mono">from ragas.metrics import AspectCritic</span>，会告警），尚未迁移到 collections。</li>
  </ul>
</div>
"""

LESSON_18 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
Agent 不是一问一答，而是<strong>多轮 + 调工具</strong>地干活。评它得换一套指标，而且都吃<strong>多轮样本</strong>（<a href="05-multi-turn-sample.html">第 5 课</a> 的消息列表）。本课看四个 collections 指标如何把"Agent 好不好"拆成<strong>工具、目标、话题</strong>几个可测维度。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  评 Agent 像评<strong>一个实习生干一单活</strong>：<strong>工具用对没</strong>（该查天气你别去订餐，参数也别填错）、<strong>目标达成没</strong>（最后真把桌订上了吗）、<strong>有没有跑题</strong>（只准聊业务，别被带去闲扯）。一个维度一把尺子，合起来才看得清这个"实习生"靠不靠谱。
</div>

<h2>工具维度：ToolCallAccuracy / ToolCallF1（纯规则）</h2>
<p>这两个指标<strong>不用裁判模型</strong>——虽然也是 collections（继承 <span class="inline">BaseMetric</span>），但纯靠规则比对。它们先从对话的 <span class="inline">AIMessage</span> 里抽出 Agent 实际发起的 <span class="inline">tool_calls</span>，再和 <span class="mono">reference_tool_calls</span> 对：</p>
<pre class="code"><span class="cm"># ToolCallAccuracy：序列对齐 + 参数精确匹配</span>
pred = [tc <span class="kw">for</span> m <span class="kw">in</span> user_input
        <span class="kw">if</span> isinstance(m, AIMessage) <span class="kw">and</span> m.tool_calls
        <span class="kw">for</span> tc <span class="kw">in</span> m.tool_calls]

aligned = int(self._is_sequence_aligned(            <span class="cm"># strict_order 默认 True：名字顺序要一致</span>
    [t.name <span class="kw">for</span> t <span class="kw">in</span> pred], [t.name <span class="kw">for</span> t <span class="kw">in</span> reference_tool_calls]))
score = (arg_precision_sum / len(reference_tool_calls)) * aligned   <span class="cm"># 长度不齐再打覆盖折扣</span></pre>
<p>这是简化写法：<span class="inline">arg_precision_sum</span> 是每个匹配工具的<strong>参数精确度</strong>之和，<span class="inline">aligned</span> 把"调用顺序 / 数量不齐"折成惩罚因子——所以真实分数可能比"纯按参数匹配"更低。</p>
<p><span class="inline">ToolCallF1</span> 则把工具调用当成<strong>集合</strong>（名字 + 参数都相同才算一个），用集合运算算 TP/FP/FN 再求 F1：</p>
<pre class="code"><span class="cm"># ToolCallF1：集合化后算 F1（顺序无关）</span>
TP = len(actual &amp; expected)   <span class="cm"># 预测 ∩ 参考</span>
FP = len(actual - expected)   <span class="cm"># 只在预测里（多调了）</span>
FN = len(expected - actual)   <span class="cm"># 只在参考里（漏调了）</span>
f1 = calculate_f1_score(TP, FP, FN)</pre>
<p>区别：<span class="inline">ToolCallAccuracy</span> 在意<strong>顺序与参数</strong>（默认 <span class="mono">strict_order=True</span>），<span class="inline">ToolCallF1</span> 把调用看成无序集合、只问"该调的调了没、有没有多调"。</p>

<h2>目标维度：AgentGoalAccuracy（LLM，0/1）</h2>
<p>判"这单活到底办成没"。先让 LLM 从整段对话<strong>推断最终状态</strong>，再判断是否达成，输出二元 0/1。分有无参考两种：</p>
<pre class="code"><span class="cm"># WithReference：拿外部给的 reference 当目标</span>
workflow = <span class="kw">await</span> self._infer_goal_outcome(conversation)   <span class="cm"># 推断 end_state</span>
verdict  = <span class="kw">await</span> self._compare_outcomes(reference, workflow.end_state)

<span class="cm"># WithoutReference：连"用户想要什么"都由 LLM 从对话里推</span>
workflow = <span class="kw">await</span> self._infer_goal_outcome(conversation)   <span class="cm"># 推断 user_goal + end_state</span>
verdict  = <span class="kw">await</span> self._compare_outcomes(workflow.user_goal, workflow.end_state)</pre>
<p><span class="inline">AgentGoalAccuracy</span> 是 <span class="inline">AgentGoalAccuracyWithReference</span> 的别名。有参考时拿你给的 <span class="mono">reference</span> 当标准答案，无参考时连用户目标也让模型从对话里推断出来再比。</p>

<h2>话题维度：TopicAdherence（LLM，P/R/F1）</h2>
<p>判"有没有守在允许的话题里"。给一组 <span class="mono">reference_topics</span>，指标分四步：抽话题 → 看每个话题<strong>答了还是拒答</strong> → 判每个话题<strong>是否在允许范围内</strong> → 按 <span class="inline">mode</span>（默认 f1）算 P/R/F1：</p>
<pre class="code">topics      = <span class="kw">await</span> self._extract_topics(conversation)            <span class="cm"># 对话里聊了哪些话题</span>
answered    = <span class="kw">await</span> self._check_topics_answered(conversation, topics) <span class="cm"># 答了(True)/拒答(False)</span>
classified  = <span class="kw">await</span> self._classify_topics(reference_topics, topics)   <span class="cm"># 是否属于允许话题</span>
<span class="cm"># TP=答了且该答, FP=答了却不该答（跑题）, FN=该答却拒答 → precision/recall/f1</span></pre>

<table class="t">
  <tr><th>指标</th><th>评什么</th><th>靠 LLM？</th><th>关键输入</th><th>计分</th></tr>
  <tr><td class="mono">ToolCallAccuracy</td><td>工具调用对不对（顺序 + 参数）</td><td>否（规则）</td><td class="mono">user_input + reference_tool_calls</td><td>参数精度 × 序列对齐</td></tr>
  <tr><td class="mono">ToolCallF1</td><td>工具调用集合的 F1</td><td>否（规则）</td><td class="mono">user_input + reference_tool_calls</td><td>集合 TP/FP/FN → F1</td></tr>
  <tr><td class="mono">AgentGoalAccuracy</td><td>是否达成用户目标</td><td>是</td><td class="mono">user_input（+ reference）</td><td>0 / 1</td></tr>
  <tr><td class="mono">TopicAdherence</td><td>是否守在允许话题内</td><td>是</td><td class="mono">user_input + reference_topics</td><td>P / R / F1</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么有的 Agent 指标不用 LLM？ <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 能用规则就别请裁判</div>
      <div class="a">工具调用是<strong>结构化</strong>的（名字 + 参数字典），"对不对"可以直接比对，不存在语义模糊。所以 <span class="inline">ToolCallAccuracy</span> / <span class="inline">ToolCallF1</span> 走纯规则：<strong>零 token、确定可复现、还快</strong>。而"目标有没有达成""跑没跑题"涉及语义理解，才请 LLM 当裁判。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 都吃多轮消息</div>
      <div class="a">四个指标的 <span class="mono">user_input</span> 都是一<strong>列消息</strong>（<span class="mono">HumanMessage</span> / <span class="mono">AIMessage</span> / <span class="mono">ToolMessage</span>，来自 <span class="mono">ragas.messages</span>），正是 <span class="inline">MultiTurnSample</span> 承载的那串对话（<a href="05-multi-turn-sample.html">第 5 课</a>）。工具调用从 <span class="mono">AIMessage.tool_calls</span> 里取。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  规范实现都在 <span class="mono">src/ragas/metrics/collections/</span>：<span class="mono">tool_call_accuracy/metric.py</span>（<span class="mono">ToolCallAccuracy</span>，<span class="mono">strict_order</span> + <span class="mono">_is_sequence_aligned</span>，<span class="mono">util.py</span> 的 <span class="mono">exact_match_args</span>）、<span class="mono">tool_call_f1/metric.py</span>（<span class="mono">ToolCallF1</span>，<span class="mono">util.py</span> 的 <span class="mono">tool_call_to_hashable</span> / <span class="mono">calculate_f1_score</span>）、<span class="mono">agent_goal_accuracy/metric.py</span>（<span class="mono">AgentGoalAccuracyWithReference</span> / <span class="mono">WithoutReference</span>，<span class="mono">AgentGoalAccuracy</span> 是前者别名；提示 <span class="mono">InferGoalOutcomePrompt</span> / <span class="mono">CompareOutcomePrompt</span>）、<span class="mono">topic_adherence/metric.py</span>（<span class="mono">TopicAdherence</span>，<span class="mono">mode</span> 默认 f1；三个提示 <span class="mono">TopicExtraction</span> / <span class="mono">TopicRefused</span> / <span class="mono">TopicClassification</span>）。消息类型在 <span class="mono">ragas/messages.py</span>，多轮样本见 <span class="mono">dataset_schema.py</span> 的 <span class="mono">MultiTurnSample</span>。legacy 镜像在 <span class="mono">_tool_call_accuracy.py</span> / <span class="mono">_tool_call_f1.py</span> / <span class="mono">_goal_accuracy.py</span> / <span class="mono">_topic_adherence.py</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>把"Agent 好不好"拆成可测维度</strong>：工具（用对没）、目标（成了没）、话题（跑没跑），各自一个指标，比一个笼统分更可诊断。</li>
    <li><strong>规则与 LLM 各司其职</strong>：结构化的工具调用用规则（省钱可复现），语义性的目标 / 话题才上 LLM——成本与准确度的务实取舍。</li>
    <li><strong>P/R/F1 范式再次复用</strong>：TopicAdherence 又把"答了 / 该答"映射成 TP/FP/FN（呼应 <a href="17-answer-metrics-internals.html">第 17 课</a>），同一套分类指标思路贯穿全书。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Agent 评测靠<strong>多轮样本 + 多维度指标</strong>：工具（ToolCallAccuracy / ToolCallF1）、目标（AgentGoalAccuracy）、话题（TopicAdherence）。</li>
    <li>工具类指标<strong>纯规则、不用 LLM</strong>（顺序 + 参数 / 集合 F1）；目标与话题类才用 LLM 当裁判。</li>
    <li><span class="inline">AgentGoalAccuracy</span> = <span class="inline">WithReference</span> 别名，另有 <span class="inline">WithoutReference</span>；TopicAdherence 用 <span class="mono">reference_topics</span> + <span class="mono">mode</span>（默认 f1）。</li>
  </ul>
</div>
"""
