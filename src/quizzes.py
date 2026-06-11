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
                    "因为 vibe check 必须先攒够大量人工标注才能给出结论，太重了",
                    "因为主观判断不可量化、不可复现，换个人或换一天结论就变",
                    "因为 LLM 没办法评价自己生成的内容，只能靠人工",
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
                    "因为这些具名指标都是运行时动态生成的，没有固定类定义可登记",
                    "因为公开面越小越稳，能降低耦合、减少升级时的破坏性变更",
                    "因为登记进顶层的名字会被锁定，用户无法再自定义同名指标",
                    "因为 <code>__all__</code> 最多只能登记几十个名字，装不下成百上千个指标",
                ],
                "answer": 1,
                "why": "顶层只放「人人都要用」的门面（入口 + 数据模型），庞杂实现关进子包，按需从 <code>ragas.metrics</code> / <code>ragas.llms</code> 等子模块导入。公开面越小，升级时越不容易误伤用户代码。",
            },
            {
                "q": "<code>ragas.experimental</code> 用模块级 <code>__getattr__</code> 惰性加载，主要好处是什么？",
                "opts": [
                    "为了每次访问时都重新加载实验模块，确保拿到最新代码",
                    "没装可选依赖时 import ragas 本身不报错，真用到才触发导入并提示安装",
                    "为了把实验功能限制为仅供 ragas 内部测试使用",
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
                    "为了让出错的行用全局均值自动填补，保持样本量不变",
                    "为了让个别失败行不中断整轮评测，且均值用 <code>safe_nanmean</code> 自动忽略它",
                    "为了节省 token",
                    "因为 <code>np.nan</code> 会触发 ragas 自动换一个备用 LLM 重算该行",
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
                    "因为不同指标会动态往样本里增删字段，必须全设成可选",
                    "为了用一个模型适配不同指标——缺哪栏就空着，按需带列",
                    "因为缺失的字段会在评测时由 LLM 自动补全，所以可以先留空",
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
                    "为了在构造对象时自动调整错乱的消息顺序，省去手工整理",
                    "让「工具结果凭空出现」「对话顺序错乱」等问题在造样本阶段就报错，错误前移、定位更快",
                    "因为 <code>field_validator</code> 是唯一能在评测中途动态插入检查的钩子",
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
                    "让 <code>Dataset</code> 与 <code>Experiment</code> 各自实现一套独立的存取逻辑、互不影响",
                    "让 <code>load</code> / <code>save</code> / <code>_resolve_backend</code> 只写一遍，靠 <code>DATATABLE_TYPE</code> 区分身份（DRY）",
                    "靠泛型的类型参数在运行时区分 <code>Dataset</code> 与 <code>Experiment</code> 的身份，省掉 <code>DATATABLE_TYPE</code> 类属性",
                    "让 <code>Experiment</code> 自动继承 <code>EvaluationDataset</code> 的 <code>to_csv</code> / <code>to_jsonl</code> 转换器，免去自己实现持久化",
                ],
                "answer": 1,
                "why": "<code>DataTable</code> 把存取逻辑收敛到一处，<code>Dataset</code> 与 <code>Experiment</code> 复用，靠类属性 <code>DATATABLE_TYPE</code>（<code>'Dataset'</code> / <code>'Experiment'</code>）区分身份，无需各写一套。",
            },
            {
                "q": "为什么存储型数据集允许用字符串 <code>'local/csv'</code> 指定 backend，而不是直接 import 后端类？",
                "opts": [
                    "因为字符串能让多个数据集共享同一个全局后端单例，省去重复实例化",
                    "用户无需 import 具体类，新后端注册进 registry 即可被字符串引用——插件式扩展，报错时还顺带列出可用项",
                    "因为 <code>_resolve_backend</code> 会把字符串当成文件路径直接定位读写，跳过注册表查找",
                    "因为字符串在运行时解析，能按环境变量自动切到不同后端，传类则做不到",
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
                    "自动降级用一个轻量的本地规则裁判，完全不产生 API 费用",
                ],
                "answer": 1,
                "why": "缺裁判时自动兜底建 <code>gpt-4o-mini</code>（embeddings 同理走 <code>embedding_factory</code>），最小例子无需手动配模型即可跑（仍需设 <code>OPENAI_API_KEY</code>），也可在 metric 级覆盖。",
            },
            {
                "q": "为什么 <code>result.total_cost()</code> / <code>total_tokens()</code> 需要在调用 <code>evaluate</code> 时传 <code>token_usage_parser</code> 才能用？",
                "opts": [
                    "因为统计 token 会拖慢评测，ragas 默认关闭、传了 parser 才开启",
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
                    "为了让每次实验都覆盖上一次的结果，只保留最新版",
                    "experiments-first：每次改动都留下可对比的记录，便于一版版迭代回看",
                    "为了在内存里缓存结果，加快下一次相同实验的速度",
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
                    "把实验结果同步上传到远程 git 仓库做备份",
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
                    "让从旧路径导入的 Faithfulness 自动切换成 collections 的新实现",
                    "在 import 时就抛出 <code>ImportError</code>，强制用户立刻改用新路径",
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
                    "因为它要先把检索到的上下文向量化，再判断是否相关",
                    "因为它要去检索新的上下文",
                ],
                "answer": 0,
                "why": "AnswerRelevancy 让 LLM 从回答反推可能的问题，再用 embeddings 计算这些问题与原问题的余弦相似度来衡量「切题」，所以构造时必须注入 embeddings。",
            },
            {
                "q": "RAG 四件套为什么要分成「两个查检索质量、两个查生成质量」？",
                "opts": [
                    "因为检索质量与生成质量本质是同一回事，分开只是表述习惯",
                    "RAG 同时依赖检索与生成两端，分开各盯一段，才能定位问题出在检索还是生成",
                    "因为检索和生成必须用不同的 LLM",
                    "因为四个指标必须成套使用，缺一个就无法出分",
                ],
                "answer": 1,
                "why": "ContextPrecision / ContextRecall 查检索质量，Faithfulness / AnswerRelevancy 查生成质量；两端分别体检，才能判断 RAG 是「检索没找对」还是「答案跑偏」。",
            },
        ],
        "open": [
            "给你自己的 RAG 应用挑四件套：如果手头没有标准答案（<code>reference</code>），ContextPrecision / ContextRecall 还能照常用吗？缺了它你会用什么来近似评检索质量？",
        ],
    },
    "11-custom-metrics.html": {
        "mcq": [
            {
                "q": "<code>DiscreteMetric</code> 在 <code>__post_init__</code> 里用 <code>Literal[...]</code> 自动生成一个 pydantic 响应模型，这样设计的核心目的是什么？",
                "opts": [
                    "为了让指标跑得更快、少花 token",
                    "因为只有 <code>Literal[...]</code> 才允许 LLM 在 <code>allowed_values</code> 之外补充新取值",
                    "把 LLM 输出从源头卡死在 <code>allowed_values</code> 之内，省掉事后解析与兜底",
                    "为了让指标自动支持多轮对话",
                ],
                "answer": 2,
                "why": "<code>__post_init__</code> 把 <code>allowed_values</code> 转成 <code>Literal[...]</code>，再用 <code>create_auto_response_model</code> 造响应模型，于是 LLM 只能吐出合法取值——从源头杜绝「答非所选」，不必写解析与异常兜底。速度 / token、多轮都不是它要解决的问题。",
            },
            {
                "q": "Simple 栈同时给了「类」和「装饰器」两副面孔，该怎么选？",
                "opts": [
                    "要复用 / 保存（<code>load</code>）就用类；把现成函数一键变成指标就用装饰器",
                    "装饰器只能做离散指标，类只能做数值指标",
                    "两者功能完全相同，纯粹是语法糖",
                    "类不需要 LLM，装饰器一定需要 LLM",
                ],
                "answer": 0,
                "why": "类适合需要复用、版本化保存的指标；装饰器适合把一个现成函数快速包成指标，并按 <code>allowed_values</code> 的类型自动选指标种类。两者并非语法糖，也都可不依赖 LLM（如纯规则的情绪判断）。",
            },
        ],
        "open": [
            "给你自己的应用设计一个自定义指标：它的输出该是离散、数值还是排序？你会用类还是装饰器？为什么这样选？",
        ],
    },
    "12-traditional-metrics.html": {
        "mcq": [
            {
                "q": "为什么 BLEU / ROUGE / chrF / ExactMatch 这类传统指标特别适合放进 CI 回归？",
                "opts": [
                    "因为它们比 LLM 指标更懂语义",
                    "因为它们确定、零 token、毫秒级：同样输入永远同样输出",
                    "因为它们会根据历史结果自我校准，越跑越准",
                    "因为它们必须联网调用 API 才更准",
                ],
                "answer": 1,
                "why": "确定性算法同输入同输出、不花 token、毫秒出结果，跨次跨人结论一致，适合反复跑的 CI；代价是不懂语义（换个说法分可能偏低），所以常与 LLM 指标混用。",
            },
            {
                "q": "关于 <code>SQLSemanticEquivalence</code> 与 <code>DataCompyScore</code> 的对照，下列哪项正确？",
                "opts": [
                    "两者都是确定性算法，都不需要 LLM",
                    "两者都需要 LLM 当裁判",
                    "<code>DataCompyScore</code> 需要 LLM，<code>SQLSemanticEquivalence</code> 是确定性的",
                    "<code>SQLSemanticEquivalence</code> 其实需要 LLM 判语义等价，确定性的对照是 <code>DataCompyScore</code>",
                ],
                "answer": 3,
                "why": "名字带 Semantic 容易让人误以为是确定性比对，其实 <code>SQLSemanticEquivalence</code> 用 LLM 判两条 SQL 是否语义等价（构造需 <code>llm</code>）；真正确定性、直接比表格数据的是 <code>DataCompyScore</code>。",
            },
        ],
    },
    "13-metric-base.html": {
        "mcq": [
            {
                "q": "为什么 collections 的 <code>BaseMetric</code> 在构造时（<code>_validate_llm</code>）就拒收 langchain 包装的 LLM、只认 <code>InstructorBaseRagasLLM</code>？",
                "opts": [
                    "把错误前移到构造期：传错模型当场 <code>ValueError</code>，而不是评测跑到一半才炸",
                    "因为 langchain 包装的 LLM 只有同步接口，无法支持异步打分",
                    "因为构造时校验能让打分本身更快",
                    "因为 <code>InstructorBaseRagasLLM</code> 不需要 API key",
                ],
                "answer": 0,
                "why": "现代栈靠 instructor 拿结构化输出，必须是 <code>InstructorBaseRagasLLM</code>；构造期就校验能让「传错模型」立刻报错，而不是跑到一半才崩——这是把失败前移的务实设计。",
            },
            {
                "q": "经典栈与现代栈的调用接口差别，下列哪项正确？",
                "opts": [
                    "两代接口完全一样，只是导入路径不同",
                    "经典栈返回 <code>MetricResult</code>，现代栈返回裸 <code>float</code>",
                    "经典栈 <code>single_turn_ascore(sample)</code> 吃样本对象、返回 <code>float</code>；现代栈 <code>ascore(**kwargs)</code> 吃关键字、返回 <code>MetricResult</code>",
                    "现代栈只支持多轮样本，经典栈只支持单轮",
                ],
                "answer": 2,
                "why": "两代算法相同、接口不同：经典栈 <code>single_turn_ascore</code> / <code>multi_turn_ascore</code> 吃一个样本对象返回 <code>float</code>（解释另存）；现代栈统一 <code>ascore(**kwargs)</code> 返回带值与理由的 <code>MetricResult</code>。",
            },
        ],
    },
    "14-metric-result.html": {
        "mcq": [
            {
                "q": "<code>MetricResult</code> 重载 <code>__float__</code> / <code>__add__</code> / <code>__gt__</code> 等运算符，主要为了什么？",
                "opts": [
                    "为了让它能用 <code>==</code> 直接比较两个结果的 reason 文本是否一致",
                    "让它无需先 <code>.value</code> 解包就能直接当数字参与运算 / 比较 / <code>sum()</code>，无侵入替换裸数字",
                    "为了禁止它参与浮点运算，强制开发者先手动 <code>.value</code> 解包",
                    "为了在序列化时把 <code>value</code> 和 <code>reason</code> 合并成一个字符串",
                ],
                "answer": 1,
                "why": "靠运算符重载，已有按 <code>float</code> 写的聚合代码几乎不改就能接收 <code>MetricResult</code>——它能直接算、比大小、被 <code>sum()</code>，而 reason 始终不丢。",
            },
            {
                "q": "为什么 <code>MetricResult</code> 既带 <code>value</code> 又带 <code>reason</code>，而不是只返回一个分数？",
                "opts": [
                    "为了可解释：既能统计（数值），又能复盘为什么得这个分（评语）",
                    "因为 reason 是给 <code>safe_nanmean</code> 标记缺失值用的",
                    "因为 reason 会作为下一次调用的缓存 key",
                    "因为 value 单独存在时无法序列化",
                ],
                "answer": 0,
                "why": "「分数带 why」是 ragas 可解释性的关键：<code>value</code> 用于统计聚合，<code>reason</code> 记录判分依据便于复盘；只给冷冰冰的数字就丢了诊断能力。",
            },
        ],
    },
    "15-faithfulness-internals.html": {
        "mcq": [
            {
                "q": "Faithfulness 为什么先把答案拆成「原子陈述」再逐句做 NLI，而不是对整段笼统打分？",
                "opts": [
                    "因为整段打分会消耗更多 token",
                    "因为 LLM 一次只能对一个句子做蕴含判断，无法整段处理",
                    "因为拆句之后就不再需要检索资料",
                    "逐句查证更精确，还天然产出可读的逐句 <code>reason</code>",
                ],
                "answer": 3,
                "why": "先拆成无代词、可独立判断的原子陈述，再逐句对照 context 判蕴含，比「整段一把抓」更精确，也让每句都带上判定理由；得分 = 有据句数 / 总句数。",
            },
            {
                "q": "legacy 的 <code>FaithfulnesswithHHEM</code> 与标准 Faithfulness 是什么关系？",
                "opts": [
                    "算法骨架一样（拆句 → 逐句判 → 占比），只把第二步的逐句判断从 LLM 换成交叉编码器模型",
                    "它完全抛弃拆句，直接对整段打分",
                    "它用 LLM 做判断，而标准版用交叉编码器",
                    "它是确定性指标，不需要任何模型",
                ],
                "answer": 0,
                "why": "HHEM 变体仍用 LLM 拆句，但把逐句裁决换成 cross-encoder（vectara 幻觉评估模型）打分取整。说明算法骨架稳定、只是第二步的「裁判」可换；该变体仅在 legacy。",
            },
        ],
        "open": [
            "把答案拆成原子陈述时，拆得越细越好吗？想想拆得过细 / 过粗分别会怎样影响忠实度的分数与调用成本。",
        ],
    },
    "16-context-metrics-internals.html": {
        "mcq": [
            {
                "q": "<code>ContextPrecision</code> 为什么用「平均精度（MAP）」而不是简单的命中比例来计分？",
                "opts": [
                    "因为 MAP 不需要逐条判定",
                    "因为简单比例无法处理 0/1 裁决",
                    "因为它要奖励把相关资料排在前面：相关项越靠前 <code>precision@k</code> 越高",
                    "纯粹是为了和 Recall 共用同一个公式",
                ],
                "answer": 2,
                "why": "检索讲究排序——把有用的资料压在后面要扣分。平均精度让相关项越靠前得分越高，正是信息检索经典的 MAP 思路；简单命中比例体现不出「排序好坏」。",
            },
            {
                "q": "关于现代 collections 版 Context 指标是否使用多次采样投票（Ensemble），下列哪项正确？",
                "opts": [
                    "现代 collections「不用」ensemble 投票（Precision 每条一次、Recall 整体一次）；投票是 legacy 的做法",
                    "现代 collections 必须多次采样投票才能出分",
                    "两代都用 ensemble 投票",
                    "只有 Recall 用投票，Precision 不用",
                ],
                "answer": 0,
                "why": "legacy 的 <code>_context_*.py</code> 用 <code>generate_multiple</code> + <code>ensembler</code> 多数投票对抗随机性；collections 已简化为单次调用，稳定性改由 instructor 结构化输出兜底。讲新栈要以源码为准。",
            },
        ],
    },
    "17-answer-metrics-internals.html": {
        "mcq": [
            {
                "q": "AnswerRelevancy 为什么要从答案「反向生成问题」再与原问题算余弦相似度，而不是直接问 LLM「切题吗」？",
                "opts": [
                    "因为反向生成不需要 embeddings",
                    "把主观的「切不切题」转成可计算的相似度：真切题，反推出的问题就与原问题语义相近",
                    "因为直接问「切题吗」只能得到是 / 否，无法给出 0–1 的连续分",
                    "因为这样就可以完全不调用 LLM",
                ],
                "answer": 1,
                "why": "直接问「切题吗」主观难量化。反向生成把它转成可计算：若答案真在回答原问题，反推出的问题应与原问题相似度高；跑题则对不上。它需 <code>embeddings</code>，且全敷衍（noncommittal）直接 0 分。",
            },
            {
                "q": "<code>AspectCritic</code> 与 AnswerRelevancy / FactualCorrectness 在「所属栈」上有何不同？",
                "opts": [
                    "<code>AspectCritic</code> 目前「只有 legacy 版」（导入会触发废弃告警），尚未迁移到 collections",
                    "三者都已在 collections 里",
                    "<code>AspectCritic</code> 在 collections，另两个在 legacy",
                    "三者都只有 legacy 版",
                ],
                "answer": 0,
                "why": "AnswerRelevancy 与 FactualCorrectness 在现代 collections；<code>AspectCritic</code> 仍停在经典栈（<code>from ragas.metrics import</code> 会告警），底层是 <code>MetricWithLLM</code> + 单 / 多轮。",
            },
        ],
    },
    "18-agent-metrics-internals.html": {
        "mcq": [
            {
                "q": "为什么 <code>ToolCallAccuracy</code> / <code>ToolCallF1</code> 用纯规则比对，而不请 LLM 当裁判？",
                "opts": [
                    "因为工具调用的正确与否带有语义模糊，必须靠规则消除歧义",
                    "因为规则比对虽更慢但更准",
                    "因为工具调用的参数都是自由文本，只有规则能逐字符比对",
                    "工具调用是结构化的（名字 + 参数），对不对可直接比对——纯规则零 token、确定可复现",
                ],
                "answer": 3,
                "why": "工具调用是名字 + 参数字典的结构化数据，正确与否可精确比对、无语义模糊，所以走规则：零 token、确定、可复现、快。而「目标达成没 / 跑没跑题」涉及语义才请 LLM。",
            },
            {
                "q": "<code>ToolCallAccuracy</code> 与 <code>ToolCallF1</code> 的判定口径差别是什么？",
                "opts": [
                    "Accuracy 在意顺序与参数（默认 <code>strict_order=True</code>）；F1 把调用看成无序集合，只问该调的调了没、有没有多调",
                    "两者完全一样，只是名字不同",
                    "Accuracy 用 LLM，F1 用规则",
                    "F1 在意顺序，Accuracy 把调用看成集合",
                ],
                "answer": 0,
                "why": "<code>ToolCallAccuracy</code> 做序列对齐 + 参数精确匹配（讲顺序）；<code>ToolCallF1</code> 把调用集合化（名字 + 参数都同才算一个）算 TP/FP/FN 求 F1（顺序无关）。",
            },
        ],
        "open": [
            "给你自己的 Agent 设计评测：哪些维度可以用规则（零 token）来判、哪些必须请 LLM 当裁判？你会怎么在成本与准确度之间取舍？",
        ],
    },
    "19-prompt-system.html": {
        "mcq": [
            {
                "q": "<code>PydanticPrompt</code> 的输出签名来自 <code>output_model.model_json_schema()</code>，这样设计好在哪？",
                "opts": [
                    "为了让 prompt 更短、省 token",
                    "把「答题格式」变成机器可校验的强约束，而不是口头叮嘱",
                    "为了让输出可以是任意自由文本",
                    "因为 <code>model_json_schema()</code> 会把 few-shot 例题也一并编码进去",
                ],
                "answer": 1,
                "why": "用 <code>output_model</code> 的 JSON schema 当输出签名，等于把格式要求写成机器可校验的强约束；再配 <code>RagasOutputParser</code> 校验、<code>FixOutputFormat</code> 在坏 JSON 时退回重填，鲁棒性藏在解析器里。",
            },
            {
                "q": "为什么现代 collections 指标改用更薄的 <code>BasePrompt</code>（只有 <code>to_string</code>、没有 <code>generate</code>）？",
                "opts": [
                    "因为现代指标不再需要 few-shot 例题",
                    "因为现代指标根本不调用 LLM",
                    "因为解析与重试交给了 instructor，prompt 对象只需把考卷拼成字符串",
                    "因为薄 <code>BasePrompt</code> 运行时不依赖 pydantic",
                ],
                "answer": 2,
                "why": "instructor 直接把 LLM 输出校验成 pydantic 对象，格式约束与重试由它兜底；于是 collections 的 prompt 退化成「只拼字符串」，再 <code>await llm.agenerate(prompt_str, OutputModel)</code>——是一处真实的减法。",
            },
        ],
    },
    "20-prompt-advanced.html": {
        "mcq": [
            {
                "q": "动态 few-shot（<code>DynamicFewShotPrompt</code>）相比写死的静态例题，好在哪？",
                "opts": [
                    "按当前输入用 embedding 余弦相似度从例题库临场挑最相关的 top-k，比固定例题更贴题",
                    "它完全不需要任何例题",
                    "它能让 prompt 不再依赖 LLM",
                    "它把所有例题都塞进 prompt，越多越好",
                ],
                "answer": 0,
                "why": "静态 <code>examples</code> 每次都喂同样例题；动态版按输入用 <code>embed_query</code> + 余弦相似度挑 top-k（默认阈值 0.7），例题随题目变化更贴题。Simple 栈没 embedding 时优雅退回最近 N 条。",
            },
            {
                "q": "<code>adapt()</code> 把 prompt 翻译到另一种语言时，为什么强制「译后条数 == 译前条数」？",
                "opts": [
                    "因为翻译会随机丢例题，必须事后补齐",
                    "保证 few-shot 例题结构不变、一一对应，只换语言而不重写 prompt",
                    "因为只有条数一致，<code>adapt</code> 才能原地修改 prompt 而不新建对象",
                    "因为条数变了 prompt 就无法序列化",
                ],
                "answer": 1,
                "why": "<code>adapt</code> 把 <code>examples</code> 整批翻译并返回一张新 prompt（不改原件），强制条数一致能保证例题一一对应、结构零改动——题目不变、语言变了；条数对不上则报错。",
            },
        ],
        "open": [
            "你的评测要服务多语言用户：你会用 <code>adapt()</code> 把 prompt 整体翻译，还是为每种语言单独维护一套？动态 few-shot 在跨语言场景下又能帮上什么忙？",
        ],
    },
    "21-llm-abstraction.html": {
        "mcq": [
            {
                "q": "现代 instructor 路径让 LLM「直接产出 pydantic 对象」，相比经典 langchain wrapper 好在哪？",
                "opts": [
                    "因为 instructor 会缓存每次结构化输出，相同输入直接复用",
                    "因为 pydantic 对象在网络传输时比 JSON 字符串更紧凑、更省带宽",
                    "LLM 输出被直接校验成 pydantic 对象，省掉手写 JSON 解析，格式约束与重试都交给 instructor 兜底",
                    "因为 instructor 会在 LLM 出错时自动切换到另一个模型重试",
                ],
                "answer": 2,
                "why": "经典路径要自己拼 prompt、再手写解析 + 重试；现代 instructor 路径给 client 打补丁，让 LLM 直接吐出校验过的 pydantic 对象，解析与重试由库兜底——是一处实打实的减法。",
            },
            {
                "q": "<code>llm_factory(model, client=..., adapter='auto')</code> 里 client 必填、adapter 默认 'auto'，体现了什么取舍？",
                "opts": [
                    "client 可选，adapter 才是必填项",
                    "client 必填，因为 instructor 要给真实 client 打补丁，传 None 直接 <code>ValueError</code>；adapter='auto' 则按 client 自动挑适配器，省去手填",
                    "client 只用于鉴权，真正发起调用的是 adapter",
                    "adapter 必须和 client 来自同一个第三方库，否则报错",
                ],
                "answer": 1,
                "why": "没有具体 client，instructor 无从打补丁，所以 client 缺失即 <code>ValueError</code>；adapter 默认 'auto' 让它按 client 自动选适配器，常见场景一行就够——必填的是「真用得上的」，能猜的就给默认。",
            },
        ],
        "open": [
            "你的项目里已经有一套基于 langchain wrapper 的经典调用，现在要不要迁到 instructor 路径？你会怎么权衡「免手写解析 / 拿到结构化输出」的收益与迁移、依赖成本？",
        ],
    },
    "22-embedding-abstraction.html": {
        "mcq": [
            {
                "q": "现代 <code>BaseRagasEmbedding</code> 与 legacy <code>BaseRagasEmbeddings</code> 为什么并存？",
                "opts": [
                    "新接口删掉了所有异步方法",
                    "两者完全相同，只是改了名字大小写",
                    "legacy 才支持多 provider，新版只支持一家",
                    "现代版收敛出更精简的 <code>embed_text</code> / <code>aembed_text</code> 接口，与 legacy 并存是为了平滑迁移、不逼人一次性重写",
                ],
                "answer": 3,
                "why": "新旧接口并存是迁移友好：现代 <code>BaseRagasEmbedding</code> 提供更薄的 <code>embed_text</code> / <code>aembed_text</code>，老代码仍可用 legacy 的 <code>BaseRagasEmbeddings</code>，逐步切换而非推倒重来。",
            },
            {
                "q": "<code>_infer_embedding_provider_from_llm</code>（按所选 LLM 推断 embedding provider）解决的是什么？",
                "opts": [
                    "让用户少配一次：既然已经选了某家 LLM，就顺势推断同厂 embedding provider，减少重复配置",
                    "因为 embedding 必须和 LLM 同厂，否则一定报错",
                    "因为这样就能完全不用 embedding 也能跑",
                    "因为推断比显式配置更省 token",
                ],
                "answer": 0,
                "why": "在你已选好 LLM 时顺势猜出同厂 embedding provider，是「少配一次」的体贴默认；想换别家仍可显式指定，并非强制同厂，也跟省 token 无关。",
            },
        ],
    },
    "23-executor.html": {
        "mcq": [
            {
                "q": "<code>Executor</code> 为什么要用 <code>wrap_callable_with_index</code> 给每个任务带上原始索引？",
                "opts": [
                    "因为索引被当作缓存 key，用来命中上次相同任务的结果",
                    "并发完成的顺序是乱的，带上原始索引，收集后才能按输入顺序还原，保证结果保序",
                    "因为 tenacity 重试必须靠索引",
                    "因为索引决定任务的执行优先级",
                ],
                "answer": 1,
                "why": "<code>wrap_callable_with_index</code> 把输入下标绑在结果上：并发返回是乱序的，带着索引才能在汇总时还原成与输入一一对应的顺序——评测最怕结果错位。",
            },
            {
                "q": "单个任务抛错时，为什么默认（<code>raise_exceptions=False</code>）把它转成 <code>np.nan</code> 而不是让整轮崩掉？",
                "opts": [
                    "因为把失败行记成 <code>np.nan</code> 相当于给它打 0 分，对均值最保守",
                    "因为异常对象无法被 <code>Executor</code> 的结果列表收集，只能用 <code>np.nan</code> 占位",
                    "因为这样能自动重跑所有失败任务",
                    "一行出错就废掉整批评测代价太大；转成 <code>np.nan</code> 让该行缺测、其余结果照常产出，整轮更稳健",
                ],
                "answer": 3,
                "why": "评测动辄成百上千行，单题失败若直接抛出会拖垮整轮。默认 <code>raise_exceptions=False</code> 把异常吞成 <code>np.nan</code>：坏的那行记缺失，好的结果照样落地（配合 <code>RunConfig</code> 默认 timeout=180 / max_retries=10 / max_workers=16 与 tenacity 重试）。",
            },
        ],
    },
    "24-callbacks-cost-cache.html": {
        "mcq": [
            {
                "q": "<code>cacher</code> + <code>DiskCacheBackend</code> 为什么用「调用内容的 sha256 哈希」当缓存 key？",
                "opts": [
                    "相同输入必得相同哈希、不同输入极难碰撞，用内容指纹当 key 才能精准复用上次的 LLM / embedding 结果",
                    "因为 sha256 不可逆，能防止别人从缓存里还原出 prompt 内容",
                    "因为时间戳总在变，所以改用哈希",
                    "因为哈希值定长，能让缓存文件大小固定、便于管理",
                ],
                "answer": 0,
                "why": "以「调用内容的 sha256」为 key：同样的输入 → 同样的 key → 直接命中缓存，省掉重复的 LLM / embedding 花费；哈希只是内容指纹，与加密、计费无关。",
            },
            {
                "q": "<code>new_group</code> / <code>RagasTracer</code> 把一次评测组织成「run 树」，主要图什么？",
                "opts": [
                    "因为树结构能让评测整体跑得更快",
                    "因为只有组织成树，<code>CostCallbackHandler</code> 才能聚合 token 与成本",
                    "把 评测 → 每行 → 每个指标 的调用嵌套成 trace 树，方便回看每一步、定位是哪行哪个指标出了问题",
                    "因为 trace 树会自动把失败的调用重跑一遍",
                ],
                "answer": 2,
                "why": "<code>new_group</code> 开运行分组，<code>RagasTracer</code> 把一轮记成 EVALUATION → ROW → METRIC 的 trace 树；<code>CostCallbackHandler</code> 再顺手聚合 token / 成本。可观测性是为了「出问题能顺树查到底」，不是提速。",
            },
        ],
        "open": [
            "如果你的评测每天要重复跑很多次，你会怎么权衡「开缓存省钱省时间」与「缓存可能让你看不到模型 / 数据已经悄悄变了」之间的风险？什么时候该主动清缓存？",
        ],
    },
    "25-testgen-overview.html": {
        "mcq": [
            {
                "q": "为什么要「自动造测试集」，而不是全靠人手写？",
                "opts": [
                    "因为只有自动生成的题目才能附带标准答案（reference），手写的不行",
                    "手写测试集往往量少、覆盖偏、还慢；自动生成能放量、铺开覆盖面，而且整条管道可复现",
                    "因为自动生成完全不需要任何文档",
                    "因为手写测试集的格式无法被 <code>EvaluationDataset</code> 接收",
                ],
                "answer": 1,
                "why": "手写测试集的三宗罪是少 / 偏 / 慢；测试生成线用文档自动造数据，量能上去、覆盖更全，且可复现——这正是它存在的理由。",
            },
            {
                "q": "测试生成被拆成 docs → KnowledgeGraph → personas → scenarios → samples → Testset 这样的分阶段管道，好在哪？",
                "opts": [
                    "因为阶段拆得越多整体跑得越快",
                    "因为分阶段后，知识图谱那一步就不再需要源文档",
                    "每步职责单一、产物可检查可复现，既贴近真实使用，又便于单独调试某一阶段",
                    "因为中间产物都能缓存，重跑时整条管道都不必再调用 LLM",
                ],
                "answer": 2,
                "why": "把造数据拆成「建图 → 生成 persona → 编排 scenario → 落成 sample → 打包 Testset」，每一步都有可检查的中间产物，定位问题、替换某一阶段都更容易。",
            },
        ],
        "open": [
            "拿你自己的一个知识库设想：用自动测试生成来造评测集时，你最担心生成出来的题目在哪些方面「不像真实用户会问的」？你会怎么校验这批生成结果的质量？",
        ],
    },
    "26-knowledge-graph.html": {
        "mcq": [
            {
                "q": "<code>KnowledgeGraph</code> 为什么要建成「节点 + 关系（边）」的图，而不是一个扁平文档列表？",
                "opts": [
                    "因为图会按相似度自动合并重复节点，扁平列表则会塞满冗余文档",
                    "因为图天然支持按节点类型（DOCUMENT / CHUNK）建索引，查询比扁平列表快得多",
                    "因为只有挂在图节点上的文本才能被切块（chunk），列表里的文档无法切分",
                    "图能显式记录节点之间的关联，后续才能沿边做跨节点（多跳）推理出题；扁平列表丢掉了这层关系",
                ],
                "answer": 3,
                "why": "<code>KnowledgeGraph</code> 由 <code>Node</code> + <code>Relationship</code> 组成（节点类型分 DOCUMENT / CHUNK）。把关系显式存成边，多跳出题才有「路」可走；一堆孤立文档是连不出多跳题的。",
            },
            {
                "q": "<code>find_indirect_clusters</code> / <code>find_two_nodes_single_rel</code> 这类簇 / 三元组查询是为什么准备的？",
                "opts": [
                    "为多跳题备料：先把「能连起来的节点组」找出来，synthesizer 才有跨节点素材出题",
                    "为单跳题挑出唯一的那个节点",
                    "为出题前裁掉图里的孤立节点，缩小遍历范围",
                    "为了给重复节点做去重",
                ],
                "answer": 0,
                "why": "<code>find_indirect_clusters</code> / <code>find_n_indirect_clusters</code> / <code>find_two_nodes_single_rel</code> 都在图里捞「可连接的节点簇 / 三元组」，专为多跳 synthesizer 备料；单跳题只需一个节点，用不上这些。",
            },
        ],
    },
    "27-transforms.html": {
        "mcq": [
            {
                "q": "transform 被分成 Extractor / Splitter / RelationshipBuilder / NodeFilter 四类，这种拆分意义何在？",
                "opts": [
                    "因为这四类正好对应知识图谱的四种节点类型",
                    "把建图拆成切块、抽属性、连边、过滤四种单一职责的积木，便于拼装与替换出不同管道",
                    "因为这四类必须严格按固定顺序执行，否则建图会出错",
                    "因为拆成四类后，建图就不再需要调用 LLM",
                ],
                "answer": 1,
                "why": "四类 transform 是四种单一职责的可组合积木；<code>default_transforms</code> 把它们按「切块 → 抽摘要 / 主题 / NER / embedding → 按相似度连边」拼成标准管道，<code>Parallel</code> 还能把同层变换并行分组。",
            },
            {
                "q": "<code>rollback_transforms</code> 当前直接抛 <code>NotImplementedError</code>，最贴切的解读是？",
                "opts": [
                    "说明回滚功能已被废弃、永不会实现",
                    "说明你调用的姿势不对",
                    "先占住「回滚」这个接口与语义位，但实现尚未完成——是显式的「保留接口、暂未实现」",
                    "说明缺了某个依赖没装上",
                ],
                "answer": 2,
                "why": "API 形状先定下来、占住位置，实现留待后续。这是一种「先声明意图」的占位，既不是废弃，也不是在指引你换调用方式或补依赖。",
            },
        ],
    },
    "28-persona-scenario.html": {
        "mcq": [
            {
                "q": "persona 为什么用 <code>generate_personas_from_kg</code> 从知识图谱自动生成，而不是让用户手填？",
                "opts": [
                    "personas 直接源自图谱里的真实内容，自动生成既贴合语料又省人工，提问视角更有据",
                    "因为手填的 persona 无法被序列化保存",
                    "因为 persona 必须和 LLM 来自同一家",
                    "因为自动生成 persona 能省 token",
                ],
                "answer": 0,
                "why": "<code>generate_personas_from_kg</code> 从知识图谱里「就地取材」造提问者：视角来自真实语料、不靠拍脑袋，也免去人工编写——「谁来问」这件事因此既贴题又省力。",
            },
            {
                "q": "<code>BaseScenario</code> = nodes + style（<code>QueryStyle</code>）+ length（<code>QueryLength</code>）+ persona，这样组合的目的是？",
                "opts": [
                    "因为这四个字段缺一个就无法存盘",
                    "因为风格和长度决定了该用哪个合成器出题",
                    "因为这样能减少图里的节点数量",
                    "用「谁问 × 什么风格 × 多长 × 基于哪些节点」的组合撑开测试集多样性，覆盖更多真实提问形态",
                ],
                "answer": 3,
                "why": "把节点、风格、长度、persona 四个维度组合起来，等于用一个笛卡尔积去覆盖各种真实提问形态；调节组合就能调节测试集的多样性与难度分布。",
            },
        ],
    },
    "29-synthesizers.html": {
        "mcq": [
            {
                "q": "出题为什么拆成 <code>generate_scenarios</code> → <code>generate_sample</code> 两步？",
                "opts": [
                    "因为一步生成问答会超出 LLM 的上下文窗口，必须拆开",
                    "因为拆成两步比一步更省 token",
                    "先定「考什么场景」，再落成具体样本；两步解耦让场景规划与样本生成各自可控、可复用",
                    "因为 scenario 和 sample 必须来自不同的模型",
                ],
                "answer": 2,
                "why": "<code>generate_scenarios</code> 先编排「用哪些节点、谁问、什么风格 / 长度」，<code>generate_sample</code> 再把场景写成真正的问答样本。解耦后可以先批量定场景、再统一生成，调试与复用都更灵活。",
            },
            {
                "q": "<code>default_query_distribution</code> 为什么要「过滤掉没有有效簇的合成器」？",
                "opts": [
                    "因为合成器太多会导致超时",
                    "多跳合成器需要图里有可连接的节点簇；图谱撑不起时先剔除，免得分了配额却出不出题",
                    "因为单跳合成器从来不会被用到",
                    "因为没有有效簇的合成器会直接抛异常中断整个出题流程",
                ],
                "answer": 1,
                "why": "它按概率给各题型（单跳 <code>SingleHopSpecific</code> vs 多跳 <code>MultiHopAbstract</code> / <code>Specific</code>）配比，但会先检查图能不能撑起该题型，撑不起的合成器直接过滤——避免「分了名额却生不出题」的空转。",
            },
        ],
    },
    "30-testset-generator.html": {
        "mcq": [
            {
                "q": "<code>generate</code> 为什么要复用 <code>Executor</code> + <code>new_group</code> 来「分阶段并发出题」？",
                "opts": [
                    "因为 <code>new_group</code> 会把多次 LLM 调用合并成一次，省钱",
                    "因为不借助 <code>Executor</code> 就建不出知识图谱",
                    "因为只有分阶段，<code>new_group</code> 才能把出题结果直接存进 backend",
                    "出题是大量独立的 LLM 调用，交给 <code>Executor</code> 并发提速、用 <code>new_group</code> 分阶段记录，直接复用评测线已有的调度与可观测能力",
                ],
                "answer": 3,
                "why": "<code>generate_with_langchain_docs</code> / <code>generate</code> 把 transforms → KG → personas → 分配 → 出题 串起来，其中出题是海量独立 LLM 调用，正好复用 <code>Executor</code> 并发与 <code>new_group</code> 分阶段 trace——两条线共用一套基础设施。",
            },
            {
                "q": "<code>Testset.to_evaluation_dataset()</code> 这一步的设计意义是？",
                "opts": [
                    "把「测试生成线」的产物一键转成评测线吃的数据集，让造好的题目直接回流去跑 evaluate / 实验，闭合两条线",
                    "因为 <code>Testset</code> 本身没法保存到磁盘",
                    "因为评测线只接受 CSV 格式",
                    "因为这样就能省去构建知识图谱的步骤",
                ],
                "answer": 0,
                "why": "它把生成出来的测试集转成 <code>EvaluationDataset</code>，直接喂给 <code>evaluate</code> / <code>@experiment</code>——测试生成线由此接回评测线，两大支柱在这里合龙。",
            },
        ],
        "open": [
            "你用 <code>generate_with_langchain_docs</code> 造好了一批测试集，准备 <code>to_evaluation_dataset()</code> 回到评测线。在正式拿它当「考卷」前，你会做哪些抽检来确认这批自动生成的题目值得信任？",
        ],
    },
    "31-experiments-deep.html": {
        "mcq": [
            {
                "q": "<code>@experiment</code> 的 <code>arun</code> 为什么用 <code>asyncio.as_completed</code> 并发跑每一行，而不是顺序逐行评测？",
                "opts": [
                    "每行评测都是独立的 IO 密集调用（等 LLM / 检索），并发能榨干等待时间、谁先完成先收谁",
                    "因为 <code>as_completed</code> 会自动跳过出错的行，让评测更稳",
                    "因为顺序执行会导致结果无法 <code>save</code> 落盘",
                    "因为 <code>asyncio.as_completed</code> 能保证按输入顺序返回结果",
                ],
                "answer": 0,
                "why": "<code>arun</code> 把每行的「调你的 RAG + 打分」包成协程，用 <code>asyncio.as_completed</code> 并发——这些任务大多在等 LLM / 检索返回，属 IO 密集，并发把等待时间利用起来；顺序跑只会白白空等。",
            },
            {
                "q": "<code>version_experiment</code> 为什么要用 git 给每次实验单独建一个 <code>ragas/{name}</code> 分支？",
                "opts": [
                    "因为建分支能让实验跑得更快",
                    "因为不建分支就解析不出 backend",
                    "给「这版代码跑出这版结果」拍不可变快照，可回溯、可对比，把「改→跑→比」闭成环",
                    "因为 git 是 ragas 唯一的存储后端",
                ],
                "answer": 2,
                "why": "把每次实验版本化成 <code>ragas/{name}</code> 分支，等于给代码与结果拍快照；日后随时切回任一版做对比，评测因此成为可复现、可迭代的闭环——这正是 experiments-first 的落点。",
            },
        ],
        "open": [
            "你给同一个 RAG 先后跑了 v1 / v2 两次 <code>@experiment</code>，分数互有高低。借助 <code>version_experiment</code> 的 git 分支，你会怎样组织这两次实验，才能既快速并排对比分数、又能随时切回任一版的代码与数据？",
        ],
    },
    "32-backends.html": {
        "mcq": [
            {
                "q": "ragas 让你用字符串 <code>'local/csv'</code> 选后端，而不是直接 import 具体后端类，好处是什么？",
                "opts": [
                    "因为同一个字符串在不同项目里会自动映射到不同的后端实现",
                    "解耦：调用方只依赖一个名字，<code>get_registry</code> 按名查找；换实现 / 加新后端都不必改用户代码",
                    "因为后端类的构造参数各家不同，用字符串能屏蔽这些差异、统一调用",
                    "因为 csv 是唯一被支持的后端",
                ],
                "answer": 1,
                "why": "<code>BaseBackend</code> 统一了 load / save 接口，<code>get_registry</code> 用字符串解析到具体实现；用户代码只写一个名字，背后换 csv / jsonl / 内存 / 网盘都无感——实现可换、可插。",
            },
            {
                "q": "第三方通过 pyproject 的 entry-points 注册自己的 backend，核心价值在哪？",
                "opts": [
                    "必须先 fork ragas 源码才能加后端",
                    "注册后会覆盖掉所有内置后端",
                    "entry-points 注册的后端只能在安装时使用一次，重启后失效",
                    "<code>pip install</code> 带 entry-point 的包后，注册表启动一扫即发现，无需改 ragas 一行即可即插即用",
                ],
                "answer": 3,
                "why": "entry-points 是标准插件发现机制：别人把后端打成包发布，你装上 ragas 就认得。对扩展开放、对修改封闭——这正是统一 <code>BaseBackend</code> 接口换来的红利。",
            },
        ],
    },
    "33-optimization-training.html": {
        "mcq": [
            {
                "q": "<code>MetricWithLLM.train</code> 为什么要从人工标注（<code>MetricAnnotation</code>）里学，而不是凭空优化？",
                "opts": [
                    "以人类判断为「金标准」对齐：优化指令 + 挑 few-shot 示例，让 LLM 裁判与人类打分的相关性更高",
                    "因为标注能直接微调底层 LLM 的权重，省去 prompt 工程",
                    "因为没有人工标注，<code>GeneticOptimizer</code> 就无法并行评估候选 prompt",
                    "因为标注只是用来让训练更快收敛",
                ],
                "answer": 0,
                "why": "<code>train</code> 拿人工标注当目标，去优化 prompt 指令、挑选 few-shot 示例，并用「与人类标注的相关性」衡量好坏——让 LLM 裁判一步步贴近人类判断，这才是优化指标的意义。",
            },
            {
                "q": "<code>train</code> 为什么按指标的 <code>output_type</code> 自动挑损失函数（BINARY→<code>BinaryMetricLoss</code>，连续 / 离散→<code>MSELoss</code>）？",
                "opts": [
                    "因为二分类指标的误差天然比连续指标大，必须用更重的 loss 压制",
                    "因为 <code>MSELoss</code> 只能反向传播梯度，离散指标没有梯度所以要换 loss",
                    "不同输出类型「错得有多离谱」的度量方式不同，选对 loss 才能给优化器正确的方向",
                    "因为选错 loss 会让 <code>DSPyOptimizer</code> 直接无法启动",
                ],
                "answer": 2,
                "why": "二分类的对 / 错与连续值的偏差，本质是两种误差度量；按 <code>output_type</code> 自动选 loss，<code>GeneticOptimizer</code>（默认）/ <code>DSPyOptimizer</code> 才能拿到合理的适应度信号，把指标往「更像人」推。",
            },
        ],
    },
    "34-integrations-frameworks.html": {
        "mcq": [
            {
                "q": "各框架集成为什么把它依赖的第三方库 import 下沉到各自子模块，而不在 <code>integrations</code> 包顶层统一导入？",
                "opts": [
                    "因为顶层 <code>__init__</code> 里写 import 会和子模块形成循环依赖",
                    "因为按子模块下沉能让每个集成自动选用各自最新版的依赖",
                    "「按插头分装」：缺某框架的依赖只断那一路集成，不会让整个 <code>integrations</code> 包 import 失败",
                    "因为各框架依赖之间一定会互相覆盖",
                ],
                "answer": 2,
                "why": "把 import 下沉到子模块，每个集成各管各的依赖——没装 <code>llama_index</code> 不影响你用 <code>langchain</code> 集成。可选能力按需加载，缺哪个插头只断哪一路，这与 backend 的可选导入一脉相承。",
            },
            {
                "q": "<code>TestsetGenerator.from_langchain</code> / <code>from_llama_index</code> 这类入口体现了什么设计意图？",
                "opts": [
                    "接住各框架的文档 / 对象，转成 ragas 能用的输入，让你在原有生态里平滑接入测试生成",
                    "强迫用户放弃原框架、把数据全部重写一遍",
                    "因为 ragas 只能读这两个框架的数据",
                    "因为不提供入口就根本无法生成测试集",
                ],
                "answer": 0,
                "why": "<code>from_langchain</code> / <code>from_llama_index</code> 把别家的文档对象「翻译」成 ragas 的输入——你不必离开熟悉的框架，集成层替你做适配，接入成本因此很低。",
            },
        ],
        "open": [
            "你的应用基于 LlamaIndex，同事的服务却用 LangGraph。结合 ragas 各集成「依赖各自下沉、互不拖累」的设计，你会怎样在一个仓库里同时评测这两套，又尽量避免依赖互相打架？",
        ],
    },
    "35-integrations-observability.html": {
        "mcq": [
            {
                "q": "把评测过程上报到 Langfuse / MLflow / LangSmith 这类观测平台，主要解决什么问题？",
                "opts": [
                    "把评测的打分逻辑外包给观测平台，本地不再计算指标",
                    "让每次评测的每一步可视化、可回溯，便于在生产级大盘上定位薄弱环节",
                    "自动把多次评测的分数合并成一个综合排行榜",
                    "让评测彻底离线、不留任何记录",
                ],
                "answer": 1,
                "why": "<code>observe</code> 把评测的调用链与分数上报到专业大盘，评测从「黑盒跑完给个数」变成「每步可视、可回溯」——这正是生产环境排查与监控所需要的。",
            },
            {
                "q": "ragas 同时适配 Langfuse / MLflow / LangSmith / Helicone / Opik 多家观测平台，为什么不锁定一家？",
                "opts": [
                    "因为每家平台只能上报一种指标",
                    "因为不同平台分别负责上报 token、成本和分数，缺一不可",
                    "团队各有既用的观测栈，多家适配让 ragas 融入现有工具链，而非逼人迁移",
                    "因为这些平台在技术上完全相同",
                ],
                "answer": 2,
                "why": "观测平台往往是团队既成事实；ragas 提供多家「插头」（如 <code>helicone_config</code> 在评测里启用 Helicone），谁用哪家接哪家，缺某家依赖也只影响那一路——融入生态而非强加平台。",
            },
        ],
    },
    "36-source-debug-contribute.html": {
        "mcq": [
            {
                "q": "ragas 的测试为什么大量用 <code>fake_llm</code> / <code>fake_embedding</code> fixture，而不真的调用 LLM？",
                "opts": [
                    "因为真实 LLM 的输出无法写进断言，pytest 没法判断对错",
                    "因为 fake fixtures 能顺便测出指标在真实场景下的准确率",
                    "因为这样才能测出底层 LLM 的真实质量",
                    "让指标测试确定、可复现且零成本——不受网络 / 计费 / 随机性影响，CI 才能稳定红绿",
                ],
                "answer": 3,
                "why": "真调 LLM 又慢、又花钱、又有随机性，测试会时红时绿。fake fixtures 给出可控的确定输出，把「指标逻辑对不对」稳稳验证下来，CI 不被外部因素干扰。",
            },
            {
                "q": "项目把 <code>make format</code> / <code>type</code> / <code>test</code> / <code>run-ci</code> 一键化，意图是什么？",
                "opts": [
                    "为了让本地和 CI 各跑一套不同的流程，互不干扰",
                    "统一开发动作、降低贡献门槛，本地与 CI 跑同一套流程，减少「我这能过、你那挂」",
                    "因为 <code>uv</code> 没法直接跑 <code>pytest</code>",
                    "因为只有 Makefile 才能安装依赖",
                ],
                "answer": 1,
                "why": "把格式化 / 类型 / 测试 / CI 收敛成几个 make 目标（环境用 <code>uv</code> 管，<code>make install-minimal</code> 起步），新人照着跑即可；本地与 CI 同一入口，最大限度避免「在我机器上是好的」。",
            },
        ],
    },
    "37-cli.html": {
        "mcq": [
            {
                "q": "你 <code>pip install</code> ragas 后就能直接敲 <code>ragas</code> 命令，这是怎么做到的？",
                "opts": [
                    "因为安装时 ragas 改写了你的 shell 配置文件",
                    "因为 <code>typer</code> 会自动扫描 <code>PATH</code> 找命令",
                    "pyproject 的 <code>[project.scripts]</code> 把 <code>ragas</code> 指向 <code>ragas.cli:app</code>，安装时自动生成可执行入口",
                    "因为必须手动 export 一个别名才行",
                ],
                "answer": 2,
                "why": "<code>[project.scripts]</code> 里 <code>ragas='ragas.cli:app'</code> 是标准的控制台脚本声明，pip / uv 据此生成 <code>ragas</code> 可执行文件——Python 打包体系提供的入口机制，无需用户手动配置。",
            },
            {
                "q": "CLI 选用 <code>typer</code> + <code>rich</code> 这套组合，主要图什么？",
                "opts": [
                    "因为 <code>rich</code> 负责解析命令行参数、<code>typer</code> 负责给输出上色",
                    "<code>typer</code> 靠类型注解声明命令 / 参数省样板，<code>rich</code> 把评测结果渲染成好读的表格——好写又好看",
                    "因为它们能把评测分数自动上传到观测平台",
                    "因为 <code>sdk.py</code> 必须靠它们才能运行",
                ],
                "answer": 1,
                "why": "<code>typer</code> 让定义 <code>quickstart</code> / <code>evals</code> / <code>hello_world</code> 几乎只靠函数签名，<code>rich</code> 把 <code>evals</code> 的分数渲染成清爽表格；一个管「好写」、一个管「好读」。（顺带：<code>sdk.py</code> 目前只是空占位，不影响 CLI。）",
            },
        ],
    },
    "38-capstone.html": {
        "mcq": [
            {
                "q": "把新版 <code>collections</code> 指标直接传给经典的 <code>evaluate()</code> 会怎样？为什么这么设计？",
                "opts": [
                    "正常运行，两代指标本就可以随意混用",
                    "会自动把它降级成旧版指标再跑",
                    "会静默跳过该指标、继续评测其余项",
                    "会抛 <code>TypeError</code>——<code>evaluate()</code> 只收旧版 <code>ragas.metrics</code> 指标，<code>collections</code> 指标应走 <code>@experiment</code> 直接 <code>ascore</code>",
                ],
                "answer": 3,
                "why": "两代指标各配入口：<code>collections</code> 指标在 <code>@experiment</code> 里直接 <code>ascore</code>，<code>evaluate()</code> 只认旧版 <code>ragas.metrics</code> 指标；混用因类型不匹配抛 <code>TypeError</code>。「指标配对的入口」是端到端不踩坑的关键。",
            },
            {
                "q": "capstone 的链路 <code>TestsetGenerator</code> → <code>to_evaluation_dataset</code> → 选指标 → <code>@experiment</code>，体现了全书怎样的主线？",
                "opts": [
                    "测试生成与评测是两条永不相交的平行线",
                    "造题线产出经 <code>to_evaluation_dataset</code> 接回评测线，再用实验跑分对比迭代，两大支柱在此合龙闭环",
                    "只有纯手工写的数据集才能拿去评测",
                    "<code>@experiment</code> 其实只用于生成测试集",
                ],
                "answer": 1,
                "why": "<code>to_evaluation_dataset</code> 是「测试生成线」与「评测线」的接口：造好题→转评测集→选 <code>collections</code> 指标→<code>@experiment</code> 跑并对比，正是全书「改→跑→比」闭环的完整落地。",
            },
        ],
        "open": [
            "为你自己的一个 LLM 应用规划一条 capstone 流水线：从 <code>TestsetGenerator</code> 造题到 <code>@experiment</code> 对比迭代，逐步列出每步用什么，并特别说明你会怎样避免把 <code>collections</code> 指标误传给 <code>evaluate()</code> 这类「入口配错」的坑。",
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
