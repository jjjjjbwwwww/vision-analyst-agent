
## Agent 的核心思想

Vision Agent 并非一次性回答问题，而是执行一个“可解释的分析过程”。

整个流程遵循：

Goal → Plan → Tool Calls → Aggregate → Trace
执行流程
Step 1：接收用户 Goal
用户输入一个高层目标，例如：

“请描述图片内容，并总结关键物体与细节”

Step 2：生成 Plan（规划）
Agent 会自动生成分析步骤，例如：

生成一句话图像概括（Caption）

提问关键问题（场景 / 主体 / 细节）

汇总为要点报告

返回 Trace

Step 3：工具调用（Tool Use）
Agent 调用感知工具完成每一步：

Caption → /vqa

多问题分析 → /vqa_batch

Step 4：结果汇总
将所有中间结果组合成最终回答：

Scene

Main object

Details

Step 5：生成 Trace
保存完整执行过程，包括：

输入参数

Plan

工具调用结果

最终输出