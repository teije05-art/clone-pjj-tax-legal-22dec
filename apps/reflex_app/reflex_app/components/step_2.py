"""Step 2: Confirm Categories Component - KPMG Professional Styling."""

import reflex as rx
from ..state import TaxState
from .ui import (
    step_container, step_header, kpmg_button, info_callout,
    error_callout, warning_callout, content_card, kpmg_badge,
    KPMG_NAVY, KPMG_BLUE, KPMG_PURPLE, KPMG_PINK, SLATE_600, SLATE_700
)


def category_badge(category: str) -> rx.Component:
    """Render a single category badge with KPMG styling."""
    return rx.box(
        rx.text(category, style={"font-size": "0.875rem", "font-weight": "500"}),
        style={
            "background": f"linear-gradient(to right, rgba(0, 51, 141, 0.1), rgba(109, 32, 119, 0.1))",
            "color": KPMG_NAVY,
            "padding": "0.375rem 0.75rem",
            "border-radius": "9999px",
            "border": "1px solid rgba(0, 51, 141, 0.2)",
        },
    )


def step_2() -> rx.Component:
    """Step 2: User confirms suggested categories with KPMG styling."""
    return step_container(
        rx.vstack(
            # Step header with gradient icon
            step_header(
                icon_name="tags",
                title="Confirm Categories",
                description="Review the suggested tax categories. Adjust the selection if needed before searching.",
            ),

            # User review callout
            warning_callout("User Review Required: Confirm the categories to use for searching."),

            # Show the question being analyzed
            content_card(
                rx.vstack(
                    rx.text("Your Question:", style={"font-size": "0.875rem", "font-weight": "600", "color": KPMG_NAVY}),
                    rx.text(
                        TaxState.request_text,
                        style={"color": SLATE_600, "white-space": "pre-wrap"},
                    ),
                    spacing="2",
                    align="start",
                    width="100%",
                ),
                accent="slate",
            ),

            # Suggested categories display
            content_card(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("sparkles", size=16, color=KPMG_PURPLE),
                            style={
                                "width": "1.5rem",
                                "height": "1.5rem",
                                "border-radius": "0.375rem",
                                "background": f"rgba(109, 32, 119, 0.1)",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                            },
                        ),
                        rx.text("AI Suggested Categories", style={"font-size": "0.875rem", "font-weight": "600", "color": KPMG_NAVY}),
                        spacing="2",
                        align="center",
                    ),
                    rx.hstack(
                        rx.foreach(
                            TaxState.suggested_categories,
                            category_badge,
                        ),
                        wrap="wrap",
                        spacing="2",
                        style={"gap": "0.5rem"},
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                accent="purple",
            ),

            # Category selection
            content_card(
                rx.vstack(
                    rx.text("Select Categories to Use:", style={"font-size": "0.875rem", "font-weight": "600", "color": KPMG_NAVY}),
                    rx.vstack(
                        rx.foreach(
                            TaxState.suggested_categories,
                            lambda cat: rx.hstack(
                                rx.checkbox(
                                    checked=TaxState.confirmed_categories.contains(cat),
                                    on_change=lambda checked, c=cat: TaxState.toggle_category(c),
                                ),
                                rx.text(cat, style={"font-size": "0.875rem", "color": SLATE_700}),
                                spacing="2",
                                align="center",
                            ),
                        ),
                        spacing="3",
                        align="start",
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                accent="blue",
            ),

            # Error message
            rx.cond(
                TaxState.error_message != "",
                error_callout(TaxState.error_message),
                rx.fragment(),
            ),

            # Navigation buttons
            rx.hstack(
                kpmg_button(
                    text="Back",
                    on_click=TaxState.go_to_step_1,
                    variant="outline",
                    icon="arrow-left",
                ),
                kpmg_button(
                    text=rx.cond(TaxState.is_loading, "Searching...", "Confirm & Search"),
                    on_click=TaxState.confirm_categories,
                    variant="primary",
                    icon="search",
                    icon_right=True,
                    disabled=TaxState.is_loading,
                    loading=TaxState.is_loading,
                ),
                justify="between",
                width="100%",
            ),

            spacing="5",
            width="100%",
        ),
    )
