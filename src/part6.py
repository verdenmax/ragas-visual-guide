"""Content for part6 — 第六部分 · 测试集生成（25-30）."""

LESSON_25 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
评测需要数据，可很多团队卡在第一步：<strong>手里只有一堆文档，却没有一份像样的测试集</strong>。
ragas 的<strong>第二大支柱</strong>就是把"造测试集"自动化——读完你的文档，自动产出一套覆盖面广、贴近真实提问的问答对，
再喂回评测线。本部分（25–30 课）就来拆解这条<strong>测试生成流水线</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  与其让老师<strong>临时人肉出几道题</strong>——出得少、还容易只考自己熟的章节，不如让机器<strong>读完整本教材</strong>，
  自动出一套<strong>覆盖全书、难度分布合理的卷子</strong>：既有"翻一页就能答"的单点题，也有"要串好几章才能答"的综合题。
  ragas 的测试生成做的正是这件事。
</div>

<h2>手写测试集的四宗罪</h2>
<p>真要给 RAG / LLM 应用做评测，第一道坎往往不是指标，而是<strong>"拿什么数据来评"</strong>。纯手写测试集有几个绕不开的麻烦：</p>

<table class="t">
  <tr><th>痛点</th><th>手写测试集</th><th>自动生成的做法</th></tr>
  <tr><td><strong>数量少</strong></td><td>一条条人肉编，几十条就累瘫</td><td>一次调用产出成百上千条</td></tr>
  <tr><td><strong>有偏差</strong></td><td>只想得到自己熟悉的问法</td><td>用 <span class="mono">persona</span> × 风格 × 长度撑开多样性</td></tr>
  <tr><td><strong>覆盖窄</strong></td><td>容易漏掉跨章节的综合题</td><td>用知识图谱找出<strong>能跨节点</strong>的多跳组合</td></tr>
  <tr><td><strong>难复现</strong></td><td>换个人重写，分布又变了</td><td>固定<strong>文档 + 流水线</strong>，可重跑可版本化</td></tr>
</table>

<h2>端到端流水线：从文档到测试集</h2>
<p>ragas 把"造测试集"拆成一条<strong>可复现的流水线</strong>，核心思路是先把文档变成一张<strong>知识图谱</strong>，再在图上"出题"：</p>
<ol>
  <li><strong>文档 → 节点</strong>：每篇文档先变成一个 <span class="inline">Node</span>（类型 <span class="mono">DOCUMENT</span>）。</li>
  <li><strong>Transforms 加工 → 知识图谱</strong>：切块、抽摘要 / 关键词 / 实体、按相似度连边，得到 <span class="inline">KnowledgeGraph</span>（<a href="26-knowledge-graph.html">第 26 课</a>、<a href="27-transforms.html">第 27 课</a>）。</li>
  <li><strong>生成 persona</strong>：从图谱里自动产出几个"虚拟提问者"（<a href="28-persona-scenario.html">第 28 课</a>）。</li>
  <li><strong>生成 scenario</strong>：按题型配比，组合出"用哪些节点、谁来问、什么风格 / 长度"的场景（<a href="29-synthesizers.html">第 29 课</a>）。</li>
  <li><strong>生成 sample</strong>：每个场景交给 synthesizer，产出一条问答样本。</li>
  <li><strong>汇总成 Testset</strong>：打包为 <span class="inline">Testset</span>，再用 <span class="mono">to_evaluation_dataset()</span> 回到评测线（<a href="30-testset-generator.html">第 30 课</a>）。</li>
</ol>

<details class="accordion">
  <summary><span class="badge-num">1</span> 这条线和"评测线"是什么关系？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两条主线如何接上</div>
      <div class="a"><a href="02-architecture.html">第 2 课</a>讲过 ragas 有<strong>两条主线</strong>：评测线（已有数据 → 打分）和测试生成线（只有文档 → 造数据）。
        测试生成线的终点 <span class="inline">Testset</span> 有个 <span class="mono">to_evaluation_dataset()</span>，产物正好是评测线的入口 <span class="inline">EvaluationDataset</span>，于是两条线无缝衔接。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 为什么要先建图，而不是直接问 LLM 出题</div>
      <div class="a">直接让 LLM"看一篇文档出几道题"只能出<strong>单篇范围</strong>的题；而把文档建成图、再找"能跨多个节点的组合"，才能稳定地造出<strong>多跳综合题</strong>，覆盖更接近真实用户的复杂提问。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  测试生成子包在 <span class="mono">src/ragas/testset/</span>。对外门面在 <span class="mono">testset/__init__.py</span>，只导出三样：
  <span class="mono">TestsetGenerator</span>、<span class="mono">Testset</span>、<span class="mono">TestsetSample</span>。
  端到端入口是 <span class="mono">testset/synthesizers/generate.py</span> 里的 <span class="mono">TestsetGenerator</span>，
  最常用方法 <span class="mono">generate_with_langchain_docs(documents, testset_size)</span> 内部再调 <span class="mono">generate()</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>把"造测试集"做成可复现流水线</strong>：从文档到 Testset 每一步都是代码，可重跑、可版本化，而不是一次性的人肉劳动。</li>
    <li><strong>从真实文档生成 → 贴近生产分布</strong>：题目来自你自己的资料，问法和难度更接近真实用户，评测结论才有参考价值。</li>
    <li><strong>与评测线无缝衔接</strong>：产物 <span class="inline">Testset</span> 一步转成 <span class="inline">EvaluationDataset</span>，直接喂给 <span class="inline">evaluate</span> / <span class="inline">@experiment</span>。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>测试生成是 ragas 的<strong>第二大支柱</strong>：从文档自动造出覆盖面广、贴近真实的问答测试集。</li>
    <li>记住流水线骨架：<strong>文档 → 知识图谱 → persona → scenario → sample → Testset</strong>。</li>
    <li>本课只搭整体心智图，后面 26–30 课逐一拆解每个零件（细节都在那里）。</li>
  </ul>
</div>
"""

LESSON_26 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
要让机器"跨章节出题"，先得让它<strong>看懂文档之间的关系</strong>。ragas 的办法是把文档拆成<strong>节点</strong>、
在节点之间连<strong>边</strong>，组成一张 <span class="mono">KnowledgeGraph</span>（知识图谱）——它是整条测试生成流水线的<strong>中枢数据结构</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把一摞文档摊开，每个知识点钉成一颗<strong>图钉（节点）</strong>，再用线把相关的图钉<strong>连起来（边）</strong>，就成了一张"知识地图"。
  想出一道综合题？顺着线找<strong>几颗连在一起的图钉</strong>就行——这正是"多跳题"的来源。
</div>

<h2>三个基本元件：Node / Relationship / NodeType</h2>
<p>知识图谱由两类东西构成——<strong>节点</strong>和<strong>边</strong>，节点还带一个<strong>类型</strong>：</p>

<table class="t">
  <tr><th>元件</th><th>是什么</th><th>关键字段 / 方法</th></tr>
  <tr><td class="mono">NodeType</td><td>节点类型枚举</td><td><span class="mono">DOCUMENT</span>（整篇）/ <span class="mono">CHUNK</span>（切出的小块）/ <span class="mono">UNKNOWN</span></td></tr>
  <tr><td class="mono">Node</td><td>图里的一个知识点</td><td><span class="mono">id</span> · <span class="mono">properties</span> · <span class="mono">type</span>；<span class="mono">add_property</span> / <span class="mono">get_property</span></td></tr>
  <tr><td class="mono">Relationship</td><td>两节点间的一条边</td><td><span class="mono">source</span> · <span class="mono">target</span> · <span class="mono">type</span> · <span class="mono">bidirectional</span></td></tr>
</table>

<pre class="code"><span class="kw">class</span> <span class="fn">NodeType</span>(str, Enum):
    UNKNOWN  = <span class="st">""</span>
    DOCUMENT = <span class="st">"document"</span>      <span class="cm"># 整篇文档</span>
    CHUNK    = <span class="st">"chunk"</span>         <span class="cm"># 切出来的小块</span>

node = Node(type=NodeType.DOCUMENT, properties={<span class="st">"page_content"</span>: text})
node.add_property(<span class="st">"summary"</span>, <span class="st">"……"</span>)   <span class="cm"># key 大小写不敏感（内部转小写）</span>
rel = Relationship(source=a, target=b, type=<span class="st">"summary_similarity"</span>, bidirectional=<span class="kw">True</span>)</pre>

<h2>KnowledgeGraph：存节点 + 存边 + 落盘</h2>
<p><span class="inline">KnowledgeGraph</span> 内部就是两个列表 <span class="mono">nodes</span> 与 <span class="mono">relationships</span>。
<span class="inline">add()</span> 会按类型自动分派，<span class="inline">save()</span> / <span class="inline">load()</span> 把整张图存成 / 读回 JSON（UTF-8）：</p>
<pre class="code">kg = KnowledgeGraph()
kg.add(node)                          <span class="cm"># add() 自动分派 Node / Relationship</span>
kg.add(rel)
kg.save(<span class="st">"kg.json"</span>)               <span class="cm"># 建图很贵，存盘后可反复复用</span>
kg = KnowledgeGraph.load(<span class="st">"kg.json"</span>)</pre>

<h2>簇查询：为"多跳出题"找组合</h2>
<p>图建好后，怎么找出"能跨多个节点一起出题"的组合？<span class="inline">KnowledgeGraph</span> 提供了三个查询方法：</p>

<table class="t">
  <tr><th>方法</th><th>返回</th><th>用途</th></tr>
  <tr><td class="mono">find_indirect_clusters</td><td>List[Set[Node]]（Leiden 社区发现 + 路径）</td><td>找间接相连的节点簇</td></tr>
  <tr><td class="mono">find_n_indirect_clusters</td><td>n 个 Set[Node]（路径，针对大图做了优化）</td><td>抽象多跳题：取 n 条跨节点路径</td></tr>
  <tr><td class="mono">find_two_nodes_single_rel</td><td>(Node, Relationship, Node) 三元组列表</td><td>具体多跳题：取"两节点 + 一条边"</td></tr>
</table>
<p>其中默认出题管道实际只用到后两个（<span class="inline">find_n_indirect_clusters</span> / <span class="inline">find_two_nodes_single_rel</span>，见 <a href="29-synthesizers.html">第 29 课</a>）；<span class="inline">find_indirect_clusters</span> 是更通用的簇发现 API，默认分布里并不直接调用。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> "indirect cluster"（间接簇）到底指什么？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一条路径就是一个簇</div>
      <div class="a">源码注释说得很直白：若图里存在 <span class="mono">A → B → C → D</span> 这条路径，则 <span class="mono">{A, B, C, D}</span> 就构成一个簇；
        若还有 <span class="mono">A → B → C → E</span>，那是另一个簇。<span class="inline">depth_limit</span> 控制路径最长几跳（默认 3）。
        这些"虽不直接相连、却经由其他节点产生关联"的节点组合，正是多跳题需要的素材。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 为什么单跳题用不到簇查询</div>
      <div class="a">单跳题只需<strong>一个</strong>节点，synthesizer 直接挑选符合条件的节点即可；只有<strong>跨节点</strong>的多跳题，才需要靠簇 / 三元组查询把"能连起来的节点"找出来（<a href="29-synthesizers.html">第 29 课</a>）。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  核心都在 <span class="mono">testset/graph.py</span>：枚举 <span class="mono">NodeType</span>、模型 <span class="mono">Node</span> / <span class="mono">Relationship</span>、
  数据类 <span class="mono">KnowledgeGraph</span>（含 <span class="mono">add</span> / <span class="mono">save</span> / <span class="mono">load</span> / <span class="mono">get_node_by_id</span> 及三个簇查询方法）。
  另有 <span class="mono">testset/graph_queries.py</span> 提供 <span class="mono">get_child_nodes</span> / <span class="mono">get_parent_nodes</span> 沿 <span class="mono">child</span> 边做层级遍历。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>用图结构承载文档关系</strong>：节点 + 边的表示天然支持单跳（单节点）与多跳（跨节点）两种出题。</li>
    <li><strong>簇查询找"可跨节点出题"的组合</strong>：<span class="inline">find_n_indirect_clusters</span> 取路径、<span class="inline">find_two_nodes_single_rel</span> 取三元组，分别服务抽象 / 具体多跳。</li>
    <li><strong>可序列化复用</strong>：<span class="inline">save</span> / <span class="inline">load</span> 把昂贵的建图结果落盘，调参出题时不必每次重建。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>知识图谱 = <strong>Node + Relationship</strong>，节点带 <span class="mono">NodeType</span>（DOCUMENT / CHUNK）。</li>
    <li><span class="inline">KnowledgeGraph</span> 是测试生成的<strong>中枢数据结构</strong>：存节点、存边、可 <span class="mono">save</span> / <span class="mono">load</span>。</li>
    <li>三个簇查询（<span class="mono">find_indirect_clusters</span> / <span class="mono">find_n_indirect_clusters</span> / <span class="mono">find_two_nodes_single_rel</span>）为多跳出题找组合。</li>
  </ul>
</div>
"""

LESSON_27 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课的知识图谱不是凭空出现的——文档刚进来时只是一堆"光秃秃的大节点"。
真正把它<strong>加工成富图</strong>（切块、抽摘要 / 关键词 / 实体、按相似度连边）的，是一组叫 <span class="mono">Transforms</span> 的变换。
本课看清这条<strong>文档加工流水线</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把建图想成一条<strong>食材加工流水线</strong>：先把大块食材<strong>切小</strong>（splitter），再给每块<strong>贴标签</strong>——摘要、关键词、实体（extractor），其间<strong>挑掉不合格的块</strong>（filter），最后把<strong>味道相近的摆到一起</strong>（relationship builder 连边）。一道道工序下来，原料才变成能直接用的"半成品"。
</div>

<h2>四类加工动作</h2>
<p>所有变换都继承自 <span class="mono">BaseGraphTransformation</span>，按职责分成四类：</p>

<table class="t">
  <tr><th>类别</th><th>干什么</th><th>代表实现</th></tr>
  <tr><td class="mono">Extractor</td><td>给节点<strong>抽属性</strong>写进 <span class="mono">properties</span></td><td><span class="mono">SummaryExtractor</span> / <span class="mono">KeyphrasesExtractor</span> / <span class="mono">TitleExtractor</span> / <span class="mono">HeadlinesExtractor</span> / <span class="mono">NERExtractor</span> / <span class="mono">ThemesExtractor</span>（均继承 <span class="mono">LLMBasedExtractor</span>）；另有 <span class="mono">EmbeddingExtractor</span> 与正则类</td></tr>
  <tr><td class="mono">Splitter</td><td>把大节点<strong>切成小块</strong></td><td><span class="mono">HeadlineSplitter</span>（按标题层级切）</td></tr>
  <tr><td class="mono">RelationshipBuilder</td><td>在节点间<strong>连边</strong></td><td><span class="mono">CosineSimilarityBuilder</span> / <span class="mono">JaccardSimilarityBuilder</span> / <span class="mono">OverlapScoreBuilder</span></td></tr>
  <tr><td class="mono">NodeFilter</td><td><strong>剔除</strong>不合格节点</td><td><span class="mono">CustomNodeFilter</span></td></tr>
</table>

<h2>Parallel 并行 + apply_transforms 执行</h2>
<p>一个 transforms 既可以是<strong>列表</strong>（按顺序逐个执行），也可以用 <span class="inline">Parallel(...)</span> 把<strong>彼此独立</strong>的几个变换打包并行跑。
真正落地是 <span class="inline">apply_transforms(kg, transforms)</span>——它<strong>就地</strong>把图加工好：</p>
<pre class="code"><span class="kw">from</span> ragas.testset.transforms <span class="kw">import</span> default_transforms, apply_transforms

trans = default_transforms(documents=docs, llm=llm, embedding_model=emb)
apply_transforms(kg, trans)             <span class="cm"># 就地把 kg 加工成"富图"</span></pre>
<p>注意：还有一个 <span class="inline">rollback_transforms</span> 作为"回滚"接口被<strong>预留</strong>了，但当前实现直接抛 <span class="mono">NotImplementedError</span>（仅是空接口，尚未实现）。</p>

<h2>default_transforms：开箱即用的标准管道</h2>
<p><span class="inline">default_transforms</span> 会按<strong>文档长度自适应</strong>地拼出一条标准管道。以"长文档"分支为例，工序顺序是：</p>
<pre class="code">transforms = [
    headline_extractor,    <span class="cm"># 抽标题层级（HeadlinesExtractor）</span>
    splitter,              <span class="cm"># HeadlineSplitter：按标题切块</span>
    summary_extractor,     <span class="cm"># 抽摘要（SummaryExtractor）</span>
    node_filter,           <span class="cm"># CustomNodeFilter：剔除低质量块</span>
    Parallel(summary_emb_extractor, theme_extractor, ner_extractor),  <span class="cm"># 并行：摘要向量 / 主题 / 实体</span>
    Parallel(cosine_sim_builder, ner_overlap_sim),                    <span class="cm"># 并行：按摘要相似度 / 实体重叠连边</span>
]</pre>
<p>文档太短（约 100 token 以下）会直接报错——没有足够内容可加工。这条默认管道<strong>开箱即用</strong>，但每个零件都能替换或重排，自己拼一条也行。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么要用 Parallel 而不是全部顺序跑？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 哪些步骤能并行</div>
      <div class="a">"抽摘要向量 / 抽主题 / 抽实体"这三件事<strong>彼此不依赖</strong>，都只读各自节点、各写一个属性，互不干扰，所以打包进同一个 <span class="inline">Parallel</span> 一起跑能省时间。
        但"先切块再抽摘要"有<strong>先后依赖</strong>（摘要要针对切好的块），就只能放在列表里按顺序排。</div>
    </div>
    <div class="qa">
      <div class="q">✅ Extractor 为什么大多是 LLM 驱动</div>
      <div class="a">摘要 / 关键词 / 标题 / 实体这些都需要"读懂内容"，所以 <span class="inline">SummaryExtractor</span> 等继承 <span class="inline">LLMBasedExtractor</span>，内部用结构化 Prompt 调 LLM（<a href="19-prompt-system.html">第 19 课</a>）；而 <span class="inline">EmbeddingExtractor</span> 走向量、正则类走规则，不必每件事都麻烦 LLM。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  四类基类在 <span class="mono">testset/transforms/base.py</span>（<span class="mono">BaseGraphTransformation</span> 及 <span class="mono">Extractor</span> / <span class="mono">LLMBasedExtractor</span> / <span class="mono">Splitter</span> / <span class="mono">RelationshipBuilder</span> / <span class="mono">NodeFilter</span>）。
  引擎 <span class="mono">transforms/engine.py</span> 提供 <span class="mono">Parallel</span> / <span class="mono">apply_transforms</span> / <span class="mono">rollback_transforms</span>（后者抛 <span class="mono">NotImplementedError</span>）。
  具体实现分布在 <span class="mono">transforms/extractors/</span>（<span class="mono">llm_based.py</span>、<span class="mono">embeddings.py</span>、<span class="mono">regex_based.py</span>）、<span class="mono">transforms/splitters/headline.py</span>、<span class="mono">transforms/relationship_builders/</span>；标准管道在 <span class="mono">transforms/default.py</span> 的 <span class="mono">default_transforms</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>可组合</strong>：四类变换都是同一基类，能像乐高一样自由拼装、替换、重排。</li>
    <li><strong>可并行</strong>：把无依赖的变换塞进 <span class="inline">Parallel</span>，<span class="inline">apply_transforms</span> 一次性并发执行，建图更快。</li>
    <li><strong>默认管道又开箱即用又可定制</strong>：<span class="inline">default_transforms</span> 按文档长度自适应给一条合理管道，不满意可整条替换。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>知识图谱是被 transforms <strong>一步步"加工"出来的</strong>，不是一次成型。</li>
    <li>四类动作：<strong>Extractor（抽属性）· Splitter（切块）· RelationshipBuilder（连边）· NodeFilter（过滤）</strong>。</li>
    <li><span class="inline">Parallel</span> 并行 + <span class="inline">apply_transforms</span> 就地执行；<span class="inline">default_transforms</span> 给一条标准管道（<span class="inline">rollback_transforms</span> 暂未实现）。</li>
  </ul>
</div>
"""
LESSON_28 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
同样一份资料，"产品经理"和"工程师"会问出完全不同的问题；同一个问题，又能用<strong>不同风格、不同长度</strong>问。
ragas 把这两层变化拆成 <span class="mono">Persona</span>（谁在问）和 <span class="mono">Scenario</span>（怎么问），用<strong>组合</strong>撑开测试集的多样性。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  出卷子前先想清楚两件事：<strong>"谁来考"</strong>——给小学生和给研究生的题肯定不一样（persona）；
  <strong>"怎么出"</strong>——同一个考点可以出成简答、出成长论述，也可以故意写得口语化甚至带点错别字（scenario 的风格 / 长度）。
  把"谁来考 × 怎么出 × 考哪些知识点"排列组合，一套题的<strong>多样性</strong>就出来了。
</div>

<h2>Persona：从图谱里长出来的"提问者"</h2>
<p>一个 <span class="inline">Persona</span> 很简单，就两字段：<span class="mono">name</span> 和 <span class="mono">role_description</span>。
关键在于它<strong>不用你手写</strong>——<span class="inline">generate_personas_from_kg</span> 会读图谱里各文档的摘要，按相似度聚类，给每个代表性摘要让 LLM 生成一个贴合内容的 persona：</p>
<pre class="code"><span class="kw">class</span> <span class="fn">Persona</span>(BaseModel):
    name: str
    role_description: str

<span class="kw">from</span> ragas.testset.persona <span class="kw">import</span> generate_personas_from_kg

personas = generate_personas_from_kg(kg=kg, llm=llm, num_personas=3)
<span class="cm"># 例：Persona(name="Digital Marketing Specialist",</span>
<span class="cm">#            role_description="Focuses on engaging audiences and growing the brand online.")</span></pre>

<h2>Scenario：一次出题的"配方"</h2>
<p>每出一道题，先要定一份<strong>配方</strong>——这就是 <span class="inline">BaseScenario</span>，四个要素：</p>
<table class="t">
  <tr><th>要素</th><th>含义</th><th>取值</th></tr>
  <tr><td class="mono">nodes</td><td>这道题用到哪些节点</td><td>单跳=1 个，多跳=多个</td></tr>
  <tr><td class="mono">persona</td><td>谁来问</td><td>来自上面生成的 persona</td></tr>
  <tr><td class="mono">style</td><td>问法风格（<span class="mono">QueryStyle</span>）</td><td>MISSPELLED · PERFECT_GRAMMAR · POOR_GRAMMAR · WEB_SEARCH_LIKE</td></tr>
  <tr><td class="mono">length</td><td>问句长度（<span class="mono">QueryLength</span>）</td><td>SHORT · MEDIUM · LONG</td></tr>
</table>
<p>具体的 synthesizer 会在 <span class="inline">BaseScenario</span> 上再加自己的字段——比如单跳加 <span class="mono">term</span>（主题词）、多跳加 <span class="mono">combinations</span>（跨节点的概念组合）。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 多样性为什么靠"组合"而不是靠提示词？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一道题 = 一个组合</div>
      <div class="a">把 <strong>persona × style × length × nodes</strong> 排列组合，每一种组合就对应一道<strong>风味不同</strong>的题：
        "营销专员 + 口语化 + 短问句 + 节点A" 和 "工程师 + 规范语法 + 长问句 + 节点A、B" 会问出截然不同的东西。
        多样性是<strong>结构化、可枚举、可控</strong>的，而不是靠一句"请多样化一点"碰运气。</div>
    </div>
    <div class="qa">
      <div class="q">✅ persona 为什么要从 KG 生成</div>
      <div class="a">硬编码的 persona（"好奇的用户"）与你的资料未必搭。从图谱摘要聚类生成，能得到<strong>贴合文档主题</strong>的提问者（金融文档→分析师、营销文档→营销专员），出的题自然更对路。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  <span class="mono">testset/persona.py</span> 定义 <span class="mono">Persona</span>、<span class="mono">PersonaGenerationPrompt</span> 和 <span class="mono">generate_personas_from_kg</span>（按 <span class="mono">summary_embedding</span> 余弦相似度聚类，取代表性摘要并行生成）。
  <span class="mono">testset/synthesizers/base.py</span> 定义 <span class="mono">BaseScenario</span>（<span class="mono">nodes</span> / <span class="mono">style</span> / <span class="mono">length</span> / <span class="mono">persona</span>）、枚举 <span class="mono">QueryStyle</span> 与 <span class="mono">QueryLength</span>，以及出题基类 <span class="mono">BaseSynthesizer</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>多样性可控</strong>：<span class="inline">persona × style × length</span> 是结构化组合，能枚举、能配比，而不是听天由命。</li>
    <li><strong>persona 从 KG 自动产出</strong>：贴合你文档的真实主题，比硬编码角色更接地气。</li>
    <li><strong>scenario 与 synthesizer 解耦</strong>：基类只管"配方四要素"，各题型在其上叠加自己的字段，扩展新题型很顺手。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="inline">Persona</span> = <strong>name + role_description</strong>，由 <span class="inline">generate_personas_from_kg</span> 从图谱自动生成。</li>
    <li><span class="inline">Scenario</span> = <strong>nodes + style + length + persona</strong>，是"出一道题"的配方。</li>
    <li>多样性 = <strong>persona + 风格 + 长度</strong>（再乘上节点）的组合，可控可枚举。</li>
  </ul>
</div>
"""

LESSON_29 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
有了知识图谱、persona 和 scenario 配方，谁来真正"出题"？答案是 <span class="mono">Synthesizer</span>（合成器 / 出题官）。
ragas 区分<strong>单跳</strong>（一个节点）和<strong>多跳</strong>（跨节点推理）两类，并按比例自动分配题量。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把出题交给两类<strong>出题官</strong>：一类专出<strong>单跳题</strong>——翻一页、对着一个知识点就能答；
  另一类专出<strong>多跳题</strong>——必须把好几页串起来推理才能答。教务处（<span class="inline">default_query_distribution</span>）再按比例把题量分给他们。
</div>

<h2>两类出题官：单跳 vs 多跳</h2>
<table class="t">
  <tr><th>Synthesizer</th><th>用几个节点</th><th>靠什么找组合</th><th>题型</th></tr>
  <tr><td class="mono">SingleHopSpecificQuerySynthesizer</td><td>单节点</td><td><span class="mono">get_node_clusters</span> 选含 <span class="mono">entities</span> 的 chunk</td><td>具体 · 单跳</td></tr>
  <tr><td class="mono">MultiHopAbstractQuerySynthesizer</td><td>多节点（路径）</td><td><span class="mono">find_n_indirect_clusters</span>（<span class="mono">summary_similarity</span> 边）</td><td>抽象 · 多跳</td></tr>
  <tr><td class="mono">MultiHopSpecificQuerySynthesizer</td><td>两节点 + 一条边</td><td><span class="mono">find_two_nodes_single_rel</span>（<span class="mono">entities_overlap</span> 边）</td><td>具体 · 多跳</td></tr>
</table>
<p>单跳与多跳分别有自己的场景类 <span class="inline">SingleHopScenario</span>（带 <span class="mono">term</span>）和 <span class="inline">MultiHopScenario</span>（带 <span class="mono">combinations</span>），都继承自第 28 课的 <span class="inline">BaseScenario</span>。</p>

<h2>两步出题：generate_scenarios → generate_sample</h2>
<p>每个 synthesizer 出题都分<strong>两步</strong>，由基类 <span class="inline">BaseSynthesizer</span> 统一编排：</p>
<pre class="code"><span class="cm"># ① 场景生成：先决定"出哪些题"——挑节点、配 persona / 风格 / 长度</span>
scenarios = <span class="kw">await</span> synth.generate_scenarios(n=5, knowledge_graph=kg, persona_list=personas)

<span class="cm"># ② 样本生成：再决定"题面长啥样"——按场景调 LLM 产出问答对</span>
sample = <span class="kw">await</span> synth.generate_sample(scenarios[0])</pre>
<p>这一拆分把"<strong>出哪些题</strong>"和"<strong>题面怎么写</strong>"解耦：场景阶段只在图上做组合与采样（便宜、可控），样本阶段才真正花 LLM 调用把问答写出来。</p>

<h2>default_query_distribution：自动按图能力配题型</h2>
<p>不指定题型配比时，<span class="inline">default_query_distribution</span> 默认给上面三种 synthesizer <strong>等概率</strong>。
但它会先用每个 synthesizer 的 <span class="mono">get_node_clusters</span> 探一探：<strong>图谱撑不起的题型直接剔除</strong>：</p>
<pre class="code"><span class="kw">from</span> ragas.testset.synthesizers <span class="kw">import</span> default_query_distribution

dist = default_query_distribution(llm, kg)
<span class="cm"># 对每个候选 synthesizer 调 get_node_clusters(kg)；非空才保留</span>
<span class="cm"># 保留下来的等概率：例如三种都可用 → 各 1/3</span></pre>
<p>所以如果你的文档之间几乎没有可连的边，多跳题型就会被自动跳过，不会硬出一堆无效的多跳题。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> "abstract" 和 "specific" 多跳有什么区别？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 看它们靠什么边找组合</div>
      <div class="a"><strong>抽象多跳</strong>（<span class="inline">MultiHopAbstract…</span>）沿 <span class="mono">summary_similarity</span> 边、用 <span class="inline">find_n_indirect_clusters</span> 取一条<strong>路径</strong>，问的是跨多段、偏综合 / 解释性的问题；
        <strong>具体多跳</strong>（<span class="inline">MultiHopSpecific…</span>）沿 <span class="mono">entities_overlap</span> 边、用 <span class="inline">find_two_nodes_single_rel</span> 取<strong>两节点 + 边</strong>，问的是依赖具体事实拼接的问题。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 默认为什么没有"单跳抽象"题</div>
      <div class="a">默认分布里只放了 <span class="inline">SingleHopSpecificQuerySynthesizer</span>（单跳具体）。其实 ragas <strong>单跳只实现了"具体"这一种</strong>——abstract / specific 的区分<strong>只用于多跳</strong>，并没有现成的"单跳抽象"类。你可以自定义 <span class="inline">QueryDistribution</span> 调整这三种内置题型的配比，或自行实现新题型。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  默认配比在 <span class="mono">testset/synthesizers/__init__.py</span> 的 <span class="mono">default_query_distribution</span>（类型别名 <span class="mono">QueryDistribution</span>）。
  两步编排在 <span class="mono">synthesizers/base.py</span>（<span class="mono">BaseSynthesizer.generate_scenarios</span> / <span class="mono">generate_sample</span>）。
  单跳在 <span class="mono">synthesizers/single_hop/specific.py</span>（<span class="mono">SingleHopSpecificQuerySynthesizer</span>、<span class="mono">get_node_clusters</span>）；
  多跳在 <span class="mono">synthesizers/multi_hop/abstract.py</span> 与 <span class="mono">multi_hop/specific.py</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>两步解耦</strong>："场景生成"（图上组合采样，便宜）与"样本生成"（LLM 写题面，贵）分开，便于调试与并发。</li>
    <li><strong>按图能力配题型</strong>：<span class="inline">default_query_distribution</span> 先用 <span class="inline">get_node_clusters</span> 过滤掉图谱撑不起的题型，避免无效出题。</li>
    <li><strong>题型可插拔</strong>：单跳 / 多跳都继承统一基类，自定义 <span class="inline">QueryDistribution</span> 即可增删题型、调整配比。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>题型由 synthesizer 决定：<strong>单跳具体 · 多跳抽象 · 多跳具体</strong>三种默认。</li>
    <li>出题分两步：<strong>generate_scenarios（出哪些题）→ generate_sample（写题面）</strong>。</li>
    <li>配比由 <span class="inline">default_query_distribution</span> 给（默认等概率），并自动剔除图谱撑不起的题型。</li>
  </ul>
</div>
"""

LESSON_30 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前面五课的零件——知识图谱、transforms、persona、scenario、synthesizer——到这里被 <span class="mono">TestsetGenerator</span> <strong>串成一条龙</strong>：
投入一堆文档，产出一套<strong>可直接评测</strong>的测试集。本课走通这条端到端流水线。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  <span class="inline">TestsetGenerator</span> 像一台<strong>全自动出卷机</strong>：你把教材（文档）塞进去，按一下"出 10 道题"的按钮，
  它内部依次完成<strong>建图 → 设定考生 → 排题 → 写题</strong>，最后吐出一份装订好的卷子——还能<strong>一键转成</strong>评测线认得的格式。
</div>

<h2>一行调用的背后</h2>
<p>最常见的用法只有三行——构造生成器、喂文档出题、转成评测数据集：</p>
<pre class="code"><span class="kw">from</span> ragas.testset <span class="kw">import</span> TestsetGenerator

generator = TestsetGenerator(llm=generator_llm, embedding_model=generator_embeddings)
dataset = generator.generate_with_langchain_docs(docs, testset_size=10)

eval_dataset = dataset.to_evaluation_dataset()   <span class="cm"># 回到评测线（EvaluationDataset）</span></pre>
<p>除了 <span class="inline">generate_with_langchain_docs</span>，还有 <span class="inline">from_langchain</span> / <span class="inline">from_llama_index</span> 两个类方法帮你包好 LLM 与 embedding，以及面向 LlamaIndex 文档、预切块文档的对应入口。</p>

<h2>generate() 的内部流程</h2>
<p><span class="inline">generate_with_langchain_docs</span> 先把文档转成节点、<span class="inline">apply_transforms</span> 建好图，再调 <span class="inline">generate()</span>。后者的步骤是：</p>
<ol>
  <li><strong>定题型配比</strong>：没传就用 <span class="inline">default_query_distribution(llm, kg)</span>（<a href="29-synthesizers.html">第 29 课</a>）。</li>
  <li><strong>生成 persona</strong>：<span class="inline">generate_personas_from_kg</span>（默认 <span class="mono">num_personas=3</span>）。</li>
  <li><strong>切份额</strong>：<span class="inline">calculate_split_values</span> 按配比把 <span class="mono">testset_size</span> 分给每个 synthesizer（向上取整）。</li>
  <li><strong>Scenario Generation</strong>：开一个 <span class="inline">Executor</span> 并发跑各 synthesizer 的 <span class="mono">generate_scenarios</span>。</li>
  <li><strong>Sample Generation</strong>：再开一个 <span class="inline">Executor</span> 并发跑 <span class="mono">generate_sample</span>，把每个场景写成问答。</li>
  <li><strong>打包</strong>：每条样本包成 <span class="inline">TestsetSample</span>（带 <span class="mono">synthesizer_name</span>），汇总为 <span class="inline">Testset</span>。</li>
</ol>
<p>两个阶段各自用 <span class="inline">new_group</span> 起了名为 <span class="mono">"Scenario Generation"</span> 和 <span class="mono">"Sample Generation"</span> 的回调组，便于在追踪里<strong>分阶段</strong>看进度与耗时（<a href="24-callbacks-cost-cache.html">第 24 课</a>）。</p>

<h2>产物 Testset：可直接评测</h2>
<p><span class="inline">Testset</span> 装着一串 <span class="inline">TestsetSample</span>，提供两个衔接评测线的关键方法：</p>
<table class="t">
  <tr><th>方法</th><th>作用</th></tr>
  <tr><td class="mono">to_evaluation_dataset()</td><td>转成 <span class="mono">EvaluationDataset</span>，直接喂给 <span class="mono">evaluate</span> / <span class="mono">@experiment</span>（<a href="06-two-datasets.html">第 6</a>、<a href="07-evaluate.html">7</a>、<a href="08-experiment.html">8 课</a>）</td></tr>
  <tr><td class="mono">from_annotated(path)</td><td>从人工标注的 JSON 里只挑 <span class="mono">approved</span> 的样本，组成精选 Testset</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么要分"两个 Executor 阶段"？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 先全量出场景，再全量写题</div>
      <div class="a">第一阶段把<strong>所有 synthesizer 的场景</strong>都生成完、收齐，第二阶段才统一把这些场景<strong>并发写成样本</strong>。
        这样每个阶段内部都能吃满并发（<a href="23-executor.html">第 23 课</a>的 <span class="inline">Executor</span>），阶段之间用 <span class="inline">new_group</span> 分隔，出错时也能定位是"排题"还是"写题"出的问题。</div>
    </div>
    <div class="qa">
      <div class="q">✅ to_evaluation_dataset() 丢掉了什么</div>
      <div class="a">它只取每个样本的 <span class="mono">eval_sample</span>（真正用于评测的问 / 答 / 上下文），把 <span class="mono">synthesizer_name</span> 这类"出题元信息"留在 Testset 里。评测只关心问答本身，元信息用于分析来源分布。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  端到端入口在 <span class="mono">testset/synthesizers/generate.py</span>：<span class="mono">TestsetGenerator</span>（<span class="mono">from_langchain</span> / <span class="mono">from_llama_index</span>、<span class="mono">generate_with_langchain_docs</span>、<span class="mono">generate</span>），
  内部用 <span class="mono">Executor</span> + <span class="mono">new_group("Scenario Generation")</span> / <span class="mono">new_group("Sample Generation")</span>；份额计算 <span class="mono">calculate_split_values</span> 在 <span class="mono">synthesizers/utils.py</span>。
  数据模型在 <span class="mono">synthesizers/testset_schema.py</span>：<span class="mono">TestsetSample</span>、<span class="mono">Testset</span>（<span class="mono">to_evaluation_dataset</span> / <span class="mono">from_annotated</span>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>端到端并发 + 分阶段追踪</strong>：用 <span class="inline">Executor</span> 吃满并发，<span class="inline">new_group</span> 把"场景 / 样本"两阶段拆开，进度与成本一目了然。</li>
    <li><strong>Testset → EvaluationDataset 无缝衔接</strong>：一个 <span class="inline">to_evaluation_dataset()</span> 把测试生成线接回评测线，两条主线在此合龙。</li>
    <li><strong>留人工复核的口子</strong>：<span class="inline">from_annotated</span> 支持"机器出题 + 人工审核挑 approved"，自动化与质量把关兼得。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>一行 <span class="inline">generate_with_langchain_docs</span> 背后是<strong>整条流水线</strong>：transforms → KG → persona → scenario → sample → Testset。</li>
    <li><span class="inline">generate()</span> 用两个 <span class="inline">Executor</span> 阶段（<strong>Scenario / Sample</strong>）并发出题。</li>
    <li>产物 <span class="inline">Testset</span> 一步 <span class="inline">to_evaluation_dataset()</span> 即可<strong>直接评测</strong>，两条主线在此闭环。</li>
  </ul>
</div>
"""
