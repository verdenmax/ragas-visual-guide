"""Content for part5 — 第五部分 · 引擎与基础设施（19-24）."""

LESSON_19 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
指标要让 LLM 当裁判，就得先递给它一张<strong>结构化的考卷</strong>。经典指标用 <span class="inline">PydanticPrompt</span> 把"指令 + 输出格式 + 例题 + 输入"拼成考卷，还自带解析与纠错；现代 collections 指标改用一张<strong>更薄</strong>的 <span class="inline">BasePrompt</span>，把解析和修复全交给 instructor。本课看清这套 Prompt 系统的两代写法。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  <span class="inline">PydanticPrompt</span> 像一张<strong>带标准答题格式的考卷</strong>：印着题面（instruction）、必须遵守的答题格式（输出的 JSON schema）、几道例题（few-shot），最后才是这次的题目（输入）。考生（LLM）答完，<strong>阅卷机先按格式核对</strong>——格式不对就把卷子<strong>退回去让它照格式重填</strong>，直到合格或用完重试次数。
</div>

<p><strong>本课流程一眼看</strong>：PydanticPrompt 把一次「问 LLM」变成结构化、可自我纠错的流程 👇</p>
<div class="flow">
  <div class="node"><div class="nt">拼考卷</div><div class="nd">指令 + schema + 例题 + 输入</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">LLM 作答</div><div class="nd">按 schema 输出</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">解析校验</div><div class="nd">格式不对 → 带错重试</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">结构化对象</div><div class="nd">pydantic OutputModel</div></div>
</div>

<h2>经典栈：PydanticPrompt 怎么拼出一张考卷</h2>
<p><span class="inline">PydanticPrompt[InputModel, OutputModel]</span> 用四个类属性定义一张考卷——输入模型、输出模型、指令、例题：</p>
<pre class="code"><span class="kw">class</span> <span class="fn">StatementGeneratorPrompt</span>(
        PydanticPrompt[StatementGeneratorInput, StatementGeneratorOutput]):
    instruction  = <span class="st">"把回答拆成一条条不含代词、可独立理解的原子陈述。"</span>
    input_model  = StatementGeneratorInput      <span class="cm"># 输入字段（pydantic）</span>
    output_model = StatementGeneratorOutput      <span class="cm"># 输出字段（pydantic）</span>
    examples = [                                 <span class="cm"># few-shot 例题（可选）</span>
        (StatementGeneratorInput(question=<span class="st">"…"</span>, answer=<span class="st">"…"</span>),
         StatementGeneratorOutput(statements=[<span class="st">"…"</span>, <span class="st">"…"</span>])),
    ]</pre>
<p><span class="inline">to_string(data)</span> 再把它们拼成喂给 LLM 的最终文本，其中<strong>输出签名</strong>由 <span class="inline">output_model.model_json_schema()</span> 生成——这是对格式的强约束：</p>
<pre class="code">prompt_str = prompt.to_string(data)
<span class="cm"># = 指令 instruction</span>
<span class="cm"># + 输出签名：output_model.model_json_schema() 转成的 JSON schema（强约束格式）</span>
<span class="cm"># + few-shot 例题（_generate_examples）</span>
<span class="cm"># + "Now perform the same with the following input"</span>
<span class="cm"># + 这次的输入 data（model_dump_json）+ "Output: "</span></pre>

<h2>生成 → 解析 → 自我修复</h2>
<p><span class="inline">generate</span> 是 <span class="inline">generate_multiple(n=1)</span> 的特例。整条链路是"拼考卷 → LLM 出 JSON → 解析校验 → 失败重填"：</p>
<pre class="code">output = <span class="kw">await</span> prompt.generate(llm=llm, data=data)   <span class="cm"># 返回 output_model 实例</span>
<span class="cm"># 内部三步：</span>
<span class="cm">#   ① to_string(data) 拼考卷 → 交给 LLM 出 JSON 文本</span>
<span class="cm">#   ② RagasOutputParser 抽 JSON、校验成 output_model</span>
<span class="cm">#   ③ 解析失败 → FixOutputFormat 把坏输出退回 LLM 重填（retries_left 默认 3）</span>
<span class="cm">#      仍失败 → 抛 RagasOutputParserException</span></pre>
<p>两个可重写钩子 <span class="inline">process_input</span> / <span class="inline">process_output</span> 默认原样返回，子类可在送进 / 取出 LLM 时加工（如 <span class="mono">TranslateStatements</span> 校验翻译条数，<a href="20-prompt-advanced.html">第 20 课</a>）。<span class="inline">generate</span> 还兼容三种 LLM：langchain、instructor、<span class="mono">BaseRagasLLM</span>（<a href="21-llm-abstraction.html">第 21 课</a>）。</p>

<h2>PromptMixin：让 prompt 成为一等公民</h2>
<p>经典指标都混入了 <span class="inline">PromptMixin</span>。它靠 <span class="inline">inspect.getmembers</span> 自动发现实例上所有 <span class="mono">PydanticPrompt</span>，于是 prompt 能被<strong>发现、整张替换、翻译、存盘复用</strong>：</p>
<table class="t">
  <tr><th>方法</th><th>作用</th></tr>
  <tr><td class="mono">get_prompts()</td><td>列出该指标的所有 prompt（按 name）</td></tr>
  <tr><td class="mono">set_prompts(**p)</td><td>整张替换（非 PydanticPrompt 直接 ValueError）</td></tr>
  <tr><td class="mono">adapt_prompts(lang, llm)</td><td>把全部 prompt 翻译成另一种语言（<a href="20-prompt-advanced.html">第 20 课</a>）</td></tr>
  <tr><td class="mono">save_prompts / load_prompts</td><td>存成 <span class="mono">{name}_{language}.json</span> 再加载</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> 两个同名 BasePrompt，别认错 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 prompt/base.py vs prompt/metrics/base_prompt.py</div>
      <div class="a">仓库里有<strong>两个都叫 BasePrompt</strong> 的类：① <span class="mono">prompt/base.py:BasePrompt(ABC)</span>——经典基类，定义<strong>抽象的</strong> <span class="mono">generate</span> / <span class="mono">generate_multiple</span>，<span class="inline">PydanticPrompt</span> 与 <span class="inline">StringPrompt</span> 都继承它，<strong>自己负责</strong>调 LLM 与解析；② <span class="mono">prompt/metrics/base_prompt.py:BasePrompt(ABC, Generic[InputModel, OutputModel])</span>——现代 collections 指标专用的<strong>更薄</strong>基类，只有 <span class="mono">to_string</span> / <span class="mono">_generate_examples</span> / <span class="mono">adapt</span>，<strong>没有</strong> <span class="mono">generate</span>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 现代栈为什么更薄</div>
      <div class="a">因为 instructor 直接把 LLM 输出校验成 pydantic 对象（<a href="21-llm-abstraction.html">第 21 课</a>），<strong>格式约束与重试由 instructor 兜底</strong>，prompt 对象只需"把考卷拼成字符串"。所以 collections 的 <span class="mono">util.py</span> 里只写 <span class="mono">to_string</span>，再 <span class="mono">await llm.agenerate(prompt_str, OutputModel)</span>（<a href="15-faithfulness-internals.html">第 15 课</a> Faithfulness 即如此）。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  经典栈在 <span class="mono">src/ragas/prompt/pydantic_prompt.py</span>：<span class="mono">PydanticPrompt</span>（<span class="mono">to_string</span> / <span class="mono">_generate_output_signature</span> / <span class="mono">_generate_examples</span>、<span class="mono">generate</span> / <span class="mono">generate_multiple</span>、<span class="mono">process_input</span> / <span class="mono">process_output</span>、<span class="mono">adapt</span>），解析器 <span class="mono">RagasOutputParser</span> 与自修复 <span class="mono">FixOutputFormat</span>（输出模型 <span class="mono">StringIO</span>），翻译用 <span class="mono">translate_statements_prompt</span>（<span class="mono">TranslateStatements</span>）。基类与字符串版在 <span class="mono">prompt/base.py</span>（<span class="mono">BasePrompt</span> / <span class="mono">StringPrompt</span> / <span class="mono">StringIO</span> / <span class="mono">BoolIO</span>），prompt 发现与替换在 <span class="mono">prompt/mixin.py</span>（<span class="mono">PromptMixin</span>）。现代更薄的 <span class="mono">BasePrompt</span> 在 <span class="mono">prompt/metrics/base_prompt.py</span>，被 <span class="mono">metrics/collections/*/util.py</span> 继承、配 <span class="mono">InstructorBaseRagasLLM.agenerate</span> 使用（<a href="13-metric-base.html">第 13 课</a>、<a href="15-faithfulness-internals.html">第 15 课</a>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>输出签名来自 model_json_schema()</strong>：把"答题格式"变成机器可校验的<strong>强约束</strong>，而不是口头叮嘱。</li>
    <li><strong>FixOutputFormat 自我修复</strong>：LLM 偶尔吐坏 JSON 也能退回重填，鲁棒性藏在解析器里。</li>
    <li><strong>PromptMixin 让 prompt 成一等公民</strong>：可发现、可整张替换、可翻译、可存盘——评测标准也能版本化。</li>
    <li><strong>现代栈做减法</strong>：把解析 / 修复交给 instructor，prompt 退化成"只拼字符串"，更简单更薄。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>经典指标站 <span class="inline">PydanticPrompt</span>：<span class="mono">to_string</span> 拼"指令 + JSON schema 输出签名 + few-shot + 输入"，<span class="mono">generate</span> 自带 <span class="mono">RagasOutputParser</span> 解析与 <span class="mono">FixOutputFormat</span> 自修复。</li>
    <li><span class="inline">PromptMixin</span> 让经典 prompt 可发现 / 可替换 / 可翻译 / 可存盘。</li>
    <li>两个同名 <span class="mono">BasePrompt</span> 别搞混：<span class="mono">prompt/base.py</span> 的带 <span class="mono">generate</span>（经典 <span class="inline">PydanticPrompt</span> 的父类，自己调 LLM + 解析）；<span class="mono">prompt/metrics/base_prompt.py</span> 的只有 <span class="mono">to_string</span>（现代 collections 指标用，解析与修复交给 instructor，<a href="21-llm-abstraction.html">第 21 课</a>）。</li>
  </ul>
</div>
"""

LESSON_20 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课的 <span class="mono">examples</span> 是写死在 prompt 里的固定例题。本课看两件进阶事：① <strong>动态 few-shot</strong>——用 embedding 按当前输入临场挑最像的几道例题；② <strong>adapt</strong>——把整张 prompt 翻译成另一种语言而不用重写。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  给考生<strong>看几道例题</strong>（few-shot）能显著提分；但例题不该一成不变——好老师会<strong>按这次的题目，从题库里挑最相关的几道</strong>给你看（动态 few-shot）。而当考生换了母语，老师能<strong>把整张考卷连例题一起翻译</strong>过去（adapt）：题目不变、语言变了。
</div>

<h2>静态 vs 动态 few-shot</h2>
<p>静态：<span class="inline">PydanticPrompt.examples</span> 是固定列表，每次都喂同样的例题。动态：按输入临场从"例题库"里用<strong>余弦相似度</strong>挑 top-k。两套栈各有一个动态版：</p>
<table class="t">
  <tr><th>维度</th><th>经典栈（PydanticPrompt 侧）</th><th>Simple 栈</th></tr>
  <tr><td><strong>动态 prompt</strong></td><td class="mono">FewShotPydanticPrompt</td><td class="mono">DynamicFewShotPrompt</td></tr>
  <tr><td><strong>例题库</strong></td><td class="mono">InMemoryExampleStore</td><td class="mono">SimpleInMemoryExampleStore</td></tr>
  <tr><td><strong>选择依据</strong></td><td>embed_query + 余弦相似度</td><td>同左</td></tr>
  <tr><td><strong>默认 top-k</strong></td><td class="mono">top_k_for_examples=5</td><td class="mono">max_similar_examples=3</td></tr>
  <tr><td><strong>阈值</strong></td><td class="mono">threshold_for_examples=0.7</td><td class="mono">similarity_threshold=0.7</td></tr>
  <tr><td><strong>没 embedding 时</strong></td><td>—</td><td>退回最近 N 条</td></tr>
</table>
<pre class="code"><span class="cm"># 经典侧：从一个普通 PydanticPrompt 升级成动态 few-shot</span>
few = FewShotPydanticPrompt.from_pydantic_prompt(prompt, embeddings)
<span class="cm"># 内部：把 prompt.examples 灌进 InMemoryExampleStore（顺便算好 embedding）</span>
<span class="cm"># generate 时：example_store.get_examples(data, top_k) 按相似度挑例题，再走原本的 generate</span>

<span class="cm"># Simple 侧：</span>
dyn = DynamicFewShotPrompt.from_prompt(
    prompt, embedding_model=emb, max_similar_examples=<span class="st">3</span>, similarity_threshold=<span class="st">0.7</span>)
dyn.format(question=<span class="st">"…"</span>)   <span class="cm"># 临场挑最像的例题拼进去</span></pre>

<h2>轻量的 Prompt：Simple 栈的 f-string 模板</h2>
<p><span class="inline">DynamicFewShotPrompt</span> 的父类是 <span class="inline">simple_prompt.Prompt</span>——自定义指标（<a href="11-custom-metrics.html">第 11 课</a>）用的极简 prompt：<span class="mono">instruction</span> 里写 <span class="mono">{占位符}</span>，<span class="inline">format(**kwargs)</span> 填充，<span class="inline">add_example(输入dict, 输出dict)</span> 加例题，可选 <span class="mono">response_model</span>，支持 <span class="mono">save</span> / <span class="mono">load</span>（含 <span class="mono">.gz</span> 压缩）：</p>
<pre class="code">p = Prompt(<span class="st">"判断摘要是否准确：\nResponse: {response}"</span>)
p.add_example({<span class="st">"response"</span>: <span class="st">"…"</span>}, {<span class="st">"verdict"</span>: <span class="st">"accurate"</span>})
p.format(response=<span class="st">"今天下雨"</span>)   <span class="cm"># 指令 + Examples 段拼成字符串</span></pre>

<h2>adapt：把考卷翻译成另一种语言</h2>
<p><span class="inline">adapt(target_language, llm)</span> 把 <span class="mono">examples</span> 里的字符串<strong>整批翻译</strong>、保持条数一致，返回一张<strong>新</strong> prompt（不改原件）。可选 <span class="mono">adapt_instruction=True</span> 连指令也翻：</p>
<pre class="code">zh_prompt = <span class="kw">await</span> prompt.adapt(target_language=<span class="st">"chinese"</span>, llm=llm)
<span class="cm"># examples 全部译成中文、条数不变；instruction 默认保留，adapt_instruction=True 才翻</span></pre>
<p>经典栈用 <span class="inline">TranslateStatements</span>（一个 <span class="mono">PydanticPrompt</span>，<a href="19-prompt-system.html">第 19 课</a>），现代薄 <span class="mono">BasePrompt</span> 用内部 <span class="inline">_translate_strings</span>；<span class="inline">PromptMixin.adapt_prompts</span> 能一次翻译一个指标的<strong>全部</strong> prompt。两者都<strong>强制译后条数 == 译前条数</strong>，否则报错。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 多模态 prompt：让裁判"看图答题" <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 ImageTextPrompt</div>
      <div class="a"><span class="mono">prompt/multi_modal_prompt.py</span> 的 <span class="inline">ImageTextPrompt</span> 也继承 <span class="mono">PydanticPrompt</span>，但把输入拼成"<strong>文字 + 图片</strong>"的消息（<span class="mono">to_prompt_value</span> → <span class="mono">ImageTextPromptValue.to_messages</span>），让裁判模型能"看图答题"，适合多模态评测。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 同一套骨架的延伸</div>
      <div class="a">few-shot、翻译、多模态都建立在 <span class="mono">PydanticPrompt</span> 的 <span class="mono">to_string</span> / <span class="mono">examples</span> 骨架上——换的是"<strong>例题怎么选、用什么语言、带不带图片</strong>"，核心结构不变。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  动态 few-shot：经典侧在 <span class="mono">src/ragas/prompt/few_shot_pydantic_prompt.py</span>（<span class="mono">FewShotPydanticPrompt</span>、<span class="mono">ExampleStore</span> / <span class="mono">InMemoryExampleStore</span>、<span class="mono">from_pydantic_prompt</span>），Simple 侧在 <span class="mono">prompt/dynamic_few_shot.py</span>（<span class="mono">DynamicFewShotPrompt</span>、<span class="mono">SimpleExampleStore</span> / <span class="mono">SimpleInMemoryExampleStore</span>、<span class="mono">from_prompt</span>），都用 <span class="mono">embed_query</span> + 余弦相似度选 top-k（阈值 0.7）。轻量 <span class="mono">Prompt</span> 在 <span class="mono">prompt/simple_prompt.py</span>（<span class="mono">format</span> / <span class="mono">add_example</span> / <span class="mono">save</span> / <span class="mono">load</span>）。翻译 <span class="mono">adapt</span> 在 <span class="mono">pydantic_prompt.py</span>（<span class="mono">TranslateStatements</span> / <span class="mono">translate_statements_prompt</span>）与 <span class="mono">prompt/metrics/base_prompt.py</span>（<span class="mono">_translate_strings</span>），批量入口 <span class="mono">PromptMixin.adapt_prompts</span> 在 <span class="mono">prompt/mixin.py</span>。多模态在 <span class="mono">prompt/multi_modal_prompt.py</span>（<span class="mono">ImageTextPrompt</span> / <span class="mono">ImageTextPromptValue</span>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>动态 few-shot 用 embedding 选最相关示例</strong>：例题随输入变化，比固定例题更贴题（依赖 embedding，<a href="22-embedding-abstraction.html">第 22 课</a>）。</li>
    <li><strong>没 embedding 也能用</strong>：Simple 栈退回"最近 N 条"，优雅降级而不报错。</li>
    <li><strong>adapt 让 prompt 跨语言迁移不重写</strong>：翻译 examples 并强制条数一致，结构零改动。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>静态 few-shot 是写死的 <span class="mono">examples</span>；动态 few-shot 用 embedding 按输入挑 top-k（默认阈值 0.7）。</li>
    <li>两套栈各有动态版：<span class="inline">FewShotPydanticPrompt</span> + <span class="mono">InMemoryExampleStore</span>（经典）/ <span class="inline">DynamicFewShotPrompt</span> + <span class="mono">SimpleInMemoryExampleStore</span>（Simple）。</li>
    <li><span class="inline">adapt()</span> 把 examples 整批翻译、条数不变，prompt 跨语言迁移不用重写；多模态有 <span class="mono">ImageTextPrompt</span>。</li>
  </ul>
</div>
"""

LESSON_21 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
指标要打分，得先有个会说话的模型。ragas 把"底下接哪家模型"和"上面怎么调用"解耦成 <strong>LLM 抽象层</strong>：经典栈用 langchain 包装器返回<strong>文本</strong>，现代栈用 instructor 直接返回 <strong>pydantic 对象</strong>。优先用 <span class="inline">llm_factory</span>，它会替你自动选适配器。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  LLM 抽象层像一个<strong>万能转接头</strong>：底下能插 OpenAI、Anthropic、Google、本地模型，上面给指标一个<strong>统一插口</strong>。现代版转接头还自带"<strong>结构化输出</strong>"——你要什么形状的数据（pydantic 模型），它就吐什么形状，省得你自己拿钳子去解析 JSON。
</div>

<h2>两条路径：返回文本 vs 返回对象</h2>
<pre class="code"><span class="cm"># 经典：BaseRagasLLM（llms/base.py）</span>
<span class="kw">class</span> <span class="fn">BaseRagasLLM</span>(ABC):
    <span class="kw">async def</span> <span class="fn">agenerate_text</span>(prompt, n, temperature, stop, callbacks) -> LLMResult
    <span class="cm"># 返回 langchain 的 LLMResult（文本）；解析交给 PydanticPrompt（第 19 课）</span>
    <span class="cm"># 实现：LangchainLLMWrapper / LlamaIndexLLMWrapper</span>

<span class="cm"># 现代：InstructorBaseRagasLLM</span>
<span class="kw">class</span> <span class="fn">InstructorBaseRagasLLM</span>(ABC):
    <span class="kw">async def</span> <span class="fn">agenerate</span>(prompt: str, response_model: Type[T]) -> T
    <span class="cm"># 直接返回 response_model 的实例（pydantic 对象），免手写解析</span>
    <span class="cm"># 实现：InstructorLLM</span></pre>

<h2>llm_factory：一个工厂，自动选适配器</h2>
<pre class="code"><span class="kw">def</span> <span class="fn">llm_factory</span>(model, provider=<span class="st">"openai"</span>, client=<span class="kw">None</span>,
                adapter=<span class="st">"auto"</span>, cache=<span class="kw">None</span>, mode=<span class="kw">None</span>, **kwargs) -> InstructorBaseRagasLLM</pre>
<p><span class="mono">client</span> <strong>必填</strong>（去掉了隐式 text-only 模式，传 <span class="mono">None</span> 直接 <span class="mono">ValueError</span>）。<span class="mono">adapter="auto"</span> 时由 <span class="inline">auto_detect_adapter</span> 选：</p>
<ul>
  <li>client 来自 <strong>litellm</strong> 模块 → <span class="mono">litellm</span> 适配器；</li>
  <li>provider 是 <strong>google / gemini</strong>：新版 <span class="mono">google-genai</span> SDK → <span class="mono">instructor</span>，旧版 SDK → <span class="mono">litellm</span>；</li>
  <li>其它 → <span class="mono">instructor</span>（默认）。</li>
</ul>
<pre class="code"><span class="kw">from</span> openai <span class="kw">import</span> AsyncOpenAI
<span class="kw">from</span> ragas.llms <span class="kw">import</span> llm_factory

llm = llm_factory(<span class="st">"gpt-4o-mini"</span>, client=AsyncOpenAI())     <span class="cm"># 异步：用 AsyncOpenAI</span>
result = <span class="kw">await</span> llm.agenerate(prompt_str, MyOutputModel) <span class="cm"># 直接拿 pydantic 对象</span></pre>

<h2>instructor 怎么直接吐 pydantic</h2>
<p><span class="inline">InstructorLLM</span> 把传入的 client 用 instructor "打补丁"，<span class="inline">generate</span> / <span class="inline">agenerate</span> 内部调 <span class="mono">client.chat.completions.create(model=…, messages=…, response_model=OutputModel, **provider_kwargs)</span>，由 instructor 把回复<strong>校验成 OutputModel</strong>。不同厂商参数不一样，靠 <span class="inline">_map_provider_params</span> 分流：</p>
<table class="t">
  <tr><th>厂商</th><th>映射函数</th><th>处理</th></tr>
  <tr><td>OpenAI / Azure</td><td class="mono">_map_openai_params</td><td>o 系列 / gpt-5 把 <span class="mono">max_tokens</span> 改 <span class="mono">max_completion_tokens</span>、<span class="mono">temperature</span> 固定 1.0</td></tr>
  <tr><td>Google</td><td class="mono">_map_google_params</td><td>参数包进 <span class="mono">generation_config</span></td></tr>
  <tr><td>Anthropic / LiteLLM</td><td>—</td><td>原样透传</td></tr>
</table>
<p>构造时探测 <span class="inline">is_async</span>：用同步 client 调 <span class="mono">agenerate</span> 会直接报错，提示改用 <span class="mono">generate</span>。</p>

<h2>旧 wrapper 平滑退场</h2>
<p><span class="inline">LangchainLLMWrapper</span> / <span class="inline">LlamaIndexLLMWrapper</span> 仍可导入，但被 <span class="inline">DeprecationHelper</span> 包了一层：一旦<strong>调用或取属性</strong>就发 <span class="mono">DeprecationWarning</span>，并转发到真正的类。老代码不立刻报错，但会被提醒迁移到 <span class="mono">llm_factory</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么有 instructor 和 litellm 两个适配器 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 两个适配器分工</div>
      <div class="a"><span class="mono">instructor</span> 适配器（<span class="mono">adapters/instructor.py</span>）直接给原生 client 打补丁，支持 OpenAI / Anthropic / Azure / Groq / Mistral / Google 等；<span class="mono">litellm</span> 适配器把 100+ 家模型统一路由。<span class="inline">auto_detect_adapter</span> 按 client 模块名与 provider 决定用哪个，也能用 <span class="mono">adapter="litellm"</span> 显式指定。</div>
    </div>
    <div class="qa">
      <div class="q">✅ mode 是干嘛的</div>
      <div class="a"><span class="mono">mode</span> 是 instructor 的<strong>结构化输出模式</strong>（默认 JSON）。某些不支持 <span class="mono">response_format</span> 的后端要用 <span class="mono">Mode.MD_JSON</span>。这些细节都被 <span class="mono">llm_factory</span> 收进一个参数，调用方一般不用管。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  LLM 抽象都在 <span class="mono">src/ragas/llms/base.py</span>：经典基类 <span class="mono">BaseRagasLLM</span>（<span class="mono">generate_text</span> / <span class="mono">agenerate_text</span> / <span class="mono">is_finished</span>，<span class="mono">generate</span> 用 <span class="mono">RunConfig</span> 加 tenacity 重试，<a href="23-executor.html">第 23 课</a>）与包装器 <span class="mono">LangchainLLMWrapper</span> / <span class="mono">LlamaIndexLLMWrapper</span>；现代基类 <span class="mono">InstructorBaseRagasLLM</span> 与实现 <span class="mono">InstructorLLM</span>（<span class="mono">generate</span> / <span class="mono">agenerate</span>、<span class="mono">_map_provider_params</span> / <span class="mono">_map_openai_params</span> / <span class="mono">_map_google_params</span>、<span class="mono">is_async</span>）。工厂 <span class="mono">llm_factory</span> 也在此。适配器在 <span class="mono">llms/adapters/</span>（<span class="mono">__init__.py</span> 的 <span class="mono">auto_detect_adapter</span> / <span class="mono">get_adapter</span>、<span class="mono">instructor.py</span> 的 <span class="mono">InstructorAdapter</span>、<span class="mono">litellm.py</span>）。导出与弃用包装（<span class="mono">DeprecationHelper</span>，定义在 <span class="mono">ragas/utils.py</span>）在 <span class="mono">llms/__init__.py</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>instructor 让 LLM 直接吐 pydantic 对象</strong>：免手写 JSON 解析，结构化输出由库兜底（呼应 <a href="19-prompt-system.html">第 19 课</a> 的薄 prompt）。</li>
    <li><strong>llm_factory 自动选适配器</strong>：把 OpenAI / Google / LiteLLM 的差异藏进 <span class="mono">auto_detect_adapter</span>，调用方一行搞定。</li>
    <li><strong>client 必填</strong>：去掉隐式 text-only 模式，强制显式注入客户端，行为更可预期。</li>
    <li><strong>DeprecationHelper 平滑迁移</strong>：旧 wrapper 不立刻删，调用即提醒，老用户不被一次性打断。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>优先用 <span class="inline">llm_factory(model, client=…)</span>：返回 <span class="mono">InstructorBaseRagasLLM</span>，<span class="mono">await llm.agenerate(prompt_str, Model)</span> 直接拿 pydantic 对象。</li>
    <li>两条路径：经典 <span class="mono">BaseRagasLLM</span>（langchain 包装、返回文本、配 PydanticPrompt 解析）vs 现代 <span class="mono">InstructorLLM</span>（instructor、返回对象）。</li>
    <li>适配器自动选择：litellm client → litellm；google 新 / 旧 SDK → instructor / litellm；其它 → instructor。</li>
    <li>旧 wrapper 经 <span class="mono">DeprecationHelper</span> 保留并提醒迁移；collections 指标只认现代 LLM（<a href="13-metric-base.html">第 13 课</a>）。</li>
  </ul>
</div>
"""

LESSON_22 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
相似度类指标（语义相似度、上下文召回的匹配……）要先把文本变成向量。ragas 把这件事抽象成 <strong>Embedding 层</strong>，同样是新旧两套插口；而且 <span class="inline">evaluate()</span> 还能<strong>从你选的 LLM 反推 embedding 提供商</strong>，让你少配一次。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  Embedding 是把文本变成向量的"<strong>翻译机</strong>"——把"今天下雨"翻成一串数字坐标，意思相近的句子坐标也相近。ragas 给这台翻译机配了<strong>新旧两套插口</strong>：老插口沿用 langchain，新插口是 ragas 自己的极简接口；你只要 <span class="mono">embed_text</span> 一下，底下接 OpenAI 还是 HuggingFace 都行。
</div>

<h2>新旧两个基类：就差一个 s</h2>
<table class="t">
  <tr><th>维度</th><th>遗留（legacy）</th><th>现代（modern）</th></tr>
  <tr><td><strong>基类名</strong></td><td class="mono">BaseRagasEmbeddings（带 s）</td><td class="mono">BaseRagasEmbedding（不带 s）</td></tr>
  <tr><td><strong>底座</strong></td><td>继承 langchain <span class="mono">Embeddings</span></td><td>ragas 自有 ABC</td></tr>
  <tr><td><strong>核心方法</strong></td><td class="mono">embed_query / embed_documents</td><td class="mono">embed_text / aembed_text</td></tr>
  <tr><td><strong>批处理</strong></td><td>由 langchain 提供</td><td class="mono">embed_texts / aembed_texts（默认实现）</td></tr>
</table>
<p>类名只差一个字母 <span class="mono">s</span>，极易看混——带 s 是老的、不带 s 是新的。</p>

<h2>四个现代 provider</h2>
<pre class="code"><span class="cm"># 都实现 BaseRagasEmbedding（不带 s）的 embed_text / aembed_text</span>
OpenAIEmbeddings        <span class="cm"># embeddings/openai_provider.py</span>
GoogleEmbeddings        <span class="cm"># embeddings/google_provider.py</span>
HuggingFaceEmbeddings   <span class="cm"># embeddings/huggingface_provider.py</span>
LiteLLMEmbeddings       <span class="cm"># embeddings/litellm_provider.py（统一路由很多家）</span></pre>
<p><span class="inline">embedding_factory</span> 是统一入口，能自动判断该给老接口还是新接口：</p>
<pre class="code"><span class="kw">def</span> <span class="fn">embedding_factory</span>(provider=<span class="st">"openai"</span>, model=<span class="kw">None</span>, run_config=<span class="kw">None</span>,
    client=<span class="kw">None</span>, interface=<span class="st">"auto"</span>, base_url=<span class="kw">None</span>, cache=<span class="kw">None</span>, **kwargs)</pre>
<p>注：<span class="mono">modern_embedding_factory</span> 只是已弃用的别名，新代码直接用 <span class="mono">embedding_factory</span>。</p>

<h2>从 LLM 反推 embedding 提供商</h2>
<p>这是省心的关键一招。<span class="inline">evaluate()</span> 里如果某指标需要 embedding 而你没传，会调 <span class="inline">_infer_embedding_provider_from_llm(llm)</span>：读 <span class="mono">llm.provider</span>（或按 LLM 类名映射），缺省回退 <span class="mono">"openai"</span>，再用<strong>同一个 client</strong> 建 embedding：</p>
<pre class="code"><span class="cm"># evaluation.py（节选思路）</span>
provider = _infer_embedding_provider_from_llm(llm)
embeddings = embedding_factory(provider=provider,
                               client=getattr(llm, <span class="st">"client"</span>, <span class="kw">None</span>))
<span class="cm"># 你只配了 LLM，embedding 自动跟上同一家——少配一次</span></pre>

<details class="accordion">
  <summary><span class="badge-num">1</span> 批处理工具：每家的"最佳批大小"不一样 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 embeddings/utils.py</div>
      <div class="a"><span class="inline">validate_texts</span> 校验输入、<span class="inline">batch_texts(texts, batch_size)</span> 切批、<span class="inline">get_optimal_batch_size(provider, model)</span> 给经验值：openai→100、cohere→96、google / vertex→5、huggingface→32、其它→10。把"一次发多少条"按厂商调到合适档位，优化吞吐又不超限。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 为什么相似度指标离不开它</div>
      <div class="a">答案相关性（<span class="inline">AnswerRelevancy</span>）要把"从回答反推出的问题"与原问题算余弦相似度，必须先 embed 再算（用法见 <a href="10-rag-metrics.html">第 10 课</a>、内部见 <a href="17-answer-metrics-internals.html">第 17 课</a>）。Embedding 质量与一致性直接决定这些分数，所以它是这类指标的"地基"。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  接口与工厂在 <span class="mono">src/ragas/embeddings/base.py</span>：遗留基类 <span class="mono">BaseRagasEmbeddings</span>（带 s，继承 langchain <span class="mono">Embeddings</span>）与现代基类 <span class="mono">BaseRagasEmbedding</span>（不带 s，<span class="mono">embed_text</span> / <span class="mono">aembed_text</span> 抽象，<span class="mono">embed_texts</span> / <span class="mono">aembed_texts</span> 默认实现）；工厂 <span class="mono">embedding_factory</span> 与已弃用别名 <span class="mono">modern_embedding_factory</span>；推断函数 <span class="mono">_infer_embedding_provider_from_llm</span>。Provider 各自成文件：<span class="mono">openai_provider.py</span>（<span class="mono">OpenAIEmbeddings</span>）、<span class="mono">google_provider.py</span>（<span class="mono">GoogleEmbeddings</span>）、<span class="mono">huggingface_provider.py</span>（<span class="mono">HuggingFaceEmbeddings</span>）、<span class="mono">litellm_provider.py</span>（<span class="mono">LiteLLMEmbeddings</span>）。批处理工具 <span class="mono">validate_texts</span> / <span class="mono">batch_texts</span> / <span class="mono">get_optimal_batch_size</span> 在 <span class="mono">embeddings/utils.py</span>。<span class="mono">_infer_embedding_provider_from_llm</span> 在 <span class="mono">evaluation.py</span> 中被调用。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>从 LLM 反推 embedding 提供商</strong>：<span class="mono">_infer_embedding_provider_from_llm</span> 复用同一个 client，让用户少配一次、少出错。</li>
    <li><strong>批处理按厂商调档</strong>：<span class="mono">get_optimal_batch_size</span> 把各家上限差异收进经验表，优化吞吐。</li>
    <li><strong>新旧并存、命名留痕</strong>：仅靠一个 <span class="mono">s</span> 区分新旧基类，迁移期老 langchain 资产仍可用。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Embedding 也分新旧栈：<span class="mono">BaseRagasEmbeddings</span>（带 s，legacy / langchain）vs <span class="mono">BaseRagasEmbedding</span>（不带 s，modern）。</li>
    <li>四个现代 provider + 统一入口 <span class="inline">embedding_factory</span>（<span class="mono">modern_embedding_factory</span> 为弃用别名）。</li>
    <li><span class="inline">evaluate()</span> 用 <span class="mono">_infer_embedding_provider_from_llm</span> 从 LLM 反推提供商；像 <span class="mono">AnswerRelevancy</span> 这类指标依赖 embedding（呼应 <a href="10-rag-metrics.html">第 10 课</a>、<a href="17-answer-metrics-internals.html">第 17 课</a>）。</li>
  </ul>
</div>
"""

LESSON_23 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
一次评测往往要跑成百上千次 LLM 调用。<strong>Executor</strong> 是 ragas 的"<strong>阅卷调度中心</strong>"：并发跑、谁卡住超时跳过、单题出错记零分不拖累整体、还能中途叫停；而 <span class="inline">RunConfig</span> 是这套并发与容错的<strong>总开关</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  想象一个<strong>阅卷调度中心</strong>：多位老师<strong>并发</strong>改卷；某份卷子改太久就<strong>超时跳过</strong>；某份算错了不至于让整轮作废，而是<strong>记零分</strong>继续；中途还能<strong>喊停</strong>全场。最关键的是——不管谁先改完，<strong>最后成绩单要按学号原序排列</strong>，不能乱。
</div>

<p><strong>本课流程一眼看</strong>：Executor 怎么把上千次调用并发跑完、又保持原序 👇</p>
<div class="flow">
  <div class="node"><div class="nt">submit 任务</div><div class="nd">wrap_callable 带索引</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">并发跑</div><div class="nd">as_completed · 超时跳过</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">容错</div><div class="nd">出错记 np.nan（可重试）</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">按索引排序</div><div class="nd">还原提交顺序</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">结果列表</div><div class="nd">顺序 == 提交顺序</div></div>
</div>

<h2>保序并发：包装时记下索引</h2>
<p>并发执行后结果是乱序到达的。Executor 在 <span class="inline">submit</span> 时给每个任务编号，用 <span class="inline">wrap_callable_with_index(callable, counter)</span> 把返回值包成 <span class="mono">(counter, result)</span>；收齐后按索引排序再剥掉编号，于是<strong>输出顺序 == 提交顺序</strong>：</p>
<pre class="code"><span class="kw">def</span> <span class="fn">wrap_callable_with_index</span>(callable, counter):
    <span class="kw">async def</span> <span class="fn">wrapped</span>(*args, **kwargs):
        <span class="kw">try</span>:
            result = <span class="kw">await</span> callable(*args, **kwargs)
            <span class="kw">return</span> (counter, result)
        <span class="kw">except</span> Exception <span class="kw">as</span> e:
            <span class="kw">if</span> self.raise_exceptions:
                <span class="kw">raise</span> e
            <span class="cm"># 不抛异常时：记日志，单题结果填 np.nan</span>
            <span class="kw">return</span> (counter, np.nan)
    <span class="kw">return</span> wrapped

<span class="cm"># aresults：sorted(results, key=lambda x: x[0]) 后剥掉索引 → 原序还原</span></pre>
<p>单个任务失败时（默认 <span class="mono">raise_exceptions=False</span>）填 <span class="inline">np.nan</span> 而不是炸掉整轮——某一格分数缺失，整张成绩单照样产出。</p>

<h2>RunConfig：并发 / 超时 / 重试的总开关</h2>
<p>Executor 的行为由一个 <span class="inline">RunConfig</span> 收口。<strong>实测默认值</strong>（<span class="mono">run_config.py</span>）：</p>
<table class="t">
  <tr><th>字段</th><th>默认值</th><th>含义</th></tr>
  <tr><td class="mono">timeout</td><td class="mono">180</td><td>单任务超时（秒）</td></tr>
  <tr><td class="mono">max_retries</td><td class="mono">10</td><td>最大重试次数</td></tr>
  <tr><td class="mono">max_wait</td><td class="mono">60</td><td>重试退避上限（秒）</td></tr>
  <tr><td class="mono">max_workers</td><td class="mono">16</td><td>最大并发数</td></tr>
  <tr><td class="mono">exception_types</td><td class="mono">(Exception,)</td><td>哪些异常触发重试</td></tr>
  <tr><td class="mono">log_tenacity</td><td class="mono">False</td><td>是否打印重试日志</td></tr>
  <tr><td class="mono">seed</td><td class="mono">42</td><td>随机种子</td></tr>
</table>
<p>重试由 <strong>tenacity</strong> 实现：<span class="inline">add_retry</span> / <span class="inline">add_async_retry</span> 组装 <span class="mono">wait_random_exponential(multiplier=1, max=max_wait)</span> + <span class="mono">stop_after_attempt(max_retries)</span> + <span class="mono">reraise=True</span>——指数退避加随机抖动，重试到上限仍失败就抛出。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 中途叫停与一次性批处理 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 cancel 怎么停</div>
      <div class="a">Executor 持有一个 <span class="mono">_cancel_event = threading.Event()</span>。<span class="inline">cancel()</span> 置位、<span class="inline">is_cancelled()</span> 查询；<span class="mono">_process_jobs</span> 在调度循环里检查这个事件，置位后不再派发新任务，实现"喊停全场"。</div>
    </div>
    <div class="qa">
      <div class="q">✅ run_async_batch</div>
      <div class="a">便捷函数 <span class="inline">run_async_batch(desc, func, kwargs_list, batch_size)</span> 内部建一个 <span class="mono">RunConfig()</span> + <span class="mono">Executor(raise_exceptions=True)</span>，把一批同构调用并发跑完。注意它<strong>默认抛异常</strong>，适合"要么全成、要么报错"的批处理场景。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  调度核心在 <span class="mono">src/ragas/executor.py</span>：dataclass <span class="mono">Executor</span>（<span class="mono">desc</span> / <span class="mono">show_progress</span> / <span class="mono">raise_exceptions=False</span> / <span class="mono">batch_size</span> / <span class="mono">run_config</span> / <span class="mono">_cancel_event</span>），方法 <span class="mono">submit</span>、<span class="mono">wrap_callable_with_index</span>、<span class="mono">_process_jobs</span>、<span class="mono">results</span> / <span class="mono">aresults</span>（<span class="mono">sorted(..., key=lambda x: x[0])</span> 保序）、<span class="mono">cancel</span> / <span class="mono">is_cancelled</span>，以及便捷函数 <span class="mono">run_async_batch</span>。配置在 <span class="mono">src/ragas/run_config.py</span>：<span class="mono">RunConfig</span>（默认 <span class="mono">timeout=180</span> / <span class="mono">max_retries=10</span> / <span class="mono">max_wait=60</span> / <span class="mono">max_workers=16</span> / <span class="mono">seed=42</span>）与 <span class="mono">add_retry</span> / <span class="mono">add_async_retry</span>（tenacity 退避重试）。失败填 <span class="mono">np.nan</span> 的逻辑在 <span class="mono">wrap_callable_with_index</span>。补充一点：单任务<strong>超时</strong>其实由 metric 侧的 <span class="mono">asyncio.wait_for</span> 在 <span class="mono">single_turn_ascore</span>（<span class="mono">metrics/base.py</span>）里强制，超时与异常一样落到 <span class="mono">np.nan</span>——并非 Executor 自己计时。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>包装时捕获索引</strong>：并发乱序执行、结果按原序重排，调用方无感。</li>
    <li><strong>单任务失败转 <span class="mono">np.nan</span></strong>：一题翻车不拖垮整轮评测，鲁棒性拉满（默认 <span class="mono">raise_exceptions=False</span>）。</li>
    <li><strong>RunConfig 收敛配置</strong>：把并发 / 超时 / 重试 / 种子统一成一个对象，配一处、处处生效。</li>
    <li><strong>tenacity 指数退避</strong>：重试带随机抖动，避免一窝蜂重试压垮上游。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Executor 用 <span class="mono">wrap_callable_with_index</span> 保序、用 <span class="mono">np.nan</span> 容错、用 <span class="mono">_cancel_event</span> 叫停。</li>
    <li><span class="inline">RunConfig</span> 是并发与容错的总开关，默认 <span class="mono">timeout=180 / max_retries=10 / max_wait=60 / max_workers=16 / seed=42</span>。</li>
    <li>重试基于 tenacity（指数退避 + 抖动 + reraise）；评测的并发与容错都在这一层（呼应 <a href="03-evaluation-lifecycle.html">第 3 课</a> 的评测生命周期）。</li>
  </ul>
</div>
"""

LESSON_24 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
评测要工程化，得能<strong>看清</strong>、<strong>算钱</strong>、<strong>省时</strong>。本课讲三件套：<strong>Callbacks</strong> 把一次运行组织成可追踪的树、<strong>Cost</strong> 统计 token 与花费、<strong>Cache</strong> 用内容哈希复用结果不重跑。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  追踪（callbacks）像<strong>行车记录仪</strong>，把每一步谁调谁、输入输出都录下来；成本（cost）像<strong>油表</strong>，实时显示这趟烧了多少 token、合多少钱；缓存（cache）像<strong>记住走过的路</strong>——同样的路口同样的问题，直接用上次的答案，不再重开一遍导航。
</div>

<h2>Callbacks：把一次运行组织成树</h2>
<p><span class="inline">new_group(name, inputs, callbacks, ...)</span> 开一个分组，返回 <span class="mono">(run_manager, group_manager)</span>，让子调用挂到父节点下。<span class="inline">RagasTracer</span> 是个回调处理器，把整轮运行记成一棵 <strong>trace 树</strong>：</p>
<pre class="code"><span class="cm"># ChainType：运行树的层级</span>
<span class="kw">class</span> <span class="fn">ChainType</span>(Enum):
    EVALUATION    <span class="cm"># 整轮评测（树根·第1层）</span>
    METRIC        <span class="cm"># 某个指标（第3层·嵌在 ROW 之下）</span>
    ROW           <span class="cm"># 某一行样本（第2层）</span>
    RAGAS_PROMPT  <span class="cm"># 一次 prompt 调用（叶·第4层）</span>

<span class="cm"># RagasTracer：on_chain_start 建节点并链到父节点 children，</span>
<span class="cm"># on_chain_end 记录 outputs；traces: Dict[str, ChainRun]</span>
<span class="cm"># parse_run_traces 自根而下遍历 EVALUATION→ROW→METRIC→PROMPT</span></pre>
<p>于是"哪个指标、哪一行、调了哪个 prompt、输入输出是什么"都能被还原——可观测性做成了一个<strong>可挂载的回调层</strong>。</p>

<h2>Cost：按厂商统一算账</h2>
<p><span class="inline">TokenUsage</span> 记 <span class="mono">input_tokens</span> / <span class="mono">output_tokens</span> / <span class="mono">model</span>，支持同模型相加；<span class="inline">cost(cost_per_input_token, cost_per_output_token)</span> 折算费用。<span class="inline">CostCallbackHandler</span> 在每次 <span class="mono">on_llm_end</span> 收集用量，聚合出 <span class="mono">total_tokens</span> / <span class="mono">total_cost</span>。各厂商响应格式不同，靠对应 parser 抹平：</p>
<table class="t">
  <tr><th>厂商</th><th>解析器</th><th>取值字段</th></tr>
  <tr><td>OpenAI</td><td class="mono">get_token_usage_for_openai</td><td class="mono">prompt_tokens / completion_tokens</td></tr>
  <tr><td>Anthropic</td><td class="mono">get_token_usage_for_anthropic</td><td class="mono">usage.input_tokens / output_tokens</td></tr>
  <tr><td>Bedrock</td><td class="mono">get_token_usage_for_bedrock</td><td class="mono">prompt_tokens / completion_tokens</td></tr>
</table>
<pre class="code"><span class="kw">from</span> ragas.cost <span class="kw">import</span> get_token_usage_for_openai
result = evaluate(dataset, metrics, llm=llm,
                  token_usage_parser=get_token_usage_for_openai)
result.total_tokens()   <span class="cm"># 聚合用量</span>
result.total_cost(cost_per_input_token=<span class="st">5e-6</span>, cost_per_output_token=<span class="st">15e-6</span>)</pre>

<h2>Cache：内容哈希做 key，复用省钱</h2>
<p><span class="inline">cacher(cache_backend)</span> 是个装饰器，包住 LLM / embedding 调用；后端为 <span class="mono">None</span> 时原样返回（零成本可关）。缓存键由<strong>函数 + 参数</strong>哈希而来：</p>
<pre class="code"><span class="cm"># cache.py</span>
<span class="kw">class</span> <span class="fn">CacheInterface</span>(ABC):        <span class="cm"># get / set / has_key</span>
<span class="kw">class</span> <span class="fn">DiskCacheBackend</span>(CacheInterface): <span class="cm"># cache_dir=".cache"，基于 diskcache</span>

<span class="cm"># _generate_cache_key：排除 EXCLUDE_KEYS（如 callbacks），</span>
<span class="cm"># 再 json.dumps(sort_keys=True) + sha256；_make_hashable 递归处理嵌套</span>

<span class="nd">@cacher</span>(cache_backend=DiskCacheBackend())
<span class="kw">async def</span> <span class="fn">agenerate</span>(...): ...   <span class="cm"># 相同输入直接命中缓存</span></pre>
<p>键里特意<strong>排除 <span class="mono">callbacks</span></strong>——它每轮都变且不影响结果，否则永远命不中缓存。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么用内容哈希、而不是简单计数 <span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 内容寻址</div>
      <div class="a">用"<strong>函数 + 参数内容</strong>"的 sha256 当 key，意味着<strong>只要输入一样，结果就能复用</strong>，与调用顺序、调用次数无关。<span class="inline">_make_hashable</span> 递归把 dict / list / pydantic 等转成可排序的稳定结构，保证同一份输入永远算出同一个 key。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 三件套的边界</div>
      <div class="a">回调<strong>只观察、不改结果</strong>；成本<strong>只统计、不计费扣款</strong>（费率由你传入）；缓存<strong>只复用、可随时关</strong>（后端给 <span class="mono">None</span> 即旁路）。三者都是<strong>可选挂载</strong>，不侵入指标逻辑。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  追踪在 <span class="mono">src/ragas/callbacks.py</span>：<span class="mono">new_group</span>、<span class="mono">ChainType</span>（<span class="mono">EVALUATION</span> / <span class="mono">METRIC</span> / <span class="mono">ROW</span> / <span class="mono">RAGAS_PROMPT</span>）、<span class="mono">ChainRun</span>（<span class="mono">run_id</span> / <span class="mono">parent_run_id</span> / <span class="mono">children</span> / <span class="mono">inputs</span> / <span class="mono">outputs</span>）、<span class="mono">RagasTracer</span>（<span class="mono">traces</span>、<span class="mono">on_chain_start</span> / <span class="mono">on_chain_end</span>、<span class="mono">to_jsons</span>）、<span class="mono">parse_run_traces</span>。成本在 <span class="mono">src/ragas/cost.py</span>：<span class="mono">TokenUsage</span>（<span class="mono">__add__</span> / <span class="mono">cost</span>）、<span class="mono">CostCallbackHandler</span>、解析器 <span class="mono">get_token_usage_for_openai</span> / <span class="mono">_anthropic</span> / <span class="mono">_bedrock</span>。缓存在 <span class="mono">src/ragas/cache.py</span>：<span class="mono">CacheInterface</span>、<span class="mono">DiskCacheBackend</span>（<span class="mono">cache_dir=".cache"</span>）、<span class="mono">cacher</span> 装饰器、<span class="mono">_generate_cache_key</span> / <span class="mono">_make_hashable</span>（sha256、排除 <span class="mono">callbacks</span>）。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>可观测性做成可挂载层</strong>：回调不改业务逻辑，按需挂上即可还原整棵运行树。</li>
    <li><strong>缓存用内容哈希做 key</strong>：相同输入复用结果省钱，且与调用次序无关；排除 <span class="mono">callbacks</span> 防止永不命中。</li>
    <li><strong>成本对各厂商统一抽象</strong>：用 parser 抹平字段差异，<span class="mono">TokenUsage</span> 聚合一处看清花费。</li>
    <li><strong>三者皆可选</strong>：缓存后端给 <span class="mono">None</span> 即旁路，工程化能力按需启用。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>Callbacks：<span class="mono">new_group</span> + <span class="mono">RagasTracer</span> 把一轮运行组织成 <span class="mono">EVALUATION→ROW→METRIC→PROMPT</span> 的 trace 树。</li>
    <li>Cost：<span class="mono">CostCallbackHandler</span> + 各厂商 parser 统计 <span class="mono">TokenUsage</span>，算 <span class="mono">total_tokens</span> / <span class="mono">total_cost</span>。</li>
    <li>Cache：<span class="mono">cacher</span> + <span class="mono">DiskCacheBackend</span> 以内容 sha256 为 key 复用 LLM / embedding 结果（呼应 <a href="21-llm-abstraction.html">第 21 课</a>、<a href="22-embedding-abstraction.html">第 22 课</a>）。</li>
    <li>可观测、可算钱、可缓存——评测工程化的三件套。</li>
  </ul>
</div>
"""
