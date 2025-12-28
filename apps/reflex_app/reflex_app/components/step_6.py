"""Step 6: Complete Component - KPMG Professional Styling."""

import reflex as rx
from ..state import TaxState
from .ui import (
    step_container, kpmg_button, success_callout, kpmg_badge,
    KPMG_NAVY, KPMG_BLUE, EMERALD, SLATE_200, SLATE_400, SLATE_500, SLATE_600
)


def source_doc_reference(doc: dict) -> rx.Component:
    """Compact source document reference with KPMG styling."""
    filename = doc.get("filename", "Unknown")
    content = doc.get("content", "No content")

    return rx.accordion.item(
        header=rx.hstack(
            rx.box(
                rx.icon("file-text", size=12, color=SLATE_400),
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
            rx.text(filename, style={"font-size": "0.75rem", "font-weight": "500", "color": SLATE_500}),
            width="100%",
            align="center",
            spacing="2",
        ),
        content=rx.scroll_area(
            rx.text(
                content,
                style={"font-size": "0.75rem", "color": SLATE_600, "white-space": "pre-wrap"},
            ),
            max_height="100px",
            style={"padding-right": "0.5rem"},
        ),
        value=filename,
    )


def step_6() -> rx.Component:
    """Step 6: Final response display with KPMG styling."""
    return step_container(
        rx.vstack(
            # Success header with gradient styling
            rx.vstack(
                rx.box(
                    rx.icon("circle-check", size=32, color="white"),
                    style={
                        "width": "4rem",
                        "height": "4rem",
                        "border-radius": "1rem",
                        "background": f"linear-gradient(to bottom right, {EMERALD}, #059669)",
                        "display": "flex",
                        "align-items": "center",
                        "justify-content": "center",
                        "box-shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                    },
                ),
                rx.heading(
                    "Tax Analysis Complete",
                    style={
                        "font-size": "1.5rem",
                        "font-weight": "700",
                        "color": "#065f46",
                    },
                ),
                rx.text(
                    "Your KPMG tax memorandum has been generated successfully.",
                    style={"color": SLATE_600},
                ),
                spacing="3",
                align="center",
            ),

            # Success callout
            success_callout("The response has been finalized. You can copy or export it below."),

            # Final response display with KPMG styling
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("file-check", size=16, color=EMERALD),
                            style={
                                "width": "2rem",
                                "height": "2rem",
                                "border-radius": "0.5rem",
                                "background": "#ecfdf5",
                                "display": "flex",
                                "align-items": "center",
                                "justify-content": "center",
                            },
                        ),
                        rx.text("Final KPMG Memorandum", style={"font-size": "1.125rem", "font-weight": "600", "color": KPMG_NAVY}),
                        rx.spacer(),
                        rx.button(
                            rx.hstack(
                                rx.icon("copy", size=14),
                                rx.text("Copy", style={"font-size": "0.875rem"}),
                                spacing="1",
                            ),
                            on_click=rx.set_clipboard(TaxState.final_response),
                            style={
                                "background": "#f1f5f9",
                                "color": SLATE_600,
                                "padding": "0.375rem 0.75rem",
                                "border-radius": "0.5rem",
                                "font-size": "0.875rem",
                                "cursor": "pointer",
                                "_hover": {"background": "#e2e8f0"},
                            },
                        ),
                        spacing="3",
                        align="center",
                        width="100%",
                    ),
                    rx.divider(style={"border-color": "#a7f3d0"}),
                    rx.scroll_area(
                        rx.box(
                            rx.markdown(TaxState.final_response),
                            style={"padding": "1rem"},
                        ),
                        max_height="450px",
                        style={"padding-right": "0.5rem"},
                    ),
                    spacing="3",
                    align="start",
                    width="100%",
                ),
                style={
                    "background": "white",
                    "border-radius": "0.75rem",
                    "border": "2px solid #a7f3d0",
                    "box-shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                    "overflow": "hidden",
                },
                width="100%",
            ),

            # Source documents reference
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("book-open", size=14, color=SLATE_400),
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
                        rx.text("Source Documents Referenced", style={"font-size": "0.875rem", "font-weight": "600", "color": SLATE_600}),
                        spacing="2",
                        align="center",
                    ),
                    rx.accordion.root(
                        rx.foreach(
                            TaxState.selected_files,
                            source_doc_reference,
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

            # Summary stats with KPMG badges
            rx.hstack(
                rx.box(
                    rx.hstack(
                        rx.icon("tags", size=12, color=KPMG_BLUE),
                        rx.text(f"{TaxState.confirmed_categories.length()} categories", style={"font-size": "0.75rem", "font-weight": "500", "color": KPMG_BLUE}),
                        spacing="1",
                        align="center",
                    ),
                    style={"background": "rgba(0, 51, 141, 0.1)", "padding": "0.375rem 0.75rem", "border-radius": "9999px"},
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("file-text", size=12, color=EMERALD),
                        rx.text(f"{TaxState.selected_file_names.length()} documents", style={"font-size": "0.75rem", "font-weight": "500", "color": EMERALD}),
                        spacing="1",
                        align="center",
                    ),
                    style={"background": "#ecfdf5", "padding": "0.375rem 0.75rem", "border-radius": "9999px"},
                ),
                rx.box(
                    rx.hstack(
                        rx.icon("hash", size=12, color=SLATE_500),
                        rx.text(f"Session: {TaxState.short_session_id}", style={"font-size": "0.75rem", "font-weight": "500", "color": SLATE_500}),
                        spacing="1",
                        align="center",
                    ),
                    style={"background": "#f1f5f9", "padding": "0.375rem 0.75rem", "border-radius": "9999px"},
                ),
                spacing="2",
                wrap="wrap",
                justify="center",
                style={"gap": "0.5rem"},
            ),

            # Action button
            rx.hstack(
                kpmg_button(
                    text="Start New Analysis",
                    on_click=TaxState.reset_workflow,
                    variant="secondary",
                    icon="rotate-ccw",
                ),
                justify="center",
                width="100%",
            ),

            spacing="6",
            width="100%",
        ),
        max_width="900px",
    )
