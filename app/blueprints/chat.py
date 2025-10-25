"""
Chat blueprint.

This module handles AI chat routes for data exploration with multi-provider support.
Supports: OpenAI, Google Gemini, and Anthropic Claude.
"""

import logging

import pandas as pd
from flask import Blueprint, render_template, request, jsonify, current_app

from app.services import ChatService
from app.utils import login_required

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat')
@login_required
def chat_page():
    """
    Display chat interface.

    Prepares CSV data for the chat agent.
    """
    try:
        # Convert Excel to CSV for chat agent
        data_file = current_app.config['DATA_FILE']
        csv_file = current_app.config['DATA_CSV']

        df = pd.read_excel(data_file, sheet_name='Fee-Earnings')
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)
        df.to_csv(csv_file, index=False)

        return render_template('chat.html')

    except Exception as e:
        logger.error(f"Error loading chat page: {str(e)}")
        return f"Error loading chat: {str(e)}", 500


@chat_bp.route('/chat/provider-info', methods=['GET'])
@login_required
def provider_info():
    """
    Get information about available AI providers.

    Returns:
        JSON response with provider availability
    """
    try:
        chat_service = ChatService(current_app.config)
        info = chat_service.get_provider_info()

        return jsonify(info)

    except Exception as e:
        logger.error(f"Error getting provider info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """
    Handle chat message from user with multi-provider support.

    Returns:
        JSON response with user message and model response
    """
    try:
        user_message = request.form.get('user_message', '').strip()
        preferred_provider = request.form.get('provider', None)

        if not user_message:
            return jsonify({
                'user_message': '',
                'model_response': 'Please enter a message.'
            })

        # Initialize chat service
        chat_service = ChatService(current_app.config)

        # Check if any provider is available
        provider_info = chat_service.get_provider_info()

        if not provider_info['has_any_provider']:
            error_msg = _get_no_provider_error_message()
            return jsonify({
                'user_message': user_message,
                'model_response': error_msg,
                'provider': None
            })

        # Load agent with preferred or auto-detected provider
        csv_file = current_app.config['DATA_CSV']
        agent_loaded = chat_service.load_agent(csv_file, preferred_provider)

        if not agent_loaded:
            error_msg = _get_agent_failed_error_message(chat_service, preferred_provider)
            return jsonify({
                'user_message': user_message,
                'model_response': error_msg,
                'provider': None
            })

        # Get response
        response = chat_service.chat(user_message)
        current_provider = chat_service.get_current_provider()

        logger.info(f"Chat query processed using {current_provider}: {user_message[:50]}...")

        return jsonify({
            'user_message': user_message,
            'model_response': response,
            'provider': current_provider,
            'provider_display': _get_provider_display_name(current_provider)
        })

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            'user_message': user_message if 'user_message' in locals() else '',
            'model_response': f'Sorry, an error occurred: {str(e)}',
            'provider': None
        })


def _get_no_provider_error_message() -> str:
    """Generate error message when no AI provider is configured."""
    return (
        "⚠️ No AI Provider API Key Configured\n\n"
        "The AI Chat feature requires at least one API key from these providers:\n\n"
        "🔹 OpenAI (GPT-3.5-turbo, GPT-4)\n"
        "   • Get key: https://platform.openai.com/api-keys\n"
        "   • Set: OPENAI_API_KEY=your-key\n"
        "   • Cost: ~$0.002 per 1K tokens\n\n"
        "🔹 Google Gemini (Gemini Pro)\n"
        "   • Get key: https://makersuite.google.com/app/apikey\n"
        "   • Set: GOOGLE_API_KEY=your-key\n"
        "   • Cost: FREE (with generous limits)\n\n"
        "🔹 Anthropic Claude (Claude 3 Haiku)\n"
        "   • Get key: https://console.anthropic.com/\n"
        "   • Set: ANTHROPIC_API_KEY=your-key\n"
        "   • Cost: ~$0.0008 per 1K tokens\n\n"
        "Setup Steps:\n"
        "1. Choose a provider and get an API key\n"
        "2. Create .env file (copy from .env.example)\n"
        "3. Add your API key to .env\n"
        "4. Restart the application\n\n"
        "💡 Tip: Google Gemini is FREE and works great!"
    )


def _get_agent_failed_error_message(chat_service, preferred_provider: str = None) -> str:
    """Generate error message when agent fails to initialize."""
    provider_info = chat_service.get_provider_info()
    available = [p for p, avail in provider_info['available_providers'].items() if avail]

    if preferred_provider and preferred_provider not in available:
        return (
            f"⚠️ Chat Assistant Unavailable\n\n"
            f"We're having trouble connecting to the analytics service.\n\n"
            f"Please refresh the page and try again. If the issue persists, contact support."
        )

    return (
        "⚠️ Chat Assistant Temporarily Unavailable\n\n"
        "We're having trouble loading the chat assistant right now.\n\n"
        "What you can try:\n"
        "• Refresh the page\n"
        "• Check your data file is uploaded correctly\n"
        "• Try again in a few moments\n\n"
        "If the problem continues, please contact support for assistance."
    )


def _get_provider_display_name(provider: str) -> str:
    """Get user-friendly display name for provider."""
    provider_names = {
        'openai': 'Analytics Assistant',
        'gemini': 'Analytics Assistant',
        'anthropic': 'Analytics Assistant'
    }
    return provider_names.get(provider, 'Analytics Assistant')
