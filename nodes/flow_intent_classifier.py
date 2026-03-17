import json
import os
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert Axiom flow designer.
Given a user's goal, produce a FlowBuildContext describing the intended flow with candidate node names to search for."""


def flow_intent_classifier(log: AxiomLogger, secrets: AxiomSecrets, input: AgentRequest) -> FlowBuildContext:
    api_key = secrets.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Design an Axiom flow for this goal: {input.prompt}

Return JSON:
{{
  "name": "<kebab-case-flow-name>",
  "description": "<one sentence>",
  "candidate_nodes": ["<node-name-1>", "<node-name-2>"]
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

    # Store candidate_nodes in graph_json as a JSON object for NodeResolver to consume.
    ctx = FlowBuildContext(
        name=data.get("name", "new-flow"),
        description=data.get("description", input.prompt),
        graph_json=json.dumps({"candidate_nodes": data.get("candidate_nodes", [])}),
    )

    return ctx
