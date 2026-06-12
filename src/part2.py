"""Content for part2 — 第二部分 · 数据与入口（04-08）."""

LESSON_04 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
<span class="inline">SingleTurnSample</span> 是 ragas 里最小的数据单位——把"一问一答"的全部证据塞进一个 pydantic 模型：
问题、参考资料、标准答案、模型作答……一行就是一道题。本课认清它的字段语义，以及它如何汇成 <span class="inline">EvaluationDataset</span>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  一行 <span class="inline">SingleTurnSample</span> 就像一张<strong>考卷</strong>：<strong>题目</strong>是 <span class="inline">user_input</span>，
  <strong>允许翻阅的参考资料</strong>是 <span class="inline">retrieved_contexts</span>，<strong>标准答案</strong>是 <span class="inline">reference</span>，
  <strong>考生的作答</strong>是 <span class="inline">response</span>。阅卷（评测）时，老师正是对照这几栏来打分。
</div>

<h2>一行样本 = 一张考卷</h2>
<p><span class="inline">SingleTurnSample</span> 的字段<strong>全部是 Optional</strong>（默认 <span class="inline">None</span>），所以同一个模型能适配不同指标——缺哪栏就空着：</p>

<table class="t">
  <tr><th>字段</th><th>类型</th><th>一句话含义</th></tr>
  <tr><td class="mono">user_input</td><td class="mono">Optional[str]</td><td>用户的问题 / 查询（考题）</td></tr>
  <tr><td class="mono">retrieved_contexts</td><td class="mono">Optional[List[str]]</td><td>检索到的上下文（考生翻到的资料）</td></tr>
  <tr><td class="mono">reference_contexts</td><td class="mono">Optional[List[str]]</td><td>应当检索到的参考上下文（标准资料）</td></tr>
  <tr><td class="mono">retrieved_context_ids</td><td class="mono">Optional[List[Union[str, int]]]</td><td>检索上下文的 ID（按 ID 比对召回）</td></tr>
  <tr><td class="mono">reference_context_ids</td><td class="mono">Optional[List[Union[str, int]]]</td><td>参考上下文的 ID</td></tr>
  <tr><td class="mono">response</td><td class="mono">Optional[str]</td><td>模型生成的回答（考生作答）</td></tr>
  <tr><td class="mono">multi_responses</td><td class="mono">Optional[List[str]]</td><td>同一问题的多个候选回答</td></tr>
  <tr><td class="mono">reference</td><td class="mono">Optional[str]</td><td>参考答案 / ground truth（标准答案）</td></tr>
  <tr><td class="mono">rubrics</td><td class="mono">Optional[Dict[str, str]]</td><td>打分细则（rubric 评分用）</td></tr>
  <tr><td class="mono">persona_name</td><td class="mono">Optional[str]</td><td>生成该问题时所用的画像名（测试集生成元信息）</td></tr>
  <tr><td class="mono">query_style</td><td class="mono">Optional[str]</td><td>问题风格（如 formal / casual）</td></tr>
  <tr><td class="mono">query_length</td><td class="mono">Optional[str]</td><td>问题长度档（如 short / medium / long）</td></tr>
</table>

<p>不同指标只挑自己要的栏：<span class="inline">Faithfulness</span> 需要 <span class="inline">user_input</span> + <span class="inline">response</span> + <span class="inline">retrieved_contexts</span>；
<span class="inline">ContextRecall</span> 还要 <span class="inline">reference</span>。缺列会在校验阶段直接报错（哪个指标缺哪列，<a href="10-rag-metrics.html">第 10 课</a>细讲）。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> BaseSample 的三件套：to_dict / get_features / to_string <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 to_dict 自动丢掉 None</div>
      <div class="a"><span class="inline">to_dict()</span> 实际是 <span class="mono">model_dump(exclude_none=True)</span>——只保留你填了的字段，样本因此"按需带列"：
<pre class="code"><span class="kw">from</span> ragas <span class="kw">import</span> SingleTurnSample

sample = SingleTurnSample(
    user_input=<span class="st">"谁写了《哈姆雷特》？"</span>,
    response=<span class="st">"莎士比亚。"</span>,
    reference=<span class="st">"威廉·莎士比亚"</span>,
)
sample.to_dict()       <span class="cm"># 只含这 3 个字段，其余 None 全部丢弃</span>
sample.get_features()  <span class="cm"># ['user_input', 'response', 'reference']</span></pre>
      </div>
    </div>
    <div class="qa">
      <div class="q">✅ get_features / to_string 的用处</div>
      <div class="a"><span class="inline">get_features()</span> 返回"非 None 字段名"列表——校验"指标要的列在不在"时正是看它；<span class="inline">to_string()</span> 把样本拼成可读文本，便于打印调试。三件套都定义在基类 <span class="inline">BaseSample</span> 上，单轮 / 多轮样本共享。</div>
    </div>
  </div>
</details>

<h2>从样本到数据集：EvaluationDataset</h2>
<p>把一堆样本装进 <span class="inline">EvaluationDataset</span>，就得到喂给评测的"一叠考卷"。它继承自抽象基类 <span class="inline">RagasDataset</span>，后者统一实现了一层<strong>转换器</strong>，让数据在多种格式间自由进出：</p>

<table class="t">
  <tr><th>转换器</th><th>作用</th></tr>
  <tr><td class="mono">to_pandas() / from_pandas(df)</td><td>与 pandas DataFrame 互转</td></tr>
  <tr><td class="mono">to_hf_dataset() / from_hf_dataset(ds)</td><td>与 HuggingFace Dataset 互转</td></tr>
  <tr><td class="mono">to_csv(path) / to_jsonl(path) / from_jsonl(path)</td><td>落盘成 CSV / JSONL，或从 JSONL 读回</td></tr>
  <tr><td class="mono">from_list(data) / from_dict(mapping)</td><td>从原始 dict 列表 / 字典构造（自动判断单轮 or 多轮）</td></tr>
</table>

<p><span class="inline">from_list</span> 会看每行的 <span class="inline">user_input</span> 是不是列表：是 → 当作 <span class="inline">MultiTurnSample</span>（<a href="05-multi-turn-sample.html">第 5 课</a>），否则当作 <span class="inline">SingleTurnSample</span>。<span class="inline">to_list</span> 则反过来把样本批量 <span class="inline">to_dict</span>（同样丢弃 None）。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  全部在 <span class="mono">src/ragas/dataset_schema.py</span>：基类 <span class="mono">BaseSample</span> 提供 <span class="mono">to_dict</span>（<span class="mono">model_dump(exclude_none=True)</span>）/ <span class="mono">get_features</span> / <span class="mono">to_string</span>；
  <span class="mono">SingleTurnSample</span> 的 12 个字段全为 <span class="mono">Optional</span>；转换器层在抽象基类 <span class="mono">RagasDataset</span>（<span class="mono">to_pandas</span> / <span class="mono">from_hf_dataset</span> / <span class="mono">to_csv</span> / <span class="mono">to_jsonl</span> / <span class="mono">from_list</span> …），
  <span class="mono">EvaluationDataset</span> 是其具体子类（<span class="mono">to_list</span> / <span class="mono">from_list</span> 自动分流单轮 / 多轮）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>一个模型适配多指标</strong>：字段全 Optional + <span class="inline">to_dict</span> 丢弃 None，让同一个 <span class="inline">SingleTurnSample</span> 既能装齐全 RAG 样本、也能只装"问题 + 回答"，喂给不同指标都不浪费列。</li>
    <li><strong>统一转换层</strong>：pandas / HuggingFace / CSV / JSONL 的互转都收敛到 <span class="inline">RagasDataset</span> 一处实现，子类无需各写一套（DRY）。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">SingleTurnSample</span> 把"一问一答"装进一个模型：核心是 <span class="inline">user_input</span> / <span class="inline">retrieved_contexts</span> / <span class="inline">response</span> / <span class="inline">reference</span>，字段全 Optional。</li>
    <li><span class="inline">to_dict</span> 丢弃 None、<span class="inline">get_features</span> 列出非空列——这是后续"指标缺列校验"的依据。</li>
    <li>数据流向：<strong>样本 → EvaluationDataset → 评测</strong>；下一课看多轮样本与消息（<a href="05-multi-turn-sample.html">第 5 课</a>）。</li>
  </ul>
</div>
"""

LESSON_05 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
单轮样本装"一问一答"，但 Agent 会<strong>多轮对话、还会调用工具</strong>。<span class="inline">MultiTurnSample</span> 用一串<strong>结构化消息</strong>把这些都装下，
并在构造时就校验"对话顺序合不合法"。本课讲清五种消息与这道校验。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  一个 <span class="inline">MultiTurnSample</span> 就像<strong>一段聊天记录 + 几张工具调用小票</strong>：谁说了什么（人类 / AI）、AI 中途"喊"了哪个工具、
  工具又回了什么结果，全都按时间顺序记在一条对话流里——评 Agent 时就照着这段记录复盘。
</div>

<h2>五种消息：对话的积木</h2>
<p>消息类型定义在 <span class="mono">messages.py</span>，都是 pydantic 模型。<span class="inline">ToolCall</span> 本身不是消息，而是 <span class="inline">AIMessage</span> 里"想调用哪个工具"的描述：</p>

<table class="t">
  <tr><th>类型</th><th>关键字段</th><th>含义</th></tr>
  <tr><td class="mono">Message</td><td class="mono">content, metadata</td><td>所有消息的基类（共同字段）</td></tr>
  <tr><td class="mono">HumanMessage</td><td class="mono">type="human"</td><td>用户发言</td></tr>
  <tr><td class="mono">AIMessage</td><td class="mono">type="ai", tool_calls</td><td>模型发言，可携带一组 ToolCall</td></tr>
  <tr><td class="mono">ToolMessage</td><td class="mono">type="tool"</td><td>工具返回的结果</td></tr>
  <tr><td class="mono">ToolCall</td><td class="mono">name, args</td><td>一次工具调用：工具名 + 参数（AIMessage.tool_calls 的元素）</td></tr>
</table>

<p><span class="inline">MultiTurnSample</span> 的 <span class="inline">user_input</span> 是一串消息（<span class="mono">List[Union[HumanMessage, AIMessage, ToolMessage]]</span>），
而且是<strong>唯一必填</strong>字段；其余 <span class="inline">reference</span> / <span class="inline">reference_tool_calls</span> / <span class="inline">rubrics</span> / <span class="inline">reference_topics</span> 都是可选的参考标准。</p>

<pre class="code"><span class="kw">from</span> ragas <span class="kw">import</span> MultiTurnSample
<span class="kw">from</span> ragas.messages <span class="kw">import</span> HumanMessage, AIMessage, ToolMessage, ToolCall

sample = MultiTurnSample(user_input=[
    HumanMessage(content=<span class="st">"北京今天天气如何？"</span>),
    AIMessage(content=<span class="st">""</span>, tool_calls=[
        ToolCall(name=<span class="st">"get_weather"</span>, args={<span class="st">"city"</span>: <span class="st">"北京"</span>}),
    ]),
    ToolMessage(content=<span class="st">"晴，26°C"</span>),          <span class="cm"># 承接上一条 AI 的工具调用</span>
    AIMessage(content=<span class="st">"北京今天晴，约 26 度。"</span>),
])
print(sample.pretty_repr())   <span class="cm"># 打印成可读的多轮对话</span></pre>

<details class="accordion">
  <summary><span class="badge-num">1</span> field_validator 如何在"构造时"就拦下非法对话 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三条排序规则</div>
      <div class="a"><span class="inline">MultiTurnSample</span> 在 <span class="inline">user_input</span> 上挂了一个 <span class="inline">field_validator</span>，逐条检查：
        ① 每个元素必须是 <span class="inline">HumanMessage</span> / <span class="inline">AIMessage</span> / <span class="inline">ToolMessage</span> 之一；
        ② <span class="inline">ToolMessage</span> 之前必须出现过 <span class="inline">AIMessage</span>；
        ③ <span class="inline">ToolMessage</span> 必须紧跟在"带 <span class="inline">tool_calls</span> 的 <span class="inline">AIMessage</span>"或"另一个 <span class="inline">ToolMessage</span>"之后。任一条不满足就抛 <span class="inline">ValueError</span>——比如把一条 <span class="inline">ToolMessage</span> 放在对话开头（前面没有 <span class="inline">AIMessage</span>），构造样本时就会立刻报错。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 为什么把校验放在数据层</div>
      <div class="a">pydantic 的 <span class="inline">field_validator</span> 在<strong>构造对象时</strong>立即执行，于是"工具结果凭空出现""对话顺序错乱"等问题在<strong>造样本阶段</strong>就报错，而不是拖到评测中途才崩。错误前移、定位更快。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  消息定义在 <span class="mono">src/ragas/messages.py</span>：<span class="mono">Message</span>（<span class="mono">content</span> / <span class="mono">metadata</span>）派生出 <span class="mono">HumanMessage</span> / <span class="mono">AIMessage</span>（带 <span class="mono">tool_calls</span>）/ <span class="mono">ToolMessage</span>，外加 <span class="mono">ToolCall</span>（<span class="mono">name</span> / <span class="mono">args</span>）。
  <span class="mono">MultiTurnSample</span> 在 <span class="mono">dataset_schema.py</span>：<span class="mono">user_input</span> 上的 <span class="mono">field_validator</span>（<span class="mono">validate_user_input</span>）校验消息序，另有 <span class="mono">to_messages</span> / <span class="mono">pretty_repr</span> 与 <span class="mono">reference_tool_calls</span> / <span class="mono">reference_topics</span> 等参考字段。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>结构化消息</strong>：把"对话 + 工具调用"拆成 Human / AI / Tool 三类消息 + <span class="inline">ToolCall</span>，让 Agent 行为可被程序读取与打分，而不是一坨纯文本。</li>
    <li><strong>调用与结果配对</strong>：<span class="inline">AIMessage.tool_calls</span> 描述"模型想调哪个工具"，随后的 <span class="inline">ToolMessage</span> 承接其结果。注意 ragas 的消息<strong>没有 OpenAI / LangChain 那种 <span class="inline">tool_call_id</span></strong>——纯靠<strong>出现顺序</strong>配对，由 <span class="inline">field_validator</span> 保证合法。</li>
    <li><strong>构造即校验</strong>：合法性检查放在数据层，把错误前移到"造样本"阶段，避免评测半途因脏数据中断。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>单轮 <span class="mono">SingleTurnSample</span>（<a href="04-single-turn-sample.html">第 4 课</a>）装"一问一答"，多轮 <span class="mono">MultiTurnSample</span> 装"一段带工具调用的对话"。</li>
    <li>五种结构：<span class="mono">Message</span> / <span class="mono">HumanMessage</span> / <span class="mono">AIMessage</span> / <span class="mono">ToolMessage</span> / <span class="mono">ToolCall</span>；<span class="inline">user_input</span> 是消息列表（唯一必填）。</li>
    <li>消息是 <strong>Agent / 多轮指标</strong>的评测载体（<a href="18-agent-metrics-internals.html">第 18 课</a>深入）。</li>
  </ul>
</div>
"""

LESSON_06 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
ragas 里有<strong>两个都叫 "Dataset" 的东西</strong>，分属两套体系、用途不同——这是最容易踩的混淆点。
本课用一张对照表把边界一次讲清：哪个是"评测输入"，哪个是"带存储的台账"。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  <span class="inline">EvaluationDataset</span> 是<strong>待阅的一叠考卷</strong>——评测的输入，装满样本、直接交给阅卷。
  而 <span class="inline">Dataset</span> / <span class="inline">DataTable</span> 是<strong>带存储的台账</strong>——像一本能存进抽屉（backend）、可反复增删查改、随时取回的工作簿。
</div>

<h2>一张对照表认清两者</h2>
<table class="t">
  <tr><th>维度</th><th>EvaluationDataset</th><th>Dataset / DataTable</th></tr>
  <tr><td><strong>来历模块</strong></td><td class="mono">dataset_schema.py</td><td class="mono">dataset.py</td></tr>
  <tr><td><strong>继承体系</strong></td><td>继承 <span class="mono">RagasDataset</span></td><td><span class="mono">DataTable</span> 泛型基类（<span class="mono">Dataset</span> 是其子类）</td></tr>
  <tr><td><strong>装什么</strong></td><td>SingleTurnSample / MultiTurnSample 列表</td><td>任意 pydantic 模型或 dict 行</td></tr>
  <tr><td><strong>主要用途</strong></td><td>评测输入（喂给 evaluate）</td><td>带存储的数据台账（实验数据源）</td></tr>
  <tr><td><strong>持久化方式</strong></td><td>to_csv / to_jsonl / to_pandas 显式导出</td><td>绑定 backend，load / save / reload</td></tr>
  <tr><td><strong>backend 解析</strong></td><td>有 backend 字段，但不走 registry</td><td><span class="mono">_resolve_backend</span> 解析字符串（如 "local/csv"）</td></tr>
  <tr><td><strong>谁在用</strong></td><td><span class="mono">evaluate()</span>（<a href="07-evaluate.html">第 7 课</a>）</td><td><span class="mono">@experiment</span> 实验流（<a href="08-experiment.html">第 8 课</a>）</td></tr>
</table>

<p>关键点：<span class="inline">DataTable</span> 是个<strong>泛型基类</strong>（<span class="mono">Generic[T]</span>），用类属性 <span class="inline">DATATABLE_TYPE</span> 标记自己是 <span class="mono">"Dataset"</span> 还是 <span class="mono">"Experiment"</span>；
<span class="inline">Dataset</span> 与 <span class="inline">Experiment</span>（<a href="08-experiment.html">第 8 课</a>）<strong>都继承它</strong>，共用 <span class="inline">load</span> / <span class="inline">save</span> / <span class="inline">_resolve_backend</span>。
而 <span class="inline">EvaluationDataset</span> 走的是<strong>另一条</strong>（<span class="inline">RagasDataset</span>）继承链——两者只是名字相近，并无父子关系。</p>

<p>存储型 <span class="inline">Dataset</span> 的 <span class="inline">backend</span> 可直接写字符串（如 <span class="mono">"local/csv"</span>），由 <span class="inline">_resolve_backend</span> 去全局 registry 查类并实例化，查不到则报错并列出可用后端——免去手动 import 具体后端类，<strong>插件式可扩展</strong>。这套注册/解析机制详见 <a href="32-backends.html">第 32 课</a>，本课只需知道"存储型才带 backend"。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  <span class="mono">src/ragas/dataset.py</span>：泛型基类 <span class="mono">DataTable[T]</span>（含 <span class="mono">DATATABLE_TYPE</span>、静态方法 <span class="mono">_resolve_backend</span>、<span class="mono">load</span> / <span class="mono">save</span> / <span class="mono">reload</span>）与子类 <span class="mono">Dataset</span>（<span class="mono">DATATABLE_TYPE = "Dataset"</span>）。
  <span class="mono">src/ragas/dataset_schema.py</span>：<span class="mono">EvaluationDataset</span> 继承 <span class="mono">RagasDataset</span>，靠 <span class="mono">to_pandas</span> / <span class="mono">to_csv</span> / <span class="mono">to_jsonl</span> 等转换器持久化。<span class="mono">Experiment</span>（<span class="mono">experiment.py</span>）同样继承 <span class="mono">DataTable</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>同名易混 → 讲清边界</strong>：用"输入考卷 vs 存储台账"区分两者的职责，避免 import 错对象。</li>
    <li><strong>泛型基类复用</strong>：<span class="inline">DataTable</span> 被 <span class="inline">Dataset</span> 与 <span class="inline">Experiment</span> 共用，靠 <span class="inline">DATATABLE_TYPE</span> 区分身份，<span class="inline">load</span> / <span class="inline">save</span> 只写一遍（DRY）。</li>
    <li><strong>backend 字符串解析</strong>：<span class="inline">_resolve_backend</span> 把 <span class="mono">"local/csv"</span> 映射到注册的后端类，插件式可扩展、报错友好。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>分清两个 Dataset：<span class="mono">EvaluationDataset</span>（评测输入，<span class="mono">dataset_schema.py</span>）vs <span class="mono">Dataset</span> / <span class="mono">DataTable</span>（存储台账，<span class="mono">dataset.py</span>）。</li>
    <li>存储型走 <strong>backend</strong>：<span class="inline">_resolve_backend</span> 解析 <span class="mono">"local/csv"</span>；<span class="mono">Experiment</span> 也基于 <span class="mono">DataTable</span>。</li>
    <li>选型：跑 <span class="mono">evaluate</span> 用 <span class="mono">EvaluationDataset</span>（<a href="07-evaluate.html">第 7 课</a>）；做 <span class="mono">@experiment</span> 用 <span class="mono">Dataset</span>（<a href="08-experiment.html">第 8 课</a>）。</li>
  </ul>
</div>
"""

LESSON_07 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
手里已有一份评测数据时，<span class="inline">evaluate()</span> 让你"一键阅卷"：传入数据集和指标，拿回一张带分数的成绩单。
本课带你跑通最小例子、读懂结果对象，并说明它为何已被官方标记<strong>废弃</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  <span class="inline">evaluate()</span> 像<strong>一键阅卷</strong>：把一叠考卷（<span class="inline">EvaluationDataset</span>）和一套评分标准（<span class="inline">metrics</span>）丢进去，
  它自动安排"阅卷老师"并发批改，最后汇成一张成绩单（<span class="inline">EvaluationResult</span>）。
</div>

<div class="card warn">
  <div class="tag">⚠️ 先把状态摆在前面：evaluate() 已废弃</div>
  本课讲的 <span class="inline">evaluate()</span> / <span class="inline">aevaluate()</span> <strong>都会发 <span class="mono">DeprecationWarning</span></strong>、官方指向 <span class="mono">@experiment</span>（<a href="08-experiment.html">第 8 课</a>）。它仍可用、也值得理解其机制，但<strong>新项目请优先用实验装饰器</strong>——所以先点明状态，再来跑它。
</div>

<p><strong>本课流程一眼看</strong>：<span class="inline">evaluate</span> 一键阅卷的内部链路 👇</p>
<div class="flow">
  <div class="node"><div class="nt">dataset + metrics</div><div class="nd">考卷 + 评分标准</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">补裁判</div><div class="nd">缺 LLM 则建 gpt-4o-mini</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">并发打分</div><div class="nd">每个 样本 × 指标 ascore</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">汇总</div><div class="nd">safe_nanmean 忽略失败行</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">EvaluationResult</div><div class="nd">to_pandas · total_cost*</div></div>
</div>

<h2>最小可跑示例</h2>
<pre class="code"><span class="kw">from</span> ragas <span class="kw">import</span> evaluate, EvaluationDataset, SingleTurnSample
<span class="kw">from</span> ragas.metrics <span class="kw">import</span> Faithfulness

dataset = EvaluationDataset(samples=[
    SingleTurnSample(
        user_input=<span class="st">"谁写了《哈姆雷特》？"</span>,
        retrieved_contexts=[<span class="st">"《哈姆雷特》是莎士比亚的剧作。"</span>],
        response=<span class="st">"莎士比亚。"</span>,
        reference=<span class="st">"威廉·莎士比亚"</span>,
    ),
])

result = evaluate(dataset, metrics=[Faithfulness()])
print(result)            <span class="cm"># {'faithfulness': 0.89} —— 每个指标一个均值</span>
df = result.to_pandas()  <span class="cm"># 原始数据列 + 每个指标一列分数</span></pre>

<p>注意我们<strong>没传 llm</strong>。<span class="inline">Faithfulness</span> 这类需要裁判模型的指标（<span class="inline">MetricWithLLM</span>）若还没绑 LLM、你又没传，<span class="inline">evaluate</span> 会自动建一个默认裁判 <span class="mono">llm_factory("gpt-4o-mini", client=OpenAI())</span>（embeddings 同理走 <span class="inline">embedding_factory</span>）。所以最小例子能跑，但需设置 <span class="mono">OPENAI_API_KEY</span>。</p>

<p>不传 <span class="inline">metrics</span> 会怎样？<span class="inline">evaluate</span> 用 <strong>RAG 四件套</strong>兜底：<span class="mono">answer_relevancy</span>、<span class="mono">context_precision</span>、<span class="mono">faithfulness</span>、<span class="mono">context_recall</span>。</p>

<h2>读懂 EvaluationResult</h2>
<details class="accordion">
  <summary><span class="badge-num">1</span> 结果对象的三种读法 + 成本统计 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 三种读法</div>
      <div class="a"><strong>① <span class="inline">print(result)</span></strong> → 每个指标一个均值（用 <span class="inline">safe_nanmean</span>，自动忽略失败行的 <span class="mono">NaN</span>）；
        <strong>② <span class="inline">result.to_pandas()</span></strong> → 把原始数据列与分数列横向拼接成 DataFrame；
        <strong>③ <span class="inline">result["faithfulness"]</span></strong> → 取某个指标的每行分数列表。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 花了多少钱 / 多少 token</div>
      <div class="a"><span class="inline">result.total_tokens()</span> 与 <span class="inline">result.total_cost()</span> 能统计开销，但<strong>前提</strong>是调用 <span class="inline">evaluate</span> 时传了 <span class="inline">token_usage_parser</span>；否则会抛错提示"未配置成本计算"。</div>
    </div>
  </div>
</details>

<details class="accordion">
  <summary><span class="badge-num">2</span> 列名对不齐怎么办（仅 HF Dataset）<span class="hint">点击展开详解</span></summary>
  <div class="acc-body"><div class="qa"><div class="a">若数据来自 <strong>HuggingFace Dataset</strong> 且列名和 ragas 默认不一致（如 <span class="mono">contexts_v1</span>），可传 <span class="mono">column_map={"contexts": "contexts_v1"}</span>，内部 <span class="inline">remap_column_names</span> 先反向重命名再校验；直接用 <span class="inline">EvaluationDataset</span> 则按字段名匹配、无需此参。</div></div></div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  <span class="mono">src/ragas/evaluation.py</span>：<span class="mono">evaluate</span> 是同步包装（默认借 <span class="mono">nest_asyncio</span> 兼容 Jupyter），<span class="mono">aevaluate</span> 是 async 真实现，二者均 <span class="mono">warnings.warn(..., DeprecationWarning)</span>；
  不传 metrics 默认 <span class="mono">answer_relevancy / context_precision / faithfulness / context_recall</span>；缺 LLM 时 <span class="mono">client = OpenAI(); llm = llm_factory("gpt-4o-mini", client=client)</span>。
  结果对象 <span class="mono">EvaluationResult</span> 在 <span class="mono">dataset_schema.py</span>（<span class="mono">to_pandas</span> / <span class="mono">total_tokens</span> / <span class="mono">total_cost</span> / <span class="mono">__repr__</span>）；列名重映射在 <span class="mono">validation.py</span> 的 <span class="mono">remap_column_names</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>缺裁判自动兜底</strong>：没显式传 LLM 时自动建 <span class="inline">llm_factory("gpt-4o-mini")</span>，让最小例子开箱即跑（也可在 metric 级覆盖）。</li>
    <li><strong>结果自带成本统计</strong>：配上 <span class="inline">token_usage_parser</span> 后，<span class="inline">total_tokens</span> / <span class="inline">total_cost</span> 直接出账。</li>
    <li><strong>失败不拖垮整体</strong>：默认 <span class="mono">raise_exceptions=False</span>，单行失败记 <span class="mono">NaN</span>，均值用 <span class="inline">safe_nanmean</span> 忽略它。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>会跑会读：<span class="mono">EvaluationDataset</span> + <span class="mono">metrics</span> → <span class="mono">evaluate()</span> → 用 <span class="inline">print</span> / <span class="inline">to_pandas</span> / 索引读结果。</li>
    <li>缺裁判时自动建默认 <span class="mono">gpt-4o-mini</span>；成本统计需传 <span class="mono">token_usage_parser</span>。</li>
    <li><span class="mono">evaluate</span> / <span class="mono">aevaluate</span> <strong>已废弃</strong>（发 <span class="mono">DeprecationWarning</span>），官方指向 <span class="mono">@experiment</span>（<a href="08-experiment.html">第 8 课</a>）。</li>
  </ul>
</div>
"""

LESSON_08 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
<span class="inline">evaluate()</span> 之后，ragas 把推荐入口换成了 <span class="inline">@experiment</span> 装饰器——把一次"评测"写成一个"实验函数"：
对数据集每一行跑一遍、并发执行、自动把结果落盘留痕，方便一版版对比迭代。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  <span class="inline">@experiment</span> 像给评测做<strong>留痕实验</strong>：你只写"对一行数据做什么"，<span class="inline">arun</span> 负责对整张表批量跑、记录每行结果、存进 backend——
  就像实验室里每次实验都<strong>登记在册</strong>，方便回看、对比哪次改动更好。
</div>

<h2>为什么从 evaluate 转向 @experiment</h2>
<p>上一课提到，<span class="inline">evaluate</span> / <span class="inline">aevaluate</span> 都会发 <span class="mono">DeprecationWarning</span> 指向它。原因是 <strong>experiments-first</strong> 的理念：
评测只"打一次分"，而每次改 prompt、换模型、调检索，都应该跑一个实验、留下<strong>可对比的记录</strong>，而不是分数算完就丢。</p>

<h2>最小示例</h2>
<pre class="code"><span class="kw">from</span> ragas <span class="kw">import</span> experiment

<span class="cm"># 装饰器把普通 async 函数变成"可对数据集批量跑"的实验</span>
<span class="kw">@</span><span class="fn">experiment</span>()
<span class="kw">async def</span> <span class="fn">run_eval</span>(row):
    score = <span class="kw">await</span> my_metric.ascore(response=row[<span class="st">"response"</span>])
    <span class="kw">return</span> {**row, <span class="st">"score"</span>: score.value}   <span class="cm"># 返回要留痕的一行</span>

<span class="cm"># dataset 是带 backend 的 Dataset（第 6 课）</span>
exp = <span class="kw">await</span> run_eval.arun(dataset)
print(exp)   <span class="cm"># Experiment(name=..., len=...)，结果已存进 backend</span></pre>

<p>被装饰的函数接收<strong>一行数据</strong>、返回"要留痕的结果"（dict 或 pydantic 模型）；真正的批量执行交给 <span class="inline">arun</span>。</p>

<p><strong>本课流程一眼看</strong>：<span class="inline">await fn.arun(dataset)</span> 这一句，背后顺次做了 5 件事 👇</p>
<div class="vflow">
  <div class="step"><div class="num">1</div><div class="sc"><h4>取名</h4>
    <p>没给 <span class="mono">name</span> 就用 <span class="mono">memorable_names</span> 起个好记的名字（有 <span class="mono">name_prefix</span> 则拼前缀）</p></div></div>
  <div class="step"><div class="num">2</div><div class="sc"><h4>解析 backend</h4>
    <p>传入的 / 装饰器默认的，否则沿用 <span class="mono">dataset.backend</span>，经 <span class="mono">_resolve_backend</span> 解析</p></div></div>
  <div class="step"><div class="num">3</div><div class="sc"><h4>建 Experiment</h4>
    <p>新建一个 <span class="mono">Experiment</span>（继承 <span class="mono">DataTable</span>，<a href="06-two-datasets.html">第 6 课</a>）</p></div></div>
  <div class="step"><div class="num">4</div><div class="sc"><h4>并发跑</h4>
    <p>每行包成任务，用 <span class="mono">asyncio.as_completed</span> 并发执行、<span class="mono">tqdm</span> 显示进度</p></div></div>
  <div class="step"><div class="num">5</div><div class="sc"><h4>存盘</h4>
    <p><span class="mono">save()</span> 落 backend 后返回该 <span class="mono">Experiment</span></p></div></div>
</div>

<details class="accordion">
  <summary><span class="badge-num">1</span> 深挖：单行任务失败了，整轮会中断吗？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">✅ 单行失败会中断整轮吗</div>
      <div class="a">不会。<span class="inline">as_completed</span> 循环里逐个 <span class="inline">await</span>，单个任务抛错会被 <span class="mono">try/except</span> 捕获、打印一条 warning 后<strong>继续</strong>——和 <span class="inline">evaluate</span> 的"失败记 NaN"异曲同工，整批不被一行拖垮。</div>
    </div>
  </div>
</details>

<h2>version_experiment：把实验钉在某次代码上</h2>
<p>想知道"这次实验对应哪段代码"？<span class="inline">version_experiment(name)</span>（需装 GitPython）会暂存改动、提交一次（默认消息 <span class="mono">Experiment: {name}</span>），
并创建分支 <span class="mono">ragas/{name}</span>，返回 commit hash；默认在 <span class="inline">find_git_root()</span> 找到的仓库根操作。于是每个实验都能回溯到确切的代码快照。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  <span class="mono">src/ragas/experiment.py</span>：<span class="mono">experiment(...)</span> 装饰器返回 <span class="mono">ExperimentWrapper</span>；<span class="mono">__call__</span> 调用原函数（自动兼容 async / sync），<span class="mono">arun</span> 负责取名 / 解析 backend / 建 <span class="mono">Experiment</span> / <span class="mono">asyncio.as_completed</span> 并发 / <span class="mono">save</span>；<span class="mono">version_experiment</span> 用 GitPython 提交并建 <span class="mono">ragas/{name}</span> 分支；<span class="mono">Experiment</span> 继承 <span class="mono">DataTable</span>（<span class="mono">DATATABLE_TYPE = "Experiment"</span>）。转向原因见 <span class="mono">evaluation.py</span> 的 <span class="mono">DeprecationWarning</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>实验即函数 + 自动留痕</strong>：把"对一行做什么"写成函数，结果自动存进 backend，可一版版对比迭代。</li>
    <li><strong>arun 天然并发</strong>：用 <span class="inline">asyncio.as_completed</span> 并发跑所有行、<span class="inline">tqdm</span> 显示进度，单行失败只记 warning 不中断整轮。</li>
    <li><strong>可复现</strong>：<span class="inline">version_experiment</span> 把实验与 git commit / 分支绑定，随时回到当时的代码快照。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">@experiment</span> 是现代推荐入口（<span class="mono">evaluate</span> 已废弃）：装饰一个 async 函数 + <span class="mono">await fn.arun(dataset)</span>。</li>
    <li><span class="inline">arun</span> = 取名 → 解析 backend → 建 <span class="mono">Experiment</span> → 并发跑 → 存盘；结果落 backend 可复查。</li>
    <li>工作流：<strong>改动 → 跑实验 → 对比</strong>（必要时 <span class="inline">version_experiment</span> 钉住代码版本）。</li>
  </ul>
</div>
"""
