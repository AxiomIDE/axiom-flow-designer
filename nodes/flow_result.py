from gen.axiom_official_axiom_agent_messages_messages_pb2 import AnalysisResult, AgentProgress


def handle(analysis: AnalysisResult, context) -> AgentProgress:
    """Terminal node: return the artifact_id on success."""
    if not analysis.has_error:
        return AgentProgress(
            stage="complete",
            message=f"Flow designed successfully. {analysis.error_summary}",
            complete=True,
            success=True,
            artifact_id=analysis.artifact_id if hasattr(analysis, "artifact_id") else "",
        )
    else:
        return AgentProgress(
            stage="error",
            message=f"Flow design failed: {analysis.error_summary}",
            complete=True,
            success=False,
        )
