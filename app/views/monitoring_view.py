"""
Monitoring & Telemetry Dashboard View.
Visualizes real-time agent accuracy, tool usage, latency distribution,
token consumption, and complete execution traces using Plotly charts and tables.
"""

import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from monitoring.metrics import get_dashboard_summary_metrics, get_detailed_traces_dataframe
from database.db import get_db_session
from database.models import ConversationLog


def render_monitoring_view():
    """Renders the enterprise monitoring and observability dashboard."""
    st.markdown('<div class="enterprise-badge">● Observability & Telemetry</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="font-size: 1.85rem; font-weight: 800; margin: 0; color: #F8FAFC; letter-spacing: -0.02em;">
                Agent Execution & Performance Dashboard
            </h1>
            <p style="font-size: 0.88rem; color: #94A3B8; margin: 4px 0 0 0;">
                Live observability into autonomous decisions, database tool invocations, RAG retrieval, latency, and token consumption.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metrics = get_dashboard_summary_metrics()

    # Top KPI Stat Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Inquiries</div>
                <div class="stat-value">{metrics['total_queries']}</div>
                <div class="stat-subtitle">Logged in SQLite</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi2:
        acc = metrics['accuracy_pct']
        color = "#10B981" if acc >= 90 else "#FBBF24"
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Task Success Rate</div>
                <div class="stat-value" style="color: {color};">{acc}%</div>
                <div class="stat-subtitle">{metrics['successful_queries']} successful</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi3:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Avg Response Time</div>
                <div class="stat-value">{metrics['avg_latency_ms']:.0f} <span style="font-size: 1rem; font-weight: 400; color: #94A3B8;">ms</span></div>
                <div class="stat-subtitle">End-to-End Latency</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi4:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Total Tokens</div>
                <div class="stat-value">{metrics['total_tokens']:,}</div>
                <div class="stat-subtitle">{metrics['total_input_tokens']:,} in • {metrics['total_output_tokens']:,} out</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with kpi5:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Support Tickets</div>
                <div class="stat-value" style="color: #60A5FA;">{metrics['total_tickets_created']}</div>
                <div class="stat-subtitle">Created in Database</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Charts Row 1: Tool Executions & Token Breakdown
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("🛠️ Tool Executions & Status")
        tool_stats = metrics.get("tool_stats", {})
        if tool_stats:
            tool_names = list(tool_stats.keys())
            successes = [tool_stats[t]["success"] for t in tool_names]
            failures = [tool_stats[t]["failed"] for t in tool_names]

            fig_tools = go.Figure(data=[
                go.Bar(name='Success', x=tool_names, y=successes, marker_color='#10B981'),
                go.Bar(name='Failed', x=tool_names, y=failures, marker_color='#EF4444'),
            ])
            fig_tools.update_layout(
                barmode='stack',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
                margin=dict(l=20, r=20, t=20, b=30),
                height=260,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            st.plotly_chart(fig_tools, use_container_width=True)
        else:
            st.info("No tool executions recorded yet. Ask a fee, scholarship, or ticket question to generate tool telemetry.")
        st.markdown("</div>", unsafe_allow_html=True)

    with chart_col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("📊 Token Usage Breakdown")
        in_t = metrics.get("total_input_tokens", 0)
        out_t = metrics.get("total_output_tokens", 0)

        if in_t > 0 or out_t > 0:
            fig_donut = go.Figure(data=[go.Pie(
                labels=['Input Tokens (Context / RAG)', 'Output Tokens (Synthesis)'],
                values=[in_t, out_t],
                hole=.6,
                marker=dict(colors=['#3B82F6', '#8B5CF6']),
                textinfo='label+percent',
            )])
            fig_donut.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
                margin=dict(l=10, r=10, t=10, b=10),
                height=260,
                showlegend=False,
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Token metrics will appear once queries are processed.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Charts Row 2: Latency Distribution across queries
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("⏱️ Execution Latency Timeline")

    with get_db_session() as session:
        recent_logs = (
            session.query(ConversationLog)
            .order_by(ConversationLog.created_at.asc())
            .limit(50)
            .all()
        )

    if recent_logs:
        lat_data = [{
            "Query #": i + 1,
            "Latency (ms)": l.latency_ms,
            "Intent": l.intent_decision,
            "Snippet": l.query[:35] + "...",
        } for i, l in enumerate(recent_logs)]
        df_lat = pd.DataFrame(lat_data)

        fig_lat = px.line(
            df_lat,
            x="Query #",
            y="Latency (ms)",
            hover_data=["Intent", "Snippet"],
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#38BDF8'],
        )
        fig_lat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#94A3B8', family='Plus Jakarta Sans'),
            margin=dict(l=20, r=20, t=10, b=20),
            height=220,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)'),
        )
        st.plotly_chart(fig_lat, use_container_width=True)
    else:
        st.info("No queries executed yet.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Complete Agent Execution Traces Table
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    tab_traces, tab_eval = st.tabs(["📋 Live Agent Execution Traces", "🧪 Automated Evaluation Benchmark (9 Scenarios)"])

    with tab_traces:
        st.subheader("Live Interaction Traces")
        st.caption("Inspect live decision records, tools executed, RAG evidence chunks, memory lookups, and latency.")

        traces = get_detailed_traces_dataframe()
        if traces:
            df_traces = pd.DataFrame(traces)
            # Display search filter
            search_kw = st.text_input("Filter traces by keyword, decision, or student ID:", placeholder="e.g. STU1001, TOOL_CALL, fee...")
            if search_kw:
                mask = df_traces.astype(str).apply(lambda row: row.str.contains(search_kw, case=False).any(), axis=1)
                filtered_df = df_traces[mask]
            else:
                filtered_df = df_traces

            st.dataframe(
                filtered_df[["Trace ID", "Timestamp", "Student ID", "Query", "Agent Decision", "Tools Called", "Latency (ms)", "Tokens", "Status"]],
                use_container_width=True,
                hide_index=True,
            )

            # Trace detail expander
            selected_trace_idx = st.selectbox("Select trace index to view full context & evidence payload:", range(len(filtered_df)), format_func=lambda i: f"#{i+1} [{filtered_df.iloc[i]['Agent Decision']}] {filtered_df.iloc[i]['Query'][:50]}")
            if selected_trace_idx is not None and not filtered_df.empty:
                row = filtered_df.iloc[selected_trace_idx]
                st.markdown(f"**Full Query:** `{row['Query']}`")
                st.markdown(f"**Final Assistant Response:**\n> {row['Final Response']}")
                c_col1, c_col2 = st.columns(2)
                with c_col1:
                    st.markdown("**Evidence Chunks:**")
                    st.code(row['Evidence Chunks'], language="json")
                with c_col2:
                    st.markdown("**Tool Outputs:**")
                    st.code(row['Tools Called'], language="json")
        else:
            st.info("No execution traces found in the database. Run queries to view execution logs.")

    with tab_eval:
        st.subheader("Automated Evaluation Suite Results")
        st.caption("Results from running the 9 required assignment test scenarios against the agent.")
        from config.settings import settings
        csv_path = settings.EVALUATION_RESULTS_DIR / "evaluation_report.csv"
        if csv_path.exists():
            df_eval = pd.read_csv(csv_path)
            pass_count = (df_eval["status"] == "PASS").sum()
            total_count = len(df_eval)
            st.markdown(f"**Benchmark Score:** `{pass_count}/{total_count} Passed ({pass_count/total_count*100:.1f}%)`")
            st.dataframe(
                df_eval[["test_id", "test_name", "actual_intent", "actual_tools", "latency_ms", "total_tokens", "status", "failure_reason"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Evaluation report not generated yet. Run 'python evaluation/evaluator.py' to generate results.")
        
        if st.button("🚀 Re-Run 9 Automated Evaluation Scenarios"):
            with st.spinner("Executing evaluation benchmark..."):
                from evaluation.evaluator import run_evaluation
                run_evaluation()
            st.success("Evaluation suite executed successfully!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
