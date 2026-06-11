"""Content for part1 — 第一部分 · 宏观全景（01-03）."""

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

LESSON_02 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
拉远镜头看 ragas：它不是一个大文件，而是一座分工明确的"评测工厂"。本课给你一张<strong>子包地图</strong>，
认清顶层公开 API 暴露了什么、各子包各管一摊什么活，以及贯穿全书的<strong>两条主线</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  ragas 像一座<strong>评测工厂</strong>：<strong>原料区</strong>是数据（<span class="inline">Dataset</span> / <span class="inline">EvaluationDataset</span>），
  <strong>质检线</strong>是指标（<span class="inline">metrics</span>），<strong>自动出题车间</strong>是测试集生成（<span class="inline">testset</span>），
  <strong>实验台</strong>是 <span class="inline">experiment</span>，而<strong>水电基建</strong>是 LLM、Embedding 与执行引擎（<span class="inline">llms</span> / <span class="inline">embeddings</span> / <span class="inline">executor</span>）。
  逛工厂前先拿张地图，才不会在车间里迷路。
</div>

<h2>顶层公开 API：小而稳的门面</h2>
<p>打开 <span class="mono">src/ragas/__init__.py</span>，<span class="inline">__all__</span> 只导出最常用的"门面"对象——
入口、数据模型、实验与少量基建，<strong>刻意不</strong>把成百上千个指标、各种 LLM / Embedding 包装类塞进顶层：</p>

<table class="t">
  <tr><th>类别</th><th>顶层可直接 import 的名字</th></tr>
  <tr><td><strong>评测入口</strong></td><td><span class="mono">evaluate</span>, <span class="mono">aevaluate</span></td></tr>
  <tr><td><strong>实验入口</strong></td><td><span class="mono">experiment</span>, <span class="mono">Experiment</span>, <span class="mono">version_experiment</span></td></tr>
  <tr><td><strong>数据模型</strong></td><td><span class="mono">Dataset</span>, <span class="mono">DataTable</span>, <span class="mono">EvaluationDataset</span>, <span class="mono">SingleTurnSample</span>, <span class="mono">MultiTurnSample</span></td></tr>
  <tr><td><strong>基建 / 配置</strong></td><td><span class="mono">RunConfig</span>, <span class="mono">backends</span>, <span class="mono">cacher</span>, <span class="mono">CacheInterface</span>, <span class="mono">DiskCacheBackend</span>, tokenizers</td></tr>
</table>

<p>那指标和模型从哪来？答案是<strong>按需从子模块导入</strong>，例如：</p>
<pre class="code"><span class="kw">from</span> ragas <span class="kw">import</span> evaluate, EvaluationDataset   <span class="cm"># 顶层：入口 + 数据</span>
<span class="kw">from</span> ragas.metrics <span class="kw">import</span> Faithfulness        <span class="cm"># 子模块：指标</span>
<span class="kw">from</span> ragas.llms <span class="kw">import</span> llm_factory           <span class="cm"># 子模块：LLM 抽象</span></pre>
<p>顶层只放"人人都要用"的东西，把庞杂的实现关进子包，<strong>公开面越小越稳</strong>，升级时也更不容易误伤用户代码。</p>

<h2>子包地图：各管一摊</h2>
<table class="t">
  <tr><th>子包 / 模块</th><th>一句话职责</th></tr>
  <tr><td class="mono">metrics/</td><td>内置指标与 <span class="mono">Metric</span> 基类体系（Faithfulness、ContextPrecision…）</td></tr>
  <tr><td class="mono">testset/</td><td>从文档自动造测试集（知识图谱 → Transforms → Synthesizers）</td></tr>
  <tr><td class="mono">llms/</td><td>LLM 抽象与包装（<span class="mono">llm_factory</span>、<span class="mono">BaseRagasLLM</span>）</td></tr>
  <tr><td class="mono">embeddings/</td><td>Embedding 抽象与包装（<span class="mono">embedding_factory</span>）</td></tr>
  <tr><td class="mono">prompt/</td><td>结构化 Prompt 系统（<span class="mono">PydanticPrompt</span>）</td></tr>
  <tr><td class="mono">backends/</td><td>可插拔存储后端（CSV / JSONL / 内存…），给数据与实验落盘</td></tr>
  <tr><td class="mono">integrations/</td><td>与 LangChain、LlamaIndex、观测工具等框架的集成</td></tr>
  <tr><td class="mono">optimizers/</td><td>指标的提示优化 / 训练</td></tr>
  <tr><td class="mono">evaluation.py</td><td>经典评测入口 <span class="mono">evaluate</span> / <span class="mono">aevaluate</span></td></tr>
  <tr><td class="mono">experiment.py</td><td>现代实验入口 <span class="mono">@experiment</span> / <span class="mono">Experiment</span></td></tr>
  <tr><td class="mono">executor.py</td><td>异步执行引擎 <span class="mono">Executor</span>（并发跑任务）</td></tr>
  <tr><td class="mono">dataset.py</td><td><span class="mono">Dataset</span> / <span class="mono">DataTable</span>：实验数据容器</td></tr>
  <tr><td class="mono">dataset_schema.py</td><td>样本与结果模型（<span class="mono">SingleTurnSample</span>、<span class="mono">EvaluationDataset</span>、<span class="mono">EvaluationResult</span>）</td></tr>
  <tr><td class="mono">callbacks.py</td><td>链式回调与追踪（<span class="mono">new_group</span>、<span class="mono">RagasTracer</span>）</td></tr>
  <tr><td class="mono">cost.py</td><td>token 成本统计（<span class="mono">CostCallbackHandler</span>）</td></tr>
  <tr><td class="mono">cache.py</td><td>结果缓存（<span class="mono">CacheInterface</span>、<span class="mono">DiskCacheBackend</span>、<span class="mono">cacher</span>）</td></tr>
</table>

<h2>两条主线：评测线 vs 测试生成线</h2>
<p>整座工厂的物流其实只有两条主线，后面各部分都是在这两条线上做深挖：</p>
<ul>
  <li><strong>评测线</strong>：已经有数据 → 用 <span class="inline">metrics</span> 打分 → <span class="inline">evaluate</span> / <span class="inline">@experiment</span> 跑出结果（<a href="07-evaluate.html">第 7 课</a>、<a href="08-experiment.html">第 8 课</a>）。</li>
  <li><strong>测试生成线</strong>：只有文档、还没数据 → 用 <span class="inline">testset</span> 自动造测试集，再回到评测线（<a href="25-testgen-overview.html">第 25 课</a>起的第六部分）。</li>
</ul>

<details class="accordion">
  <summary><span class="badge-num">1</span> experimental 为什么要"惰性加载"？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 ragas.experimental 是怎么暴露的</div>
      <div class="a"><span class="inline">__init__.py</span> 没有直接 import 它，而是用模块级 <span class="inline">__getattr__</span> 拦截属性访问：只有当你真的写 <span class="mono">ragas.experimental</span> 时，才去 import 背后的 <span class="mono">ragas_experimental</span> 包。
<pre class="code"><span class="kw">def</span> <span class="fn">__getattr__</span>(name):
    <span class="kw">if</span> name == <span class="st">"experimental"</span>:
        <span class="kw">try</span>:
            <span class="kw">import</span> ragas_experimental <span class="kw">as</span> experimental
            <span class="kw">return</span> experimental
        <span class="kw">except</span> ImportError:
            <span class="kw">raise</span> ImportError(<span class="st">"ragas.experimental requires installation: ..."</span>)</pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ 这样设计的好处</div>
      <div class="a">没装可选依赖时，<strong>导入 ragas 本身不会报错</strong>；只有用到实验功能才触发安装提示，错误信息还直接告诉你 <span class="mono">pip install ragas[experimental]</span>。按需付费，缺啥提示啥。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  顶层门面定义在 <span class="mono">src/ragas/__init__.py</span>：<span class="mono">__all__</span> 列出对外导出的名字，模块级 <span class="mono">__getattr__</span> 负责惰性加载 <span class="mono">experimental</span>（实际导入 <span class="mono">ragas_experimental</span>）。
  各子包分别在 <span class="mono">metrics/</span>、<span class="mono">testset/</span>、<span class="mono">llms/</span>、<span class="mono">embeddings/</span>、<span class="mono">prompt/</span>、<span class="mono">backends/</span>、<span class="mono">integrations/</span>、<span class="mono">optimizers/</span> 目录下；
  核心模块为 <span class="mono">evaluation.py</span>、<span class="mono">experiment.py</span>、<span class="mono">executor.py</span>、<span class="mono">dataset.py</span>、<span class="mono">dataset_schema.py</span>、<span class="mono">callbacks.py</span>、<span class="mono">cost.py</span>、<span class="mono">cache.py</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>公开面小而稳</strong>：<span class="inline">__all__</span> 只导核心入口与数据模型，指标 / 模型一律从子模块按需导入，降低耦合、减少升级时的破坏性变更。</li>
    <li><strong>惰性加载可选功能</strong>：<span class="inline">experimental</span> 用模块级 <span class="inline">__getattr__</span> 按需加载，缺依赖时抛出带安装指引的清晰 <span class="inline">ImportError</span>，而不是在 import 阶段就崩。</li>
    <li><strong>关注点分离</strong>：每个子包各管一摊（数据 / 指标 / 出题 / 模型 / 基建），地图清晰、按图索骥。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>顶层 <span class="mono">__init__.py</span> 只暴露<strong>核心门面</strong>；指标与模型从 <span class="mono">ragas.metrics</span>、<span class="mono">ragas.llms</span> 等<strong>子模块</strong>导入。</li>
    <li>记住<strong>子包地图</strong>：metrics / testset / llms / embeddings / prompt / backends / integrations / optimizers + 一组核心模块。</li>
    <li>分清<strong>两条主线</strong>——评测线 vs 测试生成线；后续每一课都按这张图展开。</li>
  </ul>
</div>
"""

LESSON_03 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
当你写下 <span class="inline">evaluate(dataset, metrics)</span>，幕后到底发生了什么？本课把一次评测拆成
<strong>6 个步骤</strong>，看清数据如何从"一摞样本"变成"一张成绩单"。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  一次评测就像<strong>考试阅卷</strong>：<strong>试卷</strong>是样本（samples），<strong>评分标准</strong>是指标（metrics），
  把"每份试卷 × 每条标准"拆成一道道独立的判分任务，交给<strong>一屋子阅卷老师并发批改</strong>（<span class="inline">Executor</span>），
  最后把零散分数<strong>汇总成一张成绩单</strong>（<span class="inline">EvaluationResult</span>）。
</div>

<h2>生命周期：从样本到成绩单的 6 步</h2>
<p><span class="inline">evaluate()</span> 只是同步外壳，真正干活的是 <span class="inline">aevaluate()</span>。它依次做这 6 件事：</p>

<table class="t">
  <tr><th>#</th><th>步骤</th><th>发生了什么</th><th>源码符号</th></tr>
  <tr><td>1</td><td><strong>选指标</strong></td><td>没传 <span class="mono">metrics</span> 时，用一组默认 RAG 指标兜底</td><td class="mono">aevaluate()</td></tr>
  <tr><td>2</td><td><strong>规整数据</strong></td><td>HuggingFace <span class="mono">Dataset</span> 先列名重映射、v1→v2 并转成 <span class="mono">EvaluationDataset</span>；随后统一校验必需列与指标是否支持</td><td class="mono">EvaluationDataset.from_list</td></tr>
  <tr><td>3</td><td><strong>注入模型并初始化</strong></td><td>给需要的指标补上 LLM / Embedding（默认 <span class="mono">gpt-4o-mini</span>），逐个调用 <span class="mono">metric.init()</span></td><td class="mono">metric.init(run_config)</td></tr>
  <tr><td>4</td><td><strong>拆任务并提交</strong></td><td>对每个"样本 × 指标"提交一道异步打分任务（单轮 / 多轮各走对应方法）</td><td class="mono">executor.submit(...)</td></tr>
  <tr><td>5</td><td><strong>并发执行</strong></td><td>引擎并发跑完所有任务，按提交顺序收回一维结果列表</td><td class="mono">await executor.aresults()</td></tr>
  <tr><td>6</td><td><strong>汇总成绩单</strong></td><td>把一维列表按行还原成"每行一套分数"，封装为结果对象</td><td class="mono">EvaluationResult</td></tr>
</table>

<p>第 4 步按样本类型分流：<span class="inline">SingleTurnSample</span> 调 <span class="inline">single_turn_ascore</span>，
<span class="inline">MultiTurnSample</span> 调 <span class="inline">multi_turn_ascore</span>；每道任务命名为 <span class="mono">f"{metric.name}-{i}"</span>。
若传入 <span class="inline">return_executor=True</span>，则在第 4 步后<strong>直接把 <span class="mono">Executor</span> 交还给你</strong>（可手动 <span class="mono">cancel()</span> / 取结果），不再自动跑完。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 一维结果怎么还原成每行分数？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 扁平列表 → 二维成绩单</div>
      <div class="a">任务是按"行优先"提交的，所以第 <span class="inline">i</span> 行、第 <span class="inline">j</span> 个指标的结果就落在扁平列表的 <span class="mono">len(metrics) * i + j</span> 位置。汇总时再按这个公式取回来：
<pre class="code"><span class="kw">for</span> i, _ <span class="kw">in</span> enumerate(dataset):
    s = {}
    <span class="kw">for</span> j, m <span class="kw">in</span> enumerate(metrics):
        s[m.name] = results[len(metrics) * i + j]
    scores.append(s)   <span class="cm"># 每行一个 {指标名: 分数} 字典</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ EvaluationResult 收到后做什么</div>
      <div class="a">它的 <span class="inline">__post_init__</span> 把"每行一个字典"<strong>透视</strong>成"每个指标一列分数"（<span class="mono">_scores_dict</span>），再用 <span class="inline">safe_nanmean</span> 算每个指标的均值——这就是 <span class="mono">print(result)</span> 看到的 <span class="mono">{'faithfulness': 0.89, ...}</span>。<span class="inline">safe_nanmean</span> 会忽略 <span class="mono">NaN</span>，所以个别失败行不会拖垮整体均值。</div>
    </div>
  </div>
</details>

<div class="card warn">
  <div class="tag">⚠️ 为何官方转向 @experiment</div>
  从源码看，<span class="inline">evaluate()</span> 与 <span class="inline">aevaluate()</span> <strong>都会发出 <span class="mono">DeprecationWarning</span></strong>，提示"请改用 <span class="mono">@experiment</span> 装饰器"。
  评测只是"打一次分"，而实验把"改动 → 跑分 → 留痕对比"固化成闭环，更贴合工程迭代。具体用法见 <a href="08-experiment.html">第 8 课</a>。
</div>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  主流程在 <span class="mono">src/ragas/evaluation.py</span>：<span class="mono">aevaluate</span> 是 async 真实现、<span class="mono">evaluate</span> 是同步包装，二者均 <span class="mono">warnings.warn(..., DeprecationWarning)</span>；
  未传 metrics 时默认用 <span class="mono">answer_relevancy, context_precision, faithfulness, context_recall</span> 四个 RAG 指标。
  并发引擎为 <span class="mono">executor.py</span> 的 <span class="mono">Executor</span>（<span class="mono">submit</span> / <span class="mono">aresults</span>）；成绩单为 <span class="mono">dataset_schema.py</span> 的 <span class="mono">EvaluationResult</span>（<span class="mono">__post_init__</span> 透视 + <span class="mono">safe_nanmean</span> 求均值）；
  追踪树由 <span class="mono">callbacks.py</span> 的 <span class="mono">new_group</span> 按 evaluation → row 逐层建立。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>async-first</strong>：<span class="inline">aevaluate</span> 是真正的异步实现，<span class="inline">evaluate</span> 只是套了层同步外壳（必要时借 <span class="mono">nest_asyncio</span> 兼容 Jupyter）。</li>
    <li><strong>天然并发</strong>：每个"样本 × 指标"都是<strong>独立任务</strong>，提交后由 <span class="inline">Executor</span> 并发执行，再按提交顺序排回原位。</li>
    <li><strong>失败不中断整轮</strong>：单个任务抛错会被转成 <span class="mono">np.nan</span> 而非崩掉全程（默认 <span class="mono">raise_exceptions=False</span>，细节见 <a href="23-executor.html">第 23 课</a>）。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>记住生命周期 <strong>6 步</strong>：默认指标 → 规整数据 → 注入模型并 init → 拆任务提交 → 并发执行 → 汇总成 <span class="mono">EvaluationResult</span>。</li>
    <li><span class="mono">evaluate</span> / <span class="mono">aevaluate</span> <strong>均已废弃</strong>（发 <span class="mono">DeprecationWarning</span>），官方指向 <span class="mono">@experiment</span>。</li>
    <li>下一部分深入"<strong>数据与入口</strong>"：样本模型、两个 Dataset 之辨与两个入口的用法。</li>
  </ul>
</div>
"""
