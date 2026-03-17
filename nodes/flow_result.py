from gen.axiom_official_axiom_agent_messages_messages_pb2 import AnalysisResult, AgentProgress
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def flow_result(log: AxiomLogger, secrets: AxiomSecrets, input: AnalysisResult) -> AgentProgress:
    """Terminal node: return the artifact_id on success."""
    if not input.has_error:
        return AgentProgress(
            stage="complete",
            message=f"Flow designed successfully. {input.error_summary}",
            complete=True,
            success=True,
            artifact_id=input.artifact_id if hasattr(input, "artifact_id") else "",
        )
    else:
        return AgentProgress(
            stage="error",
            message=f"Flow design failed: {input.error_summary}",
            complete=True,
            success=False,
        )
