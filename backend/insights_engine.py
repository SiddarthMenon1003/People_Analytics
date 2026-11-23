"""Narrative text generators for the dashboard's executive-style copy.

Every function maps a metric (a risk label, a department, a health index)
to pre-written executive narrative. Keeping this copy here — instead of
inline in the page modules — separates "what the words say" from "how the
page is laid out."
"""

_DEPARTMENT_RECOMMENDATIONS = {
    "All": """
Recommended organizational initiatives:

- Implement enterprise-wide burnout monitoring
- Reduce sustained overtime dependency
- Strengthen retention-focused HR policies
- Improve workforce allocation strategies
- Increase employee wellness engagement
""",
    "Sales": """
Recommended Sales department initiatives:

- Reduce aggressive overtime exposure
- Improve incentive structures
- Strengthen employee engagement
- Introduce workload balancing
- Enhance managerial monitoring
""",
    "Research & Development": """
Recommended R&D department initiatives:

- Improve long-term engagement programs
- Reduce project burnout exposure
- Strengthen workforce development
- Improve career progression visibility
- Enhance collaborative workload distribution
""",
    "Human Resources": """
Recommended HR department initiatives:

- Improve workload distribution
- Strengthen support resources
- Reduce administrative pressure
- Enhance wellness monitoring
- Improve staffing support mechanisms
""",
}


def get_department_recommendation(selected_department):
    """Department-level workforce recommendation copy."""

    return _DEPARTMENT_RECOMMENDATIONS.get(selected_department, _DEPARTMENT_RECOMMENDATIONS["All"])

_DEPARTMENT_CONTENT = {
    "All": {
        "decision": """
### Recommended Immediate Executive Action

Prioritize organization-wide overtime reduction and
predictive workforce monitoring initiatives to stabilize
high-risk employee segments and improve long-term
workforce sustainability outcomes.
""",
        "summary": """
The organization currently demonstrates moderate
predictive workforce instability driven primarily
by overtime exposure, burnout pressure, and
employee engagement decline.

Strategic workforce optimization initiatives
present strong opportunities to improve retention,
reduce operational instability, and strengthen
long-term organizational sustainability.
""",
    },
    "Sales": {
        "decision": """
### Recommended Sales Leadership Action

Reduce sustained performance workload exposure and
improve employee engagement reinforcement mechanisms.
""",
        "summary": """
The Sales department demonstrates elevated workforce
pressure associated with operational workload and
workforce sustainability challenges.
""",
    },
    "Research & Development": {
        "decision": """
### Recommended R&D Leadership Action

Improve collaborative workload balancing and strengthen
long-term workforce engagement initiatives.
""",
        "summary": """
The R&D department demonstrates workforce sustainability
pressure linked to long-term engagement and burnout risk.
""",
    },
    "Human Resources": {
        "decision": """
### Recommended HR Leadership Action

Reduce administrative workforce pressure and improve
employee support sustainability mechanisms.
""",
        "summary": """
The HR department demonstrates elevated operational
pressure associated with coordination and support demands.
""",
    },
}


def get_department_content(comparison):
    """Executive narrative / decision / summary block for a department.

    The narrative is built from real figures in `comparison` (attrition vs
    the company average, overtime rate, composite-risk rank) so it can't
    contradict the data; the decision/summary copy stays qualitative.
    """

    scope = comparison["scope"]

    if scope == "All":
        narrative = (
            f"The data shows {comparison['org_attrition']}% attrition across the organization, "
            f"with {comparison['overtime_rate']}% of employees on overtime — the clearest and "
            f"most consistently measurable attrition driver in this dataset."
        )
    else:
        direction = "above" if comparison["above_avg"] else "below"
        narrative = (
            f"The data shows the {scope} department at {comparison['dept_attrition']}% attrition, "
            f"{direction} the {comparison['org_attrition']}% company average, with "
            f"{comparison['overtime_rate']}% on overtime and a composite-risk rank of "
            f"#{comparison['rank']} of {comparison['n_depts']} departments."
        )

    content = _DEPARTMENT_CONTENT.get(scope, _DEPARTMENT_CONTENT["All"])

    return {
        "narrative": narrative,
        "decision": content["decision"],
        "summary": content["summary"],
    }

_EXECUTIVE_PRIORITIES = {
    "All": {
        "title": "Reduce Overtime Exposure",
        "text": "Target workload balancing and burnout reduction to improve workforce stability.",
    },
    "Sales": {
        "title": "Reduce Performance Pressure",
        "text": "Focus on workload balancing and sustainable performance management.",
    },
    "Research & Development": {
        "title": "Improve Long-Term Engagement",
        "text": "Strengthen workforce engagement and reduce project fatigue exposure.",
    },
    "Human Resources": {
        "title": "Reduce Administrative Load",
        "text": "Improve workforce support processes and reduce coordination pressure.",
    },
}


def get_executive_priority(selected_department):
    """Top executive priority for the selected department."""

    return _EXECUTIVE_PRIORITIES.get(selected_department, _EXECUTIVE_PRIORITIES["All"])


def get_workforce_department_content(comparison):
    """Operational workforce signal built from real department figures.

    Replaces the old fixed copy (which claimed, e.g., that Sales had the
    highest overtime and that R&D was "stable" — both contradicted by the
    data) with a title/text derived from `comparison`.
    """

    scope = comparison["scope"]

    if scope == "All":
        return {
            "signal_title": "Organizational Workforce Signal",
            "signal_text": (
                f"Across the organization, attrition is {comparison['org_attrition']}% with "
                f"{comparison['overtime_rate']}% of employees on overtime. Overtime is the clearest "
                f"attrition driver in the data."
            ),
        }

    direction = "above" if comparison["above_avg"] else "below"
    title = "Elevated Workforce Pressure" if comparison["above_avg"] else "Below-Average Attrition"

    return {
        "signal_title": title,
        "signal_text": (
            f"The {scope} department shows {comparison['dept_attrition']}% attrition "
            f"({direction} the {comparison['org_attrition']}% company average) with "
            f"{comparison['overtime_rate']}% on overtime, ranking #{comparison['rank']} "
            f"of {comparison['n_depts']} departments on composite risk."
        ),
    }

_RISK_DRIVER_SIGNALS = {
    "Overtime Exposure": "Workforce Burnout Signal",
    "Low Job Satisfaction": "Engagement Risk Signal",
    "Poor Work-Life Balance": "Burnout Pressure Signal",
}


def get_risk_driver(filtered_df):
    """Most prevalent risk factor (name, signal) for the current scope.

    Computed from the data — the share of employees on overtime, with low
    job satisfaction, or with poor work-life balance — rather than a fixed
    per-department label. "Travel Fatigue" is gone: BusinessTravel is not a
    factor the app actually scores on.
    """

    factors = {
        "Overtime Exposure": (filtered_df["OverTime"] == "Yes").mean(),
        "Low Job Satisfaction": (filtered_df["JobSatisfaction"] <= 2).mean(),
        "Poor Work-Life Balance": (filtered_df["WorkLifeBalance"] <= 2).mean(),
    }
    name = max(factors, key=factors.get)

    return name, _RISK_DRIVER_SIGNALS[name]

_RISK_PERSONAS = {
    "All": (
        """
### High-Risk Persona 1

Early-career employees experiencing:
- Sustained overtime exposure
- Low work-life balance
- High workload pressure
- Reduced engagement levels
""",
        """
### High-Risk Persona 2

Employees demonstrating:
- Low job satisfaction
- Operational burnout indicators
- Short organizational tenure
- Elevated workforce instability risk
""",
    ),
    "Sales": (
        """
### Sales Performance Burnout Persona

Employees experiencing:
- Aggressive performance targets
- Sustained overtime exposure
- High client-facing workload
- Reduced engagement stability
""",
        """
### Sales Retention Risk Persona

Employees demonstrating:
- Reduced incentive satisfaction
- Elevated operational fatigue
- High performance pressure
- Increased workforce instability
""",
    ),
    "Research & Development": (
        """
### R&D Burnout Persona

Employees experiencing:
- Long project cycles
- Cognitive workload pressure
- Reduced work-life balance
- Engagement fatigue
""",
        """
### Innovation Retention Risk Persona

Employees demonstrating:
- Career stagnation concerns
- Reduced collaborative engagement
- Long-term workload fatigue
- Elevated attrition vulnerability
""",
    ),
    "Human Resources": (
        """
### HR Operational Pressure Persona

Employees experiencing:
- Administrative overload
- Workforce support fatigue
- Sustained operational pressure
- Reduced wellness balance
""",
        """
### HR Workforce Fatigue Persona

Employees demonstrating:
- Employee support burnout
- Workforce coordination pressure
- Reduced engagement sustainability
- Elevated retention vulnerability
""",
    ),
}


def get_risk_personas(selected_department):
    """(Persona 1, Persona 2) high-risk workforce personas."""

    return _RISK_PERSONAS.get(selected_department, _RISK_PERSONAS["All"])

_ACTION_PRIORITIES = {
    "All": """
1. Reduce sustained overtime dependency
2. Improve employee engagement initiatives
3. Strengthen workforce wellness monitoring
4. Increase retention-focused HR interventions
5. Improve workforce allocation efficiency
6. Develop predictive workforce monitoring systems
""",
    "Sales": """
1. Reduce aggressive performance workload pressure
2. Improve employee incentive sustainability
3. Strengthen sales engagement initiatives
4. Improve workforce balancing strategies
5. Enhance retention-focused managerial oversight
6. Reduce sustained overtime dependency
""",
    "Research & Development": """
1. Improve long-term workforce engagement
2. Reduce project-related burnout exposure
3. Strengthen workforce innovation pathways
4. Improve collaborative workload balancing
5. Enhance career growth visibility
6. Improve retention-focused development planning
""",
    "Human Resources": """
1. Reduce administrative workload pressure
2. Improve workforce support sustainability
3. Strengthen employee wellness initiatives
4. Improve operational staffing balance
5. Enhance workforce coordination support
6. Reduce burnout exposure across HR operations
""",
}


def get_risk_action_priorities(selected_department):
    """Ranked strategic action priorities for the selected department."""

    return _ACTION_PRIORITIES.get(selected_department, _ACTION_PRIORITIES["All"])

_PREDICTIVE_INTELLIGENCE = {
    "Sales": """
### Sales Department Predictive Intelligence

The Sales department demonstrates elevated workforce
instability associated with sustained performance pressure,
high overtime exposure, and engagement fatigue.
""",
    "Research & Development": """
### R&D Department Predictive Intelligence

The Research & Development department demonstrates
workforce instability patterns associated with long-term
project fatigue and engagement sustainability challenges.
""",
    "Human Resources": """
### Human Resources Predictive Intelligence

The Human Resources department demonstrates workforce
pressure associated with operational coordination demands,
employee support fatigue, and sustained administrative load.
""",
}


def get_predictive_intelligence(selected_department, high_risk_count, high_risk_percentage):
    """Predictive workforce intelligence narrative for the selected scope."""

    if selected_department != "All" and selected_department in _PREDICTIVE_INTELLIGENCE:
        return _PREDICTIVE_INTELLIGENCE[selected_department]

    return f"""
### Organization-Wide Predictive Intelligence

Predictive workforce analytics indicate that
employees exposed to sustained overtime pressure,
low satisfaction, and burnout indicators demonstrate
significantly elevated attrition risk.

Current analysis identifies **{high_risk_count}**
employees within the high-risk workforce category,
representing approximately **{high_risk_percentage}%**
of the workforce population.
"""

# RISK LABEL -> EXECUTIVE NARRATIVE ENGINES

_STRATEGIC_OUTLOOK = {
    "Low Risk": {
        "heading": "Strong workforce sustainability outlook",
        "text": "The {entity} currently demonstrates healthy workforce sustainability with manageable attrition exposure.",
    },
    "Moderate Risk": {
        "heading": "Emerging workforce instability indicators",
        "text": "Emerging workforce instability indicators require leadership attention and proactive retention planning.",
    },
    "High Risk": {
        "heading": "Immediate workforce intervention required",
        "text": "Significant workforce instability signals require immediate operational and retention intervention.",
    },
}


def get_strategic_outlook(risk_label, selected_department):
    """Strategic workforce outlook heading/text for the current risk level."""

    entity = selected_department if selected_department != "All" else "organization"
    outlook = _STRATEGIC_OUTLOOK[risk_label]

    return {"heading": outlook["heading"], "text": outlook["text"].format(entity=entity)}

_EXECUTIVE_POSITION = {
    "Low Risk": {
        "title": "Strong Workforce Stability",
        "text": "Current workforce intelligence indicates strong sustainability with healthy retention conditions and stable workforce performance.",
    },
    "Moderate Risk": {
        "title": "Moderate Workforce Stability",
        "text": "Current workforce intelligence indicates moderate sustainability with emerging retention pressure areas requiring leadership intervention and operational optimization strategies.",
    },
    "High Risk": {
        "title": "Critical Workforce Risk",
        "text": "Current workforce intelligence indicates significant workforce instability requiring immediate executive intervention and workforce stabilization measures.",
    },
}


def get_executive_position(risk_label):
    """Executive workforce position title/text for the current risk level."""

    return _EXECUTIVE_POSITION[risk_label]

_RISK_EXECUTIVE_POSITION = {
    "Low Risk": {
        "title": "Strong Workforce Stability",
        "text": "Current workforce intelligence indicates strong workforce sustainability with healthy retention conditions and stable organizational performance.",
    },
    "Moderate Risk": {
        "title": "Moderate Workforce Stability",
        "text": "Current workforce intelligence indicates a moderate workforce sustainability profile with measurable retention opportunity and emerging organizational pressure areas requiring leadership attention.",
    },
    "High Risk": {
        "title": "Critical Workforce Exposure",
        "text": "Current workforce intelligence indicates elevated workforce instability requiring immediate intervention and proactive workforce stabilization initiatives.",
    },
}


def get_risk_executive_position(risk_label):
    """Executive risk position title/text shown on the Risk Intelligence page."""

    return _RISK_EXECUTIVE_POSITION[risk_label]

_OVERVIEW_EXECUTIVE_BRIEF = {
    "Low Risk": ("Healthy Workforce Environment", "Operational Workforce Stability"),
    "Moderate Risk": ("Moderate Attrition Exposure", "Overtime Workforce Burnout"),
    "High Risk": ("Elevated Attrition Exposure", "Critical Workforce Burnout"),
}


def get_overview_executive_brief(risk_label):
    """(headline, attention area) tuple for the Overview executive brief."""

    return _OVERVIEW_EXECUTIVE_BRIEF[risk_label]

# NUMERIC-THRESHOLD ENGINES (health index, workforce maturity)


def get_health_assessment(health_index, selected_department):
    """Workforce health narrative bucketed by health index score."""

    entity = selected_department if selected_department != "All" else "organization"

    if health_index >= 75:
        return {
            "title": "Healthy Workforce",
            "text": f"The {entity} currently demonstrates strong workforce sustainability with healthy engagement indicators and stable operational retention conditions.",
        }

    if health_index >= 50:
        return {
            "title": "Moderate Stability",
            "text": f"The {entity} demonstrates moderate workforce sustainability with emerging burnout and retention pressure indicators.",
        }

    return {
        "title": "High Workforce Instability",
        "text": f"The {entity} demonstrates elevated workforce instability driven by burnout exposure and operational workload imbalance.",
    }


def get_strategy_maturity(health_index):
    """Workforce strategy maturity classification."""

    if health_index >= 80:
        return {"level": "Optimized Workforce Strategy", "icon": "\U0001f7e2"}

    if health_index >= 60:
        return {"level": "Maturing Workforce Strategy", "icon": "\U0001f7e1"}

    if health_index >= 40:
        return {"level": "Developing Workforce Strategy", "icon": "\U0001f7e0"}

    return {"level": "Reactive Workforce Strategy", "icon": "\U0001f534"}

# SCOPE-DEPENDENT NARRATIVE (organization-wide vs. single department)


def get_optimization_projection(selected_department, projected_retention_gain, projected_savings):
    """Executive workforce optimization projection, org-wide or department-scoped."""

    if selected_department == "All":
        return f"""
### Strategic Workforce Optimization Projection

If current workforce recommendations are implemented:

- Predicted retention improvement: **+{projected_retention_gain}%**
- Estimated annual organizational savings: **${projected_savings:,.0f}**
- Reduced workforce instability exposure
- Improved workforce sustainability
- Increased operational continuity
"""

    return f"""
### {selected_department} Optimization Projection

If department-level workforce initiatives are implemented:

- Predicted department retention improvement: **+{projected_retention_gain}%**
- Estimated department workforce savings: **${projected_savings:,.0f}**
"""


def get_workforce_vulnerability(selected_department):
    """Workforce vulnerability callout, org-wide or department-scoped."""

    if selected_department == "All":
        return """
### Workforce Vulnerability

The organization demonstrates elevated overtime-related
workforce instability indicators.
"""

    return f"""
### Workforce Vulnerability

The {selected_department} department demonstrates elevated
overtime-related workforce instability indicators.
"""


def get_primary_risk_driver():
    """Static primary workforce risk driver callout."""

    return """
### Primary Workforce Risk Driver

Operational workload pressure and overtime
exposure remain major workforce retention
challenges.
"""


def get_risk_simulation(selected_department, share, reduction_pct, leavers_avoided):
    """Model-based overtime-reduction scenario narrative.

    The numbers come from re-scoring the workforce with the trained model
    after moving the highest-risk `share`% of overtime employees off
    overtime — not a fixed multiplier.
    """

    scope = "the organization" if selected_department == "All" else f"the {selected_department} department"

    return f"""
### Workforce Optimization Simulation (model-based)

Moving the highest-risk **{share}%** of overtime employees in {scope} off overtime,
the trained model predicts:

- Total predicted attrition risk falls by **{reduction_pct}%** (relative)
- About **{leavers_avoided}** fewer expected leavers
- The reduction concentrates on the employees the model scores as highest-risk
"""


def get_cost_exposure(selected_department, projected_attrition_impact):
    """Estimated attrition cost exposure narrative."""

    if selected_department == "All":
        return f"""
### Estimated Attrition Exposure: ${projected_attrition_impact:,.0f}

Projected workforce instability impact includes:

- Recruitment costs
- Onboarding expenses
- Productivity disruption
- Workforce transition instability
- Operational performance decline
"""

    return f"""
### Estimated {selected_department} Department Exposure: ${projected_attrition_impact:,.0f}

Projected department instability impact includes:

- Workforce replacement costs
- Operational productivity disruption
- Team performance instability
- Increased workforce transition exposure
"""


def get_risk_summary(selected_department, high_risk_percentage, risk_level):
    """One-line executive risk summary, org-wide or department-scoped."""

    if selected_department == "All":
        return (
            f"Workforce intelligence indicates {high_risk_percentage}% high-risk workforce "
            f"concentration across organizational segments, requiring proactive workforce monitoring."
        )

    return (
        f"{selected_department} demonstrates {risk_level.lower()} with {high_risk_percentage}% "
        f"predictive workforce exposure requiring targeted intervention."
    )


def get_overview_insights(
    selected_department,
    highest_attrition_dept,
    stable_dept,
    department_attrition=None,
    overtime_percentage=None,
):
    """Key workforce insights block for the Overview page."""

    if selected_department == "All":
        return f"""
### Organizational Workforce Intelligence

- Highest workforce instability detected in **{highest_attrition_dept}**
- Strongest workforce stability observed in **{stable_dept}**
- Overtime exposure remains the primary workforce risk driver
- Workforce optimization initiatives present significant retention opportunities
- Predictive workforce intelligence indicates moderate organizational sustainability pressure
"""

    return f"""
### {selected_department} Workforce Intelligence

- Department attrition rate: **{department_attrition:.1f}%**
- Overtime exposure: **{overtime_percentage:.1f}%**
- Workforce sustainability requires continued monitoring
- Employee engagement and workload balance remain key retention drivers
- Predictive workforce analytics indicate moderate optimization opportunity
"""
