
from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class Turn:
    q: str
    a: str
    ts: float


class SessionMemory:
    """
    一个非常轻量的“对话记忆”：
    - 以 session_id 为key
    - 每轮保存 {q, a, ts}
    - 落盘到 runs/sessions/<session_id>.json
    """

    def __init__(self, base_dir: Path, max_turns: int = 20):
        self.base_dir = base_dir
        self.max_turns = max_turns
        self.sessions_dir = self.base_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, session_id: str) -> Path:
        safe = "".join([c for c in session_id if c.isalnum() or c in ("-", "_")])[:64]
        if not safe:
            safe = "default"
        return self.sessions_dir / f"{safe}.json"

    def load(self, session_id: str) -> List[Turn]:
        p = self._path(session_id)
        if not p.exists():
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            turns = []
            for item in data.get("turns", []):
                turns.append(Turn(q=item.get("q", ""), a=item.get("a", ""), ts=float(item.get("ts", 0.0))))
            return turns
        except Exception:
            return []

    def save(self, session_id: str, turns: List[Turn]) -> None:
        p = self._path(session_id)
        data = {
            "session_id": session_id,
            "updated_at": time.time(),
            "turns": [asdict(t) for t in turns[-self.max_turns :]],
        }
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def append(self, session_id: str, q: str, a: str) -> List[Turn]:
        turns = self.load(session_id)
        turns.append(Turn(q=q, a=a, ts=time.time()))
        turns = turns[-self.max_turns :]
        self.save(session_id, turns)
        return turns

    def to_ui_list(self, turns: List[Turn]) -> List[Dict[str, Any]]:
        """
        给前端用的简化结构：[{idx, q, a}]
        """
        out = []
        for i, t in enumerate(turns, start=1):
            out.append({"idx": i, "q": t.q, "a": t.a})
        return out
