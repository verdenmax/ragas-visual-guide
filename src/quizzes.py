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

QUIZZES = {}


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
