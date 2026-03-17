import json
import logging
import os
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowSpec

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert Axiom flow graph assembler.
Given resolved nodes and a description, produce a valid React Flow graph JSON with correct edge connections.
Edges must map output fields from one node to input fields of the next."""


def handle(spec: FlowSpec, context) -> FlowSpec:
    api_key = context.secrets.get("ANTHROPIC_API_KEY") if hasattr(context, 'secrets') else os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    fix_section = f"\n\nFix instructions:\n{spec.fix_instructions}" if spec.fix_instructions else ""

    resolved = {}
    if spec.graph_json:
        try:
            resolved = json.loads(spec.graph_json)
        except json.JSONDecodeError:
            pass

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Assemble a flow graph for: {spec.description}

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
        spec.graph_json = json.dumps(graph)
    except json.JSONDecodeError:
        logger.warning("LLM returned invalid JSON for graph; keeping existing graph_json")

    spec.fix_instructions = ""
    return spec
