
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any


def ensure_dirs(runs_dir: Path) -> Dict[str, Path]:
    traces_dir = runs_dir / "traces"
    reports_dir = runs_dir / "reports"
    traces_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return {"traces": traces_dir, "reports": reports_dir}


def save_trace_and_report(
    runs_dir: Path,
    trace_id: str,
    payload: Dict[str, Any],
) -> Dict[str, str]:
   
    d = ensure_dirs(runs_dir)
    trace_path = d["traces"] / f"{trace_id}.json"
    md_path = d["reports"] / f"{trace_id}.md"

    # 1) json trace
    trace_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2) md report
    final_answer = payload.get("final_answer", "")
    plan = payload.get("plan", {})
    steps = plan.get("steps", [])
    goal = plan.get("goal", payload.get("goal", ""))

  
    outputs = payload.get("outputs", {})
    caption = ""
    if isinstance(outputs, dict):
        cap = outputs.get("caption", {})
        if isinstance(cap, dict):
            caption = cap.get("answer", "")

    lines = []
    lines.append(f"# Vision Analyst Report\n")
    if goal:
        lines.append(f"## Goal\n- {goal}\n")
    if steps:
        lines.append("## Plan\n")
        for i, s in enumerate(steps, start=1):
            lines.append(f"{i}. {s}\n")
        lines.append("\n")

    if caption:
        lines.append("## Caption\n")
        lines.append(f"- {caption}\n\n")

    lines.append("## Final Answer\n")
    lines.append(final_answer if final_answer else "(empty)\n")
    lines.append("\n")

    # trace 摘要
    trace_obj = payload.get("trace", {})
    if isinstance(trace_obj, dict):
        tool_calls = trace_obj.get("tool_calls", [])
        if tool_calls:
            lines.append("## Trace (tool calls)\n")
            for tc in tool_calls:
                tool = tc.get("tool", "tool")
                ok = tc.get("ok", True)
                err = tc.get("error", None)
                lines.append(f"- **{tool}** ok={ok} err={err}\n")
            lines.append("\n")

    md_path.write_text("".join(lines), encoding="utf-8")

    return {"trace_json": str(trace_path), "report_md": str(md_path)}
