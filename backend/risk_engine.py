"""Workforce risk scoring and classification.

Risk/health color semantics are owned here (not imported from the UI layer)
so this module stays independent of Streamlit — the three colors below are
kept in sync with `frontend.theme`'s status palette by convention.
"""

GOOD_COLOR = "#22C55E"
WARNING_COLOR = "#F59E0B"
CRITICAL_COLOR = "#EF4444"

LOW_RISK_THRESHOLD = 30
MODERATE_RISK_THRESHOLD = 50
HIGH_RISK_THRESHOLD = 70


def classify_risk(score):
    """Classify a 0-100 risk score into Low / Moderate / High risk."""

    if score < LOW_RISK_THRESHOLD:
        return {"label": "Low Risk", "color": GOOD_COLOR, "status": "\U0001f7e2 Low Workforce Risk"}

    if score < MODERATE_RISK_THRESHOLD:
        return {"label": "Moderate Risk", "color": WARNING_COLOR, "status": "\U0001f7e1 Moderate Workforce Risk"}

    return {"label": "High Risk", "color": CRITICAL_COLOR, "status": "\U0001f534 High Workforce Risk"}


def get_risk_severity(score):
    """Four-tier severity messaging (adds a "critical" band above High Risk)."""

    if score < LOW_RISK_THRESHOLD:
        return "success", "\U0001f7e2 LOW RISK — Workforce stability remains strong."

    if score < MODERATE_RISK_THRESHOLD:
        return "warning", "\U0001f7e1 MODERATE RISK — Burnout indicators increasing."

    if score < HIGH_RISK_THRESHOLD:
        return "error", "\U0001f7e0 HIGH RISK — Overtime pressure significantly impacting retention."

    return "error", "\U0001f534 CRITICAL RISK — Severe workforce instability detected."


def classify_workforce_health(retention_percent):
    """Classify overall workforce health from the retention rate."""

    if retention_percent >= 85:
        return {"label": "Excellent Stability", "color": GOOD_COLOR}

    if retention_percent >= 75:
        return {"label": "Healthy Workforce", "color": "#60A5FA"}

    if retention_percent >= 65:
        return {"label": "Moderate Stability", "color": WARNING_COLOR}

    return {"label": "Retention Risk", "color": CRITICAL_COLOR}


def classify_overtime_risk(overtime_percent):
    """Classify overtime pressure level."""

    if overtime_percent >= 60:
        return {"label": "High", "color": CRITICAL_COLOR, "severity": "critical"}

    if overtime_percent >= 30:
        return {"label": "Moderate", "color": WARNING_COLOR, "severity": "warning"}

    return {"label": "Low", "color": GOOD_COLOR, "severity": "healthy"}


def generate_risk_scores(dataframe):
    """Attach a weighted RiskScore (0-100) and RiskLevel to each employee."""

    risk_df = dataframe.copy()

    risk_df["RiskScore"] = (
        (risk_df["OverTime"] == "Yes").astype(int) * 30
        + (risk_df["JobSatisfaction"] <= 2).astype(int) * 25
        + (risk_df["WorkLifeBalance"] <= 2).astype(int) * 20
        + (risk_df["YearsAtCompany"] <= 2).astype(int) * 15
        + (risk_df["MonthlyIncome"] < risk_df["MonthlyIncome"].median()).astype(int) * 10
    )

    risk_df["RiskLevel"] = risk_df["RiskScore"].apply(lambda x: classify_risk(x)["label"])

    return risk_df
