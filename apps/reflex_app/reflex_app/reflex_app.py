"""
KPMG Tax Workflow System - Reflex Frontend

A professional 6-step tax analysis workflow:
    Step 1: Enter Question      - User submits tax question
    Step 2: Confirm Categories  - User confirms tax categories
    Step 3: Past Responses      - Select relevant past memoranda
    Step 4: Source Documents    - Select tax regulations
    Step 5: Review Draft        - Review synthesized response
    Step 6: Complete            - Final response display

Run with:
    cd apps/reflex_app
    reflex run
"""

import reflex as rx

from .state import TaxState
from .components.header import header
from .components.progress import progress_bar
from .components.step_1 import step_1
from .components.step_2 import step_2
from .components.step_3 import step_3
from .components.step_4 import step_4
from .components.step_5 import step_5
from .components.step_6 import step_6

# KPMG Brand Colors
KPMG_NAVY = "#00338D"
KPMG_PINK = "#E6007E"
KPMG_PURPLE = "#6D2077"


def index() -> rx.Component:
    """Main page with KPMG professional styling - Single page, no scroll."""
    return rx.box(
        # Deep navy background with subtle magenta glow in corner
        rx.box(
            style={
                "position": "fixed",
                "inset": "0",
                "z-index": "-1",
                "background": KPMG_NAVY,
            },
        ),
        # Subtle magenta glow in bottom-right corner
        rx.box(
            style={
                "position": "fixed",
                "bottom": "-20%",
                "right": "-10%",
                "width": "50%",
                "height": "50%",
                "z-index": "-1",
                "background": f"radial-gradient(circle, rgba(230, 0, 126, 0.15) 0%, transparent 70%)",
                "pointer-events": "none",
            },
        ),
        # Subtle purple glow in top-left corner
        rx.box(
            style={
                "position": "fixed",
                "top": "-10%",
                "left": "-10%",
                "width": "40%",
                "height": "40%",
                "z-index": "-1",
                "background": f"radial-gradient(circle, rgba(109, 32, 119, 0.1) 0%, transparent 70%)",
                "pointer-events": "none",
            },
        ),
        # Header with KPMG branding
        header(),
        # Progress bar
        progress_bar(),
        # Main content area - flex: 1 to fill remaining space
        rx.box(
            rx.cond(TaxState.current_step == 1, step_1()),
            rx.cond(TaxState.current_step == 2, step_2()),
            rx.cond(TaxState.current_step == 3, step_3()),
            rx.cond(TaxState.current_step == 4, step_4()),
            rx.cond(TaxState.current_step == 5, step_5()),
            rx.cond(TaxState.current_step == 6, step_6()),
            style={
                "flex": "1",
                "display": "flex",
                "align-items": "center",
                "justify-content": "center",
                "overflow-y": "auto",
                "padding": "1rem",
            },
        ),
        # Footer with Jupiter branding
        rx.box(
            rx.hstack(
                rx.text(
                    "KPMG Tax Workflow System",
                    style={
                        "font-size": "0.8rem",
                        "font-weight": "500",
                        "color": "rgba(255, 255, 255, 0.7)",
                    },
                ),
                rx.box(
                    style={
                        "width": "1px",
                        "height": "1rem",
                        "background": "rgba(255, 255, 255, 0.2)",
                    },
                ),
                rx.hstack(
                    rx.text(
                        "Powered by",
                        style={
                            "font-size": "0.8rem",
                            "color": "rgba(255, 255, 255, 0.5)",
                        },
                    ),
                    rx.box(
                        rx.text(
                            "Jupiter",
                            style={
                                "font-size": "0.8rem",
                                "font-weight": "700",
                                "color": "white",
                            },
                        ),
                        style={
                            "background": f"linear-gradient(135deg, {KPMG_PINK}, {KPMG_PURPLE})",
                            "padding": "0.2rem 0.6rem",
                            "border-radius": "9999px",
                        },
                    ),
                    spacing="2",
                    align="center",
                ),
                spacing="4",
                align="center",
                justify="center",
            ),
            style={
                "flex": "0 0 auto",
                "padding": "1rem 0",
                "background": "rgba(0, 20, 60, 0.8)",
                "backdrop-filter": "blur(8px)",
                "border-top": "1px solid rgba(255, 255, 255, 0.05)",
            },
        ),
        # Main container - 100vh, no scroll, flex column
        style={
            "height": "100vh",
            "overflow": "hidden",
            "display": "flex",
            "flex-direction": "column",
        },
    )


# Create app with KPMG styling
app = rx.App(
    theme=rx.theme(
        accent_color="blue",
        gray_color="slate",
        radius="medium",
        scaling="100%",
    ),
    stylesheets=[
        "/styles/kpmg-theme.css",
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
    ],
)

app.add_page(index, title="KPMG Tax Workflow System")
