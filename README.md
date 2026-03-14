# Vision Analyst Agent (Project 3)
> Goal-aware planning + traceable questioning for multimodal image analysis  
> 端口：test6=8006, test7=8007, analyst_api=8010

---

## 中文简介
这是一个“目标驱动 (goal-aware)”的视觉分析 Agent：  
用户上传图片并给出目标（goal），Agent 会**自动生成计划（Plan）**，并按计划调用多模态问答模型（test6/test7）完成**多轮提问**，最终输出结构化报告。同时，它会保存 **Trace（可复现/可调试）**：记录每一步为什么问、问了什么、模型怎么答、最终怎么汇总。

### 项目 3 相比项目 2 的升级点
- ✅ **Plan 不再是固定 4 步**：不同 goal → 自动选择不同问题路径  
- ✅ Trace 里提供 **question_trace**：能解释“为什么问这些问题”以及每一步的问答结果  
- ✅ UI 展示完整链路：Plan（title/why/questions） + Trace（why + Q&A） + 最终报告  
- ✅ 方便 Debug：每次请求生成 trace_id，并落盘保存 json / md

---

## Architecture（文字版架构图）
User(UI) → (8010) Vision Analyst API (/analyze)
  → Agent Core (goal-aware planner + trace recorder)
     → calls upstream test7 (/agent/run or /agent/chat, 8007)
        → calls upstream test6 BLIP VQA (/vqa, /vqa_batch, 8006)
  ← returns {plan, final_answer, trace_id, raw.trace.question_trace}

---

## Requirements
- Windows 10/11
- Python 3.10+
- 已完成并在本机可用：
  - test6（BLIP VQA service） running at `http://127.0.0.1:8006`
  - test7（Agent service） running at `http://127.0.0.1:8007`
- 本项目（Project3）运行在 `http://127.0.0.1:8010`

---

## Installation
```bash
conda activate torch
pip install -r requirements.txt
Run (recommended: one-click scripts)
Option A: 手动启动
启动 test6（端口 8006）

python -m uvicorn app:app --host 127.0.0.1 --port 8006
启动 test7（端口 8007）

uvicorn api:app --host 127.0.0.1 --port 8007
启动本项目（端口 8010）

uvicorn app.analyst_api:app --host 127.0.0.1 --port 8010
打开 UI

访问：http://127.0.0.1:8010/ui.html

API
POST /analyze
multipart/form-data

image: image file (required)

goal: string (required)

session_id: string (optional, default: "default")

offline: "true" / "false" (optional, default: "true")

max_new_tokens: int as string (optional, default: "40")

Response

{
  "ok": true,
  "trace_id": "trace_...",
  "session_id": "default",
  "plan": {
    "goal": "...",
    "steps": [
      {
        "title": "场景分析",
        "why": "解释为什么问这类问题",
        "questions": ["...","..."]
      }
    ]
  },
  "final_answer": "..."
}
UI
UI 页面会展示：

左侧：历史轮次（Q1/Q2/Q3…），当前轮高亮

中间：多轮对话 + 最终报告

右侧：📋 Agent Plan（title/why/questions）

Trace 区：展示 question_trace（每一步 “为什么问 + 提问 + 回答”）

Trace & Reproducibility
每次 /analyze 会保存：

runs/traces/<trace_id>.json

runs/reports/<trace_id>.md

Trace 关键字段：

plan.steps[]: title/why/questions（结构化计划）

raw.trace.question_trace[]: why + questions + answers（可解释决策链路）

Common Issues
502 Upstream error
通常是：

test6/test7 没启动

开启了系统代理导致本地转发失败（你已验证：关闭代理恢复正常）

422 Unprocessable Entity
通常是 UI 请求体字段与 /analyze 的 form-data 参数不匹配。
确保字段名是：image / goal / session_id / offline / max_new_tokens

English README (short)
Vision Analyst Agent (Project 3)
A goal-aware multimodal agent that generates a structured plan and a traceable question chain (question_trace) for image analysis.
It calls upstream services: test7 (agent) → test6 (BLIP VQA).
The UI shows plan + trace + final report for reproducibility and debugging.

Run: test6:8006, test7:8007, this project:8010, UI: /ui.html

