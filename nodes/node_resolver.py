import json
import logging
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowSpec

logger = logging.getLogger(__name__)


def handle(spec: FlowSpec, context) -> FlowSpec:
    """Search the marketplace for each candidate node and resolve their ULIDs."""

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")
    headers = {"Authorization": f"Bearer {axiom_api_key}"}

    resolved_nodes = []
    for node_name in spec.candidate_nodes:
        try:
            resp = httpx.post(
                f"{bff_url}/app/marketplace/search/semantic",
                json={"q": node_name},
                headers=headers,
                timeout=10.0,
            )
            if resp.status_code == 200:
                data = resp.json()
                packages = data.get("packages", [])
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
            logger.warning(f"Failed to resolve node {node_name}: {e}")

    if resolved_nodes:
        spec.graph_json = json.dumps({"resolved_nodes": resolved_nodes})

    return spec
