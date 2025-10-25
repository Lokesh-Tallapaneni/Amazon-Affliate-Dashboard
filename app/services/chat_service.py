"""
Chat service for AI-powered data exploration.

This module handles LangChain CSV agent for natural language queries
with support for multiple AI providers: OpenAI, Google Gemini, and Anthropic Claude.
"""

import logging
import os
from typing import Optional, Dict, Any

from langchain_experimental.agents.agent_toolkits import create_csv_agent

logger = logging.getLogger(__name__)


class ChatService:
    """Service class for AI chat operations with multi-provider support."""

    SUPPORTED_PROVIDERS = ['openai', 'gemini', 'anthropic']

    def __init__(self, config):
        """
        Initialize ChatService.

        Args:
            config: Application configuration object
        """
        self.config = config
        self._agent = None
        self._current_provider = None

        # Set up API keys from config
        self._setup_api_keys(config)

    def _setup_api_keys(self, config):
        """Set up API keys for all supported providers."""
        # Handle both Flask config dict and config class
        def get_config_value(key):
            return config.get(key) if hasattr(config, 'get') else getattr(config, key, None)

        # OpenAI
        openai_key = get_config_value('OPENAI_API_KEY')
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key

        # Google Gemini
        gemini_key = get_config_value('GOOGLE_API_KEY')
        if gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key

        # Anthropic
        anthropic_key = get_config_value('ANTHROPIC_API_KEY')
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key

    def detect_available_provider(self) -> Optional[str]:
        """
        Detect which AI provider is available based on API keys.

        Returns:
            str: Provider name ('openai', 'gemini', 'anthropic') or None
        """
        # Check in order of preference
        if os.environ.get("OPENAI_API_KEY"):
            return 'openai'
        elif os.environ.get("GOOGLE_API_KEY"):
            return 'gemini'
        elif os.environ.get("ANTHROPIC_API_KEY"):
            return 'anthropic'
        return None

    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about available providers.

        Returns:
            dict: Provider availability and current provider
        """
        return {
            'available_providers': {
                'openai': bool(os.environ.get("OPENAI_API_KEY")),
                'gemini': bool(os.environ.get("GOOGLE_API_KEY")),
                'anthropic': bool(os.environ.get("ANTHROPIC_API_KEY"))
            },
            'current_provider': self._current_provider,
            'has_any_provider': self.detect_available_provider() is not None
        }

    def _create_llm(self, provider: str):
        """
        Create LLM instance for the specified provider.

        Args:
            provider (str): Provider name ('openai', 'gemini', 'anthropic')

        Returns:
            LLM instance

        Raises:
            ValueError: If provider is not supported or API key not found
        """
        if provider == 'openai':
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY not set")

            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7
            )

        elif provider == 'gemini':
            if not os.environ.get("GOOGLE_API_KEY"):
                raise ValueError("GOOGLE_API_KEY not set")

            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",  # Latest stable Flash model (fast & cost-effective)
                temperature=0.7,
                convert_system_message_to_human=True
            )

        elif provider == 'anthropic':
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY not set")

            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model="claude-3-haiku-20240307",
                temperature=0.7
            )

        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def load_agent(self, csv_file: str, provider: Optional[str] = None) -> bool:
        """
        Load CSV agent for the given file with specified or auto-detected provider.

        Args:
            csv_file (str): Path to CSV file
            provider (str, optional): Provider to use ('openai', 'gemini', 'anthropic').
                                     If None, auto-detects available provider.

        Returns:
            bool: True if agent loaded successfully
        """
        try:
            # Auto-detect provider if not specified
            if provider is None:
                provider = self.detect_available_provider()

            if provider is None:
                logger.error("No AI provider API key configured")
                return False

            if provider not in self.SUPPORTED_PROVIDERS:
                logger.error(f"Unsupported provider: {provider}")
                return False

            # Create LLM for the provider
            llm = self._create_llm(provider)

            # Create CSV agent
            self._agent = create_csv_agent(
                llm,
                csv_file,
                verbose=True,
                agent_type="openai-tools" if provider == 'openai' else "zero-shot-react-description",
                allow_dangerous_code=True  # Required for pandas operations
            )

            self._current_provider = provider
            logger.info(f"CSV agent loaded with provider: {provider}")
            return True

        except Exception as e:
            logger.error(f"Error loading CSV agent: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def chat(self, prompt: str) -> str:
        """
        Send a prompt to the chat agent.

        Args:
            prompt (str): User prompt/question

        Returns:
            str: Agent response
        """
        try:
            if self._agent is None:
                return "Chat agent not initialized. Please try again."

            logger.info(f"Processing chat with {self._current_provider}: {prompt[:50]}...")

            # Add friendly instructions to the prompt
            enhanced_prompt = f"""You are Analytics Assistant, a friendly helper for Amazon affiliate data analysis.

IMPORTANT:
- Speak conversationally, avoid technical jargon
- Never mention "pandas", "dataframe", "Python", or code
- Focus on business insights and recommendations
- For off-topic questions, say: "I'm sorry, I can only help with questions about your Amazon affiliate data and analytics."

User question: {prompt}

Please provide a clear, business-focused answer."""

            # Use invoke instead of deprecated run method
            result = self._agent.invoke({"input": enhanced_prompt})

            # Extract the output from the result
            if isinstance(result, dict):
                response = result.get('output', str(result))
            else:
                response = str(result)

            logger.info(f"Chat response generated successfully using {self._current_provider}")
            return response

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error processing chat: {error_msg}")
            logger.error(f"Error type: {type(e).__name__}")

            # Handle output parsing errors - extract the LLM response from error message
            if "Could not parse LLM output:" in error_msg:
                # Extract the actual response from between backticks
                import re
                match = re.search(r'Could not parse LLM output: `(.+?)`', error_msg, re.DOTALL)
                if match:
                    response = match.group(1)
                    logger.info(f"Extracted response from parsing error: {response[:100]}...")
                    return response

            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return f"Sorry, I encountered an error. Please try rephrasing your question or ask something about your affiliate data."

    def get_current_provider(self) -> Optional[str]:
        """Get the currently active provider."""
        return self._current_provider

    def reset_agent(self) -> None:
        """Reset the chat agent."""
        self._agent = None
        self._current_provider = None
        logger.info("Chat agent reset")

    def switch_provider(self, csv_file: str, provider: str) -> bool:
        """
        Switch to a different AI provider.

        Args:
            csv_file (str): Path to CSV file
            provider (str): Provider to switch to

        Returns:
            bool: True if switch was successful
        """
        logger.info(f"Switching provider from {self._current_provider} to {provider}")
        self.reset_agent()
        return self.load_agent(csv_file, provider)
