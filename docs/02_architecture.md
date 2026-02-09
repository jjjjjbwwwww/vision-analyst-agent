# 系统架构设计

## 总体架构

Vision Agent 采用分层解耦的系统架构，将多模态感知、Agent 决策与用户交互分离。

整体架构如下（文字版）：

[ Web UI ]
     |
     v
[ Vision Analyst API :80010 ]
     |
     v
[ Agent Engine ]
     |
     +--> [ Perception Service :8006 ]
     |
     +--> [ Agent Planning & Trace :8007 ]
     |
     v
[ Trace / JSON / Markdown 存储 ]

模块说明
1. Web UI（前端）

提供图片上传与多轮对话

展示 Agent 的 Plan、Trace 和最终回答

支持 Session 级别的上下文记忆

2. Vision Analyst API（主服务）

统一对外接口（/analyze）

管理 Session 与历史轮次

负责错误处理与上游服务调度

3. Perception Service（test6）

提供基础多模态能力：

图像描述（Caption）

图像问答（VQA / VQA Batch）

专注于“看图”，不参与策略决策

4. Agent Planning Service（test7）

根据用户 Goal 生成分析 Plan

调度 Perception 工具执行任务

汇总结果并生成结构化输出

5. Trace & Storage

每次 Agent 执行都会生成：

JSON Trace（机器可读）

Markdown Trace（人类可读）

用于调试、复现和离线评估