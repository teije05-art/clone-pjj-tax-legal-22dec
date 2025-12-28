"""Step 5: Review Draft Component - KPMG Professional Styling."""

import reflex as rx
from ..state import TaxState
from .ui import (
    step_container, step_header, kpmg_button, warning_callout, error_callout, content_card,
    KPMG_NAVY, KPMG_PURPLE, KPMG_PINK, SLATE_200, SLATE_400, SLATE_500, SLATE_600, SLATE_700
)


def source_doc_preview(doc: dict) -> rx.Component:
    """Preview of a source document used in synthesis with KPMG styling."""
    filename = doc.get("filename", "Unknown")
    content = doc.get("content", "No content")

    return rx.accordion.item(
        header=rx.hstack(
            rx.box(
                rx.icon("file-text", size=12, color=SLATE_500),
                style={
                    "width": "1.25rem",
                    "height": "1.25rem",
                    "border-radius": "0.25rem",
                    "background": "#f1f5f9",
                    "display": "flex",
                    "align-items": "center",
                    "justify-content": "center",
                },
            ),
            rx.text(filename, style={"font-size": "0.75rem", "font-weight": "500", "color": SLATE_600}),
            width="100%",
            align="center",
            spacing="2",
        ),
        content=rx.scroll_area(
            rx.text(
                content,
                style={"font-size": "0.75rem", "color": SLATE_600, "white-space": "pre-wrap"},
            ),
            max_height="150px",
            style={"padding-right": "0.5rem"},
        ),
        value=filename,
    )


def step_5() -> rx.Component:
    """Step 5: User reviews and approves the synthesized draft with KPMG styling."""
    return step_container(
        rx.vstack(
            # Step header with gradient icon
            step_header(
                icon_name="file-check",
                title="Review Draft",
                description="Review the synthesized KPMG memorandum. Make sure all claims are accurate and properly sourced.",
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
                        rx.text("Synthesizing professional response...", style={"color": SLATE_600, "font-weight": "500"}),
                        rx.text("This may take a moment.", style={"font-size": "0.875rem", "color": SLATE_400}),
                        spacing="3",
                        align="center",
                    ),
                    style={"padding": "4rem 0", "width": "100%", "display": "flex", "justify-content": "center"},
                ),
                rx.fragment(
                    # Review warning callout
                    warning_callout("Human Review Required: Verify accuracy and completeness before approving."),

                    # Draft response display with KPMG styling
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("file-text", size=16, color=KPMG_PURPLE),
                                    style={
                                        "width": "2rem",
                                        "height": "2rem",
                                        "border-radius": "0.5rem",
                                        "background": f"rgba(109, 32, 119, 0.1)",
                                        "display": "flex",
                                        "align-items": "center",
                                        "justify-content": "center",
                                    },
                                ),
                                rx.text("Draft KPMG Memorandum", style={"font-size": "1.125rem", "font-weight": "600", "color": KPMG_NAVY}),
                                spacing="3",
                                align="center",
                            ),
                            rx.divider(style={"border-color": SLATE_200}),
                            rx.scroll_area(
                                rx.box(
                                    rx.markdown(TaxState.draft_response),
                                    style={"padding": "1rem"},
                                ),
                                max_height="400px",
                                style={"padding-right": "0.5rem"},
                            ),
                            spacing="3",
                            align="start",
                            width="100%",
                        ),
                        style={
                            "background": "white",
                            "border-radius": "0.75rem",
                            "border": f"2px solid rgba(109, 32, 119, 0.2)",
                            "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                            "overflow": "hidden",
                        },
                        width="100%",
                    ),

                    # Source documents section
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    rx.icon("book-open", size=14, color=SLATE_500),
                                    style={
                                        "width": "1.5rem",
                                        "height": "1.5rem",
                                        "border-radius": "0.25rem",
                                        "background": "#f1f5f9",
                                        "display": "flex",
                                        "align-items": "center",
                                        "justify-content": "center",
                                    },
                                ),
                                rx.text("Source Documents Used", style={"font-size": "0.875rem", "font-weight": "600", "color": SLATE_700}),
                                spacing="2",
                                align="center",
                            ),
                            rx.accordion.root(
                                rx.foreach(
                                    TaxState.selected_files,
                                    source_doc_preview,
                                ),
                                type="multiple",
                                collapsible=True,
                                width="100%",
                            ),
                            spacing="3",
                            align="start",
                            width="100%",
                        ),
                        style={
                            "background": "#f8fafc",
                            "border-radius": "0.75rem",
                            "padding": "1rem",
                            "border": f"1px solid {SLATE_200}",
                        },
                        width="100%",
                    ),
                ),
            ),

            # Error message
            rx.cond(
                TaxState.error_message != "",
                error_callout(TaxState.error_message),
                rx.fragment(),
            ),

            # Navigation buttons (only show when not loading)
            rx.cond(
                ~TaxState.is_loading,
                rx.hstack(
                    kpmg_button(
                        text="Back",
                        on_click=TaxState.go_to_step_4,
                        variant="outline",
                        icon="arrow-left",
                    ),
                    rx.hstack(
                        kpmg_button(
                            text="Regenerate",
                            on_click=TaxState.regenerate_draft,
                            variant="warning",
                            icon="refresh-cw",
                        ),
                        kpmg_button(
                            text="Approve & Finalize",
                            on_click=TaxState.approve_draft,
                            variant="success",
                            icon="check",
                            icon_right=True,
                        ),
                        spacing="3",
                    ),
                    justify="between",
                    width="100%",
                ),
                rx.fragment(),
            ),

            spacing="5",
            width="100%",
        ),
        max_width="900px",
    )
