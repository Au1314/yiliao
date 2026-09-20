"""对 NL2SQL Agent 的回答与查询结果做后处理，供前端展示。

对外接口：
- process_result(answer, data) -> dict{answer_html, chart, summary}

内部：
- md_to_html: 把 LLM 输出的 markdown 转成安全 HTML（先转义，只产出白名单标签，防 XSS）
- build_chart: 根据查询结果（columns/rows）自动生成 ECharts 配置（饼图/柱状图）
- build_summary: 从查询结果抽取关键数字，生成结构化摘要卡片
"""
import html
import re


# ---------------------------------------------------------------- markdown

_INLINE_CODE = re.compile(r'`([^`]+)`')


def _inline(text: str) -> str:
    """处理行内 markdown（文本已 HTML 转义）。"""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    text = _INLINE_CODE.sub(r'<code>\1</code>', text)
    return text


def md_to_html(text: str) -> str:
    """把 markdown 文本转成安全 HTML。先整体转义，只允许标题/加粗/斜体/
    列表/引用/代码等白名单结构，因此不会引入 script 等危险标签。"""
    if not text:
        return ""
    text = html.escape(text)
    lines = text.split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        stripped = lines[i].strip()

        # 代码块 ``` ... ```
        if stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结尾 ```
            out.append("<pre><code>" + "\n".join(code_lines) + "</code></pre>")
            continue

        if not stripped:
            i += 1
            continue

        # 标题
        m = re.match(r'^(#{1,6})\s+(.*)$', stripped)
        if m:
            lv = len(m.group(1))
            out.append(f"<h{lv}>{_inline(m.group(2))}</h{lv}>")
            i += 1
            continue

        # 分隔线
        if re.fullmatch(r'(-{3,}|\*{3,}|_{3,})', stripped):
            out.append("<hr/>")
            i += 1
            continue

        # 引用
        if stripped.startswith(">"):
            out.append("<blockquote>" + _inline(stripped.lstrip("> ")) + "</blockquote>")
            i += 1
            continue

        # 无序列表
        if re.match(r'^[-*+]\s+', stripped):
            items = []
            while i < n and re.match(r'^[-*+]\s+', lines[i].strip()):
                items.append("<li>" + _inline(re.sub(r'^[-*+]\s+', '', lines[i].strip())) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue

        # 有序列表
        if re.match(r'^\d+[.)]\s+', stripped):
            items = []
            while i < n and re.match(r'^\d+[.)]\s+', lines[i].strip()):
                items.append("<li>" + _inline(re.sub(r'^\d+[.)]\s+', '', lines[i].strip())) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue

        # 普通段落行
        out.append("<p>" + _inline(stripped) + "</p>")
        i += 1
    return "".join(out)


# ---------------------------------------------------------------- 数值判断

def _to_number(v):
    """安全地把值转成 float，无法转换返回 None。"""
    if v is None:
        return None
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(",", "")
    if not s or s in ("无", "None", "null", "NULL", "-", "—"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _is_numeric_col(values) -> bool:
    vals = [v for v in values if v is not None and str(v).strip() != ""]
    if not vals:
        return False
    num = sum(1 for v in vals if _to_number(v) is not None)
    return num / len(vals) >= 0.8


def _fmt(v):
    if v is None:
        return ""
    f = float(v)
    return str(int(f)) if f.is_integer() else f"{f:.2f}"


# ---------------------------------------------------------------- 自动出图

def build_chart(columns, rows):
    """根据查询结果自动生成 ECharts 配置。仅处理简单的聚合结果：
    - 1 个数值列 + 1 个分类列 -> 柱状图（类目多）或饼图（类目少）
    其余情况返回 None（前端只显示表格）。"""
    if not columns or not rows:
        return None
    ncol = len(columns)
    col_values = [[r[i] if i < len(r) else None for r in rows] for i in range(ncol)]
    numeric_flags = [_is_numeric_col(cv) for cv in col_values]
    if sum(numeric_flags) != 1:
        return None
    cat_indices = [i for i in range(ncol) if not numeric_flags[i]]
    if not cat_indices:
        return None

    val_i = numeric_flags.index(True)
    cat_i = cat_indices[0]
    cats = [str(r[cat_i]) for r in rows]
    vals = []
    for r in rows:
        v = _to_number(r[val_i])
        vals.append(int(v) if v is not None and float(v).is_integer() else (v if v is not None else 0))

    MAX_CAT = 30
    if len(cats) > MAX_CAT:
        cats = cats[:MAX_CAT]
        vals = vals[:MAX_CAT]

    title = f"{columns[cat_i]} 分布"
    axis_label = {"color": "#d3dcf7"}
    if len(cats) <= 8:
        return {
            "type": "pie",
            "title": title,
            "option": {
                "tooltip": {"trigger": "item"},
                "legend": {"orient": "vertical", "left": "right",
                           "textStyle": {"color": "#d3dcf7"}},
                "series": [{
                    "name": columns[cat_i], "type": "pie", "radius": "62%",
                    "center": ["40%", "50%"],
                    "data": [{"name": c, "value": v} for c, v in zip(cats, vals)],
                    "label": {"color": "#d3dcf7"},
                }],
            },
        }
    return {
        "type": "bar",
        "title": title,
        "option": {
            "tooltip": {"trigger": "axis"},
            "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
            "xAxis": {"type": "category", "data": cats,
                      "axisLabel": {**axis_label, "rotate": 30, "interval": 0}},
            "yAxis": {"type": "value", "axisLabel": axis_label},
            "series": [{
                "name": columns[val_i], "type": "bar", "data": vals,
                "itemStyle": {"color": "#26fffd"},
                "barMaxWidth": 32,
            }],
        },
    }


# ---------------------------------------------------------------- 结构化摘要

def build_summary(columns, rows):
    """从查询结果抽取关键数字，生成结构化摘要卡片 [{label, value}]。"""
    if not columns or not rows:
        return None
    ncol = len(columns)
    col_values = [[r[i] if i < len(r) else None for r in rows] for i in range(ncol)]
    numeric_flags = [_is_numeric_col(cv) for cv in col_values]

    # 单数值单行 -> 单个 KPI 数字
    if ncol == 1 and numeric_flags[0] and len(rows) == 1:
        return [{"label": columns[0], "value": _fmt(rows[0][0])}]

    # 1 数值列 + 1 分类列
    if ncol == 2 and sum(numeric_flags) == 1:
        val_i = numeric_flags.index(True)
        cat_i = 1 - val_i
        pairs = [(str(r[cat_i]), _to_number(r[val_i])) for r in rows]
        pairs = [(c, v) for c, v in pairs if v is not None]
        if not pairs:
            return None
        items = []
        max_c, max_v = max(pairs, key=lambda x: x[1])
        items.append({"label": "最多", "value": f"{max_c}（{_fmt(max_v)}）"})
        if len(pairs) > 1 and all(v is not None and float(v).is_integer() for _, v in pairs):
            items.append({"label": "合计", "value": _fmt(int(sum(v for _, v in pairs)))})
        return items
    return None


# ---------------------------------------------------------------- 统一入口

def process_result(answer, data) -> dict:
    """把 Agent 的原始回答与查询结果加工成前端可展示的结构。"""
    columns, rows = [], []
    if isinstance(data, dict):
        columns = data.get("columns") or []
        rows = data.get("rows") or []
    return {
        "answer_html": md_to_html(answer or ""),
        "chart": build_chart(columns, rows),
        "summary": build_summary(columns, rows),
    }
