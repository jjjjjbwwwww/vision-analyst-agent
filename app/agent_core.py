from __future__ import annotations

import json
import time
import hashlib
from typing import Dict, Any, List, Optional

import httpx


TEST6_BASE = "http://127.0.0.1:8006"


def _now_trace_id() -> str:
    ts = time.strftime("%Y%m%d_%H%M%S")
    rnd = hashlib.md5(str(time.time()).encode("utf-8")).hexdigest()[:8]
    return f"trace_{ts}_{rnd}"


async def _post_multipart_json(
    url: str,
    img_bytes: bytes,
    filename: str,
    fields: Dict[str, str],
    timeout_s: float = 120.0,
) -> Dict[str, Any]:
    """
    用 multipart/form-data 调用 test6 的 /vqa 或 /vqa_batch
    """
    files = {"image": (filename, img_bytes, "image/jpeg")}
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        r = await client.post(url, data=fields, files=files)
    # 502/500 也把 body 带回来，方便你定位
    ct = r.headers.get("content-type", "")
    body = r.text if r.text else ""
    if r.status_code != 200:
        raise RuntimeError(f"Upstream error: url={url} status={r.status_code} content_type={ct} body={body[:500]}")
    try:
        return r.json()
    except Exception:
        raise RuntimeError(f"Upstream JSON decode failed: url={url} content_type={ct} body={body[:500]}")


def _build_plan(goal: str) -> Dict[str, Any]:
    """
    不同 goal -> 不同 steps/questions/why

    """
    g = (goal or "").strip().lower()

    # 简单意图分类
    want_ocr = any(k in g for k in ["文字", "ocr", "text", "logo", "标志", "招牌"])
    want_count = any(k in g for k in ["多少", "几个", "数量", "how many", "count"])
    want_object = any(k in g for k in ["是什么", "what is", "main object", "主体", "物体", "objects"])
    want_scene = any(k in g for k in ["场景", "哪里", "room", "indoor", "outdoor", "environment"])

    steps: List[Dict[str, Any]] = []

    
    steps.append({
        "title": "一句话概括",
        "why": "先用一句话抓住全局，降低后续问答偏题风险。",
        "questions": [
            "What is shown in the image? Answer in one short sentence."
        ]
    })

   
    if want_scene or (not want_object and not want_ocr and not want_count):
        steps.append({
            "title": "场景分析",
            "why": "用户目标可能需要环境信息（室内/室外、房间类型），用于组织更准确的总结。",
            "questions": [
                "Is this indoor or outdoor?",
                "What room or place is this?",
                "Describe the environment briefly."
            ]
        })

    
    if want_object or True:
        steps.append({
            "title": "主体与关键物体",
            "why": "明确主要物体与关键细节，回答“是什么/有什么”的核心问题。",
            "questions": [
                "What is the main object in the image?",
                "List three important objects you can see.",
                "Describe one notable detail (color/material/position)."
            ]
        })

   
    if want_ocr:
        steps.append({
            "title": "文字与标志",
            "why": "当用户关注文字/标志时，优先提问可见文本与 logo 信息。",
            "questions": [
                "Is there any visible text, sign, or logo? If yes, what does it say?"
            ]
        })

    
    if want_count:
        steps.append({
            "title": "数量估计",
            "why": "用户明确要数量时，单独提问能减少模型在总结时遗漏数字。",
            "questions": [
                "How many main objects are visible? Give the best estimate."
            ]
        })

    return {
        "goal": goal.strip(),
        "steps": steps
    }


def _format_final_answer(goal: str, caption: str, qa_blocks: List[Dict[str, Any]]) -> str:
    
    lines: List[str] = []
    lines.append(f"Goal: {goal}")
    lines.append(f"Caption: {caption}")
    lines.append("")
    lines.append("Key Q&A:")
    q_idx = 1
    for blk in qa_blocks:
        for qa in blk.get("qas", []):
            q = qa.get("q", "")
            a = qa.get("a", "")
            lines.append(f"  Q{q_idx}. {q}")
            lines.append(f"      A: {a}")
            q_idx += 1

    # Summary
    lines.append("")
    lines.append("Summary:")
    # 从已有答案里抽几个关键字段
    scene = ""
    main_obj = ""
    details = ""
    for blk in qa_blocks:
        for qa in blk.get("qas", []):
            q = (qa.get("q", "") or "").lower()
            a = (qa.get("a", "") or "").strip()
            if "indoor" in q or "outdoor" in q:
                scene = a
            if "room" in q or "place" in q:
                if a:
                    scene = (scene + " / " + a).strip(" /")
            if "main object" in q:
                main_obj = a
            if "three important objects" in q or "important objects" in q:
                details = a

    if not scene:
        scene = "unknown"
    if not main_obj:
        main_obj = "unknown"
    if not details:
        details = "unknown"

    lines.append(f"- Scene: {scene}")
    lines.append(f"- Main object: {main_obj}")
    lines.append(f"- Details: {details}")

    return "\n".join(lines)


async def run_agent_a(
    img_bytes: bytes,
    filename: str,
    goal: str,
    session_id: str = "default",
    offline: str = "true",
    max_new_tokens: str = "40",
    model_dir: Optional[str] = None,  # 允许你传本地模型目录
) -> Dict[str, Any]:
    """
     最小 Executor：
    """
    trace_id = _now_trace_id()

    plan = _build_plan(goal)

    question_trace: List[Dict[str, Any]] = []
    qa_blocks: List[Dict[str, Any]] = []

    # 1) Caption
    cap_q = plan["steps"][0]["questions"][0]
    fields_vqa = {
        "question": cap_q,
        "offline": str(offline).lower(),
        "max_new_tokens": str(max_new_tokens),
    }
    if model_dir:
        fields_vqa["model_dir"] = model_dir

    cap_out = await _post_multipart_json(
        TEST6_BASE + "/vqa",
        img_bytes=img_bytes,
        filename=filename,
        fields=fields_vqa,
    )
    caption = (cap_out.get("answer") or "").strip()

    # 记录 caption step trace
    question_trace.append({
        "title": plan["steps"][0]["title"],
        "why": plan["steps"][0]["why"],
        "questions": plan["steps"][0]["questions"],
        "answers": [{"q": cap_q, "a": caption}],
    })
    qa_blocks.append({
        "title": plan["steps"][0]["title"],
        "qas": [{"q": cap_q, "a": caption}],
    })

    # 2) 其余 steps -> /vqa_batch
    for step in plan["steps"][1:]:
        qs = step.get("questions", [])
        if not qs:
            continue

        fields_batch = {
            "questions_json": json.dumps(qs, ensure_ascii=False),
            "offline": str(offline).lower(),
            "max_new_tokens": str(max_new_tokens),
        }
        if model_dir:
            fields_batch["model_dir"] = model_dir

        batch_out = await _post_multipart_json(
            TEST6_BASE + "/vqa_batch",
            img_bytes=img_bytes,
            filename=filename,
            fields=fields_batch,
        )

        results = batch_out.get("results", [])
        # results: [{"question":..., "answer":...}, ...]
        qas = [{"q": r.get("question", ""), "a": r.get("answer", "")} for r in results]

        question_trace.append({
            "title": step.get("title", ""),
            "why": step.get("why", ""),
            "questions": qs,
            "answers": qas,
        })
        qa_blocks.append({
            "title": step.get("title", ""),
            "qas": qas,
        })

    final_answer = _format_final_answer(goal, caption, qa_blocks)

   
    raw = {
        "trace_id": trace_id,
        "plan": plan,
        "outputs": {
            "caption": cap_out,
            # 不强行塞每个 batch 的原始 output
        },
        "trace": {
            "question_trace": question_trace
        }
    }

    return {
        "trace_id": trace_id,
        "plan": plan,                 
        "final_answer": final_answer, 
        "summary": {                  # 可选：给 UI 单独展示
            "caption": caption
        },
        "raw": raw                    
    }
