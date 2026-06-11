"""Content for part1 (stub)."""

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
<p class="lead">（建设中）本课内容稍后填充。</p>
<div class="card analogy"><div class="tag">🧩 生活类比</div>占位。</div>
<div class="card key"><div class="tag">✅ 本课要点</div><ul><li>占位。</li></ul></div>
"""

LESSON_03 = r"""
<p class="lead">（建设中）本课内容稍后填充。</p>
<div class="card analogy"><div class="tag">🧩 生活类比</div>占位。</div>
<div class="card key"><div class="tag">✅ 本课要点</div><ul><li>占位。</li></ul></div>
"""
