"""NL2SQL 数据分析 Agent（基于 LangGraph + 智谱 GLM）。

用户用自然语言提问，Agent 生成 SQL -> 执行只读查询 -> 用自然语言回答，
同时返回它生成的 SQL 和查询结果，供前端展示。

对外接口：answer_question(question) -> dict{answer, sql, data}
"""
import json
import os
import sys
import uuid

# 保证能 import 项目根目录下的 config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from pymysql import connect  # noqa: E402

from langchain_openai import ChatOpenAI  # noqa: E402
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage  # noqa: E402
from langchain_core.tools import tool  # noqa: E402
from langgraph.prebuilt import create_react_agent  # noqa: E402
from langgraph.checkpoint.memory import MemorySaver  # noqa: E402

MAX_ROWS = 200

# 危险关键字，防止模型生成非只读语句
_FORBIDDEN = (
    "insert", "update", "delete", "drop", "alter", "create", "truncate",
    "rename", "replace", "grant", "revoke", "call", "load", "lock",
    "unlock", "into outfile", "into dumpfile",
)


def _fetch_types():
    """读取 cases 表的全部疾病类型，用于拼进 system prompt，帮助模型精确匹配。"""
    try:
        conn = connect(
            host=config.DB_HOST, user=config.DB_USER,
            password=config.DB_PASSWORD, database=config.DB_NAME,
            port=config.DB_PORT, charset=config.DB_CHARSET,
        )
        try:
            cur = conn.cursor()
            cur.execute("select distinct type from cases")
            return [r[0] for r in cur.fetchall()]
        finally:
            conn.close()
    except Exception:
        return []


def _run_sql(sql: str) -> str:
    """在 medicalinfo 库上执行只读 SQL，返回 JSON 字符串。"""
    s = " ".join(sql.strip().strip(";").split())
    lowered = s.lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        return json.dumps({"error": "只允许执行只读的 SELECT 查询"}, ensure_ascii=False)
    for kw in _FORBIDDEN:
        if kw in lowered:
            return json.dumps({"error": f"检测到禁止的关键字 {kw}"}, ensure_ascii=False)

    conn = connect(
        host=config.DB_HOST, user=config.DB_USER,
        password=config.DB_PASSWORD, database=config.DB_NAME,
        port=config.DB_PORT, charset=config.DB_CHARSET,
    )
    try:
        cur = conn.cursor()
        cur.execute(s)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        rows = [list(r) for r in rows[:MAX_ROWS]]
        return json.dumps(
            {"columns": columns, "rows": rows, "row_count": len(rows)},
            ensure_ascii=False, default=str,
        )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    finally:
        conn.close()


@tool
def run_sql(sql: str) -> str:
    """在 MySQL 数据库 medicalinfo 上执行一条只读 SQL（只能 SELECT），返回 JSON。

    表 cases 结构（医疗病例，共 14 列）：
      id:int, type:疾病类型, gender:性别(男/女), age:年龄(文本数字),
      time:就诊时间, content:病情描述, docName:医生, docHospital:医院,
      department:科室, detailUrl:详情链接, height:身高(文本数字或'无'),
      weight:体重(文本数字或'无'), illDuration:患病时长, allergy:过敏史

    注意：age/height/weight 都是文本类型，做数值比较时用 CAST(age AS UNSIGNED)、
    CAST(height AS DECIMAL(10,2))。type 字段必须精确匹配，用 LIKE '%高血压%' 可模糊匹配。
    聚合查询尽量返回精简结果。
    """
    return _run_sql(sql)


@tool
def predict_disease(content: str) -> str:
    """根据病情/症状描述预测可能的疾病类型，返回 JSON。

    参数 content: 用户的病情或症状描述，例如"咳嗽、发烧两天了"。
    用于用户想根据症状判断可能患什么病时。结果仅供参考，不构成医疗诊断。
    """
    try:
        from machine.tree import predict_with_proba
        top = predict_with_proba(content, k=3)
        return json.dumps(
            {"description": content,
             "predictions": [{"disease": d, "prob": p} for d, p in top]},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _build_prompt() -> str:
    types = _fetch_types()
    type_list = "、".join(types) if types else "（读取失败，可用 select distinct type from cases 查询）"
    return f"""你是一个医疗数据分析助手，既能查询 MySQL 数据库 medicalinfo 中的 cases 表做统计分析，也能根据病情描述预测可能的疾病。

数据库里共有 {len(types) if types else '?'} 类疾病：{type_list}

你有两个工具：
1. run_sql —— 查询数据库（只读 SELECT），用于统计分析类问题，如"高血压有多少人""哪个科室最多"。
2. predict_disease —— 根据病情/症状描述预测可能的疾病，用于"我咳嗽发烧可能是啥病"这类问题。

回答要求：
1. 先判断问题类型：统计/查询数据用 run_sql，病情预测用 predict_disease；必要时可同时使用两个工具。
2. 先用工具获取真实结果再回答，不要凭空编造数字。
3. age / height / weight 是文本字段，数值比较必须用 CAST（例如 CAST(age AS UNSIGNED) BETWEEN 40 AND 50）。
4. type 精确匹配，若用户说的疾病名不确定，用 LIKE。
5. 病情预测的结果必须说明"仅供参考，不构成医疗诊断"。
6. 回答用简洁中文，先给结论，再列出关键数字。
7. 如果工具调用出错，检查参数并重试一次。
8. 用户可能连续追问，回答时结合之前的对话上下文（例如"再按科室分组"要基于上一轮结果）。"""


_agent = None


def _get_agent():
    global _agent
    if _agent is None:
        if not config.ZHIPU_API_KEY:
            raise RuntimeError("未配置 ZHIPU_API_KEY，请在 .env 文件中填入智谱 API Key")
        llm = ChatOpenAI(
            model=config.ZHIPU_MODEL,
            api_key=config.ZHIPU_API_KEY,
            base_url=config.ZHIPU_BASE_URL,
            temperature=0,
            extra_body={"thinking": {"type": "disabled"}},
        )
        _agent = create_react_agent(
            llm, [run_sql, predict_disease], prompt=_build_prompt(),
            checkpointer=MemorySaver(),
        )
    return _agent


def _extract(result: dict):
    """从 LangGraph 结果里抽取最终回答、执行的 SQL、查询数据、预测结果。"""
    answer = ""
    sql = ""
    data = None
    prediction = None
    tool_names = {}  # tool_call_id -> 工具名
    for m in result.get("messages", []):
        if isinstance(m, AIMessage):
            if m.content:
                answer = m.content
            for tc in getattr(m, "tool_calls", None) or []:
                name = tc.get("name")
                tid = tc.get("id")
                if tid and name:
                    tool_names[tid] = name
                if name == "run_sql":
                    sql = (tc.get("args") or {}).get("sql", "")
        elif isinstance(m, ToolMessage):
            name = tool_names.get(getattr(m, "tool_call_id", None)) or getattr(m, "name", "")
            try:
                parsed = json.loads(m.content)
            except Exception:
                parsed = m.content
            if name == "predict_disease":
                prediction = parsed
            else:
                data = parsed
    return answer, sql, data, prediction


def _clean_answer(text: str) -> str:
    """去掉思考模型可能残留的 </think> 标记与重复内容。"""
    if not text:
        return text
    text = text.strip()
    if "</think>" in text:
        text = text.split("</think>")[-1].strip()
    text = text.replace("<｜end▁of▁thinking｜>", "").replace("</think>", "")
    return text.strip()


def _make_config(thread_id):
    return {"configurable": {"thread_id": thread_id or uuid.uuid4().hex}}


def _prev_message_count(agent, config) -> int:
    """返回本轮开始前已存在的消息条数，用于把本轮新增消息与历史消息区分开。"""
    if not config:
        return 0
    try:
        snap = agent.get_state(config)
        if snap and snap.values:
            return len(snap.values.get("messages", []))
    except Exception:
        pass
    return 0


def answer_question(question: str, thread_id: str = None) -> dict:
    """非流式回答（保留用于测试/向后兼容），同样支持多轮记忆。"""
    agent = _get_agent()
    config = _make_config(thread_id)
    prev_count = _prev_message_count(agent, config)
    result = agent.invoke({"messages": [("user", question)]}, config=config)
    new_messages = result.get("messages", [])[prev_count:]
    answer, sql, data, prediction = _extract({"messages": new_messages})
    return {"answer": _clean_answer(answer), "sql": sql, "data": data, "prediction": prediction}


def stream_answer(question: str, thread_id: str = None):
    """流式回答：逐 token 产出，最后产出 done 事件（含完整结构化结果）。

    产出 dict 事件：
      {"type": "token", "content": "..."}                         增量回答文本
      {"type": "done", "answer":..., "sql":..., "data":...}      最终结果
    """
    agent = _get_agent()
    config = _make_config(thread_id)
    prev_count = _prev_message_count(agent, config)
    final_state = None
    for mode, data in agent.stream(
        {"messages": [("user", question)]},
        config=config,
        stream_mode=["messages", "values"],
    ):
        if mode == "messages":
            chunk, _meta = data
            if isinstance(chunk, AIMessageChunk):
                content = chunk.content
                if isinstance(content, str) and content:
                    yield {"type": "token", "content": content}
        elif mode == "values":
            final_state = data
    if final_state is not None:
        new_messages = final_state.get("messages", [])[prev_count:]
        answer, sql, data_out, prediction = _extract({"messages": new_messages})
        yield {"type": "done", "answer": _clean_answer(answer), "sql": sql, "data": data_out, "prediction": prediction}
