
Vision Analyst Agent (Project 3) — Goal-Aware Plan & Explainable Trace

一个“目标驱动”的视觉 Agent：前端给 goal + image，后端自动生成 结构化计划（plan），再根据每一步计划选择问题路径，调用上游多模态模型得到答案，并把“为什么这么问”写进 trace，最终输出可复现的分析报告。

1. 项目亮点（你在面试/简历里最该讲的点）
✅ 1) Goal-Aware Planning（目标驱动计划）

输入不是固定模板，而是用户的 goal（例如：描述图片、找关键信息、做要点报告）

Agent 会生成结构化计划：

{
  "steps": [
    { "title": "...", "why": "...", "questions": ["...", "..."] }
  ]
}


不同 goal → 不同 steps / questions 路径（不再是通用 4 步）

✅ 2) Explainable Trace（可解释的轨迹）

trace 中记录：每一步为何要问、问了什么、得到什么回答

UI 显示 “为什么问这些问题” + “每一步问答”，可用于调试与复现

✅ 3) Frontend + Backend 全链路可视化

Apple 风格 UI：左侧历史轮次、当前轮高亮、系统角色提示、错误友好提示

主区展示：

Plan（结构化 steps）

Answer（最终报告）

Trace（question_trace + raw JSON）

2. 架构说明
2.1 服务端口（你现在的部署）

test6 (8006)：基础 VQA（BLIP VQA / 单轮、多问题）

test7 (8007)：Agent（多轮 + 记忆 + trace 产物）

Project 3 (8010)：Vision Analyst Agent（对外统一入口）

/analyze：接收图片 + goal → 返回 plan + final_answer + trace

2.2 Project 3 的职责（关键）

Project 3 不再只是“转发上游回答”，而是做 Agent Orchestration（编排）：

解析 goal → 生成结构化 plan（steps: title/why/questions）

执行 steps：调用上游模型（test7 / test6）

汇总：final_answer（按 goal 格式输出）

记录 trace：question_trace（why + Q&A）+ 保存 runs 产物

返回给 UI：plan + final_answer + trace_id + raw

3. API
3.1 POST /analyze

FormData 参数：

image：图片文件（必填，第一轮）

goal：用户目标/问题（必填）

session_id：会话 ID（默认 default）

offline：true/false（默认 true）

max_new_tokens：生成长度（默认 40/120，按实现）

响应示例（关键字段）：

{
  "ok": true,
  "trace_id": "trace_xxx",
  "session_id": "default",
  "plan": {
    "steps": [
      {
        "title": "一句话概括",
        "why": "先抓全局，降低偏题风险",
        "questions": ["What is shown in the image? ..."]
      }
    ]
  },
  "final_answer": "...",
  "raw": {
    "trace": {
      "question_trace": [
        {
          "title": "...",
          "why": "...",
          "questions": ["..."],
          "qa": [
            {"q":"...", "a":"..."}
          ]
        }
      ]
    }
  }
}

4. UI 使用说明
4.1 入口

UI 文件：ui.html（你现在用的那个）

访问：http://127.0.0.1:8010/ui.html（按你的挂载方式）

4.2 UI 区域说明

左侧：历史轮次（Q1/Q2/Q3…），当前轮高亮

中间：Plan 卡片（结构化 steps）

Trace 展开区：

✅ “为什么问这些问题（Question Trace）”

每一步：Why + Questions + 本步问答（Q→A）

raw JSON（完整调试信息）

5. 如何运行
5.1 启动依赖（你已有）
# test6
python -m uvicorn app:app --host 127.0.0.1 --port 8006

# test7
uvicorn api:app --host 127.0.0.1 --port 8007

5.2 启动 Project 3（8010）
uvicorn app.analyst_api:app --host 127.0.0.1 --port 8010

UI：http://127.0.0.1:8010/ui.html

6. 评估与调试（Trace 的意义）
6.1 为什么要有 plan + trace？

因为多模态系统最难的问题是：

不知道模型为什么这么答

不知道哪一步出错

复现困难

Plan + Trace 的价值：

Plan 让你看到“它打算怎么做”

Trace 让你定位“它实际做了什么、为什么做、每步结果是什么”

出问题时，你能判断是：

规划错（plan 不合理）

执行错（问错/上游答错）

汇总错（summary 合成不贴 goal）