
# API 设计说明

## 核心接口

### POST /analyze

统一的视觉分析接口。

#### 请求参数（multipart/form-data）

- image: 上传的图片文件
- goal: 用户分析目标
- session_id（可选）: 会话标识

---

#### 返回字段

```json
{
  "ok": true,
  "trace_id": "trace_xxx",
  "session_id": "default",
  "plan": {...},
  "final_answer": "...",
  "raw": {...}
}