"""Per-lesson self-test (自测题): design-insight multiple-choice + open prompts.

Questions focus on *why a thing is designed the way it is* (设计亮点 / 取舍 /
引发思考), not rote syntax recall. Content lives here as data; ``render(fname)``
turns it into HTML that build.py / build_print.py append to the bottom of each
lesson (above the footnav). Data-driven => consistent markup (check_html stays
green) and one place to review/extend.

Schema per lesson::

    "NN-file.html": {
        "mcq": [{"q": "...", "opts": ["A 文本", ...], "answer": 1, "why": "..."}],
        "open": ["发散题 1", "发散题 2"],
    }

``answer`` is the 0-based index of the correct option (into ``opts`` as written).
At render time the options are deterministically shuffled per question so the
correct answer is spread across A/B/C/D (otherwise authors tend to always put it
first/second). Use <code>…</code> for inline code and single quotes inside it to
avoid escaping.
"""

import hashlib


def _shuffle(opts, answer, seed):
    """Deterministically permute ``opts`` (stable across builds) and return
    ``(new_opts, new_answer_index)`` so the correct option lands in a varied
    position instead of always being first/second."""
    order = sorted(
        range(len(opts)),
        key=lambda i: hashlib.md5(f"{seed}:{i}".encode("utf-8")).hexdigest(),
    )
    return [opts[i] for i in order], order.index(answer)

QUIZZES = {
    "01-what-is-ragas.html": {
        "mcq": [
            {
                "q": "ragas 把「评测」重塑成「做实验」（experiments-first），核心是为了解决什么问题？",
                "opts": [
                    "让每次改动都能跑分、并留下可对比的记录，支撑持续迭代",
                    "让评测跑得更快、消耗更少 token",
                    "让指标不再需要 LLM 当裁判",
                    "让测试集可以自动生成",
                ],
                "answer": 0,
                "why": "vibe check 的毛病是主观、不可复现；experiments-first 把「改动 → 跑分 → 对比」固化成闭环，每次迭代都有据可查。速度 / token、裁判、造数据都不是它要解决的核心痛点。",
            },
            {
                "q": "为什么说「我觉得还行」（vibe check）式的判断需要被 ragas 取代？",
                "opts": [
                    "因为人读不懂模型的输出",
                    "因为主观判断不可量化、不可复现，换个人或换一天结论就变",
                    "因为 LLM 的输出总是错的",
                    "因为这样能显著省钱",
                ],
                "answer": 1,
                "why": "ragas 用客观指标 + 固定数据集 + 实验记录，把「感觉还行」升级成可量化、可复现、可迭代的系统化闭环——这正是 vibe check 做不到的。",
            },
        ],
        "open": [
            "拿你手上的一个 LLM 应用，列出 3 个你现在只靠「感觉」判断好坏的地方；如果要把它们变成可量化指标，你会分别量什么、用 LLM 类还是传统类指标？",
        ],
    },
    "02-architecture.html": {
        "mcq": [
            {
                "q": "为什么 <code>ragas/__init__.py</code> 的 <code>__all__</code> 刻意不把成百上千个具名指标、各种 LLM / Embedding 包装类塞进顶层？",
                "opts": [
                    "因为这些类还没写完",
                    "因为公开面越小越稳，能降低耦合、减少升级时的破坏性变更",
                    "因为具名指标在技术上无法被 import",
                    "因为顶层只能放函数、不能放类",
                ],
                "answer": 1,
                "why": "顶层只放「人人都要用」的门面（入口 + 数据模型），庞杂实现关进子包，按需从 <code>ragas.metrics</code> / <code>ragas.llms</code> 等子模块导入。公开面越小，升级时越不容易误伤用户代码。",
            },
            {
                "q": "<code>ragas.experimental</code> 用模块级 <code>__getattr__</code> 惰性加载，主要好处是什么？",
                "opts": [
                    "让导入速度变慢，方便插断点调试",
                    "没装可选依赖时 import ragas 本身不报错，真用到才触发导入并提示安装",
                    "让 experimental 永远不可用",
                    "强制所有用户都装上实验依赖",
                ],
                "answer": 1,
                "why": "只有真的访问 <code>ragas.experimental</code> 时才去 import 背后的 <code>ragas_experimental</code>；缺依赖时抛出带安装指引的 <code>ImportError</code>，而不是在 import 阶段就崩。按需付费、缺啥提示啥。",
            },
        ],
    },
    "03-evaluation-lifecycle.html": {
        "mcq": [
            {
                "q": "评测中单个任务抛错时，引擎默认把该结果转成 <code>np.nan</code> 而不是直接崩溃。这样设计是为了什么？",
                "opts": [
                    "为了让最终分数更高",
                    "为了让个别失败行不中断整轮评测，且均值用 <code>safe_nanmean</code> 自动忽略它",
                    "为了节省 token",
                    "因为 LLM 调用不支持抛异常",
                ],
                "answer": 1,
                "why": "默认 <code>raise_exceptions=False</code>，单行失败记 <code>np.nan</code>；汇总时 <code>safe_nanmean</code> 会忽略 <code>NaN</code>，所以个别失败行不会拖垮整批，也不会污染均值。",
            },
            {
                "q": "<code>evaluate()</code> 与 <code>aevaluate()</code> 是什么关系？",
                "opts": [
                    "两者完全独立、算法不同",
                    "<code>aevaluate()</code> 是异步真实现，<code>evaluate()</code> 只是它的同步外壳",
                    "<code>evaluate()</code> 因为是同步的所以更快",
                ],
                "answer": 1,
                "why": "async-first 设计：真正并发干活的是 <code>aevaluate()</code>，<code>evaluate()</code> 只套一层同步外壳（必要时借 <code>nest_asyncio</code> 兼容 Jupyter）。二者都会发 <code>DeprecationWarning</code> 指向 <code>@experiment</code>。",
            },
        ],
        "open": [
            "若某次评测里有 30% 的行都变成了 <code>np.nan</code>，<code>safe_nanmean</code> 仍会给出一个均值——这个均值还可信吗？你会怎么发现并排查这种「被掩盖的失败」？",
        ],
    },
    "04-single-turn-sample.html": {
        "mcq": [
            {
                "q": "为什么 <code>SingleTurnSample</code> 的字段几乎全是 <code>Optional</code>（默认 <code>None</code>）？",
                "opts": [
                    "因为 pydantic 不支持必填字段",
                    "为了用一个模型适配不同指标——缺哪栏就空着，按需带列",
                    "因为这些字段其实都没用",
                    "纯粹为了减少内存占用",
                ],
                "answer": 1,
                "why": "不同指标只挑自己要的字段（如 Faithfulness 要 <code>retrieved_contexts</code>，ContextRecall 还要 <code>reference</code>）。字段全 Optional，让同一模型既能装齐全 RAG 样本、也能只装「问题 + 回答」，缺列在校验阶段才报错。",
            },
            {
                "q": "<code>retrieved_contexts</code> 和 <code>reference_contexts</code> 有什么区别？",
                "opts": [
                    "两者完全一样，只是别名",
                    "<code>retrieved_contexts</code> 是系统实际检索到的，<code>reference_contexts</code> 是「本应检索到」的标准资料",
                    "<code>retrieved_contexts</code> 是标准答案，<code>reference_contexts</code> 是检索结果",
                    "前者给单轮样本用，后者给多轮样本用",
                ],
                "answer": 1,
                "why": "retrieved 是考生实际翻到的资料，reference 是标准资料。二者分开存，ContextRecall 等指标才能衡量「该召回的是否都召回了」。",
            },
        ],
    },
    "05-multi-turn-sample.html": {
        "mcq": [
            {
                "q": "为什么 <code>MultiTurnSample</code> 把消息顺序校验放在 <code>field_validator</code>（构造对象时执行）里？",
                "opts": [
                    "为了把错误推迟到评测中途才暴露",
                    "让「工具结果凭空出现」「对话顺序错乱」等问题在造样本阶段就报错，错误前移、定位更快",
                    "因为 pydantic 不允许其他写法",
                    "为了加快评测的执行速度",
                ],
                "answer": 1,
                "why": "<code>field_validator</code> 在构造对象时立即执行，脏数据在「造样本」阶段就抛 <code>ValueError</code>，而不是拖到评测半途因脏数据中断。",
            },
            {
                "q": "ragas 的消息没有 <code>tool_call_id</code>，它靠什么把 <code>AIMessage.tool_calls</code> 和随后的 <code>ToolMessage</code> 配对？",
                "opts": [
                    "靠每条消息里的唯一 ID 字段",
                    "靠消息出现的先后顺序——<code>ToolMessage</code> 紧跟在带 <code>tool_calls</code> 的 <code>AIMessage</code> 之后",
                    "靠消息的时间戳",
                    "靠对工具名做哈希匹配",
                ],
                "answer": 1,
                "why": "ragas 消息不带 <code>tool_call_id</code>，调用与结果靠出现顺序配对；<code>field_validator</code> 校验 <code>ToolMessage</code> 必须紧跟「带 <code>tool_calls</code> 的 <code>AIMessage</code>」或「另一个 <code>ToolMessage</code>」，从而保证配对合法。",
            },
        ],
    },
    "06-two-datasets.html": {
        "mcq": [
            {
                "q": "为什么 <code>DataTable</code> 设计成泛型基类，被 <code>Dataset</code> 与 <code>Experiment</code> 共用？",
                "opts": [
                    "为了让两者的存取算法各不相同",
                    "让 <code>load</code> / <code>save</code> / <code>_resolve_backend</code> 只写一遍，靠 <code>DATATABLE_TYPE</code> 区分身份（DRY）",
                    "因为 Python 要求所有类都继承泛型",
                    "为了让 <code>Experiment</code> 不能存盘",
                ],
                "answer": 1,
                "why": "<code>DataTable</code> 把存取逻辑收敛到一处，<code>Dataset</code> 与 <code>Experiment</code> 复用，靠类属性 <code>DATATABLE_TYPE</code>（<code>'Dataset'</code> / <code>'Experiment'</code>）区分身份，无需各写一套。",
            },
            {
                "q": "为什么存储型数据集允许用字符串 <code>'local/csv'</code> 指定 backend，而不是直接 import 后端类？",
                "opts": [
                    "因为传字符串比传类运行得更快",
                    "用户无需 import 具体类，新后端注册进 registry 即可被字符串引用——插件式扩展，报错时还顺带列出可用项",
                    "因为后端类在技术上无法被 import",
                    "为了隐藏后端实现、使其不可用",
                ],
                "answer": 1,
                "why": "<code>_resolve_backend</code> 拿字符串去全局 registry 查类再实例化；查不到就列出可用后端清单。用户只写 <code>'local/csv'</code>，新后端注册即可引用，插件式可扩展、报错友好。",
            },
        ],
        "open": [
            "同样叫 「Dataset」：什么情况下你该用 <code>EvaluationDataset</code>、什么情况下该用 <code>Dataset</code> / <code>DataTable</code>？如果 import 错了对象，最早会在哪一步暴露问题？",
        ],
    },
    "07-evaluate.html": {
        "mcq": [
            {
                "q": "调用 <code>evaluate()</code> 时，若需要裁判的指标没绑 LLM、你也没传，会发生什么？为什么这样设计？",
                "opts": [
                    "直接报错，要求必须显式传入 LLM",
                    "自动建一个默认裁判 <code>llm_factory('gpt-4o-mini')</code>，让最小例子开箱即跑",
                    "跳过该指标、不打分",
                    "随机挑一个本地模型来打分",
                ],
                "answer": 1,
                "why": "缺裁判时自动兜底建 <code>gpt-4o-mini</code>（embeddings 同理走 <code>embedding_factory</code>），最小例子无需手动配模型即可跑（仍需设 <code>OPENAI_API_KEY</code>），也可在 metric 级覆盖。",
            },
            {
                "q": "为什么 <code>result.total_cost()</code> / <code>total_tokens()</code> 需要在调用 <code>evaluate</code> 时传 <code>token_usage_parser</code> 才能用？",
                "opts": [
                    "因为成本是随机生成的",
                    "因为不同 LLM 回包里 token 用量的格式不一，需要 parser 告诉 ragas 怎么解析，否则它无从统计",
                    "因为 <code>total_cost</code> 已被废弃",
                ],
                "answer": 1,
                "why": "各家模型返回 token 用量的字段格式不同，<code>token_usage_parser</code> 负责抽取；没配它，<code>total_tokens</code> / <code>total_cost</code> 会抛错提示「未配置成本计算」。",
            },
        ],
    },
    "08-experiment.html": {
        "mcq": [
            {
                "q": "<code>@experiment</code> 的 <code>arun</code> 跑完后会自动把每行结果存进 backend，这体现了什么设计理念？",
                "opts": [
                    "为了尽量占满磁盘空间",
                    "experiments-first：每次改动都留下可对比的记录，便于一版版迭代回看",
                    "为了让结果无法被读取",
                    "因为不存盘就没法并发执行",
                ],
                "answer": 1,
                "why": "评测只「打一次分」，实验把「改动 → 跑分 → 留痕对比」固化成闭环；自动落盘让每次实验登记在册，方便回看哪次改动更好。",
            },
            {
                "q": "<code>version_experiment(name)</code> 会用 GitPython 提交改动并建分支，目的是什么？",
                "opts": [
                    "自动把代码部署到生产环境",
                    "把每个实验钉在确切的代码快照上，随时回溯「这次实验对应哪段代码」",
                    "删除所有未提交的改动",
                    "加快实验的运行速度",
                ],
                "answer": 1,
                "why": "<code>version_experiment</code> 暂存改动、提交一次并建 <code>ragas/{name}</code> 分支、返回 commit hash，让实验与 git 版本绑定，实现可复现、可回溯。",
            },
        ],
        "open": [
            "为同一个 RAG 应用设计两版改动（例如换 embedding 模型、调 chunk 大小），描述你会怎么用 <code>@experiment</code> + <code>version_experiment</code> 跑出两次可对比、可回溯到代码的实验。",
        ],
    },
    "09-metrics-overview.html": {
        "mcq": [
            {
                "q": "关于两代指标的导入位置，下列哪条说法是对的？",
                "opts": [
                    "所有指标都应统一从 <code>ragas.metrics</code> 导入",
                    "具名指标（如 Faithfulness）应从 <code>ragas.metrics.collections</code> 导入；基类与 <code>DiscreteMetric</code> 等原语仍留在 <code>ragas.metrics</code>",
                    "<code>DiscreteMetric</code> 已废弃，要改从 collections 导入",
                    "collections 放基类，<code>ragas.metrics</code> 放具名指标",
                ],
                "answer": 1,
                "why": "具名指标的「正门」是 <code>ragas.metrics.collections</code>；从 <code>ragas.metrics</code> 导入它们会发 <code>DeprecationWarning</code> 并在 v1.0 移除。基类与 Simple 栈（<code>DiscreteMetric</code> / <code>NumericMetric</code> / <code>RankingMetric</code>）未废弃，仍在 <code>ragas.metrics</code>。",
            },
            {
                "q": "旧代码 <code>from ragas.metrics import Faithfulness</code> 仍能用、但会告警。这种「导入即告警」是为了什么？",
                "opts": [
                    "立刻删除旧路径，逼用户马上重写",
                    "用模块级 <code>__getattr__</code> 做平滑过渡：旧路径暂时可用、同时提示迁移到 collections，到 v1.0 再移除",
                    "让 Faithfulness 算出的分数变低",
                    "彻底禁止任何人使用 Faithfulness",
                ],
                "answer": 1,
                "why": "<code>ragas/metrics/__init__.py</code> 把具名指标放进 <code>_DEPRECATED_METRICS</code>，由模块级 <code>__getattr__</code> 拦截、发告警后仍返回实现；算法与分数口径不变，只是提示改导入路径，实现平滑迁移。",
            },
        ],
    },
    "10-rag-metrics.html": {
        "mcq": [
            {
                "q": "为什么 <code>AnswerRelevancy</code> 构造时除了 <code>llm</code> 还必须传 <code>embeddings</code>，其他三件套却只需 <code>llm</code>？",
                "opts": [
                    "因为它要把「从回答反推出的问题」与原问题算余弦相似度",
                    "因为它根本不需要 LLM",
                    "因为 embeddings 只是用来让它跑得更快",
                    "因为它要去检索新的上下文",
                ],
                "answer": 0,
                "why": "AnswerRelevancy 让 LLM 从回答反推可能的问题，再用 embeddings 计算这些问题与原问题的余弦相似度来衡量「切题」，所以构造时必须注入 embeddings。",
            },
            {
                "q": "RAG 四件套为什么要分成「两个查检索质量、两个查生成质量」？",
                "opts": [
                    "因为四个指标的算法其实完全相同",
                    "RAG 同时依赖检索与生成两端，分开各盯一段，才能定位问题出在检索还是生成",
                    "因为检索和生成必须用不同的 LLM",
                    "纯粹是为了凑成四个指标",
                ],
                "answer": 1,
                "why": "ContextPrecision / ContextRecall 查检索质量，Faithfulness / AnswerRelevancy 查生成质量；两端分别体检，才能判断 RAG 是「检索没找对」还是「答案跑偏」。",
            },
        ],
        "open": [
            "给你自己的 RAG 应用挑四件套：如果手头没有标准答案（<code>reference</code>），ContextPrecision / ContextRecall 还能照常用吗？缺了它你会用什么来近似评检索质量？",
        ],
    },
}


def render(fname):
    """Return the self-test HTML block for ``fname`` (or '' if none defined)."""
    data = QUIZZES.get(fname)
    if not data:
        return ""
    out = ['<div class="selftest">', "<h2>🧪 自测 · 想一想为什么这么设计</h2>"]
    for i, item in enumerate(data.get("mcq", []), 1):
        shuffled, ans = _shuffle(item["opts"], item["answer"], f"{fname}:{i}")
        opts = "\n".join(f"    <li>{o}</li>" for o in shuffled)
        letter = chr(65 + ans)
        out.append(
            f'<div class="quiz">\n'
            f'  <div class="qn">{i}. {item["q"]}</div>\n'
            f'  <ol class="opts">\n{opts}\n  </ol>\n'
            f'  <details class="accordion">\n'
            f'    <summary>看答案与解析 <span class="hint">点击展开</span></summary>\n'
            f'    <div class="acc-body"><div class="qa"><div class="a">'
            f'<strong>答案：{letter}</strong>。{item.get("why", "")}'
            f"</div></div></div>\n"
            f"  </details>\n"
            f"</div>"
        )
    opens = data.get("open", [])
    if opens:
        lis = "\n".join(f"    <li>{o}</li>" for o in opens)
        out.append(
            '<div class="card spark">\n'
            '  <div class="tag">💭 发散思考（没有标准答案，动手或动脑想想）</div>\n'
            f"  <ul>\n{lis}\n  </ul>\n"
            "</div>"
        )
    out.append("</div>")
    return "\n".join(out)
