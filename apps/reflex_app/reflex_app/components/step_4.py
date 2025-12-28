"""Step 4: Source Documents Component - KPMG Professional Styling."""

import reflex as rx
from ..state import TaxState
from .ui import (
    step_container, step_header, kpmg_button, info_callout,
    error_callout, content_card, kpmg_badge,
    KPMG_NAVY, KPMG_PINK, EMERALD, SLATE_200, SLATE_500, SLATE_600, SLATE_700
)


def document_card(doc: dict) -> rx.Component:
    """Render a single document card with KPMG styling."""
    filename = doc.get("filename", "Unknown")
    content = doc.get("content", doc.get("summary", "No content available"))
    category = doc.get("category", "Unknown")

    return rx.accordion.item(
        header=rx.hstack(
            rx.box(
                rx.icon("file-code", size=14, color=EMERALD),
                style={
                    "width": "1.5rem",
                    "height": "1.5rem",
                    "border-radius": "0.375rem",
                    "background": "#ecfdf5",
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                },
            ),
            rx.text(filename, style={"font-size": "0.875rem", "font-weight": "500", "color": SLATE_700}),
            rx.spacer(),
            rx.box(
                rx.text(category, style={"font-size": "0.75rem", "font-weight": "500", "color": "#065f46"}),
                style={"background": "#ecfdf5", "padding": "0.125rem 0.5rem", "border-radius": "9999px"},
            ),
            width="100%",
            align="center",
            spacing="2",
        ),
        content=rx.box(
            rx.vstack(
                rx.text("Document Content:", style={
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


def step_4() -> rx.Component:
    """Step 4: User selects source documents with KPMG styling."""
    return step_container(
        rx.vstack(
            # Step header with gradient icon
            step_header(
                icon_name="database",
                title="Source Documents",
                description="Review relevant tax regulations and documents. Select the ones to include in your response.",
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
                        rx.text("Searching tax database...", style={"color": SLATE_600}),
                        spacing="3",
                        align="center",
                    ),
                    style={"padding": "3rem 0", "width": "100%", "display": "flex", "justify-content": "center"},
                ),
                rx.fragment(
                    # Results section
                    rx.cond(
                        TaxState.recommended_files.length() > 0,
                        rx.vstack(
                            # Info callout
                            info_callout(f"Found {TaxState.recommended_files.length()} relevant documents. Select the ones to use."),

                            # Preview accordion with KPMG styling
                            rx.box(
                                rx.accordion.root(
                                    rx.foreach(
                                        TaxState.recommended_files,
                                        document_card,
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
                                    rx.text("Select Documents to Use:", style={"font-size": "0.875rem", "font-weight": "600", "color": KPMG_NAVY}),
                                    rx.vstack(
                                        rx.foreach(
                                            TaxState.document_options,
                                            lambda name: rx.hstack(
                                                rx.checkbox(
                                                    checked=TaxState.selected_file_names.contains(name),
                                                    on_change=lambda checked, n=name: TaxState.toggle_file(n),
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
                                accent="green",
                            ),

                            # Selection count badge
                            rx.cond(
                                TaxState.selected_file_names.length() > 0,
                                rx.box(
                                    rx.hstack(
                                        rx.icon("check", size=14, color=EMERALD),
                                        rx.text(
                                            f"{TaxState.selected_file_names.length()} documents selected",
                                            style={"font-size": "0.875rem", "font-weight": "500", "color": "#065f46"},
                                        ),
                                        spacing="2",
                                        align="center",
                                    ),
                                    style={
                                        "background": "#ecfdf5",
                                        "border": "1px solid #a7f3d0",
                                        "border-radius": "0.5rem",
                                        "padding": "0.5rem 0.75rem",
                                    },
                                ),
                                rx.fragment(),
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        # No results
                        error_callout("No relevant documents found in the tax database."),
                    ),
                ),
            ),

            # Navigation buttons (only show when not loading)
            rx.cond(
                ~TaxState.is_loading,
                rx.hstack(
                    kpmg_button(
                        text="Back",
                        on_click=TaxState.go_to_step_3,
                        variant="outline",
                        icon="arrow-left",
                    ),
                    kpmg_button(
                        text="Synthesize Response",
                        on_click=TaxState.synthesize_response,
                        variant="primary",
                        icon="sparkles",
                        icon_right=True,
                        disabled=TaxState.selected_file_names.length() == 0,
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
