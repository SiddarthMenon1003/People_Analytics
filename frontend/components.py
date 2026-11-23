# shared UI blocks; palette from frontend.theme. each builds HTML as one unbroken
# string: a blank line ends Streamlit's HTML block and would split a card in two.

from contextlib import contextmanager
from itertools import count

import streamlit as st

from frontend.theme import PLOTLY_LAYOUT, STATUS_GOOD

_glass_card_ids = count()


def styled_layout(**overrides):
    """Plotly layout dict seeded from the shared theme, with per-chart overrides."""

    layout = dict(PLOTLY_LAYOUT)
    layout.update(overrides)
    return layout


def page_header(eyebrow, title, description, badge_text=None, badge_color=STATUS_GOOD):
    """Gradient hero banner used at the top of every page."""

    badge_html = ""
    if badge_text:
        badge_html = f'<div class="ph-badge" style="--badge-color:{badge_color};">{badge_text}</div>'

    body = (
        f'<div class="ph-body">'
        f'<div class="ph-eyebrow">{eyebrow}</div>'
        f'<div class="ph-title">{title}</div>'
        f'<div class="ph-description">{description}</div>'
        f"</div>"
    )

    st.markdown(f'<div class="page-header">{body}{badge_html}</div>', unsafe_allow_html=True)


def section_title(title, subtitle=None):
    """Left-aligned section heading as a rounded glass card."""

    inner = f'<div class="section-title">{title}</div>'
    if subtitle:
        inner += f'<div class="section-subtitle">{subtitle}</div>'

    st.markdown(f'<div class="section-title-block">{inner}</div>', unsafe_allow_html=True)


def divider():
    """Slim gradient rule used to separate major page sections."""

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)


def badge(text, color=STATUS_GOOD):
    """Small pill badge, e.g. a live-status or risk-level indicator."""

    st.markdown(
        f'<span class="status-badge" style="--badge-color:{color};">{text}</span>',
        unsafe_allow_html=True,
    )


def _badge_html(text, color):
    return f'<span class="status-badge" style="--badge-color:{color};">{text}</span>'


def kpi_row(cards):
    """Responsive row of KPI cards; each a dict {icon, label, value, accent?, sub?}."""

    columns = st.columns(len(cards))

    for column, card in zip(columns, cards):
        with column:
            accent = card.get("accent", "#60A5FA")

            body = (
                f'<div class="kpi-top">'
                f'<span class="kpi-icon">{card.get("icon", "")}</span>'
                f'<span class="kpi-label">{card["label"]}</span>'
                f"</div>"
                f'<div class="kpi-value">{card["value"]}</div>'
            )
            if card.get("sub"):
                body += f'<div class="kpi-sub">{card["sub"]}</div>'

            st.markdown(
                f'<div class="kpi-card" style="--kpi-accent:{accent};">{body}</div>',
                unsafe_allow_html=True,
            )


def progress_bar(pct, color="#60A5FA"):
    """Slim horizontal progress bar, capped at 100%."""

    width = max(0, min(pct, 100))

    st.markdown(
        f'<div class="progress-track">'
        f'<div class="progress-fill" style="width:{width}%; background:{color};"></div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def metric_line(label, value, color="#CBD5E1", show_bar=False, bar_pct=0, large=False):
    """One label/value row, with an optional progress bar beneath."""

    size_class = "metric-line-lg" if large else "metric-line-sm"

    st.markdown(
        f'<div class="metric-line {size_class}">'
        f'<span class="metric-line-label">{label}</span>'
        f'<span class="metric-line-value" style="color:{color};">{value}</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

    if show_bar:
        progress_bar(bar_pct, color)


def stat_rows(items):
    """Stacked icon + title/subtitle + value rows; item dict {icon,color,title,subtitle,value,show_bar?,bar_pct?}."""

    for index, item in enumerate(items):
        st.markdown(
            f'<div class="stat-row">'
            f'<div class="stat-row-left">'
            f'<div class="stat-icon" style="--stat-color:{item["color"]};">{item["icon"]}</div>'
            f'<div><div class="stat-title">{item["title"]}</div>'
            f'<div class="stat-subtitle">{item["subtitle"]}</div></div>'
            f"</div>"
            f'<div class="stat-row-right">'
            f'<div class="stat-value" style="color:{item["color"]};">{item["value"]}</div>'
            f'<div class="stat-caption">{item.get("caption", "")}</div>'
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if item.get("show_bar"):
            progress_bar(item.get("bar_pct", 0), item["color"])

        if index < len(items) - 1:
            st.markdown('<div class="stat-row-hr"></div>', unsafe_allow_html=True)


def ring_metric(color, value_text, label, size=88, inner_caption=None):
    """Conic-gradient ring with a centered value; size varies per call site."""

    pct = max(0.0, min(float(str(value_text).rstrip("%") or 0), 100.0))
    inner_size = round(size * 0.75)
    value_font = max(14, round(size * 0.24))
    caption_html = f'<div class="ring-caption">{inner_caption}</div>' if inner_caption else ""

    st.markdown(
        f'<div class="ring-metric">'
        f'<div class="ring-outer" style="width:{size}px;height:{size}px;'
        f'background:conic-gradient({color} {pct}%, rgba(255,255,255,0.08) 0);">'
        f'<div class="ring-inner" style="width:{inner_size}px;height:{inner_size}px;font-size:{value_font}px;">'
        f"{value_text}{caption_html}</div></div>"
        f'<div class="ring-label">{label}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def executive_card(eyebrow, title, text, accent="#A78BFA", dot=False, tinted=False, badges=None):
    """Shared executive-statement card; accent/dot/tinted style it, badges = (text,color) pills."""

    eyebrow_html = (
        f'<div class="exec-eyebrow-row"><span class="exec-dot" style="background:{accent};'
        f'box-shadow:0 0 14px {accent};"></span><span class="exec-eyebrow" style="color:{accent};">'
        f"{eyebrow}</span></div>"
        if dot
        else f'<div class="exec-eyebrow" style="color:{accent};">{eyebrow}</div>'
    )

    badges_html = ""
    if badges:
        pills = "".join(_badge_html(text, color) for text, color in badges)
        badges_html = f'<div class="exec-badges">{pills}</div>'

    card_class = "exec-card exec-card-tinted" if tinted else "exec-card"
    tint_style = f"--exec-accent:{accent};" if tinted else ""

    st.markdown(
        f'<div class="{card_class}" style="{tint_style}">'
        f"{eyebrow_html}"
        f'<div class="exec-title">{title}</div>'
        f'<div class="exec-text">{text}</div>'
        f"{badges_html}"
        f"</div>",
        unsafe_allow_html=True,
    )


def card_eyebrow(text, color="#A78BFA"):
    """Small uppercase label used at the top of a glass card."""

    st.markdown(f'<div class="card-eyebrow" style="color:{color};">{text}</div>', unsafe_allow_html=True)


def card_title(text):
    """In-card heading — the title role inside a `glass-card` chart/panel."""

    st.markdown(f'<div class="card-title">{text}</div>', unsafe_allow_html=True)


@contextmanager
def glass_card(extra_style=""):
    # `with glass_card():` wraps real DOM children via st.container; separate
    # st.markdown open/close would auto-close the div and orphan the content.
    # extra_style appends CSS scoped to this card's unique key (e.g. height:100%).
    key = f"glasscard_{next(_glass_card_ids)}"

    if extra_style:
        st.markdown(f'<style>div[class*="st-key-{key}"] {{ {extra_style} }}</style>', unsafe_allow_html=True)

    with st.container(border=True, key=key):
        yield


def table_height(row_count, row_height=35, header_height=38):
    """Pixel height fitting every row with no scrollbar; pass as st.dataframe height=."""

    return header_height + row_count * row_height + 3


def footer():
    st.markdown(
        '<div class="app-footer">'
        "Workforce Intelligence Dashboard"
        '<span class="app-footer-dot">&bull;</span>'
        "Predictive Analytics"
        '<span class="app-footer-dot">&bull;</span>'
        "Workforce Risk Modeling"
        '<span class="app-footer-dot">&bull;</span>'
        "Built with Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )
