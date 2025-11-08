"""Claude AI Assistant integration module."""

import os
from typing import List, Dict, Optional
from anthropic import Anthropic
from rich.console import Console


class ClaudeAssistant:
    """Claude AI personal assistant."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1024,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize Claude AI assistant.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
            max_tokens: Maximum tokens in response
            system_prompt: System prompt to set assistant behavior
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self.model = model
        self.max_tokens = max_tokens

        # Default system prompt for a helpful voice assistant
        self.system_prompt = system_prompt or (
            "You are a helpful, friendly AI voice assistant. "
            "Provide concise, clear responses that are easy to understand when spoken aloud. "
            "Keep your answers brief but informative. "
            "Be conversational and natural in your responses."
        )

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []

    def chat(
        self,
        message: str,
        use_history: bool = True,
        temperature: float = 1.0,
    ) -> str:
        """
        Send a message to Claude and get a response.

        Args:
            message: User message
            use_history: Whether to include conversation history
            temperature: Response randomness (0-1)

        Returns:
            Assistant's response text
        """
        try:
            # Build messages list
            if use_history and self.conversation_history:
                messages = self.conversation_history.copy()
                messages.append({"role": "user", "content": message})
            else:
                messages = [{"role": "user", "content": message}]

            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=temperature,
                system=self.system_prompt,
                messages=messages,
            )

            # Extract response text
            response_text = response.content[0].text

            # Update conversation history
            if use_history:
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": response_text})

            return response_text

        except Exception as e:
            raise RuntimeError(f"Failed to get Claude response: {e}")

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.

        Returns:
            List of message dictionaries
        """
        return self.conversation_history.copy()

    def set_system_prompt(self, prompt: str):
        """
        Update the system prompt.

        Args:
            prompt: New system prompt
        """
        self.system_prompt = prompt

    def get_conversation_summary(self) -> str:
        """
        Get a summary of the conversation.

        Returns:
            Formatted conversation summary
        """
        if not self.conversation_history:
            return "No conversation history."

        summary = []
        for msg in self.conversation_history:
            role = msg["role"].capitalize()
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            summary.append(f"{role}: {content}")

        return "\n".join(summary)


class ConversationManager:
    """Manage conversation state and flow for voice assistant."""

    def __init__(self, assistant: ClaudeAssistant):
        """
        Initialize conversation manager.

        Args:
            assistant: Claude assistant instance
        """
        self.assistant = assistant
        self.is_listening = False
        self.last_user_input = ""
        self.last_assistant_response = ""

    def process_voice_input(self, transcribed_text: str) -> Optional[str]:
        """
        Process voice input and generate response.

        Args:
            transcribed_text: Text from speech-to-text

        Returns:
            Assistant's response or None if input is empty
        """
        # Clean up the transcribed text
        text = transcribed_text.strip()

        if not text:
            return None

        # Store user input
        self.last_user_input = text

        # Check for special commands
        if self._is_exit_command(text):
            return "Goodbye! It was nice talking to you."

        if self._is_clear_command(text):
            self.assistant.clear_history()
            return "I've cleared our conversation history. What would you like to talk about?"

        # Get response from Claude
        try:
            response = self.assistant.chat(text)
            self.last_assistant_response = response
            return response
        except Exception as e:
            return f"I'm sorry, I encountered an error: {str(e)}"

    def _is_exit_command(self, text: str) -> bool:
        """Check if text is an exit command."""
        exit_phrases = [
            "goodbye", "bye", "exit", "quit", "stop",
            "see you", "talk to you later", "goodbye claude"
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in exit_phrases)

    def _is_clear_command(self, text: str) -> bool:
        """Check if text is a clear history command."""
        clear_phrases = ["clear history", "reset conversation", "start over", "new conversation"]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in clear_phrases)

    def get_status(self) -> dict:
        """
        Get current conversation status.

        Returns:
            Dictionary with conversation status
        """
        return {
            'is_listening': self.is_listening,
            'last_user_input': self.last_user_input,
            'last_assistant_response': self.last_assistant_response,
            'history_length': len(self.assistant.conversation_history),
        }


def create_assistant(
    api_key: Optional[str] = None,
    personality: str = "helpful",
) -> ClaudeAssistant:
    """
    Factory function to create a Claude assistant with predefined personality.

    Args:
        api_key: Anthropic API key
        personality: Personality type (helpful, concise, friendly, professional)

    Returns:
        Configured ClaudeAssistant instance
    """
    personalities = {
        "helpful": (
            "You are a helpful AI voice assistant. Provide clear, informative responses "
            "that are conversational and easy to understand when spoken aloud."
        ),
        "concise": (
            "You are a concise AI voice assistant. Give brief, to-the-point answers. "
            "Limit responses to 1-2 sentences unless more detail is specifically requested."
        ),
        "friendly": (
            "You are a friendly, warm AI voice assistant. Be conversational, use a casual tone, "
            "and make users feel comfortable. Show enthusiasm when appropriate."
        ),
        "professional": (
            "You are a professional AI voice assistant. Provide accurate, well-structured responses "
            "in a polite and formal tone. Be thorough but efficient."
        ),
        "lofi": (
            "You are a chill, relaxed AI voice assistant with a lofi vibe. "
            "Keep responses calm, friendly, and laid-back. Think of yourself as a helpful friend "
            "who's there to chat and assist without any pressure. Use a conversational, easygoing tone."
        ),
    }

    system_prompt = personalities.get(personality, personalities["helpful"])

    return ClaudeAssistant(
        api_key=api_key,
        system_prompt=system_prompt,
    )
