from pydantic import BaseModel

from typing import Optional, Union

from .settings import GEMINI_MODEL
from .schemas import ChatMessage, Role

# Import Google Gemini AI
import google.generativeai as genai


# Import Vertex AI only if needed (for genai client with vertexai=True)
try:
    import vertexai
    VERTEXAI_AVAILABLE = True
except ImportError:
    VERTEXAI_AVAILABLE = False


def create_gemini_client():
    """Create a new Google Gemini client instance (primary backend)."""
    if not VERTEXAI_AVAILABLE:
        raise ImportError(
            "Vertex AI package not installed. Run: pip install --upgrade google-cloud-aiplatform"
        )
    
    try:
        # Initialize Vertex AI for the project and location
        vertexai.init(project="gen-lang-client-0209516002", location="us-central1")

        # Return a configured GenerativeModel instance for the specific model.
        # The model will use the Vertex AI context from vertexai.init().
        client = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
        )
        return client
    except Exception as e:
        raise ValueError(
            f"Failed to initialize Gemini client via Vertex AI: {str(e)}. "
            f"Check Vertex AI project/location and permissions."
        )


def _as_gemini_message(msg: Union[ChatMessage, dict]) -> dict:
    """
    Accept ChatMessage or raw dict and return a dict in Gemini's message format.
    Gemini message format: {"role": "...", "parts": ["..."]}
    """
    if isinstance(msg, ChatMessage):
        # Map roles: USER to "user", ASSISTANT to "model".
        # System messages are often handled differently in Gemini chat,
        # but for direct conversion, map to "user" or filter out as appropriate
        # for the specific model's expectation.
        # For now, mapping ASSISTANT role to "model", USER to "user".
        # System role can be problematic here if not pre-processed.
        role_map = {Role.USER: "user", Role.ASSISTANT: "model", Role.TOOL: "user"} # Assuming TOOL results are user-like input
        role = role_map.get(msg.role, "user") # Default to user if role is not mapped
        return {"role": role, "parts": [{"text": msg.content}]}
    elif isinstance(msg, dict):
        # If it's already a dict, assume it has 'role' and 'content' similar to ChatMessage
        role_map = {"user": "user", "assistant": "model", "tool": "user", "system": "user"}
        role = role_map.get(msg.get("role", "user"), "user")
        return {"role": role, "parts": [{"text": msg.get("content", "")}]}
    else:
        raise ValueError("Invalid message type")

def get_model_response(
        messages: Optional[list[ChatMessage]] = None,
        message: Optional[str] = None,
        system_prompt: Optional[str] = None,
        client: Optional[genai.GenerativeModel] = None,
) -> str:
    """
    Get a response from Fireworks AI model with streaming enabled for large outputs.

    Args:
        messages: A list of ChatMessage objects (optional).
        message: A single message string (optional).
        system_prompt: A system prompt for the model (optional).
        client: Optional Fireworks LLM client. If None, creates a new one.

    Returns:
        A string response from the model.
    """
    if messages is None and message is None:
        raise ValueError("Either 'messages' or 'message' must be provided.")

    # Use provided client or create a new Fireworks client
    if client is None:
        client = create_gemini_client()

    # Prepare messages for Gemini
    gemini_history = []
    current_prompt_message_content = ""
    system_instruction_content = None

    if messages is None:
        # If no message list is provided, create one for the current single message
        if system_prompt:
            system_instruction_content = system_prompt
        current_prompt_message_content = message
    else:
        # Process the full message list
        for msg_obj in messages:
            if msg_obj.role == Role.SYSTEM:
                system_instruction_content = msg_obj.content
            else:
                gemini_formatted_msg = _as_gemini_message(msg_obj)
                # The last message is the current user's prompt, others are history
                if msg_obj == messages[-1]:
                    current_prompt_message_content = gemini_formatted_msg["parts"][0]["text"]
                else:
                    gemini_history.append(gemini_formatted_msg)

    # Re-initialize client if system instruction needs to be applied, or if client is None
    if system_instruction_content:
        # Configure genai globally with the system instruction
        # GEMINI_API_KEY is no longer used for configuration with Vertex AI
        client = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_instruction_content
        )
    elif client is None:
        # If no system instruction, and client not provided, create a default client
        client = create_gemini_client()


    # Call Gemini AI with streaming enabled for large outputs
    parts: list[str] = []
    chunk_count = 0
    try:
        chat_session = client.start_chat(history=gemini_history)
        stream = chat_session.send_message(current_prompt_message_content, stream=True)

        for chunk in stream:
            chunk_count += 1
            if chunk.text:
                parts.append(chunk.text)

    except Exception as e:
        # Log streaming errors but don't fail - we may have partial response
        print(f"[Gemini API] Streaming error (continuing with {len(parts)} chunks): {type(e).__name__}: {str(e)}")

    result = "".join(parts)

    # Log completion
    if result:
        print(f"[Gemini API] Response received: {len(result)} characters, {chunk_count} chunks")
    else:
        print(f"[Gemini API] WARNING: Empty response after {chunk_count} chunks - streaming may have failed")

    return result
