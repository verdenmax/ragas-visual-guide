"""Content for part8."""

LESSON_38 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
毕业课。前面 37 课拆过的零件——数据模型、指标、Prompt、引擎、测试生成、实验——在这一课<strong>合流成一条完整的 RAG 评测流水线</strong>：
从一堆文档出发，自动造测试集、选指标、用 <span class="inline">@experiment</span> 跑分留痕，再读结果迭代。走通这一条，你就握住了全书的主线。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  这一课像一份<strong>毕业设计</strong>：把散落各课的零件拼成一台能跑的机器——
  <strong>出卷机</strong>（<span class="inline">TestsetGenerator</span>）自动出题，<strong>体检仪</strong>（RAG 四件套）逐项打分，
  <strong>实验台</strong>（<span class="inline">@experiment</span>）记录每次改动前后的成绩。答辩要点只有一句：评测不是一次性打分，而是<strong>改 → 跑 → 比</strong>的闭环。
</div>

<h2>六步走完一条评测流水线</h2>
<p>一个 RAG 问答应用要管好<strong>检索 + 生成</strong>两端。下面六步把全书能力串起来，每一步都能回看对应章节：</p>

<table class="t">
  <tr><th>步骤</th><th>做什么</th><th>关键 API</th><th>回看</th></tr>
  <tr><td><strong>① 场景设定</strong></td><td>选定要评测的 RAG：用户问题 → 检索 → 生成</td><td class="mono">—</td><td><a href="01-what-is-ragas.html">第 1 课</a>、<a href="03-evaluation-lifecycle.html">第 3 课</a></td></tr>
  <tr><td><strong>② 造测试集</strong></td><td>喂文档自动出题，得到带标准答案的 Testset</td><td class="mono">generate_with_langchain_docs</td><td><a href="25-testgen-overview.html">第 25 课</a>、<a href="30-testset-generator.html">第 30 课</a></td></tr>
  <tr><td><strong>③ 转评测集</strong></td><td>把 Testset 汇入评测线的 EvaluationDataset</td><td class="mono">to_evaluation_dataset</td><td><a href="06-two-datasets.html">第 6 课</a>、<a href="30-testset-generator.html">第 30 课</a></td></tr>
  <tr><td><strong>④ 选指标</strong></td><td>挑 RAG 四件套，盯紧检索与生成两端</td><td class="mono">ragas.metrics.collections</td><td><a href="10-rag-metrics.html">第 10 课</a></td></tr>
  <tr><td><strong>⑤ 跑评测</strong></td><td>对每行：调你的 RAG → 用指标打分 → 落盘留痕</td><td class="mono">@experiment · arun</td><td><a href="08-experiment.html">第 8 课</a>、<a href="31-experiments-deep.html">第 31 课</a></td></tr>
  <tr><td><strong>⑥ 读结果迭代</strong></td><td>看分数与理由，定位薄弱、改 prompt/检索、再跑对比</td><td class="mono">.value · .reason</td><td><a href="14-metric-result.html">第 14 课</a>、<a href="31-experiments-deep.html">第 31 课</a></td></tr>
</table>

<h2>把零件接起来</h2>
<p>测试生成线的终点 <span class="inline">Testset</span>，一步 <span class="inline">to_evaluation_dataset()</span> 就汇入评测线——这正是<strong>两条主线的合流点</strong>。
要注意：测试集只给了 <span class="mono">user_input</span> + <span class="mono">reference</span>（问题 + 标准答案），你应用真实的 <span class="mono">response</span> / <span class="mono">retrieved_contexts</span> 得<strong>现跑你的 RAG</strong> 才有。
现代做法是把这步放进 <span class="inline">@experiment</span> 函数里，边跑边打分：</p>

<pre class="code"><span class="kw">from</span> ragas.testset <span class="kw">import</span> TestsetGenerator
<span class="kw">from</span> ragas.metrics.collections <span class="kw">import</span> (
    Faithfulness, ContextPrecision, ContextRecall, AnswerRelevancy,
)
<span class="kw">from</span> ragas <span class="kw">import</span> experiment, evaluate

<span class="cm"># ② 造测试集：文档 → Testset（第 25、30 课）</span>
generator = TestsetGenerator(llm=gen_llm, embedding_model=gen_emb)
testset = generator.generate_with_langchain_docs(docs, testset_size=10)

<span class="cm"># ③ 汇流：Testset → EvaluationDataset（第 6、30 课）；经典 evaluate() 直接吃它</span>
eval_dataset = testset.to_evaluation_dataset()

<span class="cm"># ④ 选指标：现代 collections 路径，注入裁判 LLM / embeddings（第 10 课）</span>
faith = Faithfulness(llm=eval_llm)
cprec = ContextPrecision(llm=eval_llm)
crec  = ContextRecall(llm=eval_llm)
arel  = AnswerRelevancy(llm=eval_llm, embeddings=emb)

<span class="cm"># ⑤ 跑评测：对每行 → 调你的 RAG → 打分 → 留痕（第 8、31 课）</span>
<span class="kw">@</span><span class="fn">experiment</span>()
<span class="kw">async def</span> <span class="fn">run_eval</span>(row):
    answer, contexts = my_rag(row[<span class="st">"user_input"</span>])          <span class="cm"># 你的 RAG：检索 + 生成（占位）</span>
    f = <span class="kw">await</span> faith.ascore(user_input=row[<span class="st">"user_input"</span>], response=answer, retrieved_contexts=contexts)
    p = <span class="kw">await</span> cprec.ascore(user_input=row[<span class="st">"user_input"</span>], reference=row[<span class="st">"reference"</span>], retrieved_contexts=contexts)
    c = <span class="kw">await</span> crec.ascore(user_input=row[<span class="st">"user_input"</span>], retrieved_contexts=contexts, reference=row[<span class="st">"reference"</span>])
    a = <span class="kw">await</span> arel.ascore(user_input=row[<span class="st">"user_input"</span>], response=answer)
    <span class="kw">return</span> {**row, <span class="st">"response"</span>: answer,
            <span class="st">"faithfulness"</span>: f.value, <span class="st">"context_precision"</span>: p.value,
            <span class="st">"context_recall"</span>: c.value, <span class="st">"answer_relevancy"</span>: a.value}          <span class="cm"># 这一行会被落盘留痕</span>

<span class="cm"># golden：把测试集的"问题 + 标准答案"放进带 backend 的 ragas Dataset（第 6、8 课）</span>
v1 = <span class="kw">await</span> run_eval.arun(golden, name=<span class="st">"v1-baseline"</span>)    <span class="cm"># 并发跑、自动落盘</span>

<span class="cm"># 经典路径（第 7 课）：evaluate() 只收旧版 ragas.metrics 指标（传统 Metric 体系），</span>
<span class="cm"># 不认上面的 collections 指标——传进去会直接 raise TypeError，这是"两代基类"之别（第 13 课）。</span>
<span class="cm"># 要走经典路径就换一套导入（旧版单例本就是传统 Metric）：</span>
<span class="cm"># from ragas.metrics import faithfulness, context_recall, answer_relevancy</span>
<span class="cm"># result = evaluate(dataset=eval_dataset, metrics=[faithfulness, context_recall, answer_relevancy], llm=eval_llm, embeddings=emb)</span></pre>

<p>被 <span class="inline">@experiment</span> 装饰的函数只描述"对一行做什么"，<span class="inline">arun</span> 负责并发跑整张表、把每行结果存进 backend（<a href="08-experiment.html">第 8 课</a>）。
经典 <span class="inline">evaluate()</span>（<a href="07-evaluate.html">第 7 课</a>）则要求数据集里 <span class="mono">response</span> / <span class="mono">retrieved_contexts</span> 已经备齐，适合"一次性算个分"。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 三个容易卡住的接缝：response 哪来 · 选哪条入口 · 怎么对比两版 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 测试集没有 response，分怎么打？</div>
      <div class="a"><span class="inline">to_evaluation_dataset()</span> 带来的是 golden：<span class="mono">user_input</span> + <span class="mono">reference</span>（再加 <span class="mono">reference_contexts</span>）。
        你应用真实的 <span class="mono">response</span> 和 <span class="mono">retrieved_contexts</span> 必须<strong>现跑你的 RAG</strong> 得到——所以才把"调 RAG"放进 <span class="inline">@experiment</span> 函数里，边跑边打分。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 用 @experiment 还是 evaluate()？</div>
      <div class="a">要"改 → 跑 → 比"的可持续迭代、每版留痕，用 <span class="inline">@experiment</span>（推荐，<a href="31-experiments-deep.html">第 31 课</a>）；
        只想对一份已填好的数据集<strong>快速算个总分</strong>，用经典 <span class="inline">evaluate()</span>（已废弃但仍可用，<a href="07-evaluate.html">第 7 课</a>）。
        注意<strong>两条入口各配一代指标</strong>：<span class="inline">@experiment</span> 里直接 <span class="mono">await</span> 现代 <span class="inline">collections</span> 指标的 <span class="inline">ascore()</span>；经典 <span class="inline">evaluate()</span> 只收旧版 <span class="mono">ragas.metrics</span> 指标（传统 <span class="mono">Metric</span> 体系），把 collections 指标传进去会直接报 <span class="mono">TypeError</span>——这正是"两代基类"之别（<a href="13-metric-base.html">第 13 课</a>）。</div>
    </div>
    <div class="qa">
      <div class="q">🔁 怎么对比两版改动？</div>
      <div class="a">改完 prompt / 检索，换个名字再跑一轮：<span class="inline">await run_eval.arun(golden, name="v2-rerank")</span>。
        两个实验各自落盘成一张表，并排看平均分与逐行打分理由，就知道这次改动是涨是跌（<a href="08-experiment.html">第 8 课</a>）。</div>
    </div>
  </div>
</details>

<h2>读结果 → 定位薄弱 → 再跑一轮</h2>
<p>最后一步才是评测的价值所在。拿到实验表后，按这个顺序闭环：</p>
<ol>
  <li><strong>看分数分布</strong>：哪条指标整体偏低？是检索端（ContextPrecision / ContextRecall）还是生成端（Faithfulness / AnswerRelevancy）？</li>
  <li><strong>逐行读理由</strong>：每个 <span class="inline">MetricResult</span> 都带打分 <span class="mono">reason</span>（<a href="14-metric-result.html">第 14 课</a>），定位是检索没召回、还是生成跑偏。</li>
  <li><strong>对症改一处</strong>：检索弱就调 chunk / 重排，生成飘就改 prompt——一次只动一个变量，方便归因。</li>
  <li><strong>换名再跑、并排比</strong>：<span class="inline">arun(..., name="v2")</span> 再来一轮，与上一版对比，确认改动确实让分数往上走（<a href="31-experiments-deep.html">第 31 课</a>）。</li>
</ol>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  这条流水线串起四个文件：<span class="mono">testset/synthesizers/generate.py</span>（<span class="mono">TestsetGenerator.generate_with_langchain_docs</span> → <span class="mono">Testset</span>）；
  <span class="mono">testset/synthesizers/testset_schema.py</span>（<span class="mono">Testset.to_evaluation_dataset()</span> 取每个样本的 <span class="mono">eval_sample</span> 组成 <span class="mono">EvaluationDataset</span>）；
  <span class="mono">metrics/collections/</span> 下各 <span class="mono">&lt;name&gt;/metric.py</span>（<span class="mono">Faithfulness</span> / <span class="mono">ContextPrecision</span> / <span class="mono">ContextRecall</span> / <span class="mono">AnswerRelevancy</span>，统一 <span class="mono">await ascore(...)</span>）；
  <span class="mono">experiment.py</span>（<span class="mono">@experiment</span> 装饰器返回 <span class="mono">ExperimentWrapper</span>，<span class="mono">arun</span> 并发跑 + 落盘）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>两条主线一处合流</strong>：测试生成线（文档 → <span class="inline">Testset</span>）与评测线（指标 → 分数）靠 <span class="inline">to_evaluation_dataset()</span> 一步对接，全书前 37 课的能力在此汇成一条龙。</li>
    <li><strong>@experiment 把评测闭环成迭代</strong>：把"调 RAG + 打分"写成一个函数，<span class="inline">arun</span> 并发跑、自动留痕，"改 → 跑 → 比"得以可持续滚动，而非算完就丢。</li>
    <li><strong>两代指标各配入口</strong>：现代 collections 四件套都是 <span class="inline">await ascore(...)</span>，配 <span class="inline">@experiment</span> 留痕迭代；要对已填好的数据集快速算总分，则改用经典 <span class="inline">evaluate()</span> + 旧版 <span class="mono">ragas.metrics</span> 指标——两代基类不通用，别混着传（<a href="13-metric-base.html">第 13 课</a>）。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>端到端六步：<strong>场景 → 造测试集 → 转评测集 → 选指标 → 跑评测 → 读结果迭代</strong>，正好把全书主线走了一遍。</li>
    <li>记住合流点：<span class="inline">generate_with_langchain_docs</span> 出 <span class="inline">Testset</span>，<span class="inline">to_evaluation_dataset()</span> 接回评测线；而 <span class="mono">response</span> / <span class="mono">retrieved_contexts</span> 要现跑你的 RAG 才有。</li>
    <li>评测是<strong>工程闭环</strong>，不是一次性打分：用 <span class="inline">@experiment</span> 让"改 → 跑 → 比"持续滚动，分数才会真的往上走。</li>
    <li>🎓 <strong>全书结业</strong>——从"我觉得还行"到"数据说它从 0.72 涨到 0.81"，你已握住 ragas 的全套手艺。去给你的 RAG 跑第一条真实的评测流水线吧！</li>
  </ul>
</div>
"""
