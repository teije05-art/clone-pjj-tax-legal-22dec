"""
Base Agent - Common functionality for all specialized agents

This module provides the foundation for all agent types in the system.
All agents inherit from BaseAgent to ensure consistent behavior and logging.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

# Clean package imports (no sys.path hacks needed)
from pjj_tax_legal.agent import Agent


@dataclass
class AgentResult:
    """Standard result format for all agent operations

    PHASE 1 (Nov 5, 2025): Added deliverables field for executor to return Deliverable objects
    """
    success: bool
    output: Any  # Changed from str to Any to support both text and Deliverable lists (Phase 1)
    metadata: Dict[str, Any]
    timestamp: str
    error: str = ""  # FIXED (Oct 31, 2025): Added explicit error field for better error handling
    deliverables: Any = None  # PHASE 1 (Nov 5): For executor to pass Deliverable objects to generator


class BaseAgent:
    """Base class for all specialized agents

    Provides common functionality:
    - Logging and coordination tracking
    - Standard result wrapping
    - Memory access
    """

    def __init__(self, agent: Agent, memory_path: Path):
        """
        Initialize base agent

        Args:
            agent: The MemAgent instance
            memory_path: Path to memory directory
        """
        self.agent = agent
        self.memory_path = memory_path
        self.agent_type = self.__class__.__name__

    def _log_agent_action(self, action: str, result: AgentResult):
        """Log agent actions to MemAgent for coordination tracking

        Args:
            action: Description of the action performed
            result: AgentResult from the action
        """
        log_entry = f"""
## {self.agent_type} Action - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Action:** {action}
**Success:** {result.success}
**Output:** {result.output[:200]}...
**Metadata:** {result.metadata}

---
"""

        # Store in agent coordination log
        # Convert to Path if it's a string
        memory_path = Path(self.memory_path) if isinstance(self.memory_path, str) else self.memory_path
        coordination_file = memory_path / "entities" / "agent_coordination.md"
        try:
            if coordination_file.exists():
                with open(coordination_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            else:
                coordination_file.write_text(f"# Agent Coordination Log\n\n{log_entry}")
        except Exception as e:
            print(f"   ⚠️ Failed to log agent action: {e}")

    def _wrap_result(self, success: bool, output: str, metadata: Dict[str, Any]) -> AgentResult:
        """Wrap agent output in standard AgentResult format

        Args:
            success: Whether operation succeeded
            output: Agent output text
            metadata: Additional metadata about the operation

        Returns:
            AgentResult with standard format
        """
        return AgentResult(
            success=success,
            output=output,
            metadata=metadata,
            timestamp=datetime.now().isoformat()
        )

    def _handle_error(self, action: str, error: Exception) -> AgentResult:
        """Handle errors consistently across all agents

        FIXED (Oct 31, 2025): Now populates both error field and metadata for consistency

        Args:
            action: Name of the action that failed
            error: The exception that was raised

        Returns:
            AgentResult indicating failure with error details
        """
        import traceback
        error_details = traceback.format_exc()
        error_msg = f"{action} failed: {str(error)}"

        # Print for terminal debugging
        print(f"   ❌ {error_msg}")
        print(f"   Error type: {type(error).__name__}")

        error_result = AgentResult(
            success=False,
            output=error_msg,
            error=str(error),  # FIXED: Now set in error field
            metadata={
                "error": str(error),
                "error_type": type(error).__name__,
                "full_traceback": error_details,
                "action": action
            },
            timestamp=datetime.now().isoformat()
        )

        self._log_agent_action(action, error_result)
        return error_result
