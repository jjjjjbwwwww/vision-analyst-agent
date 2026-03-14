# Vision Analyst Agent

An AI system that analyzes images and produces structured insights using a multimodal agent architecture.

The system integrates a reasoning agent with vision-language tools to perform automated image analysis.

---

# Features

- Goal-driven image analysis
- Multimodal reasoning
- Agent planning and execution
- Vision-language model integration
- Structured output with traces

---

# System Architecture

User
 │
 ▼
Vision Analyst Agent
 │
 ▼
Multimodal Agent
 │
 ▼
Vision Tool Server
 │
 ▼
BLIP Vision-Language Model

---

# Project Structure

vision-analyst-agent
│
├── app
│
├── scripts
│   ├── start_all.ps1
│   ├── stop_all.ps1
│
├── docs
│   └── architecture.md
│
├── requirements.txt
└── README.md
Example Use Case

Input:

Image + user question

Example:

What objects are visible in this scene?

Output:

Caption: A bedroom scene with a bed and desk.

Key Objects:
- Bed
- Laptop
- Lamp

Summary:
This image shows a bedroom workspace environment.
Tech Stack

Python

FastAPI

Multimodal AI

BLIP

Agent Architecture

Related Projects

This system depends on:

Multimodal Agent

Vision Tools Server

