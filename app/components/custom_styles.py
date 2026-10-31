"""
Enterprise CSS Stylesheet for Streamlit Frontend.
Provides dark mode styling, glassmorphism cards, modern typography,
custom chat bubble styles, and badges.
"""

import streamlit as st


def apply_enterprise_styles():
    """Inject custom CSS into Streamlit application."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1250px;
    }

    /* Top Header Badge */
    .enterprise-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(59, 130, 246, 0.12);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 9999px;
        padding: 4px 14px;
        font-size: 0.78rem;
        font-weight: 600;
        color: #60A5FA;
        letter-spacing: 0.03em;
        margin-bottom: 12px;
        text-transform: uppercase;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1.25rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
        margin-bottom: 1rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        border-color: rgba(96, 165, 250, 0.3);
    }

    /* Metric Stat Card */
    .stat-card {
        background: linear-gradient(145deg, #131B2E 0%, #0B1120 100%);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #94A3B8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .stat-subtitle {
        font-size: 0.75rem;
        color: #10B981;
    }

    /* Quick Suggestion Chips */
    .suggestion-btn {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #E2E8F0;
        text-align: left;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 6px;
    }
    .suggestion-btn:hover {
        background: rgba(59, 130, 246, 0.15);
        border-color: #3B82F6;
        color: #93C5FD;
    }

    /* Trace Detail Box */
    .trace-box {
        background: #090D16;
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 8px;
        padding: 10px 14px;
        font-size: 0.82rem;
        line-height: 1.5;
        margin-top: 8px;
        color: #CBD5E1;
    }

    /* Tag Badges */
    .tag-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .tag-tool {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .tag-rag {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .tag-memory {
        background: rgba(168, 85, 247, 0.15);
        color: #C084FC;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }
    .tag-direct {
        background: rgba(59, 130, 246, 0.15);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Sidebar Clean Styling */
    [data-testid="stSidebar"] {
        background-color: #080C14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #94A3B8 !important;
        background: rgba(15, 23, 42, 0.4) !important;
        border-radius: 6px !important;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0B0F19;
    }
    ::-webkit-scrollbar-thumb {
        background: #1E293B;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
