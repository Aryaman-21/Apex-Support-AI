"""
Metrics Aggregation and Analytics Module.
Calculates actual task accuracy, tool usage statistics, latency distribution,
token consumption, and evidence retrieval records for the Streamlit dashboard.
"""

import json
from typing import Dict, Any, List
from sqlalchemy import func
from database.db import get_db_session
from database.models import ConversationLog, SupportTicket


def get_dashboard_summary_metrics() -> Dict[str, Any]:
    """
    Computes real-time execution metrics directly from the SQLite conversation logs.
    Never hardcodes metrics.
    """
    with get_db_session() as session:
        total_queries = session.query(func.count(ConversationLog.trace_id)).scalar() or 0
        successful_queries = session.query(func.count(ConversationLog.trace_id)).filter(
            ConversationLog.status == "SUCCESS"
        ).scalar() or 0

        avg_latency = session.query(func.avg(ConversationLog.latency_ms)).scalar() or 0.0
        total_tokens = session.query(func.sum(ConversationLog.total_tokens)).scalar() or 0
        total_input_tokens = session.query(func.sum(ConversationLog.input_tokens)).scalar() or 0
        total_output_tokens = session.query(func.sum(ConversationLog.output_tokens)).scalar() or 0

        # Tool executions breakdown
        tool_stats: Dict[str, Dict[str, int]] = {}
        all_logs = session.query(ConversationLog).all()

        for log in all_logs:
            if log.tools_called:
                try:
                    tools = json.loads(log.tools_called)
                    for t in tools:
                        t_name = t if isinstance(t, str) else t.get("name", "unknown")
                        if t_name not in tool_stats:
                            tool_stats[t_name] = {"executions": 0, "success": 0, "failed": 0}
                        tool_stats[t_name]["executions"] += 1
                        if log.status == "SUCCESS":
                            tool_stats[t_name]["success"] += 1
                        else:
                            tool_stats[t_name]["failed"] += 1
                except Exception:
                    pass

        # Total Support Tickets created
        total_tickets = session.query(func.count(SupportTicket.ticket_id)).scalar() or 0

        accuracy_pct = round((successful_queries / total_queries * 100), 1) if total_queries > 0 else 100.0

        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": total_queries - successful_queries,
            "accuracy_pct": accuracy_pct,
            "avg_latency_ms": round(float(avg_latency), 2),
            "total_tokens": int(total_tokens),
            "total_input_tokens": int(total_input_tokens),
            "total_output_tokens": int(total_output_tokens),
            "tool_stats": tool_stats,
            "total_tickets_created": total_tickets,
        }


def get_detailed_traces_dataframe() -> List[Dict[str, Any]]:
    """Retrieve structured traces formatted for tabular display and filtering."""
    with get_db_session() as session:
        logs = (
            session.query(ConversationLog)
            .order_by(ConversationLog.created_at.desc())
            .limit(100)
            .all()
        )
        data = []
        for l in logs:
            data.append({
                "Trace ID": l.trace_id[:8] + "...",
                "Timestamp": l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "-",
                "Student ID": l.student_id or "Anonymous",
                "Query": l.query,
                "Agent Decision": l.intent_decision,
                "Tools Called": l.tools_called,
                "Evidence Chunks": l.retrieved_evidence,
                "Memory Used": l.memory_retrieved,
                "Context Selected": l.context_selected,
                "Final Response": l.response,
                "Latency (ms)": round(l.latency_ms, 1),
                "Tokens": l.total_tokens,
                "Status": l.status,
                "Error": l.error_message or "None",
            })
        return data
