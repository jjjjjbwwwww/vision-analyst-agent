
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List

import httpx
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.agent_core import run_agent_a


# =========================
# Config
# =========================
APP_TITLE = "Vision Analyst Agent"
APP_PORT = 8010

# 你的上游 test7（Agent）地址
TEST7_BASE = "http://127.0.0.1:8007"
TEST7_CHAT_PATH = "/agent/chat"
TEST7_RUN_PATH = "/agent/run"

# 默认会话
DEFAULT_SESSION_ID = "default"

# =========================
# Paths
# =========================
# 重要：此文件在 vision_analyst_agent/app/ 下
# 项目根目录 = parent.parent
ROOT_DIR = Path(__file__).resolve().parent.parent
UI_DIR = ROOT_DIR / "ui"
UI_FILE_AT_ROOT = ROOT_DIR / "ui.html"          # 如果你放在根目录
UI_FILE_IN_UI_DIR = UI_DIR / "ui.html"          # 如果你放在 ui/ 目录


# =========================
# App
# =========================
app = FastAPI(title=APP_TITLE)


# =========================
# Helpers
# =========================
def now_trace_id() -> str:
    return "trace_" + time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]


def pick_ui_file() -> Optional[Path]:
    """
    支持两种放置方式：
    1) ROOT/ui.html
    2) ROOT/ui/ui.html
    """
    if UI_FILE_IN_UI_DIR.exists():
        return UI_FILE_IN_UI_DIR
    if UI_FILE_AT_ROOT.exists():
        return UI_FILE_AT_ROOT
    return None


async def post_multipart(
    url: str,
    image_bytes: bytes,
    image_filename: str,
    fields: Dict[str, str],
    timeout_s: float = 120.0,
) -> Dict[str, Any]:
    """
    以 multipart/form-data 方式转发到上游。
    这会避免 json 编码/转义问题，也是 test6/test7 常用的方式。
    """
    files = {
        "image": (image_filename, image_bytes, "image/jpeg"),
    }
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        r = await client.post(url, data=fields, files=files)

    ct = r.headers.get("content-type", "")
    text = r.text if r.text is not None else ""

    if r.status_code >= 400:
        # 把关键信息都带回来，便于你定位（包括空 body 的情况）
        raise RuntimeError(
            f"Upstream error: url={url} status={r.status_code} content_type={ct} body={text[:800]}"
        )

    # 尽量按 JSON 解析；解析失败也要报清楚
    try:
        return r.json()
    except Exception as e:
        raise RuntimeError(f"Upstream returned non-JSON: url={url} ct={ct} body={text[:800]} err={e}")


async def post_json(url: str, payload: Dict[str, Any], timeout_s: float = 120.0) -> Dict[str, Any]:
    async with httpx.AsyncClient(timeout=timeout_s) as client:
        r = await client.post(url, json=payload)

    ct = r.headers.get("content-type", "")
    text = r.text if r.text is not None else ""
    if r.status_code >= 400:
        raise RuntimeError(
            f"Upstream error: url={url} status={r.status_code} content_type={ct} body={text[:800]}"
        )
    try:
        return r.json()
    except Exception as e:
        raise RuntimeError(f"Upstream returned non-JSON: url={url} ct={ct} body={text[:800]} err={e}")


def err_json(message: str, trace_id: str, session_id: str, extra: Optional[Dict[str, Any]] = None, status: int = 500):
    data = {"error": message, "trace_id": trace_id, "session_id": session_id}
    if extra:
        data.update(extra)
    return JSONResponse(status_code=status, content=data)


# =========================
# Static UI serving
# =========================
# 如果存在 ui/ 目录，则挂载静态目录：/ui/xxx
if UI_DIR.exists() and UI_DIR.is_dir():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR), html=False), name="ui")


@app.get("/", response_class=HTMLResponse)
def index():
    """
    访问 http://127.0.0.1:8010/ 直接打开 UI
    """
    ui = pick_ui_file()
    if ui is None:
        # 给出清晰提示，避免你“404 不知道为啥”
        return HTMLResponse(
            content=(
                "<h3>UI not found</h3>"
                "<p>Expected one of:</p>"
                f"<pre>{UI_FILE_AT_ROOT}\n{UI_FILE_IN_UI_DIR}</pre>"
                "<p>Please place ui.html accordingly.</p>"
            ),
            status_code=200,
        )
    return FileResponse(str(ui), media_type="text/html")


@app.get("/ui.html")
def ui_html():
    """
    兼容你手动访问 /ui.html
    """
    ui = pick_ui_file()
    if ui is None:
        return JSONResponse(
            status_code=404,
            content={"error": "ui.html not found", "expected": [str(UI_FILE_AT_ROOT), str(UI_FILE_IN_UI_DIR)]},
        )
    return FileResponse(str(ui), media_type="text/html")


# =========================
# API: Analyze
# =========================
@app.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    goal: str = Form(...),
    session_id: str = Form(DEFAULT_SESSION_ID),
    offline: str = Form("true"),
    max_new_tokens: str = Form("40"),
):
    """
    A 路线：前端给 goal + 图片，我们调用 test7 /agent/run，返回 plan + final_answer + trace_id
    """
    trace_id = now_trace_id()
    try:
        if image is None:
            return err_json("未选择图片", trace_id, session_id, status=422)
        if goal is None or not goal.strip():
            return err_json("goal 不能为空", trace_id, session_id, status=422)

        img_bytes = await image.read()
        if not img_bytes:
            return err_json("图片内容为空（可能没正确上传）", trace_id, session_id, status=422)

        out = await run_agent_a(
            img_bytes=img_bytes,
            filename=image.filename or "image.jpg",
            goal=goal.strip(),
            session_id=session_id,
            offline=str(offline).lower(),
            max_new_tokens=str(max_new_tokens),
        )

        return {
            "ok": True,
            "trace_id": out.get("trace_id", trace_id),
            "session_id": session_id,
            "plan": out.get("plan"),
            "final_answer": out.get("final_answer"),
            "summary": out.get("summary"),
            "raw": out.get("raw"),
        }


    except Exception as e:
        # 这里是你之前看到的 “Upstream 502 空 body”
        return err_json(f"对话失败：{e}", trace_id, session_id, status=500)


# =========================
# API: Chat (multi-turn + memory)
# =========================
@app.post("/chat")
async def chat(
    image: Optional[UploadFile] = File(None),
    question: str = Form(...),
    session_id: str = Form(DEFAULT_SESSION_ID),
    offline: str = Form("true"),
    max_new_tokens: str = Form("40"),
):
    """
    多轮：前端只发 question（可选 image），由 test7 /agent/chat 管记忆
    """
    trace_id = now_trace_id()
    try:
        if question is None or not question.strip():
            return err_json("问题不能为空", trace_id, session_id, status=422)

        url = TEST7_BASE + TEST7_CHAT_PATH

        # chat 场景：图片可选
        if image is not None:
            img_bytes = await image.read()
            if not img_bytes:
                return err_json("图片内容为空（可能没正确上传）", trace_id, session_id, status=422)

            fields = {
                "question": question.strip(),
                "session_id": session_id,
                "offline": str(offline).lower(),
                "max_new_tokens": str(max_new_tokens),
            }
            out = await post_multipart(url, img_bytes, image.filename or "image.jpg", fields)
        else:
            # 没图就用 JSON 也行（test7 只要支持即可）
            payload = {
                "question": question.strip(),
                "session_id": session_id,
                "offline": str(offline).lower(),
                "max_new_tokens": int(max_new_tokens),
            }
            out = await post_json(url, payload)

        return {
            "ok": True,
            "trace_id": out.get("trace_id", trace_id),
            "session_id": session_id,
            # test7 可能返回 answer / final / history 等
            "answer": out.get("answer") or out.get("final") or out.get("final_answer") or out,
            "raw": out,
        }

    except Exception as e:
        return err_json(f"对话失败：{e}", trace_id, session_id, status=500)


# =========================
# Health
# =========================
@app.get("/health")
def health():
    return {
        "ok": True,
        "app": APP_TITLE,
        "root_dir": str(ROOT_DIR),
        "ui_expected": [str(UI_FILE_AT_ROOT), str(UI_FILE_IN_UI_DIR)],
        "test7_base": TEST7_BASE,
        "test7_paths": [TEST7_RUN_PATH, TEST7_CHAT_PATH],
    }
