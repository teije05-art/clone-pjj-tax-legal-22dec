"""
Reusable UI Components with KPMG Professional Styling.

These components provide consistent branding across the application.
"""

import reflex as rx
from ..state import TaxState

# KPMG Brand Colors
KPMG_NAVY = "#191E62"
KPMG_BLUE = "#00338D"
KPMG_PINK = "#E6007E"
KPMG_PURPLE = "#6D2077"
EMERALD = "#10B981"
SLATE_50 = "#f8fafc"
SLATE_100 = "#f1f5f9"
SLATE_200 = "#e2e8f0"
SLATE_300 = "#cbd5e1"
SLATE_400 = "#94a3b8"
SLATE_500 = "#64748b"
SLATE_600 = "#475569"
SLATE_700 = "#334155"


def step_container(*children, max_width: str = "700px") -> rx.Component:
    """Container for step content with clean card styling."""
    return rx.box(
        rx.box(
            *children,
            style={
                "background": "white",
                "border-radius": "1rem",
                "box-shadow": "0 10px 40px rgba(0, 0, 0, 0.12)",
                "border": "1px solid rgba(255, 255, 255, 0.8)",
                "padding": "2rem",
            },
            width="100%",
            max_width=max_width,
        ),
        width="100%",
        display="flex",
        justify_content="center",
        padding_y="2",
        padding_x="4",
    )


def step_header(icon_name: str, title: str, description: str) -> rx.Component:
    """Styled step header with gradient icon box."""
    return rx.vstack(
        rx.hstack(
            rx.box(
                rx.icon(icon_name, size=24, color="white"),
                style={
                    "width": "3rem",
                    "height": "3rem",
                    "border-radius": "0.75rem",
                    "background": f"linear-gradient(to bottom right, {KPMG_NAVY}, {KPMG_BLUE})",
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                    "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                },
            ),
            rx.heading(
                title,
                style={
                    "font-size": "1.5rem",
                    "font-weight": "700",
                    "color": KPMG_NAVY,
                },
            ),
            spacing="3",
            align="center",
        ),
        rx.text(
            description,
            style={
                "color": SLATE_600,
                "line-height": "1.625",
            },
        ),
        spacing="2",
        align="start",
        width="100%",
    )


def kpmg_button(
    text: str,
    on_click,
    variant: str = "primary",
    icon: str = None,
    icon_right: bool = False,
    disabled=False,
    loading=False,
    full_width: bool = False,
) -> rx.Component:
    """KPMG-styled button with multiple variants."""

    variant_styles = {
        "primary": {
            "background": f"linear-gradient(to right, {KPMG_PINK}, {KPMG_PURPLE})",
            "color": "white",
            "box-shadow": "0 4px 14px 0 rgba(230, 0, 126, 0.3)",
            "_hover": {
                "background": f"linear-gradient(to right, {KPMG_PURPLE}, {KPMG_PINK})",
                "transform": "translateY(-2px)",
                "box-shadow": "0 6px 20px 0 rgba(230, 0, 126, 0.4)",
            },
        },
        "secondary": {
            "background": KPMG_NAVY,
            "color": "white",
            "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "_hover": {
                "background": KPMG_BLUE,
                "transform": "translateY(-2px)",
            },
        },
        "outline": {
            "background": "white",
            "color": KPMG_NAVY,
            "border": f"2px solid {KPMG_NAVY}",
            "_hover": {
                "background": KPMG_NAVY,
                "color": "white",
            },
        },
        "ghost": {
            "background": "transparent",
            "color": SLATE_600,
            "_hover": {
                "background": SLATE_100,
            },
        },
        "success": {
            "background": EMERALD,
            "color": "white",
            "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "_hover": {
                "background": "#059669",
                "transform": "translateY(-2px)",
            },
        },
        "warning": {
            "background": "#f59e0b",
            "color": "white",
            "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
            "_hover": {
                "background": "#d97706",
                "transform": "translateY(-2px)",
            },
        },
    }

    base_style = {
        "padding": "0.75rem 1.5rem",
        "border-radius": "0.75rem",
        "font-weight": "500",
        "cursor": "pointer",
        "transition": "all 0.2s ease",
        "display": "flex",
        "align-items": "center",
        "justify-content": "center",
        "gap": "0.5rem",
        "_disabled": {
            "opacity": "0.5",
            "cursor": "not-allowed",
        },
    }

    if full_width:
        base_style["width"] = "100%"

    style = {**base_style, **variant_styles.get(variant, variant_styles["primary"])}

    return rx.button(
        rx.cond(
            loading,
            rx.hstack(
                rx.spinner(size="1"),
                rx.text(text),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.cond(
                    icon != None and not icon_right,
                    rx.icon(icon, size=16),
                    rx.fragment(),
                ),
                rx.text(text),
                rx.cond(
                    icon != None and icon_right,
                    rx.icon(icon, size=16),
                    rx.fragment(),
                ),
                spacing="2",
                align="center",
            ),
        ),
        on_click=on_click,
        disabled=disabled,
        style=style,
    )


def info_callout(message: str) -> rx.Component:
    """KPMG blue info callout."""
    return rx.box(
        rx.hstack(
            rx.box(
                rx.icon("info", size=18, color=KPMG_BLUE),
                style={"flex-shrink": "0"},
            ),
            rx.text(message, style={"font-size": "0.875rem", "color": SLATE_700}),
            spacing="3",
            align="start",
        ),
        style={
            "background": f"rgba(0, 51, 141, 0.1)",
            "border": f"1px solid rgba(0, 51, 141, 0.2)",
            "border-radius": "0.75rem",
            "padding": "0.75rem 1rem",
        },
        width="100%",
    )


def warning_callout(message: str) -> rx.Component:
    """Amber warning callout."""
    return rx.box(
        rx.hstack(
            rx.icon("triangle-alert", size=18, color="#d97706"),
            rx.text(message, style={"font-size": "0.875rem", "color": SLATE_700}),
            spacing="3",
            align="start",
        ),
        style={
            "background": "#fffbeb",
            "border": "1px solid #fcd34d",
            "border-radius": "0.75rem",
            "padding": "0.75rem 1rem",
        },
        width="100%",
    )


def error_callout(message: str) -> rx.Component:
    """Red error callout."""
    return rx.box(
        rx.hstack(
            rx.icon("circle-x", size=18, color="#dc2626"),
            rx.text(message, style={"font-size": "0.875rem", "color": "#b91c1c"}),
            spacing="3",
            align="start",
        ),
        style={
            "background": "#fef2f2",
            "border": "1px solid #fecaca",
            "border-radius": "0.75rem",
            "padding": "0.75rem 1rem",
        },
        width="100%",
    )


def success_callout(message: str) -> rx.Component:
    """Green success callout."""
    return rx.box(
        rx.hstack(
            rx.icon("circle-check", size=18, color=EMERALD),
            rx.text(message, style={"font-size": "0.875rem", "color": "#065f46"}),
            spacing="3",
            align="start",
        ),
        style={
            "background": "#ecfdf5",
            "border": "1px solid #a7f3d0",
            "border-radius": "0.75rem",
            "padding": "0.75rem 1rem",
        },
        width="100%",
    )


def content_card(*children, accent: str = "slate") -> rx.Component:
    """Content card with subtle accent border."""
    accent_styles = {
        "slate": {"border": f"1px solid {SLATE_200}", "background": "white"},
        "blue": {"border": f"1px solid rgba(0, 51, 141, 0.3)", "background": f"rgba(0, 51, 141, 0.05)"},
        "green": {"border": f"1px solid #a7f3d0", "background": "rgba(236, 253, 245, 0.5)"},
        "purple": {"border": f"1px solid rgba(109, 32, 119, 0.3)", "background": f"rgba(109, 32, 119, 0.05)"},
        "pink": {"border": f"1px solid rgba(230, 0, 126, 0.3)", "background": f"rgba(230, 0, 126, 0.05)"},
    }

    style = {
        "border-radius": "0.75rem",
        "padding": "1rem",
        **accent_styles.get(accent, accent_styles["slate"]),
    }

    return rx.box(
        *children,
        style=style,
        width="100%",
    )


def styled_text_area(
    placeholder: str,
    value,
    on_change,
    min_height: str = "180px",
) -> rx.Component:
    """KPMG-styled text area with focus states."""
    return rx.text_area(
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        min_height=min_height,
        width="100%",
        style={
            "border-radius": "0.75rem",
            "border": f"2px solid {SLATE_200}",
            "padding": "1rem",
            "color": SLATE_700,
            "background": "white",
            "_focus": {
                "border-color": KPMG_BLUE,
                "box-shadow": f"0 0 0 4px rgba(0, 51, 141, 0.2)",
                "outline": "none",
            },
            "_placeholder": {
                "color": SLATE_400,
            },
        },
    )


def section_divider() -> rx.Component:
    """Simple section divider."""
    return rx.divider(style={"margin": "1rem 0", "border-color": SLATE_200})


def kpmg_badge(text: str, color: str = "pink") -> rx.Component:
    """KPMG-styled badge."""
    color_styles = {
        "pink": {"background": KPMG_PINK, "color": "white"},
        "navy": {"background": KPMG_NAVY, "color": "white"},
        "blue": {"background": KPMG_BLUE, "color": "white"},
        "purple": {"background": KPMG_PURPLE, "color": "white"},
        "success": {"background": EMERALD, "color": "white"},
        "slate": {"background": SLATE_200, "color": SLATE_700},
    }

    return rx.box(
        rx.text(text, style={"font-size": "0.75rem", "font-weight": "500"}),
        style={
            "padding": "0.25rem 0.75rem",
            "border-radius": "9999px",
            **color_styles.get(color, color_styles["pink"]),
        },
    )
