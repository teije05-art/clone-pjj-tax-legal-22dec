from .engine import execute_sandboxed_code
from .model import get_model_response, create_gemini_client
from .utils import (
    load_system_prompt,
    create_memory_if_not_exists,
    extract_python_code,
    format_results,
    extract_reply,
    extract_thoughts,
)
from .settings import (
    MEMORY_PATH,
    SAVE_CONVERSATION_PATH,
    MAX_TOOL_TURNS,
)
from .schemas import ChatMessage, Role, AgentResponse

from typing import Union, Tuple

import json
import os
import uuid


class Agent:
    def __init__(
        self,
        max_tool_turns: int = MAX_TOOL_TURNS,
        memory_path: str = None,
        model: str = None,
        predetermined_memory_path: bool = False,
        **kwargs  # Accept and ignore legacy use_vllm/use_fireworks parameters for backward compatibility
    ):
        # Load the system prompt and add it to the conversation history
        self.system_prompt = load_system_prompt()
        self.messages: list[ChatMessage] = [
            ChatMessage(role=Role.SYSTEM, content=self.system_prompt)
        ]

        # Set the maximum number of tool turns
        self.max_tool_turns = max_tool_turns

        # Set model: use provided model or fallback to a default (e.g., Gemini)
        self.model = model
        # Initialize Gemini client
        print(f"[Agent] Initializing Gemini client for model: {self.model}")
        self._client = create_gemini_client()
        print(f"[Agent] Gemini client initialized successfully")



        # Set memory_path: use provided path or fall back to default MEMORY_PATH
        if memory_path is not None:
            # Always place custom memory paths inside a "memory/" folder
            if predetermined_memory_path:
                self.memory_path = os.path.join("memory", memory_path)
            else:
                self.memory_path = memory_path
        else:
            # Use default MEMORY_PATH but also place it inside "memory/" folder
            self.memory_path = os.path.join("memory", MEMORY_PATH)

        # Ensure memory_path is absolute for consistency
        self.memory_path = os.path.abspath(self.memory_path)
        print(f"[Agent] Agent initialized with memory_path: {self.memory_path}")

    def _add_message(self, message: Union[ChatMessage, dict]):
        """Add a message to the conversation history."""
        if isinstance(message, dict):
            self.messages.append(ChatMessage(**message))
        elif isinstance(message, ChatMessage):
            self.messages.append(message)
        else:
            raise ValueError("Invalid message type")

    def extract_response_parts(self, response: str) -> Tuple[str, str, str]:
        """
        Extract the thoughts, reply and python code from the response.

        Args:
            response: The response from the agent.

        Returns:
            A tuple of the thoughts, reply and python code.
        """
        thoughts = extract_thoughts(response)
        reply = extract_reply(response)
        python_code = extract_python_code(response)

        return thoughts, reply, python_code

    def chat(self, message: str) -> AgentResponse:
        """
        Chat with the agent.

        Args:
            message: The message to chat with the agent.

        Returns:
            The response from the agent.
        """
        print(f"[Agent.chat] Called with message length: {len(message)}")
        # Add the user message to the conversation history
        self._add_message(ChatMessage(role=Role.USER, content=message))

        # Get the response from the agent using Fireworks client
        print(f"[Agent.chat] Calling get_model_response() with {len(self.messages)} messages")
        response = get_model_response(
            messages=self.messages,
            client=self._client,
        )
        print(f"[Agent.chat] Received response from get_model_response(): {len(response)} characters")

        # Extract the thoughts, reply and python code from the response
        thoughts, reply, python_code = self.extract_response_parts(response)

        # Execute the code from the agent's response
        result = ({}, "")
        if python_code:
            create_memory_if_not_exists(self.memory_path)
            result = execute_sandboxed_code(
                code=python_code,
                allowed_path=self.memory_path,
                import_module="pjj_tax_legal.agent.tools",
            )

        # Add the agent's response to the conversation history
        self._add_message(ChatMessage(role=Role.ASSISTANT, content=response))

        remaining_tool_turns = self.max_tool_turns
        while remaining_tool_turns > 0 and not reply:
            self._add_message(
                ChatMessage(role=Role.USER, content=format_results(result[0], result[1]))
            )
            response = get_model_response(
                messages=self.messages,
                client=self._client,
            )

            # Extract the thoughts, reply and python code from the response
            thoughts, reply, python_code = self.extract_response_parts(response)

            self._add_message(ChatMessage(role=Role.ASSISTANT, content=response))
            if python_code:
                create_memory_if_not_exists(self.memory_path)
                result = execute_sandboxed_code(
                    code=python_code,
                    allowed_path=self.memory_path,
                    import_module="pjj_tax_legal.agent.tools",
                )
            # Don't reset result here - preserve results from earlier code execution
            remaining_tool_turns -= 1

        return AgentResponse(thoughts=thoughts, reply=reply, python_block=python_code, execution_results=result[0])

    def generate_response(self, prompt: str) -> str:
        """
        Wrapper for generate_response to maintain backward compatibility with tax agents.

        This method wraps the chat() method and extracts the response text for agents
        that expect a string response (e.g., RequestCategorizer expecting JSON).

        Args:
            prompt: The prompt/message to send to the agent

        Returns:
            The reply text from the agent response. Falls back to thoughts if reply is empty.
            Returns empty string if both are empty.
        """
        print(f"[Agent.generate_response] Called with prompt length: {len(prompt)}")
        response = self.chat(prompt)

        print(f"[Agent.generate_response] Chat response - reply: {len(response.reply) if response.reply else 0}, thoughts: {len(response.thoughts) if response.thoughts else 0}")

        # Prefer reply (main response), but fallback to thoughts if reply is empty
        # This ensures JSON content is available for RequestCategorizer to parse
        if response.reply:
            print(f"[Agent.generate_response] Returning reply: {len(response.reply)} characters")
            return response.reply
        elif response.thoughts:
            print(f"[Agent.generate_response] Returning thoughts (reply was empty): {len(response.thoughts)} characters")
            return response.thoughts
        else:
            print(f"[Agent.generate_response] WARNING: Both reply and thoughts are empty")
            return ""

    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        """
        Direct LLM call WITHOUT tool loop - for synthesis/generation tasks.

        Use this for tasks that need plain text generation (like memo synthesis)
        where you don't want the MemAgent tool loop to interfere.

        Args:
            prompt: The prompt to send to the LLM
            system_prompt: Optional custom system prompt (defaults to a simple assistant prompt)

        Returns:
            The raw LLM response text
        """
        print(f"[Agent.generate_text] Called with prompt length: {len(prompt)}")

        # Use a simple system prompt for direct generation (no MemAgent instructions)
        if system_prompt is None:
            system_prompt = "You are a senior tax advisor at KPMG Vietnam. Generate professional, well-structured responses."

        # Create temporary message list (don't pollute the main conversation)
        temp_messages = [
            ChatMessage(role=Role.SYSTEM, content=system_prompt),
            ChatMessage(role=Role.USER, content=prompt)
        ]

        print(f"[Agent.generate_text] Calling get_model_response() with {len(temp_messages)} messages (direct call, no tool loop)")
        response = get_model_response(
            messages=temp_messages,
            client=self._client,
        )
        print(f"[Agent.generate_text] Received response: {len(response)} characters")

        return response

    def save_conversation(self, log: bool = False, save_folder: str = None):
        """
        Save the conversation messages to a JSON file in
        the output/conversations directory.
        """
        if not os.path.exists(SAVE_CONVERSATION_PATH):
            os.makedirs(SAVE_CONVERSATION_PATH, exist_ok=True)

        unique_id = uuid.uuid4()
        if not save_folder:
            file_path = os.path.join(SAVE_CONVERSATION_PATH, f"convo_{unique_id}.json")
        else:
            folder_path = (
                save_folder  # os.path.join(SAVE_CONVERSATION_PATH, save_folder)
            )
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            file_path = os.path.join(folder_path, f"convo_{unique_id}.json")

        # Convert the execution result messages to tool role
        messages = [
            (
                ChatMessage(role=Role.TOOL, content=message.content)
                if message.content.startswith("<result>")
                else ChatMessage(role=message.role, content=message.content)
            )
            for message in self.messages
        ]
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([message.model_dump() for message in messages], f, indent=4, ensure_ascii=False)
        except Exception as e:
            if log:
                print(f"Error saving conversation: {e}")
        if log:
            print(f"Conversation saved to {file_path}")