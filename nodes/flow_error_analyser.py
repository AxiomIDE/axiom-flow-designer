import json
import os

import httpx
import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at diagnosing Axiom flow graph errors.
Analyse the test failure and debug events to identify graph topology errors, adapter mismatches, or node failures.
Produce specific fix instructions for the GraphAssembler."""


def flow_error_analyser(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    if input.test_success:
        input.has_error = False
        input.error_summary = "Flow test passed"
        return input

    api_key, _ = secrets.get("ANTHROPIC_API_KEY")
    debug_events_text = ""
    if input.session_id:
        ingress_url = os.environ.get("INGRESS_URL", "http://axiom-ingress:80")
        axiom_api_key, _ = secrets.get("AXIOM_API_KEY")
        try:
            resp = httpx.get(
                f"{ingress_url}/v1/debug-events",
                params={"session_id": input.session_id, "limit": "50"},
                headers={"Authorization": f"Bearer {axiom_api_key}"},
                timeout=10.0,
            )
            if resp.status_code == 200:
                debug_events_text = json.dumps(resp.json(), indent=2)[:3000]
        except Exception as e:
            log.warn(f"Failed to fetch debug events: {e}")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Flow test failed:
{input.test_error}

Debug events:
{debug_events_text or "(none available)"}

What changes to the graph topology or edge adapters would fix this?"""
        }]
    )

    input.has_error = True
    input.fix_instructions = message.content[0].text
    input.error_summary = (input.test_error or "Unknown error")[:200]
    input.iteration = input.iteration + 1

    return input
