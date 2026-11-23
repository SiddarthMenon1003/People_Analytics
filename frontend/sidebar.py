"""Sidebar: dataset upload, navigation, and persistent status panels."""

import streamlit as st

NAVIGATION_ITEMS = [
    "\U0001F4CA Overview",
    "\U0001F465 Workforce Analytics",
    "⚠️ Risk Intelligence",
    "\U0001F9E0 Strategic Insights",
]

DEPARTMENTS = ["All", "Sales", "Research & Development", "Human Resources"]


def render_sidebar():
    """Render the dataset upload control and return the uploaded file, if any.

    Tucked into a collapsed expander: the bundled sample dataset loads by
    default, so uploading your own CSV is an optional action rather than the
    first thing in the sidebar.
    """

    with st.sidebar.expander("Use your own dataset", expanded=False):
        st.caption(
            "Optional — the app loads the sample IBM HR dataset by default. "
            "Upload a CSV with the same columns to score your own workforce."
        )
        return st.file_uploader(
            "Upload workforce dataset (CSV)", type=["csv"], label_visibility="collapsed"
        )


def render_cost_assumption():
    """Sidebar input for the replacement-cost-per-leaver assumption.

    Every savings/exposure figure in the app is driven by this number, so it
    is an explicit, editable assumption rather than a constant hidden in the
    backend.
    """

    return st.sidebar.number_input(
        "Replacement cost per leaver (assumption, $)",
        min_value=0,
        value=15000,
        step=1000,
        key="cost_per_leaver",
    )


def render_navigation(navigation_items=NAVIGATION_ITEMS, departments=DEPARTMENTS):
    """Render the section radio and department filter; return the selections."""

    st.sidebar.markdown(
        """
        <div style="background: linear-gradient(135deg, rgba(45,55,72,0.95), rgba(30,41,59,0.92));
        border: 1.5px solid rgba(255,255,255,0.10); border-radius: 28px; padding: 26px 22px;
        margin: 18px 0; box-shadow: 0 12px 35px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.06);">
            <h2 style="color:white; font-size:28px; font-weight:800; line-height:1.15; margin:0 0 12px 0;">
                Workforce Navigator
            </h2>
            <p style="color:#CBD5E1; font-size:13px; line-height:1.8; margin:0;">
                Predictive Workforce Analytics &amp;
                Strategic Attrition Intelligence Platform
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_section = st.sidebar.radio(
        "Navigation",
        navigation_items,
        label_visibility="collapsed",
        key="sidebar_navigation",
    )

    selected_department = st.sidebar.selectbox(
        "Department Filter",
        departments,
        key="department_filter",
    )

    return selected_section, selected_department


def render_system_status():
    """Persistent sidebar panel listing what each dashboard page covers."""

    st.sidebar.markdown(
        """
        <div style='background:rgba(255,255,255,0.05); padding:18px; border-radius:16px;
        border:1px solid rgba(255,255,255,0.08); margin-top:18px;'>
            <h4 style='color:white;margin-bottom:12px;'>Dashboard Features</h4>
            <p style='color:#D1D5DB;line-height:1.8;font-size:14px;'>
                Workforce overview &amp; KPIs<br>
                Overtime &amp; burnout analytics<br>
                Department risk intelligence<br>
                Attrition driver modeling<br>
                Executive decision support
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


