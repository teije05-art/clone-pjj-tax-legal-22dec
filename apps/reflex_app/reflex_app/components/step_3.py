"""Step 3: Past Responses Component - KPMG Professional Styling."""

import reflex as rx
from ..state import TaxState
from .ui import (
    step_container, step_header, kpmg_button, info_callout,
    warning_callout, content_card,
    KPMG_NAVY, KPMG_BLUE, KPMG_PINK, SLATE_200, SLATE_500, SLATE_600, SLATE_700
)


def past_response_card(response: dict) -> rx.Component:
    """Render a single past response card with KPMG styling."""
    filename = response.get("filename", "Unknown")
    content = response.get("content", response.get("summary", "No content available"))

    return rx.accordion.item(
        header=rx.hstack(
            rx.box(
                rx.icon("file-text", size=14, color=KPMG_BLUE),
                style={
                    "width": "1.5rem",
                    "height": "1.5rem",
                    "border-radius": "0.375rem",
                    "background": f"rgba(0, 51, 141, 0.1)",
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                },
            ),
            rx.text(filename, style={"font-size": "0.875rem", "font-weight": "500", "color": SLATE_700}),
            width="100%",
            align="center",
            spacing="2",
        ),
        content=rx.box(
            rx.vstack(
                rx.text("Relevant Content:", style={
                    "font-size": "0.75rem",
                    "font-weight": "600",
                    "color": SLATE_500,
                    "text-transform": "uppercase",
                    "letter-spacing": "0.05em",
                }),
                rx.scroll_area(
                    rx.text(
                        content,
                        style={"font-size": "0.875rem", "color": SLATE_600, "white-space": "pre-wrap"},
                    ),
                    max_height="200px",
                    style={"padding-right": "0.5rem"},
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            style={
                "background": "#f8fafc",
                "border-radius": "0.5rem",
                "padding": "0.75rem",
                "border": f"1px solid {SLATE_200}",
            },
        ),
        value=filename,
        style={"border-bottom": f"1px solid {SLATE_200}"},
    )


def step_3() -> rx.Component:
    """Step 3: User selects relevant past responses with KPMG styling."""
    return step_container(
        rx.vstack(
            # Step header with gradient icon
            step_header(
                icon_name="history",
                title="Past Responses",
                description="Review similar past tax memoranda. Select any that are relevant to your question.",
            ),

            # Loading state
            rx.cond(
                TaxState.is_loading,
                rx.box(
                    rx.vstack(
                        rx.box(
                            rx.spinner(size="3"),
                            style={"color": KPMG_PINK},
                        ),
                        rx.text("Searching past responses...", style={"color": SLATE_600}),
                        spacing="3",
                        align="center",
                    ),
                    style={"padding": "3rem 0", "width": "100%", "display": "flex", "justify-content": "center"},
                ),
                rx.fragment(
                    # Results section
                    rx.cond(
                        TaxState.past_responses.length() > 0,
                        rx.vstack(
                            # Info callout
                            info_callout(f"Found {TaxState.past_responses.length()} past responses. Preview and select relevant ones."),

                            # Preview accordion with KPMG styling
                            rx.box(
                                rx.accordion.root(
                                    rx.foreach(
                                        TaxState.past_responses,
                                        past_response_card,
                                    ),
                                    type="multiple",
                                    collapsible=True,
                                    width="100%",
                                ),
                                style={
                                    "background": "white",
                                    "border-radius": "0.75rem",
                                    "border": f"1px solid {SLATE_200}",
                                    "overflow": "hidden",
                                },
                                width="100%",
                            ),

                            # Selection checkboxes
                            content_card(
                                rx.vstack(
                                    rx.text("Select Responses to Use:", style={"font-size": "0.875rem", "font-weight": "600", "color": KPMG_NAVY}),
                                    rx.vstack(
                                        rx.foreach(
                                            TaxState.past_response_options,
                                            lambda name: rx.hstack(
                                                rx.checkbox(
                                                    checked=TaxState.selected_past_response_names.contains(name),
                                                    on_change=lambda checked, n=name: TaxState.toggle_past_response(n),
                                                ),
                                                rx.text(name, style={"font-size": "0.875rem", "color": SLATE_700}),
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
                            spacing="4",
                            width="100%",
                        ),
                        # No results
                        info_callout("No similar past responses found. You can continue to search the tax database."),
                    ),
                ),
            ),

            # Navigation buttons (only show when not loading)
            rx.cond(
                ~TaxState.is_loading,
                rx.hstack(
                    kpmg_button(
                        text="Back",
                        on_click=TaxState.go_to_step_2,
                        variant="outline",
                        icon="arrow-left",
                    ),
                    kpmg_button(
                        text="Search Documents",
                        on_click=TaxState.proceed_to_documents,
                        variant="primary",
                        icon="database",
                        icon_right=True,
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.fragment(),
            ),

            spacing="5",
            width="100%",
        ),
        max_width="800px",
    )
