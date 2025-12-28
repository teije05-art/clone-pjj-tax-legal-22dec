"""Step 1: Enter Question Component - KPMG Professional Styling."""

import reflex as rx
from ..state import TaxState
from .ui import step_container, step_header, kpmg_button, info_callout, error_callout, styled_text_area


def step_1() -> rx.Component:
    """Step 1: User enters their tax question with KPMG styling."""
    return step_container(
        rx.vstack(
            # Step header with gradient icon
            step_header(
                icon_name="message-square",
                title="Enter Tax Question",
                description="Submit your tax question for analysis. Our AI will categorize it and search for relevant information from the tax database.",
            ),

            # Info callout
            info_callout("Enter your question below to get started with the analysis."),

            # Text area with enhanced styling
            styled_text_area(
                placeholder="E.g., We have a Vietnam subsidiary that imports pharmaceutical products. What are the key transfer pricing considerations for intra-group transactions?",
                value=TaxState.request_text,
                on_change=TaxState.set_request_text,
            ),

            # Error message
            rx.cond(
                TaxState.error_message != "",
                error_callout(TaxState.error_message),
                rx.fragment(),
            ),

            # Submit button
            kpmg_button(
                text=rx.cond(TaxState.is_loading, "Analyzing...", "Submit & Analyze"),
                on_click=TaxState.submit_question,
                variant="primary",
                icon="send",
                icon_right=True,
                disabled=TaxState.is_loading,
                loading=TaxState.is_loading,
                full_width=True,
            ),

            spacing="5",
            width="100%",
        ),
    )
