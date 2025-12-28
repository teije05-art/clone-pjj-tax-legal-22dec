"""KPMG Header Component - Professional Glassmorphism Design."""

import reflex as rx
from ..state import TaxState

# KPMG Brand Colors
KPMG_NAVY = "#00338D"
KPMG_PINK = "#E6007E"
KPMG_PURPLE = "#6D2077"


def header() -> rx.Component:
    """KPMG branded header with glassmorphism effect."""
    return rx.box(
        # Content container
        rx.hstack(
            # Logo and title section - no white box, direct placement
            rx.hstack(
                # KPMG Logo - directly on glass header
                rx.image(
                    src="/kpmg-logo.svg",
                    height="48px",
                    alt="KPMG",
                    style={
                        "filter": "brightness(0) invert(1)",  # Make logo white
                    },
                ),
                rx.box(
                    style={
                        "width": "1px",
                        "height": "2rem",
                        "background": "rgba(255, 255, 255, 0.3)",
                        "margin": "0 0.75rem",
                    },
                ),
                rx.vstack(
                    rx.text(
                        "Tax Workflow System",
                        style={
                            "font-weight": "700",
                            "font-size": "1.125rem",
                            "color": "white",
                            "letter-spacing": "-0.025em",
                        },
                    ),
                    rx.text(
                        "Intelligent tax analysis",
                        style={
                            "font-size": "0.75rem",
                            "color": "rgba(255, 255, 255, 0.7)",
                        },
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="0",
                align="center",
            ),
            # Right side - Step indicator and controls
            rx.hstack(
                # Current step badge (pink accent)
                rx.box(
                    rx.hstack(
                        rx.text(
                            f"Step {TaxState.current_step}",
                            style={
                                "font-size": "0.875rem",
                                "font-weight": "700",
                                "color": "white",
                            },
                        ),
                        rx.text(
                            TaxState.current_step_name,
                            style={
                                "font-size": "0.875rem",
                                "color": "rgba(255, 255, 255, 0.9)",
                            },
                        ),
                        spacing="1",
                    ),
                    style={
                        "background": KPMG_PINK,
                        "padding": "0.375rem 1rem",
                        "border-radius": "9999px",
                    },
                ),
                # Session ID
                rx.box(
                    rx.text(
                        f"Session: {TaxState.short_session_id}",
                        style={
                            "font-size": "0.75rem",
                            "color": "rgba(255, 255, 255, 0.7)",
                        },
                    ),
                    style={
                        "background": "rgba(255, 255, 255, 0.1)",
                        "padding": "0.375rem 0.75rem",
                        "border-radius": "9999px",
                    },
                ),
                # Reset button
                rx.button(
                    rx.hstack(
                        rx.icon("rotate-ccw", size=14, color="white"),
                        rx.text("Reset", style={"font-size": "0.875rem", "color": "white"}),
                        spacing="1",
                    ),
                    on_click=TaxState.reset_workflow,
                    style={
                        "background": "rgba(255, 255, 255, 0.1)",
                        "border": "1px solid rgba(255, 255, 255, 0.2)",
                        "border-radius": "0.5rem",
                        "padding": "0.375rem 0.75rem",
                        "cursor": "pointer",
                        "_hover": {
                            "background": "rgba(255, 255, 255, 0.2)",
                        },
                    },
                ),
                spacing="3",
                align="center",
            ),
            justify="between",
            width="100%",
            align="center",
            style={
                "max-width": "80rem",
                "margin": "0 auto",
                "padding": "0 1.5rem",
            },
        ),
        style={
            "position": "relative",
            "z-index": "100",
            "padding": "1rem 0",
            # Glassmorphism effect
            "background": "rgba(0, 51, 141, 0.3)",
            "backdrop-filter": "blur(12px)",
            "-webkit-backdrop-filter": "blur(12px)",
            "border-bottom": "1px solid rgba(255, 255, 255, 0.1)",
        },
    )
