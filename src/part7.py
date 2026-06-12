"""Content for part7 — 第七部分 · 实验与工程化（31-37）."""

LESSON_31 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
<a href="08-experiment.html">第 8 课</a>初识了 <span class="inline">@experiment</span>；本课钻进 <span class="mono">experiment.py</span> 把它拆到底：
<span class="inline">Experiment</span> 本质是一张<strong>挂着 backend 的表</strong>，<span class="inline">arun</span> 负责<strong>取名 → 解析存储 → 并发跑 → 落盘</strong>，
再加 <span class="inline">version_experiment</span> 的 git 版本化，凑齐"每改一次跑一轮、自动存档、可对比"的评测闭环。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把评测想成一张<strong>实验台</strong>：每改一次（换 prompt、调检索、换模型）就<strong>跑一轮</strong>，台子自动给这轮<strong>起个好记的名字</strong>、
  把每行结果<strong>记进档案柜</strong>（backend），还能用 <strong>git 给这版代码盖个时间戳</strong>。下次想比"哪版更好"，翻档案柜即可，不必靠记忆。
</div>

<h2>Experiment：一张挂着 backend 的表</h2>
<p><span class="inline">Experiment</span> 的定义短得出奇——它直接继承数据表基类 <span class="inline">DataTable</span>（<a href="06-two-datasets.html">第 6 课</a>），只改了一个类型标记：</p>
<pre class="code"><span class="kw">class</span> <span class="fn">Experiment</span>(DataTable):
    DATATABLE_TYPE = <span class="st">"Experiment"</span>   <span class="cm"># 与 Dataset 共用一套表/存储机制</span></pre>
<p>所以一个实验<strong>就是一张表</strong>：每行是"对一行数据评测后要留痕的结果"。整张表通过 backend 落盘时，
<span class="inline">save()</span> 会按 <span class="mono">DATATABLE_TYPE</span> 选择存进 <span class="mono">experiments/</span>（调 <span class="mono">save_experiment</span>）还是 <span class="mono">datasets/</span>（调 <span class="mono">save_dataset</span>）——
于是实验与数据集<strong>同套机制、分开命名空间、互不覆盖</strong>（<a href="32-backends.html">下一课</a>细讲 backend）。</p>

<h2>@experiment 与 arun：装饰器背后的五步</h2>
<p><span class="inline">@experiment(...)</span> 返回一个 <span class="inline">ExperimentWrapper</span>：它的 <span class="inline">__call__</span> 只是<strong>跑一行</strong>（自动兼容 async / sync），
真正的"对整张表批量跑"交给 <span class="inline">arun</span>。把源码压扁，<span class="inline">arun</span> 的骨架就是五步：</p>
<pre class="code"><span class="kw">async def</span> <span class="fn">arun</span>(self, dataset, name=None, backend=None):
    <span class="cm"># ① 没给名字就生成一个好记的随机名；name_prefix 会拼在名字前（即使显式传了名也照拼）</span>
    <span class="kw">if</span> name <span class="kw">is</span> None:
        name = memorable_names.generate_unique_name()

    <span class="cm"># ② 解析 backend：显式传入 > 装饰器默认 > 回退到 dataset.backend</span>
    experiment_backend = backend <span class="kw">or</span> self.default_backend
    <span class="kw">if</span> experiment_backend:
        resolved_backend = Experiment._resolve_backend(experiment_backend)
    <span class="kw">else</span>:
        resolved_backend = dataset.backend

    <span class="cm"># ③ 建一张 Experiment 表</span>
    experiment_view = Experiment(name=name, data_model=self.experiment_model, backend=resolved_backend)

    <span class="cm"># ④ 每行包成任务，as_completed 并发跑；单行失败只记 warning 不中断</span>
    tasks = [self(item) <span class="kw">for</span> item <span class="kw">in</span> dataset]
    <span class="kw">for</span> future <span class="kw">in</span> asyncio.as_completed(tasks):
        <span class="kw">try</span>:
            result = <span class="kw">await</span> future
            <span class="kw">if</span> result <span class="kw">is</span> <span class="kw">not</span> None:
                experiment_view.append(result)
        <span class="kw">except</span> Exception <span class="kw">as</span> e:
            print(<span class="st">f"Warning: Task failed with error: {e}"</span>)

    experiment_view.save()        <span class="cm"># ⑤ 落盘后返回这张表</span>
    <span class="kw">return</span> experiment_view</pre>
<p>真实代码里第 ④ 步还套了 <span class="inline">tqdm</span> 进度条（<span class="mono">desc="Running experiment"</span>），并在 <span class="mono">finally</span> 里关闭它。
注意第 ② 步的<strong>回退链</strong>：什么都不传时实验就<strong>沿用数据集的 backend</strong>，这样"读哪存哪"最省心。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 实验与数据集共用存储，凭什么不会互相覆盖？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 靠 DATATABLE_TYPE 分流</div>
      <div class="a"><span class="inline">DataTable.save()</span> 检查 <span class="mono">DATATABLE_TYPE</span>：是 <span class="mono">"Experiment"</span> 就调 <span class="inline">backend.save_experiment</span>，否则调 <span class="inline">save_dataset</span>。
        文件型 backend 把两者分别放进 <span class="mono">experiments/</span> 与 <span class="mono">datasets/</span> 两个子目录，<strong>同名也不打架</strong>。读取时同理（<span class="inline">load_experiment</span> / <span class="inline">load_dataset</span>）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 单行抛错会让整轮白跑吗</div>
      <div class="a">不会。<span class="inline">as_completed</span> 循环里逐个 <span class="inline">await</span>，单个任务的异常被 <span class="mono">try/except</span> 捕获、打印一条 warning 后<strong>继续</strong>——
        其余行照常写入、照常 <span class="inline">save()</span>。这与 <a href="07-evaluate.html">evaluate</a> 的"失败记 NaN"是同一种"整批不被一行拖垮"的容错哲学。</div>
    </div>
  </div>
</details>

<h2>version_experiment：把实验钉在某次代码上</h2>
<p>结果存进 backend 解决了"这轮跑出什么"；<span class="inline">version_experiment(name)</span> 解决"这轮对应哪段代码"。它需要 GitPython（<span class="mono">pip install ragas[git]</span>），步骤是：</p>
<ol>
  <li>定位仓库：没给 <span class="mono">repo_path</span> 就用 <span class="inline">find_git_root()</span> 找仓库根。</li>
  <li>暂存改动：默认只暂存<strong>已跟踪</strong>文件（<span class="mono">git add -u</span>）；<span class="mono">stage_all=True</span> 则连未跟踪文件一起（<span class="mono">git add .</span>）。</li>
  <li>提交：默认消息 <span class="mono">Experiment: {name}</span>；若没有任何改动，则直接用当前 <span class="mono">HEAD</span> 的 commit。</li>
  <li>建分支：<span class="mono">create_branch=True</span> 时创建分支 <span class="mono">ragas/{name}</span>，最后返回 commit hash。</li>
</ol>
<p>于是每个实验名都能<strong>回溯到确切的代码快照</strong>：结果在 backend、代码在 git 分支，两边用同一个 <span class="mono">name</span> 串起来。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  全在 <span class="mono">src/ragas/experiment.py</span>：<span class="mono">experiment(experiment_model, backend, name_prefix)</span> 装饰器返回 <span class="mono">ExperimentWrapper</span>；
  <span class="mono">ExperimentWrapper.__call__</span> 跑一行（<span class="mono">asyncio.iscoroutinefunction</span> 兼容 async/sync），<span class="mono">arun</span> 负责取名（<span class="mono">memorable_names.generate_unique_name</span>）/ 解析 backend（<span class="mono">Experiment._resolve_backend</span>，回退 <span class="mono">dataset.backend</span>）/ 建 <span class="mono">Experiment</span> / <span class="mono">asyncio.as_completed</span> + <span class="mono">tqdm</span> 并发 / <span class="mono">save</span>。
  <span class="mono">Experiment(DataTable)</span> 只设 <span class="mono">DATATABLE_TYPE="Experiment"</span>；存储分流逻辑在 <span class="mono">dataset.py</span> 的 <span class="mono">DataTable.save</span>。<span class="mono">version_experiment</span> 用 GitPython 提交并建 <span class="mono">ragas/{name}</span> 分支。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>结果落 backend + git 版本化 = 真正的评测闭环</strong>：每轮的<strong>产物</strong>进档案柜、<strong>代码</strong>进 git 分支，用同一个实验名挂钩，随时回看与对比。</li>
    <li><strong>arun 天然并发</strong>：<span class="inline">asyncio.as_completed</span> 并发跑所有行、<span class="inline">tqdm</span> 显示进度，单行失败只记 warning 不中断整轮。</li>
    <li><strong>Experiment 复用 DataTable</strong>：实验不另起炉灶，而是"一张特殊类型的表"，自动享受 backend 的存取与 <span class="mono">to_pandas</span> 等能力。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><strong>实验 = 跑一轮 + 存档 + 可对比</strong>：<span class="inline">Experiment</span> 是挂着 backend 的 <span class="mono">DataTable</span>，每行一个留痕结果。</li>
    <li><span class="inline">arun</span> 五步：<strong>取名 → 解析 backend（回退 dataset.backend）→ 建表 → as_completed 并发 → save</strong>。</li>
    <li><span class="inline">version_experiment</span> 用 git 把实验钉在代码快照上（分支 <span class="mono">ragas/{name}</span>），结果与代码两边对齐。</li>
  </ul>
</div>
"""

LESSON_32 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课的实验把结果<strong>存进了 backend</strong>，却没说存到哪、怎么换。本课打开 <span class="mono">backends/</span>：
一套统一的 <span class="inline">BaseBackend</span> 接口、四个内置实现（csv / jsonl / 内存 / 网盘），靠<strong>"注册表 + 字符串名"</strong>随意切换，
还能用 entry-points 让第三方 backend <strong>即插即用</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  backend 像插线板上的<strong>存储插槽</strong>：要本地 CSV 就插 <span class="inline">"local/csv"</span>，要保真嵌套结构就换 <span class="inline">"local/jsonl"</span>，
  想纯内存跑完即弃就插 <span class="inline">"inmemory"</span>，要存到云端就插 <span class="inline">"gdrive"</span>。上层代码只认<strong>插槽名</strong>，插的是哪块"存储电器"由注册表负责对上号。
</div>

<h2>BaseBackend：六个方法定下契约</h2>
<p><span class="mono">backends/base.py</span> 的 <span class="inline">BaseBackend</span> 是个 <span class="mono">ABC</span>，把"存取数据集 / 实验"抽象成六个方法。数据统一是 <span class="mono">List[Dict[str, Any]]</span>，数据集与实验<strong>接口相同、存储分开</strong>：</p>
<table class="t">
  <tr><th>方法</th><th>职责</th></tr>
  <tr><td class="mono">load_dataset(name)<br>load_experiment(name)</td><td>按名读出一串字典；缺失抛 <span class="mono">FileNotFoundError</span>；空集返回 <span class="mono">[]</span> 而非 <span class="mono">None</span></td></tr>
  <tr><td class="mono">save_dataset(name, data, data_model=None)<br>save_experiment(...)</td><td>覆盖式写入；按需创建存储目录；<span class="mono">data_model</span> 仅作校验上下文（可忽略）</td></tr>
  <tr><td class="mono">list_datasets()<br>list_experiments()</td><td>列出已有名字（排序、不含扩展名 / 路径）</td></tr>
</table>
<p>正因为契约只关心"按名读写一串字典"，<strong>底层存的是文件、内存还是云端，对上层完全透明</strong>——这是后面能"随意换插槽"的前提。</p>

<h2>四个内置 backend</h2>
<table class="t">
  <tr><th>类</th><th>字符串名</th><th>特点 / 适用</th></tr>
  <tr><td class="mono">LocalCSVBackend</td><td class="mono">local/csv</td><td>CSV 文件，人类可读、能用表格软件打开；但复杂结构会被<strong>压成字符串</strong>，只宜简单表格</td></tr>
  <tr><td class="mono">LocalJSONLBackend</td><td class="mono">local/jsonl</td><td>JSONL 文件，<strong>保真各种数据类型</strong>与嵌套结构，复杂数据首选</td></tr>
  <tr><td class="mono">InMemoryBackend</td><td class="mono">inmemory</td><td>纯内存、<strong>不落盘</strong>，零配置；适合临时 train/test 切分、中间结果与测试</td></tr>
  <tr><td class="mono">GDriveBackend</td><td class="mono">gdrive</td><td>存到 Google Drive；属<strong>可选依赖</strong>，装不上也不影响其余 backend（<span class="mono">__init__.py</span> 里 try/except 导入）</td></tr>
</table>
<p>文件型的 <span class="inline">LocalCSVBackend</span> / <span class="inline">LocalJSONLBackend</span> 都接收一个 <span class="mono">root_dir</span>，并在其下分出 <span class="mono">datasets/</span> 与 <span class="mono">experiments/</span> 两个子目录——正好对接上一课说的"按 <span class="mono">DATATABLE_TYPE</span> 分流"。</p>

<h2>注册表 + 字符串名：怎么选 backend</h2>
<p>你几乎不用手动 <span class="mono">import</span> 某个 backend 类——给 <span class="inline">Dataset</span> 一个<strong>字符串名</strong>即可，其余交给注册表：</p>
<pre class="code"><span class="kw">from</span> ragas <span class="kw">import</span> Dataset
<span class="kw">from</span> ragas.backends <span class="kw">import</span> get_registry, print_available_backends

print_available_backends()        <span class="cm"># 打印所有已注册 backend（名字 / 别名 / 模块 / 文档）</span>

<span class="cm"># 用字符串名选 backend；root_dir 等参数透传给该 backend 的构造函数</span>
ds = Dataset(name=<span class="st">"qa"</span>, backend=<span class="st">"local/csv"</span>, root_dir=<span class="st">"./data"</span>)</pre>
<p>背后是 <span class="inline">DataTable._resolve_backend</span>：发现 backend 是字符串，就向 <span class="inline">get_registry()</span> 拿到全局 <span class="inline">BackendRegistry</span>（单例），
按名查出类、用 <span class="mono">**kwargs</span> 实例化；查不到则报错并<strong>列出所有可用名字</strong>。需要时也能 <span class="inline">register_backend(name, cls, aliases=...)</span> 手动注册自定义 backend。</p>

<h2>entry-points：第三方 backend 即插即用</h2>
<p>内置的四个 backend 并不是写死在某个列表里，而是通过 <span class="mono">pyproject.toml</span> 的 entry-points 声明、由注册表<strong>自动发现</strong>：</p>
<pre class="code"><span class="cm"># pyproject.toml</span>
[project.entry-points.<span class="st">"ragas.backends"</span>]
<span class="st">"local/csv"</span>   = <span class="st">"ragas.backends.local_csv:LocalCSVBackend"</span>
<span class="st">"local/jsonl"</span> = <span class="st">"ragas.backends.local_jsonl:LocalJSONLBackend"</span>
<span class="st">"inmemory"</span>    = <span class="st">"ragas.backends.inmemory:InMemoryBackend"</span>
<span class="st">"gdrive"</span>      = <span class="st">"ragas.backends.gdrive_backend:GDriveBackend"</span></pre>
<p><span class="inline">BackendRegistry.discover_backends()</span> 用 <span class="inline">importlib.metadata.entry_points()</span> 扫描 <span class="mono">"ragas.backends"</span> 这一组，逐个 <span class="mono">load()</span> 注册（单个失败只记 warning）。
于是<strong>任何第三方包</strong>只要在自己的 <span class="mono">pyproject.toml</span> 里声明同组 entry-point，装上后就能被 ragas 认出来——<strong>无需改 ragas 源码</strong>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么要把 backend 名声明成 entry-points，而不是写死一个字典？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 解耦：发现机制 vs 硬编码</div>
      <div class="a">写死字典意味着每加一个 backend 都要改 ragas 本体。entry-points 把"有哪些 backend"变成<strong>安装期可发现</strong>的元数据：
        第三方 <span class="mono">pip install</span> 自己的包，注册表启动时一扫就有了。这正是 setuptools 插件体系的标准玩法（<a href="34-integrations-frameworks.html">第 34 课</a>的集成模块也走这种"可插拔"思路）。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 别名与单例</div>
      <div class="a"><span class="inline">BackendRegistry</span> 是单例（<span class="mono">__new__</span> 保证全局唯一），像字典一样支持 <span class="mono">in</span> / <span class="mono">[]</span> / <span class="mono">keys()</span>，并支持<strong>别名</strong>（<span class="inline">register_aliases</span>）。
        首次访问触发一次性 <span class="inline">discover_backends</span>，之后用 <span class="mono">_discovered</span> 标记避免重复扫描。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  接口在 <span class="mono">backends/base.py</span>（<span class="mono">BaseBackend</span> 六个抽象方法）；四个实现分别在 <span class="mono">backends/local_csv.py</span>、<span class="mono">local_jsonl.py</span>、<span class="mono">inmemory.py</span>、<span class="mono">gdrive_backend.py</span>。
  注册机制在 <span class="mono">backends/registry.py</span>：<span class="mono">BackendRegistry</span>（单例、dict-like、<span class="mono">discover_backends</span> 扫 entry-points）、<span class="mono">get_registry</span>、<span class="mono">register_backend</span>、<span class="mono">print_available_backends</span>、全局 <span class="mono">BACKEND_REGISTRY</span>。
  字符串解析在 <span class="mono">dataset.py</span> 的 <span class="mono">DataTable._resolve_backend</span>；四个内置名的声明在仓库根 <span class="mono">pyproject.toml</span> 的 <span class="mono">[project.entry-points."ragas.backends"]</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>统一接口屏蔽存储差异</strong>：六个方法 + <span class="mono">List[Dict]</span> 的约定，让 csv / jsonl / 内存 / 云端在上层<strong>长一个样</strong>，换插槽不改业务代码。</li>
    <li><strong>entry-points 让第三方 backend 即插即用</strong>：声明一条同组 entry-point 即被发现，<strong>无需改 ragas</strong>，也无需上层手动 import。</li>
    <li><strong>可选依赖优雅降级</strong>：<span class="inline">GDriveBackend</span> 装不上时被 try/except 跳过，不拖垮整包；发现失败也只记 warning。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>存储<strong>可插拔</strong>：<span class="inline">BaseBackend</span> 用六个方法定契约，四个内置实现 csv / jsonl / 内存 / 网盘任选。</li>
    <li>选 backend 靠<strong>注册表 + 字符串名</strong>：<span class="inline">Dataset(name, "local/csv", root_dir=...)</span> 经 <span class="inline">_resolve_backend</span> 查注册表实例化。</li>
    <li>记住<strong>注册机制</strong>：entry-points 组 <span class="mono">"ragas.backends"</span> 让第三方 backend 自动被发现，无需改 ragas。</li>
  </ul>
</div>
"""

LESSON_33 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
LLM 当裁判，难免和人类口味有偏差。ragas 给指标准备了一套<strong>"培训"机制</strong>：喂一批<strong>人工标注</strong>，
自动<strong>改写指令</strong>、<strong>挑选示例</strong>，把指标调到更贴合人类判断——再用<strong>与标注的相关性</strong>量化"调得准不准"。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  把一个 LLM 指标想成<strong>新来的阅卷老师</strong>：光给评分标准还不够，得拿一沓<strong>标准答案卷</strong>（人工标注）给他<strong>培训</strong>——
  一边帮他<strong>把评分标准的措辞改清楚</strong>（优化指令），一边给他<strong>看几份典型范卷</strong>（few-shot 示例）。培训完再拿没见过的卷子考他，看打分和老教师有多<strong>一致</strong>。
</div>

<p><strong>本课流程一眼看</strong>：给 LLM 指标做一次「培训」、对齐人类口味 👇</p>
<div class="flow">
  <div class="node"><div class="nt">人工标注</div><div class="nd">输入 + 人给的分（.json）</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">喂给 train()</div><div class="nd">内置 / Simple 各有入口</div></div>
  <div class="arrow">→</div>
  <div class="node"><div class="nt">优化</div><div class="nd">改写指令 + 挑 few-shot 示例</div></div>
  <div class="arrow">→</div>
  <div class="node hl"><div class="nt">更准的指标</div><div class="nd">再用与标注的相关性验证</div></div>
</div>

<p>关键点：指标"能跑"不代表"打得准"。训练的目标是<strong>对齐人类标注</strong>——用一批"输入 + 人给的分"作监督信号，自动搜索更好的<strong>指令</strong>与<strong>示例</strong>，省去人肉反复试 prompt。ragas 按指标类型提供<strong>两套</strong>入口：内置 <span class="inline">MetricWithLLM</span> 指标用 <span class="inline">train()</span>，自定义 Simple 指标用 <span class="inline">align_and_validate()</span>。</p>

<h2>MetricWithLLM.train：优化指令 + 挑示例</h2>
<p>所有 LLM 类内置指标（Faithfulness、AspectCritic、ContextPrecision… 都继承 <span class="inline">MetricWithLLM</span>，<a href="13-metric-base.html">第 13 课</a>）都带一个 <span class="inline">train()</span>。它吃一个 <strong>JSON 标注文件</strong>，按两份配置分别优化：</p>
<pre class="code"><span class="kw">from</span> ragas.metrics <span class="kw">import</span> AspectCritic
<span class="kw">from</span> ragas.config <span class="kw">import</span> InstructionConfig, DemonstrationConfig

metric = AspectCritic(name=<span class="st">"correctness"</span>, definition=<span class="st">"答案是否正确"</span>, llm=evaluator_llm)

metric.train(
    path=<span class="st">"annotations.json"</span>,                              <span class="cm"># 人工标注（必须是 .json）</span>
    instruction_config=InstructionConfig(llm=optimizer_llm),     <span class="cm"># 优化指令：默认用遗传算法</span>
    demonstration_config=DemonstrationConfig(embedding=embeddings),  <span class="cm"># 挑 few-shot 示例：按相似度</span>
)</pre>
<p>两份配置<strong>各管一摊、都可选</strong>：传谁就优化谁。背后对应两个内部步骤：</p>
<table class="t">
  <tr><th>配置</th><th>优化什么</th><th>怎么做</th></tr>
  <tr><td class="mono">InstructionConfig</td><td>prompt 的<strong>指令</strong>措辞</td><td><span class="mono">_optimize_instruction</span>：跑优化器搜出更好的指令，替换每个 prompt 的 <span class="mono">instruction</span></td></tr>
  <tr><td class="mono">DemonstrationConfig</td><td>prompt 的 <strong>few-shot 示例</strong></td><td><span class="mono">_optimize_demonstration</span>：把标注转成示例，建 <span class="mono">FewShotPydanticPrompt</span>，按 embedding 相似度挑 <span class="mono">top_k</span> 个（<a href="20-prompt-advanced.html">第 20 课</a>）</td></tr>
</table>
<p>训练数据由 <span class="inline">MetricAnnotation.from_json(path, metric_name=self.name)</span> 加载：JSON 以<strong>指标名</strong>为键，每条是"输入 + 人工给的标签/分数"。<span class="inline">DemonstrationConfig</span> 默认 <span class="mono">top_k=3</span>、<span class="mono">threshold=0.7</span>、<span class="mono">technique="similarity"</span>。</p>

<h2>优化器与损失：把 prompt 工程变成可优化问题</h2>
<p>"改指令"这步交给一个 <span class="inline">Optimizer</span>。<span class="inline">InstructionConfig</span> 默认用 <span class="inline">GeneticOptimizer</span>（遗传算法）：它先从标注里<strong>反推</strong>出一条指令，再通过<strong>交叉、变异</strong>不断演化候选，挑出在标注上表现最好的那条。
另有可选的 <span class="inline">DSPyOptimizer</span>（包装 DSPy 的 MIPROv2，同时搜索指令 + 示例，需 <span class="mono">ragas[dspy]</span>，按需 try/except 导入）。</p>
<p>"表现好不好"由一个 <span class="inline">Loss</span> 衡量。若没在 <span class="inline">InstructionConfig</span> 里显式指定，<span class="inline">train</span> 会<strong>按指标的 <span class="mono">output_type</span> 自动选</strong>：</p>
<table class="t">
  <tr><th>output_type</th><th>自动选用的 Loss</th><th>含义</th></tr>
  <tr><td class="mono">BINARY</td><td class="mono">BinaryMetricLoss</td><td>按 <span class="mono">accuracy</span> 或 <span class="mono">f1_score</span> 衡量（如 AspectCritic）</td></tr>
  <tr><td class="mono">CONTINUOUS / DISCRETE</td><td class="mono">MSELoss</td><td>预测分与标注分的均方误差（如 Faithfulness）</td></tr>
</table>

<details class="accordion">
  <summary><span class="badge-num">1</span> GeneticOptimizer 是怎么"进化"出一条好指令的？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 反推 → 交叉 → 变异</div>
      <div class="a">它内置了几个 PydanticPrompt：<span class="inline">ReverseEngineerPrompt</span> 先看"标注好的(输入, 期望输出)对"<strong>反推</strong>出"标注员当时大概拿到的指令"，得到初始种群；
        再用 <span class="inline">CrossOverPrompt</span> 杂交、<span class="inline">FeedbackMutationPrompt</span> 按反馈变异，逐代择优。可优化的步数由 <span class="mono">optimizer_config</span>（默认 <span class="mono">{"max_steps": 100}</span>）控制。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 训练数据长什么样</div>
      <div class="a"><span class="inline">MetricAnnotation</span> 是个按<strong>指标名分组</strong>的字典（<span class="mono">root: Dict[str, List[SampleAnnotation]]</span>），<span class="mono">dataset[metric_name]</span> 取出该指标的 <span class="inline">SingleMetricAnnotation</span>。
        后者支持 <span class="inline">train_test_split</span> / <span class="inline">sample</span> / <span class="inline">get_prompt_annotations</span>，正好喂给优化器与 few-shot 构造。优化器至少需要约 <span class="mono">10</span> 条标注才有意义。</div>
    </div>
  </div>
</details>

<h2>Simple 指标的对齐：align_and_validate 与相关性</h2>
<p>自定义指标（<a href="11-custom-metrics.html">第 11 课</a>）多属较新的 <span class="inline">SimpleLLMMetric</span> 栈（<span class="inline">DiscreteMetric</span> / <span class="inline">NumericMetric</span> / <span class="inline">RankingMetric</span>）——它们不走 <span class="inline">train()</span>，而走更轻的"对齐 + 验证"一条龙：</p>
<pre class="code"><span class="cm"># dataset 是带人工分数的 Dataset；一步切分 → 对齐 → 验证</span>
result = metric.align_and_validate(dataset=labeled, embedding_model=embeddings, llm=evaluator_llm)
print(result[<span class="st">"correlation"</span>], result[<span class="st">"agreement_rate"</span>])</pre>
<p>它先 <span class="inline">train_test_split</span>（默认 <span class="mono">test_size=0.2</span>），在训练集上 <span class="inline">align</span>——把相似的标注样本作为<strong>动态 few-shot</strong>塞进 prompt（默认 <span class="mono">max_similar_examples=3</span>、<span class="mono">similarity_threshold=0.7</span>，靠 embedding 检索，<a href="22-embedding-abstraction.html">第 22 课</a>）；
再在测试集上 <span class="inline">validate_alignment</span>：逐行重新打分，算出与人工标注的<strong>相关性</strong>与<strong>一致率</strong>。<span class="inline">get_correlation</span> 在基类是占位、由各子类实现：<span class="inline">DiscreteMetric</span> / <span class="inline">RankingMetric</span> 用 <span class="mono">cohen_kappa_score</span>（Cohen's Kappa），<span class="inline">NumericMetric</span> 用 <strong>Pearson</strong> 相关系数。</p>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  传统栈在 <span class="mono">metrics/base.py</span>：<span class="mono">MetricWithLLM.train</span>（加载 <span class="mono">MetricAnnotation.from_json</span>，再走 <span class="mono">_optimize_instruction</span> / <span class="mono">_optimize_demonstration</span>）。
  优化器在 <span class="mono">optimizers/</span>：<span class="mono">base.py</span> 的 <span class="mono">Optimizer</span>、<span class="mono">genetic.py</span> 的 <span class="mono">GeneticOptimizer</span>、可选 <span class="mono">dspy_optimizer.py</span> 的 <span class="mono">DSPyOptimizer</span>。
  损失在 <span class="mono">losses.py</span>（<span class="mono">Loss</span> / <span class="mono">MSELoss</span> / <span class="mono">BinaryMetricLoss</span>）；配置在 <span class="mono">config.py</span>（<span class="mono">InstructionConfig</span> / <span class="mono">DemonstrationConfig</span>）；标注模型在 <span class="mono">dataset_schema.py</span>（<span class="mono">MetricAnnotation</span> / <span class="mono">SingleMetricAnnotation</span>）。
  Simple 栈的 <span class="mono">align</span> / <span class="mono">align_and_validate</span> / <span class="mono">validate_alignment</span> / <span class="mono">get_correlation</span> 也在 <span class="mono">metrics/base.py</span> 的 <span class="mono">SimpleLLMMetric</span>，子类实现见 <span class="mono">metrics/discrete.py</span>、<span class="mono">numeric.py</span>、<span class="mono">ranking.py</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>把 prompt 工程变成可优化问题</strong>：指令搜索交给遗传算法 / DSPy，示例挑选交给 embedding 相似度——从"人肉调 prompt"升级为"用数据自动搜"。</li>
    <li><strong>用与人类标注的相关性衡量指标好坏</strong>：相关性（离散 / 排序用 Cohen's Kappa、数值用 Pearson）+ 一致率给出客观数字，"裁判准不准"也变得可量化、可对比。</li>
    <li><strong>指令与示例解耦优化</strong>：<span class="inline">InstructionConfig</span> / <span class="inline">DemonstrationConfig</span> 各自可选，按需单独或一起优化，loss 还能按 <span class="mono">output_type</span> 自动选。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>指标不仅能<strong>用</strong>，还能被<strong>训练到更准</strong>：用人工标注对齐 LLM 裁判与人类判断。</li>
    <li><span class="inline">MetricWithLLM.train</span> 从 <span class="inline">MetricAnnotation</span> 学习，优化<strong>指令</strong>（GeneticOptimizer / DSPy + loss）与 <strong>few-shot 示例</strong>（相似度挑选）。</li>
    <li>新栈 <span class="inline">SimpleLLMMetric.align_and_validate</span> 一步搞定切分→对齐→验证，用<strong>相关性 / 一致率</strong>报告效果。</li>
  </ul>
</div>
"""

LESSON_34 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
ragas 不要求你抛弃现有技术栈。<span class="mono">integrations/</span> 提供一堆<strong>"适配插头"</strong>：
把 LangChain、LlamaIndex、LangGraph、各种多 Agent 框架的对象 / 轨迹，转成 ragas 认得的<strong>消息或数据集</strong>，接进评测与测试生成。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  不同框架像不同国家的<strong>插座标准</strong>。<span class="mono">integrations/</span> 是一盒<strong>转接头</strong>：
  LangGraph 的对话、Bedrock Agent 的运行轨迹、Griptape 的输出……各配一个插头，转成 ragas 的统一插脚（<span class="inline">Message</span> / <span class="inline">EvaluationDataset</span>），
  插上就能用前面学的指标和实验去评测，<strong>不用重写</strong>你的应用。
</div>

<h2>两个方向：把别人的东西接进来</h2>
<p>集成大体分两类。<strong>评测方向</strong>——把框架产物转成 ragas 输入：要么转成 <span class="inline">EvaluationDataset</span>（<a href="06-two-datasets.html">第 6 课</a>）直接喂 <span class="inline">evaluate</span> / <span class="inline">@experiment</span>，
要么转成 ragas 的 <span class="inline">Message</span> 列表喂给 <strong>agent 指标</strong>（<a href="18-agent-metrics-internals.html">第 18 课</a>）。<strong>测试生成方向</strong>——用框架的 LLM / Embedding 造测试集：</p>
<pre class="code"><span class="kw">from</span> ragas.testset <span class="kw">import</span> TestsetGenerator

<span class="cm"># 用 LangChain 的 LLM / Embedding 包好一个生成器（也有 from_llama_index）</span>
generator = TestsetGenerator.from_langchain(llm=lc_llm, embedding_model=lc_embeddings)
testset = generator.generate_with_langchain_docs(docs, testset_size=10)   <span class="cm"># 见第 30 课</span></pre>

<h2>主要框架集成（一栏一句）</h2>
<p>下面都是 <span class="mono">integrations/</span> 里<strong>确实存在</strong>的框架 / Agent / 协议适配（观测类工具留到 <a href="35-integrations-observability.html">第 35 课</a>）：</p>
<table class="t">
  <tr><th>框架 / 系统</th><th>子模块</th><th>接入方式（公开符号）</th></tr>
  <tr><td><strong>LangChain</strong></td><td class="mono">integrations/langchain.py</td><td><span class="mono">EvaluatorChain</span>：把 ragas 指标包成 LangSmith 的 <span class="mono">RunEvaluator</span> / Chain</td></tr>
  <tr><td><strong>LlamaIndex</strong></td><td class="mono">integrations/llama_index.py</td><td><span class="mono">evaluate(query_engine, dataset, metrics)</span>：直接评测一个 query engine</td></tr>
  <tr><td><strong>LangGraph</strong></td><td class="mono">integrations/langgraph.py</td><td><span class="mono">convert_to_ragas_messages</span>：把图执行的消息转成 ragas 消息</td></tr>
  <tr><td><strong>OpenAI Swarm</strong></td><td class="mono">integrations/swarm.py</td><td><span class="mono">convert_to_ragas_messages</span>：多 Agent 对话 → ragas 消息</td></tr>
  <tr><td><strong>Amazon Bedrock</strong></td><td class="mono">integrations/amazon_bedrock.py</td><td><span class="mono">convert_to_ragas_messages(traces)</span>：从 Bedrock Agent 轨迹提取消息</td></tr>
  <tr><td><strong>Griptape</strong></td><td class="mono">integrations/griptape.py</td><td><span class="mono">transform_to_ragas_dataset</span>：转成 <span class="mono">EvaluationDataset</span></td></tr>
  <tr><td><strong>R2R</strong></td><td class="mono">integrations/r2r.py</td><td><span class="mono">transform_to_ragas_dataset</span>：把 R2R 检索结果转成 <span class="mono">EvaluationDataset</span></td></tr>
  <tr><td><strong>AG-UI</strong></td><td class="mono">integrations/ag_ui.py</td><td><span class="mono">AGUIEventCollector</span> + <span class="mono">convert_to_ragas_messages</span>：收事件流 → ragas 消息</td></tr>
</table>
<p>规律很清楚：<strong>RAG / 检索类</strong>框架（LlamaIndex、Griptape、R2R）多半转成 <span class="inline">EvaluationDataset</span>；
<strong>Agent / 多 Agent</strong>框架（LangGraph、Swarm、Bedrock、AG-UI）多半转成 <span class="inline">Message</span> 列表，对接 agent 指标。</p>

<h2>lazy import：缺依赖不炸整包</h2>
<p>这些集成各自依赖不同的第三方库（<span class="mono">langchain</span>、<span class="mono">llama-index</span>…），但 ragas <strong>不</strong>把它们设为必装。秘诀是<strong>包级别的惰性导入</strong>：
<span class="mono">integrations/__init__.py</span> 几乎是空的——只有一段文档字符串，<strong>不</strong>主动 import 任何子模块。每个框架的依赖都写在<strong>各自的子模块顶部</strong>，你<strong>用哪个才导哪个</strong>：</p>
<pre class="code"><span class="cm"># import ragas.integrations 本身不会拉进任何可选依赖</span>
<span class="kw">from</span> ragas.integrations.langgraph <span class="kw">import</span> convert_to_ragas_messages   <span class="cm"># 仅此处才需要 langchain</span>
<span class="kw">from</span> ragas.integrations.llama_index <span class="kw">import</span> evaluate                   <span class="cm"># 仅此处才需要 llama-index</span></pre>
<p>于是没装 LlamaIndex 的人，导入 <span class="mono">ragas.integrations.langgraph</span> 照样不受影响——<strong>缺哪个框架，只是那一个插头不能用，整包不受牵连</strong>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么不在 __init__.py 里统一 import 所有集成？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一处 import，全员遭殃</div>
      <div class="a">若 <span class="mono">__init__.py</span> 顶部 <span class="mono">from .llama_index import evaluate</span>，那么<strong>只要</strong>有人 <span class="mono">import ragas.integrations</span>，Python 就会去导 <span class="mono">llama_index</span>——没装就直接 <span class="mono">ImportError</span>。
        把 import 下沉到子模块，等于"按插头分装"，谁都不强迫谁。这与 <a href="32-backends.html">第 32 课</a>的可选 <span class="inline">GDriveBackend</span>（try/except 导入）是同一思路：<strong>可选能力按需加载</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 双向打通是什么意思</div>
      <div class="a">既能把<strong>别的框架</strong>的产物接进 ragas 评测（转 <span class="inline">Message</span> / <span class="inline">EvaluationDataset</span>），也能反过来把 ragas 能力<strong>嵌进</strong>别的框架——比如 <span class="inline">EvaluatorChain</span> 让 ragas 指标变成 LangSmith 里的一个 evaluator。进出两个方向都通。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  目录在 <span class="mono">src/ragas/integrations/</span>：<span class="mono">langchain.py</span>（<span class="mono">EvaluatorChain</span>）、<span class="mono">llama_index.py</span>（<span class="mono">evaluate</span>）、<span class="mono">langgraph.py</span> / <span class="mono">swarm.py</span> / <span class="mono">amazon_bedrock.py</span> / <span class="mono">ag_ui.py</span>（<span class="mono">convert_to_ragas_messages</span> 等）、<span class="mono">griptape.py</span> / <span class="mono">r2r.py</span>（<span class="mono">transform_to_ragas_dataset</span>）。
  <span class="mono">integrations/__init__.py</span> 仅含文档字符串、不做 eager import（惰性导入的关键）。测试生成侧的 <span class="mono">TestsetGenerator.from_langchain</span> / <span class="mono">from_llama_index</span> 在 <span class="mono">testset/synthesizers/generate.py</span>。观测类（Langfuse / MLflow / LangSmith / Helicone / Opik 及 <span class="mono">integrations/tracing/</span>）见下一课。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>集成模块 lazy import</strong>：依赖下沉到各子模块，缺某个框架只影响那一个插头，<strong>不炸整包</strong>。</li>
    <li><strong>与主流框架双向打通</strong>：既能把框架产物转进来评测，也能把 ragas 指标嵌进框架（如 <span class="inline">EvaluatorChain</span>）。</li>
    <li><strong>统一落到两种格式</strong>：RAG 类转 <span class="inline">EvaluationDataset</span>、Agent 类转 <span class="inline">Message</span> 列表，复用前面所有指标与实验，无需为每个框架另造评测。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>ragas <strong>不孤立</strong>：<span class="mono">integrations/</span> 把 LangChain / LlamaIndex / LangGraph / Swarm / Bedrock / Griptape / R2R / AG-UI 接进来。</li>
    <li>两个方向：转 <span class="inline">EvaluationDataset</span> 或 ragas <span class="inline">Message</span> 评测；<span class="inline">TestsetGenerator.from_langchain</span> / <span class="inline">from_llama_index</span> 造测试集。</li>
    <li>靠<strong>惰性导入</strong>容忍可选依赖：<span class="mono">__init__.py</span> 不 eager import，用哪个插头才导哪个，缺依赖不影响整包。</li>
  </ul>
</div>
"""

LESSON_35 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
上一课把别的框架接进来评测；本课把<strong>评测过程本身</strong>接到"监控大盘"。<span class="mono">integrations/tracing/</span> 加上几个观测平台适配，
让每一次评测都能<strong>可视化、可回溯</strong>——光看最后那个分数不够，你还想知道<strong>每一步</strong>发生了什么。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  只看评测的最终分数，像只看体检报告的<strong>总分</strong>——不知道哪项拖了后腿。观测平台是<strong>"监控大盘 + 行车记录仪"</strong>：
  把每一次 LLM 调用、每一行打分、耗时与成本都录下来，出了问题能<strong>回放到具体那一步</strong>。
  ragas 给 Langfuse / MLflow / LangSmith / Helicone / Opik 各配了一个<strong>"上报插头"</strong>，评测结果顺着插头进大盘。
</div>

<h2>五家观测平台（确实存在的）</h2>
<p>下面是 <span class="mono">integrations/</span> 里<strong>真实存在</strong>的观测 / 追踪适配，只列这五家，不臆造：</p>
<table class="t">
  <tr><th>平台</th><th>子模块</th><th>接入方式（公开符号）</th></tr>
  <tr><td><strong>Langfuse</strong></td><td class="mono">integrations/tracing/langfuse.py</td><td><span class="mono">observe</span> 装饰器 + <span class="mono">sync_trace()</span> → <span class="mono">LangfuseTrace.get_url()</span></td></tr>
  <tr><td><strong>MLflow</strong></td><td class="mono">integrations/tracing/mlflow.py</td><td><span class="mono">sync_trace()</span> → <span class="mono">MLflowTrace.get_url()</span>（读 <span class="mono">MLFLOW_HOST</span>）</td></tr>
  <tr><td><strong>LangSmith</strong></td><td class="mono">integrations/langsmith.py</td><td><span class="mono">upload_dataset</span> / <span class="mono">evaluate</span>（用 <span class="mono">EvaluatorChain</span> 把指标包成 evaluator）</td></tr>
  <tr><td><strong>Helicone</strong></td><td class="mono">integrations/helicone.py</td><td><span class="mono">helicone_config</span> 单例（被 <span class="mono">evaluation.py</span> 引用）</td></tr>
  <tr><td><strong>Opik</strong></td><td class="mono">integrations/opik.py</td><td><span class="mono">OpikTracer</span>（LangChain 回调，回传逐行分数）</td></tr>
</table>
<p>接法分三路：<strong>trace 录全链路</strong>（Langfuse / MLflow）、<strong>请求头归 session</strong>（Helicone，零改动）、<strong>LangChain 回调 / evaluator</strong>（Opik / LangSmith）。</p>

<h2>observe：给评测装"行车记录仪"</h2>
<p>Langfuse / MLflow 走的是 <strong>trace</strong>：把整次评测包成一条可追踪的链路，跑完再去服务器把它捞回来、拿到大盘上的可点链接。</p>
<pre class="code"><span class="kw">from</span> ragas.integrations.tracing.langfuse <span class="kw">import</span> observe, sync_trace
<span class="kw">from</span> ragas <span class="kw">import</span> evaluate

@observe()                        <span class="cm"># 把整次评测包成一条 trace</span>
<span class="kw">def</span> <span class="fn">run_evaluation</span>():
    <span class="kw">return</span> evaluate(dataset, metrics)

run_evaluation()
trace = <span class="kw">await</span> sync_trace()        <span class="cm"># 等 trace 同步到服务器（await 需在 async 上下文）</span>
print(trace.get_url())            <span class="cm"># 拿到大盘上的可点链接</span></pre>
<p><span class="mono">tracing/__init__.py</span> 用 <span class="inline">__getattr__</span> <strong>惰性导出</strong> <span class="inline">observe</span> / <span class="inline">sync_trace</span> / <span class="inline">LangfuseTrace</span> / <span class="inline">MLflowTrace</span>；
MLflow 侧的 <span class="inline">sync_trace</span> 改走 <span class="mono">get_last_active_trace_id</span> + <span class="mono">get_trace</span>，<span class="inline">MLflowTrace.get_url()</span> 用 <span class="mono">MLFLOW_HOST</span> 拼出 trace 链接。两家长得几乎一样，换平台只换 import。</p>

<h2>helicone_config：不改代码就把评测归一个 session</h2>
<p>Helicone 不靠装饰器，而是<strong>请求头</strong>。<span class="mono">helicone.py</span> 里 <span class="inline">helicone_config</span> 是个<strong>单例</strong>（<span class="inline">HeliconeSingleton</span>，用 <span class="inline">__new__</span> 保证全局唯一）。
关键是它被 <strong>评测主流程</strong>引用——<span class="mono">evaluation.py</span> 顶部 import 它，经典 <span class="inline">evaluate()</span> 一开头就判断它是否开启：</p>
<pre class="code"><span class="cm"># evaluate() 内部（精简）：设了 api_key 才生效</span>
<span class="kw">if</span> helicone_config.is_enabled:
    helicone_config.session_name = <span class="st">"ragas-evaluation"</span>
    helicone_config.session_id = str(uuid.uuid4())   <span class="cm"># 每轮评测一个新 session</span></pre>
<p><span class="inline">default_headers()</span> 把这些拼成 <span class="mono">Helicone-Session-*</span> 等请求头，于是这一轮评测的<strong>所有 LLM 调用</strong>在 Helicone 大盘里被归到<strong>同一个 session</strong>，可整体回看。
没设 <span class="mono">api_key</span> 时 <span class="inline">is_enabled</span> 为 <span class="inline">False</span>，整段完全无感——<strong>开了才花钱、才上报</strong>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 这么多观测依赖，会不会拖垮安装？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 可选依赖 + 惰性导入，按家隔离</div>
      <div class="a">追踪栈在 <span class="mono">pyproject.toml</span> 是<strong>可选 extra</strong>（<span class="mono">tracing = ["langfuse&gt;=3.2.4", "mlflow&gt;=3.1.4"]</span>），不装也能用 ragas。
        <span class="mono">tracing/__init__.py</span> 用 <span class="inline">__getattr__</span> 惰性导入，<span class="mono">langfuse.py</span> / <span class="mono">mlflow.py</span> 内部 <span class="mono">try/except</span> 设 <span class="mono">LANGFUSE_AVAILABLE</span> / <span class="mono">MLFLOW_AVAILABLE</span>，缺库时退化成 stub 而非崩溃。
        这与<a href="34-integrations-frameworks.html">上一课</a>框架集成的"惰性导入"一脉相承：<strong>缺哪个平台只影响那一个插头</strong>。</div>
    </div>
    <div class="qa">
      <div class="q">✅ Opik / LangSmith 这两路怎么接</div>
      <div class="a"><span class="inline">OpikTracer</span> 是个 <strong>LangChain 回调</strong>（继承 <span class="mono">LangchainOpikTracer</span>）：它认出评测链（<span class="mono">RAGAS_EVALUATION_CHAIN_NAME = "ragas evaluation"</span>）后，把<strong>逐行的指标分数</strong>通过 <span class="mono">log_traces_feedback_scores</span> 回传到 Opik。
        LangSmith 的 <span class="inline">evaluate</span> 则用 <span class="inline">EvaluatorChain</span>（<a href="34-integrations-frameworks.html">第 34 课</a>）把 ragas 指标变成它的 <span class="mono">custom_evaluators</span>，直接在 LangSmith 平台上跑评测。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  追踪栈在 <span class="mono">src/ragas/integrations/tracing/</span>：<span class="mono">__init__.py</span>（<span class="mono">__getattr__</span> 惰性导出）、<span class="mono">langfuse.py</span>（<span class="mono">observe</span> / <span class="mono">sync_trace</span> / <span class="mono">LangfuseTrace</span>）、<span class="mono">mlflow.py</span>（<span class="mono">MLflowTrace</span> / <span class="mono">sync_trace</span>）。
  另外三家在 <span class="mono">integrations/</span> 根：<span class="mono">langsmith.py</span>（<span class="mono">upload_dataset</span> / <span class="mono">evaluate</span> / <span class="mono">EvaluatorChain</span>）、<span class="mono">helicone.py</span>（<span class="mono">HeliconeSingleton</span> / <span class="mono">helicone_config</span> / <span class="mono">default_headers</span>，被 <span class="mono">evaluation.py</span> 的 <span class="mono">evaluate</span> 引用）、<span class="mono">opik.py</span>（<span class="mono">OpikTracer</span>，依赖 <span class="mono">RAGAS_EVALUATION_CHAIN_NAME</span>）。
  可选依赖声明在 <span class="mono">pyproject.toml</span> 的 <span class="mono">[project.optional-dependencies].tracing</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>评测可上报多家观测平台</strong>（Langfuse / MLflow / LangSmith / Helicone / Opik）→ 生产级<strong>可视化与回溯</strong>，不止一个孤零零的分数。</li>
    <li><strong>三种侵入度任选</strong>：<span class="inline">observe</span> + <span class="inline">sync_trace</span> 录全链路、<span class="inline">helicone_config</span> 零改动归 session、回调 / evaluator 接进现成平台。</li>
    <li><strong>观测依赖全是可选 extra + 惰性导入</strong>：缺库退化成 stub，不影响核心安装与使用。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>评测结果能进监控体系：Langfuse / MLflow（<span class="inline">observe</span> + <span class="inline">sync_trace</span>）、LangSmith（<span class="inline">EvaluatorChain</span>）、Helicone（session 请求头）、Opik（回调回传分数）。</li>
    <li><span class="inline">helicone_config</span> 单例被 <span class="inline">evaluate()</span> 引用：开了就给整轮评测<strong>归一个 session</strong>，闭环到生产观测。</li>
    <li>观测能力都是<strong>可选依赖、惰性加载</strong>，缺库不炸整包。</li>
  </ul>
</div>
"""

LESSON_36 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
前面把 ragas 的能力讲透了；这一课换个视角——你想<strong>下场改 ragas</strong>，怎么把开发环境搭起来、怎么跑测试还不烧钱、怎么提交。
一句话：全靠 <strong>uv</strong> 管依赖，加上一个把所有动作一键化的 <strong>Makefile</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  这是给想动手改 ragas 的人的<strong>"工地安全须知 + 工具说明书"</strong>：<span class="inline">uv</span> 是统一的<strong>建材入场口</strong>（管虚拟环境与依赖），
  <span class="inline">Makefile</span> 是墙上那排<strong>一键开关</strong>（<span class="mono">format</span> / <span class="mono">type</span> / <span class="mono">test</span> / <span class="mono">run-ci</span>），
  而 <span class="inline">fake_llm</span> 这类<strong>替身演员</strong>让你彩排时不必请真演员（真 LLM）出场——又快又零成本。
</div>

<h2>用 uv 装环境（两档）</h2>
<p>开发环境分两档，都自动建 <span class="mono">.venv</span> 并装好 pre-commit 钩子；<span class="mono">requires-python</span> 是 <span class="mono">&gt;=3.9</span>：</p>
<pre class="code"><span class="cm"># 推荐：快速最小开发环境（约 79 个包，日常开发够用）</span>
make install-minimal      <span class="cm"># 内部：uv pip install -e ".[dev-minimal]"</span>

<span class="cm"># 或全量（含完整 ML / 观测栈，依赖量大得多）</span>
make install              <span class="cm"># 内部：uv sync --group dev</span></pre>
<p><span class="mono">CONTRIBUTING.md</span> 写得很直白：<strong>用 <span class="mono">make</span> 命令而不是直接调工具</strong>；要直接跑 Python 工具时加 <span class="mono">uv run</span> 前缀。
项目还用 <strong>uv workspace</strong>（<span class="mono">members = [".", "examples"]</span>）同时管主包和 <span class="mono">ragas-examples</span> 两个包，依赖版本统一。</p>

<h2>日常三连：format / type / test</h2>
<p>改完代码，提交前的标准动作就这几个开关：</p>
<table class="t">
  <tr><th>命令</th><th>干什么</th><th>底层工具</th></tr>
  <tr><td class="mono">make format</td><td>格式化 + 自动修（含排序 / 删未用 import）</td><td class="mono">ruff format · ruff check --fix（lint 选 E/F/I）</td></tr>
  <tr><td class="mono">make type</td><td>类型检查（只查 <span class="mono">src/ragas</span>）</td><td class="mono">pyright（typeCheckingMode=basic）</td></tr>
  <tr><td class="mono">make check</td><td>快速体检 = format + type（不跑测试）</td><td class="mono">上面两个</td></tr>
  <tr><td class="mono">make test</td><td>跑单测，可 <span class="mono">k=</span> 只跑匹配的</td><td class="mono">pytest tests/unit</td></tr>
  <tr><td class="mono">make run-ci</td><td>本地完整复刻 GitHub CI</td><td class="mono">ruff --check + type + pytest --nbmake -n auto</td></tr>
</table>
<pre class="code">make check                  <span class="cm"># 格式化 + 类型检查</span>
make test                   <span class="cm"># 跑全部单测</span>
make test k=<span class="st">"faithfulness"</span>  <span class="cm"># 只跑名字匹配的用例</span>
make run-ci                 <span class="cm"># 提 PR 前本地复刻一遍 CI</span></pre>

<h2>fake_llm / fake_embedding：让指标测试确定、零成本</h2>
<p>这是整套测试设计的精髓。<span class="mono">tests/conftest.py</span> 提供几个<strong>"替身" fixture</strong>，让指标 / 引擎测试<strong>不碰真模型</strong>：</p>
<table class="t">
  <tr><th>fixture</th><th>替身类</th><th>行为</th></tr>
  <tr><td class="mono">fake_llm</td><td class="mono">EchoLLM</td><td>把 prompt 原样当回答吐回来，<span class="mono">is_finished</span> 永远 True → 确定、可断言</td></tr>
  <tr><td class="mono">fake_embedding</td><td class="mono">EchoEmbedding</td><td>返回随机 768 维向量，测维度 / 形状够用</td></tr>
  <tr><td class="mono">mock_llm</td><td class="mono">MockLLM</td><td><span class="mono">generate</span> 直接返回 response_model 的空实例，专测结构化输出路径</td></tr>
  <tr><td class="mono">mock_embedding</td><td class="mono">MockEmbedding</td><td><span class="mono">np.random.seed(42)</span> 固定种子 → 可复现</td></tr>
</table>
<pre class="code"><span class="cm"># 测试里直接声明 fixture 名，pytest 自动注入（无需真 API key）</span>
<span class="kw">def</span> <span class="fn">test_my_metric</span>(fake_llm, fake_embedding):
    metric = MyMetric(llm=fake_llm)
    <span class="cm"># 断言指标逻辑，而不是断言真模型答得好不好</span>
    ...</pre>
<p>于是"指标逻辑对不对"与"LLM 答得好不好"被<strong>解耦</strong>——单测<strong>确定、离线、零调用成本</strong>，CI 不必持有 <span class="mono">OPENAI_API_KEY</span>。
<span class="mono">tests/</span> 下还分 <span class="mono">unit/</span>（再按 <span class="mono">backends</span> / <span class="mono">integrations</span> / <span class="mono">llms</span> / <span class="mono">prompt</span> 分组）、<span class="mono">e2e/</span>、<span class="mono">benchmarks/</span>。</p>

<details class="accordion">
  <summary><span class="badge-num">1</span> 为什么所有命令都包一层 make + uv？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 一处定义，人人一致</div>
      <div class="a">把 ruff / pyright / pytest 的具体参数（排除 <span class="mono">_version.py</span>、<span class="mono">--dist loadfile -n auto</span> 等）<strong>写死在 Makefile</strong>，谁敲 <span class="mono">make run-ci</span> 跑的都和 GitHub CI 完全一样，杜绝"我本地是绿的"。
        <span class="mono">uv run --active</span> 又保证用的是项目 <span class="mono">.venv</span> 里钉死版本的工具，不被系统环境污染。</div>
    </div>
    <div class="qa">
      <div class="q">✅ benchmarks 在哪跑</div>
      <div class="a"><span class="mono">make benchmarks</span> 跑 <span class="mono">tests/benchmarks/</span> 下的 <span class="mono">benchmark_eval.py</span> / <span class="mono">benchmark_testsetgen.py</span>；<span class="mono">make benchmarks-docker</span> 在容器里跑。
        性能回归也有一键入口。日常流程见 <span class="mono">CONTRIBUTING.md</span>：开分支 → 改代码 → <span class="mono">make check</span> + <span class="mono">make test</span> → 提交，PR 前再 <span class="mono">make run-ci</span>。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  仓库根 <span class="mono">Makefile</span>：<span class="mono">install-minimal</span> / <span class="mono">install</span> / <span class="mono">format</span> / <span class="mono">type</span> / <span class="mono">check</span> / <span class="mono">test</span> / <span class="mono">run-ci</span> / <span class="mono">benchmarks</span> / <span class="mono">clean</span> 等目标（<span class="mono">make help</span> 看全）。
  <span class="mono">pyproject.toml</span>：<span class="mono">requires-python &gt;=3.9</span>、<span class="mono">[tool.uv.workspace] members = [".", "examples"]</span>、<span class="mono">[tool.ruff]</span>（line 88、select E/F/I）、<span class="mono">[tool.pyright]</span>（basic、include <span class="mono">src/ragas</span>）、<span class="mono">[tool.pytest.ini_options]</span>，以及 <span class="mono">dev-minimal</span> extra 与 <span class="mono">[dependency-groups].dev</span> 两套。
  <span class="mono">tests/conftest.py</span>：<span class="mono">fake_llm</span> / <span class="mono">fake_embedding</span> / <span class="mono">mock_llm</span> / <span class="mono">mock_embedding</span> fixture（<span class="mono">EchoLLM</span> / <span class="mono">EchoEmbedding</span> / <span class="mono">MockLLM</span> / <span class="mono">MockEmbedding</span>）。流程见 <span class="mono">CONTRIBUTING.md</span>。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><span class="inline">fake_llm</span> / <span class="inline">fake_embedding</span> 让指标测试<strong>确定、离线、零成本</strong>，CI 不需要真 API key。</li>
    <li><strong>Makefile 把整条 CI 一键化</strong>：<span class="mono">make run-ci</span> 本地即 GitHub CI，参数只定义一处，杜绝环境漂移。</li>
    <li><strong>uv workspace 管多包</strong>（主包 + <span class="mono">ragas-examples</span>），依赖版本统一、可编辑安装。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li>上手开发就用这套工具链：<span class="mono">make install-minimal</span> 装环境，<span class="mono">make format</span> / <span class="mono">type</span> / <span class="mono">test</span> 日常三连，<span class="mono">make run-ci</span> 提 PR 前自检。</li>
    <li>指标 / 引擎单测靠 <span class="mono">conftest.py</span> 的 <span class="inline">fake_llm</span> / <span class="inline">fake_embedding</span> 跑得<strong>确定又零成本</strong>。</li>
    <li>一切走 <strong>uv + Makefile</strong>：环境、依赖、CI 全统一，照 <span class="mono">CONTRIBUTING.md</span> 走即可。</li>
  </ul>
</div>
"""

LESSON_37 = r"""
<p class="lead" style="font-size:1.06rem;color:var(--muted);margin-top:-.6rem">
不想写 Python 也能用 ragas——装好包就多了个 <span class="mono">ragas</span> 命令。它用 <strong>typer</strong> 搭命令、<strong>rich</strong> 画彩色表格，
三条子命令覆盖<strong>"跑评测 / 拉模板 / 看示例"</strong>。这是除了写代码之外的<strong>另一条上手路径</strong>。
</p>

<div class="card analogy">
  <div class="tag">🧩 生活类比</div>
  CLI 是 ragas 的<strong>"命令行遥控器"</strong>：不用进代码里按按钮，在终端敲一行就能<strong>跑评测</strong>、<strong>拉一套现成模板</strong>、<strong>生成一个能跑的最小示例</strong>。
  <span class="inline">typer</span> 是遥控器的<strong>按键面板</strong>（声明式定义命令），<span class="inline">rich</span> 是它的<strong>小屏幕</strong>（彩色表格、进度动画）。
</div>

<h2>ragas 命令从哪来</h2>
<p><span class="mono">pyproject.toml</span> 的 <span class="mono">[project.scripts]</span> 注册了一行入口，装包后系统就有了 <span class="mono">ragas</span> 可执行命令；它指向 <span class="mono">cli.py</span> 里的 <span class="inline">app</span>：</p>
<pre class="code"><span class="cm"># pyproject.toml</span>
[project.scripts]
ragas = <span class="st">"ragas.cli:app"</span>

<span class="cm"># src/ragas/cli.py（精简）</span>
<span class="kw">import</span> typer
<span class="kw">from</span> ragas.utils <span class="kw">import</span> console      <span class="cm"># 一个 rich Console</span>

app = typer.Typer(help=<span class="st">"Ragas CLI for running LLM evaluations"</span>)

@app.command()
<span class="kw">def</span> <span class="fn">evals</span>(...): ...
@app.command()
<span class="kw">def</span> <span class="fn">quickstart</span>(...): ...
@app.command()
<span class="kw">def</span> <span class="fn">hello_world</span>(...): ...</pre>

<h2>三条子命令</h2>
<table class="t">
  <tr><th>命令</th><th>干什么</th></tr>
  <tr><td class="mono">ragas quickstart [模板]</td><td>拉一套<strong>完整示例工程</strong>；不带参数则列出所有模板（<span class="mono">rag_eval</span> / <span class="mono">agent_evals</span> / <span class="mono">text2sql</span> / <span class="mono">improve_rag</span> …），<span class="mono">-o</span> 指定目录。本地有 <span class="mono">ragas_examples</span> 就复制，没有就从 GitHub 下载。</td></tr>
  <tr><td class="mono">ragas evals 文件.py --dataset 名 --metrics 字段</td><td>跑一个<strong>评测模块</strong>：加载该文件，找出 Project（有 <span class="mono">get_dataset</span> / <span class="mono">get_experiment</span>）和实验函数（有 <span class="mono">run_async</span>），对数据集跑实验，用 rich 表格打印各指标；<span class="mono">--baseline</span> 可与基线对比。</td></tr>
  <tr><td class="mono">ragas hello_world [目录]</td><td>生成<strong>最小可跑示例</strong>：建 <span class="mono">hello_world/</span>（<span class="mono">datasets/</span>、<span class="mono">experiments/</span>、<span class="mono">evals.py</span> + <span class="mono">test_data.csv</span>），照提示就能 <span class="mono">ragas evals</span> 起来。</td></tr>
</table>

<h2>evals 跑完打印什么</h2>
<p><span class="inline">evals</span> 调 <span class="inline">run_experiments</span>，先用 <span class="inline">separate_metrics_by_type</span> 把指标分成<strong>数值 / 分类</strong>两类，再交给 <span class="inline">display_metrics_tables</span> 调 <span class="inline">create_numerical_metrics_table</span> / <span class="inline">create_categorical_metrics_table</span> 打印。
带 <span class="mono">--baseline</span> 时，数值表会多出 <strong>Current / Baseline / Delta（▲▼）/ Gate（pass·fail）</strong> 几列，门禁允许小于 <span class="mono">0.01</span> 的轻微回退：</p>
<pre class="code"><span class="cm"># 对 test_data 数据集、按 accuracy 指标评测 evals.py（hello_world 生成的就长这样）</span>
ragas evals hello_world/evals.py --dataset test_data --metrics accuracy

<span class="cm"># 与基线实验对比，输出带 Delta 和 pass/fail 门禁</span>
ragas evals my_eval.py --dataset qa --metrics correctness --baseline v1</pre>

<details class="accordion">
  <summary><span class="badge-num">1</span> sdk.py 是干嘛的？quickstart 为什么要"拉模板"？<span class="hint">点击展开详解</span></summary>
  <div class="acc-body">
    <div class="qa">
      <div class="q">🧪 sdk.py 目前是空的</div>
      <div class="a"><span class="mono">src/ragas/sdk.py</span> 这个文件<strong>存在但零行内容</strong>，是预留占位（未来可能放程序化 SDK 入口）。本课不依赖它——CLI 的逻辑<strong>全在 <span class="mono">cli.py</span></strong>。
        这里如实标注，免得讲一个还不存在的能力。</div>
    </div>
    <div class="qa">
      <div class="q">✅ 模板降低上手门槛</div>
      <div class="a"><span class="inline">quickstart</span> 不是从零教学，而是直接 clone 一套<strong>能跑的工程</strong>（如 <span class="mono">rag_eval</span>：带数据、指标、实验脚本），改改就能用。
        它与 <span class="inline">hello_world</span> 的"最小骨架"<strong>互补</strong>：一个给完整范例、一个给最小起点。两者都把"第一次怎么跑起来"这道坎抹平了。</div>
    </div>
  </div>
</details>

<div class="card detail">
  <div class="tag">🔬 源码对应</div>
  <span class="mono">src/ragas/cli.py</span>：<span class="mono">app = typer.Typer(...)</span>，命令 <span class="mono">evals</span> / <span class="mono">quickstart</span> / <span class="mono">hello_world</span>（<span class="mono">@app.command()</span>），表格助手 <span class="mono">create_numerical_metrics_table</span> / <span class="mono">create_categorical_metrics_table</span> / <span class="mono">separate_metrics_by_type</span> / <span class="mono">display_metrics_tables</span>，模块加载 <span class="mono">load_eval_module</span>、跑实验 <span class="mono">run_experiments</span>，输出走 <span class="mono">ragas.utils.console</span>（rich）。
  入口注册在 <span class="mono">pyproject.toml</span> 的 <span class="mono">[project.scripts] ragas = "ragas.cli:app"</span>。<span class="mono">src/ragas/sdk.py</span> 当前为空占位。
</div>

<div class="card spark">
  <div class="tag">💡 设计亮点</div>
  <ul>
    <li><strong>typer + rich</strong>：声明式定义命令 + 彩色表格 / 进度动画，CLI 体验好、代码也短。</li>
    <li><strong>quickstart 模板</strong>（本地复制或 GitHub 下载）大幅<strong>降低上手门槛</strong>，配 <span class="inline">hello_world</span> 最小骨架双管齐下。</li>
    <li><strong>evals 复用实验系统</strong>（<span class="mono">get_dataset</span> / <span class="mono">run_async</span>）与门禁（Delta / pass-fail），把"跑评测、对比基线"搬到一行命令。</li>
  </ul>
</div>

<div class="card key">
  <div class="tag">✅ 本课要点</div>
  <ul>
    <li><span class="mono">ragas</span> 命令（<span class="mono">pyproject [project.scripts]</span> → <span class="mono">cli.py</span> 的 typer <span class="inline">app</span>）是<strong>另一条上手路径</strong>，不写代码也能评测。</li>
    <li>三条命令：<span class="inline">quickstart</span> 拉模板、<span class="inline">evals</span> 跑评测 + rich 表格（带基线门禁）、<span class="inline">hello_world</span> 造最小示例。</li>
    <li><span class="mono">sdk.py</span> 目前为<strong>空占位</strong>；CLI 能力全在 <span class="mono">cli.py</span>。</li>
  </ul>
</div>
"""
