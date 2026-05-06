"""
Supervisor agent ("Lead Orchestrator").

This is the ONLY agent the user talks to. It interprets the user's
high-level goal and decides whether to:
  - answer directly (small talk, clarifying questions), or
  - delegate to the Career Specialist via an A2A handoff
    (search/save/update/summarize tasks).

ADK exposes A2A handoffs as `AgentTool` wrappers around sub-agents:
calling `career_specialist_tool` from the supervisor LLM is the explicit
A2A handoff visible in traces.
"""
from __future__ import annotations

import os

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from agents.specialist.agent import career_specialist

MODEL = os.getenv("SUPERVISOR_MODEL", "gemini-2.0-flash")

SUPERVISOR_INSTRUCTION = """
You are the Supervisor for the Agentic Career Coach (ACC). You are the
user-facing agent for a VCU graduate student managing an internship search.

Decision policy (PROMPT-BASED ROUTING):
  - If the user asks about internships, jobs, applications, deadlines, or
    their pipeline state in ANY way -> hand off to `career_specialist` with
    a clear, structured task.
  - If the user is making small talk, asking who you are, or asking how to
    use you -> answer directly without a handoff.
  - If a hand off result comes back with errors, explain the problem to the
    user in plain language; do not retry silently.

When you hand off, write the task as a short imperative sentence the
specialist can act on, and include any filters the user mentioned
(role, location, keyword, status). Examples of good handoff tasks:
  - "Find security internships in Richmond, VA."
  - "Save job-002 to my pipeline with notes 'good fit, apply this week'."
  - "Mark job-002 as applied."
  - "Summarize my current pipeline grouped by status."

After the specialist replies, compose a friendly final response for the
user that summarizes what happened. Keep it concise.
"""

career_specialist_tool = AgentTool(agent=career_specialist)

supervisor = LlmAgent(
    name="supervisor",
    model=MODEL,
    description=(
        "Lead orchestrator that talks to the user and delegates internship "
        "search and pipeline tasks to the Career Specialist."
    ),
    instruction=SUPERVISOR_INSTRUCTION,
    tools=[career_specialist_tool],
)

# `root_agent` is the symbol the ADK CLI looks for.
root_agent = supervisor
