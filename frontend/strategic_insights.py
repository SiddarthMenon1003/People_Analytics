"""Strategic Insights page — executive KPIs, health index, and forecasting."""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend.analytics import get_department_comparison, get_department_risk_ranking, get_strategic_metrics
from backend.insights_engine import (
    get_department_content,
    get_executive_position,
    get_executive_priority,
    get_health_assessment,
    get_optimization_projection,
    get_strategic_outlook,
    get_strategy_maturity,
)
from backend.model import predict_employee_risk, simulate_overtime_reduction
from frontend.components import (
    card_eyebrow,
    divider,
    executive_card,
    glass_card,
    kpi_row,
    metric_line,
    page_header,
    progress_bar,
    section_title,
    styled_layout,
    table_height,
)
from frontend.theme import STATUS_CRITICAL, STATUS_GOOD, STATUS_WARNING


def render_strategic_insights(filtered_df, df, selected_department, X, rf_model, encoders, cost_per_leaver):
    """Render the Strategic Insights page."""

    metrics = get_strategic_metrics(filtered_df, cost_per_leaver)
    high_risk_count = metrics["high_risk_count"]
    strategic_risk_score = metrics["strategic_risk_score"]
    strategic_retention_score = metrics["strategic_retention_score"]
    projected_attrition_impact = metrics["projected_attrition_impact"]
    health_index = metrics["health_index"]
    risk_label = metrics["risk_label"]
    signal_color = metrics["signal_color"]
    overtime_percentage = metrics["overtime_percentage"]
    total_employees = metrics["total_employees"]

    # headline forecast: model-scored at a default 20% overtime reduction
    headline_sim = simulate_overtime_reduction(rf_model, X, encoders, filtered_df, share=20)
    optimization_gain = headline_sim["reduction_pct"]
    retention_points = (
        round(headline_sim["leavers_avoided"] / total_employees * 100, 1) if total_employees else 0.0
    )
    forecast_improvement = retention_points
    projected_stability = round(min(strategic_retention_score + retention_points, 100), 1)

    comparison = get_department_comparison(df, selected_department)

    outlook_data = get_strategic_outlook(risk_label, selected_department)
    maturity_data = get_strategy_maturity(health_index)
    department_content = get_department_content(comparison)
    executive_position = get_executive_position(risk_label)
    executive_priority = get_executive_priority(selected_department)
    health_assessment = get_health_assessment(health_index, selected_department)

    page_header(
        eyebrow="Strategic Workforce Intelligence",
        title="Executive Workforce Strategy",
        description=(
            "Department-specific workforce intelligence transforming predictive "
            "analytics into executive decisions, retention strategy, and planning."
        ),
        badge_text="\U0001F9E0 Strategic Intelligence Active",
        badge_color="#A78BFA",
    )

    kpi_row(
        [
            {"label": "Workforce Posture", "value": executive_position["title"], "accent": "#38BDF8"},
            {"label": "Risk Score", "value": f"{strategic_risk_score}/100", "accent": "#A78BFA"},
            {"label": "Retention Strength", "value": f"{strategic_retention_score}%", "accent": STATUS_GOOD},
            {"label": "Risk Drop @20% OT off", "value": f"-{optimization_gain}%", "accent": "#60A5FA"},
        ]
    )

    insight_col, cost_col, priority_col = st.columns([1.25, 0.9, 0.9])

    with insight_col:
        executive_card(
            eyebrow="Executive Workforce Position",
            title=executive_position["title"],
            text=executive_position["text"],
            accent="#A78BFA",
        )

    with cost_col:
        kpi_row(
            [{
                "icon": "\U0001F4B0",
                "label": "Estimated Annual Impact",
                "value": f"${projected_attrition_impact:,.0f}",
                "sub": "Potential workforce cost risk",
                "accent": STATUS_WARNING,
            }]
        )

    with priority_col:
        kpi_row(
            [{
                "icon": "\U0001F3AF",
                "label": "Executive Priority",
                "value": executive_priority["title"],
                "sub": executive_priority["text"],
                "accent": "#60A5FA",
            }]
        )

    divider()
    section_title("Workforce Health Index")

    health_col, assessment_col = st.columns([0.9, 1.3])

    with health_col:
        with glass_card("height:100%;"):
            st.markdown(
                f'<div class="exec-eyebrow-row">'
                f'<span class="exec-dot" style="background:{STATUS_GOOD};box-shadow:0 0 16px {STATUS_GOOD};"></span>'
                f'<span class="exec-eyebrow" style="color:#A78BFA;">Workforce Health Score</span>'
                f"</div>"
                f'<div style="font-size:72px;font-weight:800;color:white;line-height:1;letter-spacing:-2px;'
                f'margin-bottom:12px;">{health_index}</div>'
                f'<div style="font-size:16px;color:#94A3B8;margin-bottom:20px;">Organizational Health Index</div>',
                unsafe_allow_html=True,
            )
            progress_bar(health_index, "#22C55E")
            st.markdown(
                '<div style="display:flex;justify-content:space-between;font-size:13px;color:#64748B;margin-top:6px;">'
                "<span>Critical</span><span>Healthy</span></div>",
                unsafe_allow_html=True,
            )

    with assessment_col:
        dot_color = STATUS_GOOD if health_index >= 75 else (STATUS_WARNING if health_index >= 50 else STATUS_CRITICAL)

        executive_card(
            eyebrow="Executive Workforce Assessment",
            title=health_assessment["title"],
            text=health_assessment["text"],
            accent=dot_color,
            dot=True,
        )

    divider()
    section_title("Executive Workforce Outlook")

    outlook_col, badges_col = st.columns([2.2, 1])

    with outlook_col:
        executive_card(
            eyebrow="Executive Signal",
            title=outlook_data["heading"],
            text=outlook_data["text"],
            accent=signal_color,
            dot=True,
        )

    with badges_col:
        st.markdown(
            '<div style="display:flex;flex-direction:column;gap:12px;padding-top:8px;">'
            + "".join(
                f'<span class="status-badge" style="--badge-color:{color};">{text}</span>'
                for text, color in [
                    ("Retention Focus", "#93C5FD"),
                    ("Burnout Monitoring", STATUS_WARNING),
                    ("Leadership Action", "#C4B5FD"),
                ]
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    divider()
    section_title("Strategic Priority Matrix")

    priority_df = pd.DataFrame(
        {
            "Strategic Initiative": [
                "Burnout Reduction",
                "Employee Engagement",
                "Workforce Planning",
                "Retention Optimization",
                "Leadership Monitoring",
            ],
            "Business Impact": ["High", "High", "Medium", "High", "Medium"],
            "Urgency": ["High", "Medium", "Medium", "High", "Low"],
        }
    )

    st.dataframe(
        priority_df,
        width="stretch",
        hide_index=True,
        height=table_height(len(priority_df)),
    )

    divider()
    section_title("Strategic Workforce Forecast")

    forecast_col1, forecast_col2 = st.columns([1.05, 1])

    with forecast_col1:
        fig_forecast = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=strategic_retention_score,
                number={"suffix": "%", "font": {"size": 44, "color": "white"}},
                title={"text": "Retention Stability", "font": {"size": 16}},
                gauge={
                    "shape": "angular",
                    "axis": {"range": [0, 100], "tickcolor": "rgba(0,0,0,0)"},
                    "bar": {"color": "#8ED973", "thickness": 0.3},
                    "bgcolor": "rgba(0,0,0,0)",
                    "borderwidth": 0,
                    "steps": [
                        {"range": [0, 40], "color": "rgba(239,68,68,0.15)"},
                        {"range": [40, 70], "color": "rgba(245,158,11,0.12)"},
                        {"range": [70, 100], "color": "rgba(34,197,94,0.12)"},
                    ],
                },
            )
        )
        fig_forecast.update_layout(**styled_layout(height=240))
        st.plotly_chart(fig_forecast, width="stretch", config={"displayModeBar": False})

        st.markdown(
            """
            <div style="font-size:13px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;
            color:#A5C4FF;margin-bottom:12px;">Workforce Stability Forecast</div>
            <div style="font-size:14px;line-height:1.8;color:#CBD5E1;margin-bottom:18px;">
                Workforce intelligence forecasts indicate retention performance can improve through
                targeted workforce optimization and burnout reduction strategies.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with glass_card():
            card_eyebrow("Primary Workforce Risk Drivers", color="#FBBF24")

            for driver_label, driver_value, driver_pct, driver_color in [
                ("Overtime Exposure", f"{overtime_percentage}%", overtime_percentage, "#F59E0B"),
                ("High Risk Employees", high_risk_count, min((high_risk_count / len(filtered_df)) * 100, 100), "#A855F7"),
                ("Workforce Health", f"{health_index}/100", health_index, "#22C55E"),
            ]:
                metric_line(driver_label, driver_value, driver_color, show_bar=True, bar_pct=driver_pct)

    with forecast_col2:
        st.markdown(
            """<div style="font-size:13px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;
            color:#93C5FD;margin-bottom:24px;">Stability Scenario Forecast</div>""",
            unsafe_allow_html=True,
        )

        metric_line("Current Stability", f"{strategic_retention_score}%", "white", show_bar=True, bar_pct=strategic_retention_score, large=True)
        metric_line("Projected Stability", f"{projected_stability}%", STATUS_GOOD, show_bar=True, bar_pct=projected_stability, large=True)

        st.markdown(
            f"""
            <div style="border-left:2px solid rgba(34,197,94,0.35); padding-left:18px; margin-top:28px;">
                <div style="font-size:13px;text-transform:uppercase;letter-spacing:1.3px;color:#86EFAC;
                font-weight:700;margin-bottom:10px;">Forecasted Impact</div>
                <div style="font-size:44px;font-weight:800;color:white;line-height:1;margin-bottom:10px;">
                    +{forecast_improvement}%
                </div>
                <div style="font-size:14px;line-height:1.7;color:#CBD5E1;">
                    Model-estimated retention gain from moving the highest-risk 20% of overtime
                    employees off overtime.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with glass_card("margin-top:24px;"):
            card_eyebrow("Executive Risk Snapshot", color="#93C5FD")

            for row_label, row_value, row_color in [
                ("Overtime Exposure", f"{overtime_percentage}%", "#FCA5A5"),
                ("High Risk Employees", high_risk_count, "#C4B5FD"),
                ("Health Index", f"{health_index}/100", "#86EFAC"),
            ]:
                metric_line(row_label, row_value, row_color, large=True)

    divider()
    section_title("AI Executive Narrative")
    st.info(department_content["narrative"])

    section_title("Department Risk Overview")
    ranking_df = get_department_risk_ranking(df)
    st.dataframe(
        ranking_df,
        width="stretch",
        hide_index=True,
        height=table_height(len(ranking_df)),
    )

    section_title("Executive Decision Support")
    st.success(department_content["decision"])

    section_title("Executive Impact Simulation")

    sim_share = st.slider(
        "Move this % of overtime employees (highest-risk first) off overtime",
        0,
        100,
        20,
        key="strategic_sim_share",
    )
    impact_sim = simulate_overtime_reduction(rf_model, X, encoders, filtered_df, sim_share)
    projected_retention_gain = (
        round(impact_sim["leavers_avoided"] / total_employees * 100, 1) if total_employees else 0.0
    )
    projected_savings = round(impact_sim["leavers_avoided"] * cost_per_leaver)

    st.success(
        get_optimization_projection(selected_department, projected_retention_gain, projected_savings)
    )
    st.caption(
        f"Assumes ${cost_per_leaver:,.0f} replacement cost per leaver (editable in the sidebar); "
        f"≈{impact_sim['leavers_avoided']} fewer expected leavers of {impact_sim['overtime_total']} "
        f"overtime employees in scope."
    )

    section_title("Workforce Strategy Maturity")
    st.info(
        f"""
### {maturity_data['icon']} {maturity_data['level']}

The current workforce management environment reflects
organizational maturity in managing:
• Burnout exposure
• Retention sustainability
• Workforce engagement
• Strategic workforce planning
"""
    )

    divider()
    section_title("Attrition Driver Intelligence")

    importance_df = pd.DataFrame({"Feature": X.columns, "Importance": rf_model.feature_importances_})
    importance_df = importance_df.sort_values(by="Importance", ascending=False).head(10)

    fig_ml = px.bar(
        importance_df,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Top Workforce Attrition Drivers",
        color="Importance",
        color_continuous_scale="Blues",
    )
    fig_ml.update_layout(**styled_layout(height=520, yaxis=dict(categoryorder="total ascending")))
    st.plotly_chart(fig_ml, width="stretch")

    divider()
    section_title("Live Employee Attrition Prediction")

    pred1, pred2 = st.columns(2)

    with pred1:
        age = st.slider("Employee Age", 18, 60, 30)
        monthly_income = st.slider("Monthly Income", 1000, 20000, 5000)
        years_company = st.slider("Years At Company", 0, 40, 5)

    with pred2:
        overtime = st.selectbox("Overtime", ["Yes", "No"])
        job_satisfaction = st.slider("Job Satisfaction", 1, 4, 2)
        worklife = st.slider("Work-Life Balance", 1, 4, 2)

    # model-scored; percentile is the honest headline (balanced inflates raw proba)
    score, percentile = predict_employee_risk(
        rf_model,
        X,
        encoders,
        Age=age,
        MonthlyIncome=monthly_income,
        YearsAtCompany=years_company,
        OverTime=overtime,
        JobSatisfaction=job_satisfaction,
        WorkLifeBalance=worklife,
    )

    if percentile >= 90:
        band_label, render = "High Risk", st.error
    elif percentile >= 70:
        band_label, render = "Moderate Risk", st.warning
    else:
        band_label, render = "Low Risk", st.success

    render(
        f"{band_label} — riskier than {percentile:.0f}% of employees "
        f"(model attrition probability {score:.0%})"
    )

    divider()
    section_title("Executive Strategic Summary")
    st.info(department_content["summary"])
