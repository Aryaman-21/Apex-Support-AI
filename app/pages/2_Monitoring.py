"""Streamlit Monitoring Page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from app.components.custom_styles import apply_enterprise_styles
from app.components.sidebar import render_sidebar
from app.views.monitoring_view import render_monitoring_view

apply_enterprise_styles()
render_sidebar()
render_monitoring_view()
