from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext, AgentProgress
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def flow_result(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> AgentProgress:
    """Terminal node: return the artifact_id on success."""
    if not input.has_error and input.compile_success:
        return AgentProgress(
            stage="complete",
            message=f"Flow '{input.name}' designed and compiled successfully.",
            complete=True,
            success=True,
            artifact_id=input.artifact_id,
        )
    else:
        return AgentProgress(
            stage="error",
            message=f"Flow design failed after {input.iteration} iteration(s): {input.error_summary}",
            complete=True,
            success=False,
        )
