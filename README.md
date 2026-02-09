
# Vision Analyst Agent  
*A Planning-based Multimodal Vision Agent with Traceable Reasoning*

---

##  项目简介

Vision Analyst Agent 是一个 **基于规划（Planning）与可追溯执行（Trace）** 的多模态视觉 Agent 系统。

系统能够：
- 理解用户给定的高层目标（Goal）
- 自动生成分析计划（Plan）
- 调用视觉感知工具（VQA / Caption）
- 汇总中间结果并输出结构化答案
- 生成完整可复现的执行 Trace（JSON / Markdown）

本项目不是简单的“多轮 VQA”，而是一个 具备任务分解、工具调用与过程解释能力的 Vision Agent。

---

##  核心能力

-  **Goal → Plan → Tool → Aggregate**
-  多模态感知（图像 + 文本）
-  可解释执行过程（Trace）
-  多轮对话 + 会话记忆
-  支持离线评测与策略对比

---

##  系统架构

```text
[ Web UI ]
     |
     v
[ Vision Analyst API :8010 ]
     |
     v
[ Agent Engine ]
     |
     +--> [ Perception Service :8006 ]
     |
     +--> [ Planning / Trace Service :8007 ]
     |
     v
[ JSON / Markdown Trace ]
##  模块说明
1. Perception Service（test6）
图像描述（Caption）

图像问答（VQA / VQA Batch）

专注“看图”，不参与策略决策

2. Agent Planning Service（test7）
根据用户 Goal 生成分析计划

调度感知工具

汇总结果并生成 Trace

3. Vision Analyst API（project2）
对外统一入口 /analyze

管理会话与多轮对话

处理上游异常与 Trace 落盘

4. Web UI
Apple 风格多轮对话界面

显示 Agent Plan 与执行过程

支持历史轮次与错误提示

 执行流程示例
用户目标：

“请描述图片内容，并总结关键物体与细节”

Agent 执行：

生成一句话图像概括

提问关键问题（场景 / 主体 / 细节）

汇总为要点报告

输出 Trace（JSON + Markdown）

## Trace 示例
每次执行都会生成：

runs/trace_xxx.json（机器可读）

runs/trace_xxx.md（人类可读）

用于：

调试

复现实验

离线评测

## 离线评测（test8 / test9）
项目支持多种 Agent 策略对比：

baseline

naive_reflect

gated_reflect

评测指标包括：

bad（不合理回答比例）

rep（重复度）

summary_ok（是否形成有效总结）

实验表明：

并非“更多反思 = 更好结果”，合理的 Gate 更重要。

## 启动方式（示例）
# 感知服务
uvicorn app:app --host 127.0.0.1 --port 8006

# Agent 规划服务
uvicorn api:app --host 127.0.0.1 --port 8007

# Vision Analyst 主服务
uvicorn app.analyst_api:app --host 127.0.0.1 --port 8010

API Docs: http://127.0.0.1:8010/docs

UI: http://127.0.0.1:8010/ui.html


## 项目定位
这是一个 工程化 Vision Agent 案例，重点在于：

系统设计

Agent 行为建模

工具调用与规划

可解释性与复现能力

而非单一模型效果对比。

## 技术栈
Python / FastAPI

Multimodal VQA Models

Agent Planning & Trace

Web UI (HTML / JS)

## License
Academic / Learning Purpose