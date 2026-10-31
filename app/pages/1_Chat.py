"""Streamlit Chat Page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from app.components.custom_styles import apply_enterprise_styles
from app.components.sidebar import render_sidebar
from app.views.chat_view import render_chat_view

apply_enterprise_styles()
render_sidebar()
render_chat_view()
