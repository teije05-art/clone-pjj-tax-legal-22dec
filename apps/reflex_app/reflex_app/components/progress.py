"""Progress Bar Component - Clean Professional Design."""

import reflex as rx
from ..state import TaxState

# KPMG Brand Colors
KPMG_NAVY = "#00338D"
KPMG_PINK = "#E6007E"
KPMG_PURPLE = "#6D2077"
EMERALD = "#10B981"


def progress_step(step_num: int, name: str) -> rx.Component:
    """Individual step indicator with clean styling."""
    return rx.hstack(
        rx.cond(
            TaxState.current_step > step_num,
            # Completed step - Emerald with checkmark
            rx.box(
                rx.icon("check", size=14, color="white"),
                style={
                    "width": "1.75rem",
                    "height": "1.75rem",
                    "border-radius": "9999px",
                    "background": EMERALD,
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                },
            ),
            rx.cond(
                TaxState.current_step == step_num,
                # Current step - Pink with ring
                rx.box(
                    rx.text(
                        str(step_num),
                        style={
                            "font-size": "0.75rem",
                            "font-weight": "700",
                            "color": "white",
                        },
                    ),
                    style={
                        "width": "1.75rem",
                        "height": "1.75rem",
                        "border-radius": "9999px",
                        "background": KPMG_PINK,
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "box-shadow": f"0 0 0 3px rgba(230, 0, 126, 0.3)",
                    },
                ),
                # Future step - Outline
                rx.box(
                    rx.text(
                        str(step_num),
                        style={
                            "font-size": "0.75rem",
                            "font-weight": "500",
                            "color": "rgba(255, 255, 255, 0.5)",
                        },
                    ),
                    style={
                        "width": "1.75rem",
                        "height": "1.75rem",
                        "border-radius": "9999px",
                        "background": "transparent",
                        "border": "2px solid rgba(255, 255, 255, 0.3)",
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                    },
                ),
            ),
        ),
        rx.text(
            name,
            style=rx.cond(
                TaxState.current_step == step_num,
                {
                    "font-size": "0.8rem",
                    "font-weight": "600",
                    "color": "white",
                },
                rx.cond(
                    TaxState.current_step > step_num,
                    {
                        "font-size": "0.8rem",
                        "font-weight": "500",
                        "color": EMERALD,
                    },
                    {
                        "font-size": "0.8rem",
                        "color": "rgba(255, 255, 255, 0.5)",
                    },
                ),
            ),
        ),
        spacing="2",
        align="center",
    )


def progress_connector(step_num: int) -> rx.Component:
    """Connecting line between steps."""
    return rx.box(
        style=rx.cond(
            TaxState.current_step > step_num,
            {
                "width": "1.5rem",
                "height": "2px",
                "background": EMERALD,
            },
            {
                "width": "1.5rem",
                "height": "2px",
                "background": "rgba(255, 255, 255, 0.2)",
            },
        ),
    )


def progress_bar() -> rx.Component:
    """Horizontal progress bar - transparent on navy background."""
    steps = [
        (1, "Question"),
        (2, "Categories"),
        (3, "Past Responses"),
        (4, "Documents"),
        (5, "Review"),
        (6, "Complete"),
    ]

    return rx.box(
        rx.hstack(
            *[
                rx.fragment(
                    progress_step(num, name),
                    rx.cond(
                        num < 6,
                        progress_connector(num),
                        rx.fragment(),
                    ),
                )
                for num, name in steps
            ],
            spacing="1",
            align="center",
            justify="center",
            wrap="wrap",
            style={"gap": "0.25rem"},
        ),
        style={
            "flex": "0 0 auto",
            "padding": "0.75rem 1rem",
            "background": "rgba(0, 20, 60, 0.5)",
            "backdrop-filter": "blur(8px)",
            "border-bottom": "1px solid rgba(255, 255, 255, 0.05)",
        },
    )
