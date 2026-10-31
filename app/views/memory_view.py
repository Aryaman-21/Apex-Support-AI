"""
Long-Term Memory Management View for Streamlit.
Provides inspection, CRUD operations, and privacy filtering audit for persistent memories.
"""

import streamlit as st
import pandas as pd
from memory.memory_manager import MemoryManager
from memory.memory_extractor import analyze_and_extract_memory


def render_memory_view():
    """Renders the memory management interface."""
    st.markdown('<div class="enterprise-badge">● Persistent State & Privacy</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="margin-bottom: 1.2rem;">
            <h1 style="font-size: 1.85rem; font-weight: 800; margin: 0; color: #F8FAFC; letter-spacing: -0.02em;">
                Long-Term Memory & Privacy Audit
            </h1>
            <p style="font-size: 0.88rem; color: #94A3B8; margin: 4px 0 0 0;">
                Persistent profile attributes stored in SQLite across sessions. Sensitive information (passwords, OTPs) is strictly filtered.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    student_id = st.session_state.get("student_id", "STU1001")
    active_student = st.session_state.get("active_student", {})

    memories = MemoryManager.get_all_memories(student_id=student_id)

    # Top Cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Active Student</div>
                <div class="stat-value" style="font-size: 1.25rem;">{active_student.get('name', 'Student')}</div>
                <div class="stat-subtitle">ID: {student_id}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Stored Memories</div>
                <div class="stat-value">{len(memories)}</div>
                <div class="stat-subtitle">Persistent SQLite items</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="stat-card">
                <div class="stat-label">Privacy Shield</div>
                <div class="stat-value" style="color: #10B981;">Active</div>
                <div class="stat-subtitle">OTPs, credentials blocked</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Stored Memories Table
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader(f"🧠 Persistent Memories for {active_student.get('name', 'Selected Student')}")

    if memories:
        df_mem = pd.DataFrame(memories)
        st.dataframe(
            df_mem[["id", "memory_key", "memory_value", "confidence", "source_query", "updated_at"]],
            use_container_width=True,
            hide_index=True,
        )

        # Delete action
        col_del, col_clear = st.columns([2, 1])
        with col_del:
            del_id = st.selectbox("Select Memory ID to Delete", [m["id"] for m in memories], format_func=lambda x: f"ID #{x} ({next(m['memory_key'] for m in memories if m['id'] == x)})")
            if st.button("🗑️ Delete Selected Memory"):
                MemoryManager.delete_memory(del_id)
                st.success(f"Memory #{del_id} deleted.")
                st.rerun()

        with col_clear:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("⚠️ Clear All Memories for Student", type="secondary"):
                count = MemoryManager.clear_student_memories(student_id)
                st.warning(f"Cleared {count} memories.")
                st.rerun()
    else:
        st.info(f"No persistent memories stored yet for {student_id}. Switch to Chat and tell the agent 'My preferred name is Rahul and I am studying MBA' to save memories!")
    st.markdown("</div>", unsafe_allow_html=True)

    # Privacy Filter Sandbox / Live Demonstration
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.subheader("🛡️ Memory Extraction & Sensitive Information Filter Test")
    st.caption("Verify how the extraction engine accepts useful facts (name, programme, preferences) while strictly rejecting sensitive credentials (OTPs, passwords).")

    test_input = st.text_input(
        "Enter sample text to test extraction & privacy filter:",
        value="My preferred name is Rahul and my OTP is 123456.",
    )

    if st.button("🧪 Analyze & Audit"):
        decisions = analyze_and_extract_memory(test_input)
        if decisions:
            for d in decisions:
                if d.accepted:
                    st.success(f"✅ **ACCEPTED:** Key: `{d.key}` | Value: `{d.value}`\n\n*Reason:* {d.reason}")
                else:
                    st.error(f"🛑 **REJECTED (PRIVACY SHIELD):** Key: `{d.key}`\n\n*Reason:* {d.reason}")
        else:
            st.warning("No extractable facts or entities found in this input.")
    st.markdown("</div>", unsafe_allow_html=True)
