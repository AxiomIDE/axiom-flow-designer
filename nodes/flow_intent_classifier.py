import json
import logging
import os
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, FlowSpec

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Axiom flow designer.
Given a user's goal, produce a FlowSpec describing the intended flow with candidate node names to search for."""


def handle(req: AgentRequest, context) -> FlowSpec:
    api_key = context.secrets.get("ANTHROPIC_API_KEY") if hasattr(context, 'secrets') else os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Design an Axiom flow for this goal: {req.goal}

Return JSON:
{{
  "description": "<one sentence>",
  "candidate_nodes": ["<node-name-1>", "<node-name-2>"],
  "artifact_id": ""
}}"""
        }]
    )

    content = message.content[0].text
    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        content = content[start:end].strip()
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        content = content[start:end].strip()

    data = json.loads(content)

    return FlowSpec(
        description=data.get("description", req.goal),
        candidate_nodes=data.get("candidate_nodes", []),
        artifact_id=data.get("artifact_id", ""),
        fix_instructions=req.goal,
    )
