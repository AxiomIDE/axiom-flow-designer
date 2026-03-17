import json
import os
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert Axiom flow graph assembler.
Given resolved nodes and a description, produce a valid React Flow graph JSON with correct edge connections.
Edges must map output fields from one node to input fields of the next."""


def graph_assembler(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    api_key = secrets.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    fix_section = f"\n\nFix instructions:\n{input.fix_instructions}" if input.fix_instructions else ""

    resolved = {}
    if input.graph_json:
        try:
            resolved = json.loads(input.graph_json)
        except json.JSONDecodeError:
            pass

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Assemble a flow graph for: {input.description}

Resolved nodes:
{json.dumps(resolved.get("resolved_nodes", []), indent=2)}
{fix_section}

Return a React Flow graph JSON object with:
{{
  "nodes": [{{"id": "1", "type": "axiomNode", "data": {{"nodeId": "<ulid>", "label": "<name>"}}, "position": {{"x": 0, "y": 0}}}}],
  "edges": [{{"id": "e1-2", "source": "1", "target": "2", "data": {{"adapter": {{}}}}}}]
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

    try:
        graph = json.loads(content)
        input.graph_json = json.dumps(graph)
    except json.JSONDecodeError:
        log.warn("LLM returned invalid JSON for graph; keeping existing graph_json")

    input.fix_instructions = ""
    return input
