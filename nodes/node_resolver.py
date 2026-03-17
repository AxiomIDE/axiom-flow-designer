import json
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def node_resolver(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    """Search the marketplace for each candidate node and resolve their ULIDs."""

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")
    headers = {"Authorization": f"Bearer {axiom_api_key}"}

    candidate_nodes = []
    if input.graph_json:
        try:
            data = json.loads(input.graph_json)
            candidate_nodes = data.get("candidate_nodes", [])
        except json.JSONDecodeError:
            pass

    resolved_nodes = []
    for node_name in candidate_nodes:
        try:
            resp = httpx.post(
                f"{bff_url}/app/marketplace/search/semantic",
                json={"q": node_name},
                headers=headers,
                timeout=10.0,
            )
            if resp.status_code == 200:
                packages = resp.json().get("packages", [])
                for pkg in packages[:1]:
                    for node in pkg.get("nodes", []):
                        resolved_nodes.append({
                            "id": node.get("id", ""),
                            "name": node.get("name", node_name),
                            "package": pkg.get("name", ""),
                            "input_schema": node.get("input_schema", {}),
                            "output_schema": node.get("output_schema", {}),
                        })
        except Exception as e:
            log.warn(f"Failed to resolve node {node_name}: {e}")

    input.graph_json = json.dumps({"resolved_nodes": resolved_nodes})
    return input
