"""
Chat View Component for Streamlit.
Provides rich chat bubbles, quick prompt suggestions, interactive agent activity inspect,
and trace telemetry cards.
"""

import time
import json
import streamlit as st
from agent.orchestrator import run_agent


def render_chat_view():
    """Render the primary intelligent student support chat interface."""
    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = f"sess_{int(time.time())}"

    active_student = st.session_state.get("active_student", {})
    student_id = st.session_state.get("student_id", "STU1001")
    student_name = active_student.get("name", "Student")

    # Header
    st.markdown('<div class="enterprise-badge">● Autonomous Multi-Tool Agent</div>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1.2rem;">
            <div>
                <h1 style="font-size: 1.85rem; font-weight: 800; margin: 0; color: #F8FAFC; letter-spacing: -0.02em;">
                    Student Support Concierge
                </h1>
                <p style="font-size: 0.88rem; color: #94A3B8; margin: 4px 0 0 0;">
                    Connected for <b>{student_name}</b> ({student_id}) • Database Tools, Handbook RAG, and Long-Term Memory.
                </p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Welcome Card if conversation empty
    if not st.session_state.messages:
        st.markdown(
            f"""
            <div class="glass-card" style="border-left: 4px solid #3B82F6;">
                <div style="font-weight: 700; font-size: 1.1rem; color: #F1F5F9; margin-bottom: 6px;">
                    Welcome, {student_name.split()[0]}! How can I assist you today?
                </div>
                <div style="font-size: 0.88rem; color: #CBD5E1; line-height: 1.5; margin-bottom: 12px;">
                    I am your Intelligent Student Support Assistant. I autonomously coordinate between real-time university database records,
                    official student handbook policy documents, and your persistent academic profile to answer questions and resolve requests.
                </div>
                <div style="font-size: 0.78rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; margin-bottom: 8px;">
                    Suggested Quick Inquiries:
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        suggestions = [
            ("💳 What is my current fee status?", "What is my current fee status?"),
            ("🎓 What is my scholarship application status?", "What is my scholarship application status?"),
            ("⏳ The payment portal failed. Can I pay on next working day?", "The payment portal failed. Can I pay on the next working day?"),
            ("🔄 How can I change my course or programme?", "How can I change my course?"),
            ("🎫 Raise support ticket for uncredited payment", "I want to raise a support request because my payment is not reflected."),
            ("🧠 Store name & programme memory", "My preferred name is Rahul and I am studying MBA."),
        ]

        for idx, (label, prompt_text) in enumerate(suggestions):
            target_col = col1 if idx % 2 == 0 else col2
            if target_col.button(label, key=f"quick_prompt_{idx}", use_container_width=True):
                # Trigger the prompt directly
                st.session_state.messages.append({"role": "user", "content": prompt_text})
                with st.spinner("Agent analyzing intent and coordinating sources..."):
                    agent_result = run_agent(
                        query=prompt_text,
                        student_id=student_id,
                        session_id=st.session_state.session_id,
                        conversation_history=st.session_state.messages[:-1],
                    )
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": agent_result["final_response"],
                    "trace": agent_result,
                })
                st.rerun()

    # Render Chat History
    for idx, msg in enumerate(st.session_state.messages):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        trace = msg.get("trace")

        with st.chat_message(role, avatar="🧑‍🎓" if role == "user" else "🤖"):
            st.markdown(content)

            # If message has agent trace data, display rich expandable inspection box
            if trace:
                intent = trace.get("intent", "DIRECT_ANSWER")
                tools_called = trace.get("tools_to_call", [])
                tool_results = trace.get("tool_results", [])
                rag_chunks = trace.get("rag_chunks", [])
                memories = trace.get("memories", [])
                context_audit = trace.get("selected_context", {}).get("audit", {})
                latency = trace.get("latency_ms", 0.0)
                tokens = trace.get("token_usage", {})

                # Tag Pill representation
                badge_type = "tag-direct"
                badge_icon = "💬 Direct Answer"
                if intent == "TOOL_CALL":
                    badge_type = "tag-tool"
                    t_names = ", ".join([t.get("name") for t in tools_called]) if tools_called else "Tool"
                    badge_icon = f"🛠️ Tool: {t_names}"
                elif intent == "RAG_RETRIEVAL":
                    badge_type = "tag-rag"
                    badge_icon = f"📚 Policy RAG ({len(rag_chunks)} chunks)"
                elif intent == "COMPOSITE":
                    badge_type = "tag-tool"
                    badge_icon = "⚡ Composite (Tool + RAG)"

                with st.expander(f"🔍 Agent Activity & Observable Trace • {badge_icon} • {latency:.0f}ms"):
                    st.markdown(
                        f"""
                        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
                            <span class="tag-pill {badge_type}">{intent}</span>
                            <span class="tag-pill" style="background: rgba(255,255,255,0.08); color: #E2E8F0;">⏱️ {latency:.1f} ms</span>
                            <span class="tag-pill" style="background: rgba(255,255,255,0.08); color: #E2E8F0;">🔤 {tokens.get('total_tokens', 0)} tokens</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.markdown(f"**Intent Reasoning:** {trace.get('decision_reasoning', 'N/A')}")

                    # Tool Details Tab
                    if tool_results:
                        st.markdown("**🛠️ Tool Execution Output:**")
                        for tr in tool_results:
                            st.json(tr.get("execution_result", {}))

                    # RAG Chunks Tab
                    if rag_chunks:
                        st.markdown("**📚 Retrieved Policy Handbook Evidence:**")
                        for c in rag_chunks:
                            st.markdown(
                                f"""
                                <div class="trace-box" style="border-left: 3px solid #10B981;">
                                    <b>Chunk ID:</b> <code>{c.get('chunk_id')}</code> | <b>Page:</b> {c.get('page_number')} | <b>Distance:</b> {c.get('distance_score', 0):.4f}<br/>
                                    <div style="margin-top: 4px; font-style: italic;">"{c.get('text')}"</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    # Persistent Memory Tab
                    if memories:
                        st.markdown("**🧠 Retrieved Long-Term Memories:**")
                        for m in memories:
                            st.markdown(
                                f"- **{m.get('memory_key', '').title()}:** `{m.get('memory_value')}` *(Confidence: {m.get('confidence', 1.0)})*"
                            )

                    # Context Selection Audit
                    if context_audit:
                        st.markdown(
                            f"**📦 Selected Context Sources:** `{', '.join(context_audit.get('sources_used', []))}`"
                        )

    # Chat Input Box
    user_prompt = st.chat_input("Ask about fee deadlines, scholarships, academic policies, or support tickets...")
    if user_prompt:
        # Append User Message
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        # Run Agent Orchestrator
        with st.spinner("Agent analyzing intent and coordinating sources..."):
            agent_result = run_agent(
                query=user_prompt,
                student_id=student_id,
                session_id=st.session_state.session_id,
                conversation_history=st.session_state.messages[:-1],
            )

        # Append Assistant Message
        st.session_state.messages.append({
            "role": "assistant",
            "content": agent_result["final_response"],
            "trace": agent_result,
        })
        st.rerun()
