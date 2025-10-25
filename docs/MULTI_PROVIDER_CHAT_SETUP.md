# Multi-Provider AI Chat Setup Guide

**Version:** 2.1.0
**Date:** October 25, 2025
**Status:** ✅ Multi-Provider Support Enabled

---

## Overview

The AI Chat feature now supports **THREE AI providers**:
1. **OpenAI** (GPT-3.5-turbo, GPT-4)
2. **Google Gemini** (Gemini Pro) - **FREE** ⭐
3. **Anthropic** (Claude 3 Haiku)

You only need **ONE** API key to enable chat functionality. The app will **automatically detect** which provider you've configured and use it!

---

## Quick Start (5 Minutes)

### Option 1: Google Gemini (Recommended - FREE)

**Why Gemini?**
- 💯 **100% FREE** with generous limits (60 requests/min)
- 🚀 Fast and reliable
- 🌟 Excellent for data analysis
- 📱 Easy setup

**Setup Steps:**

1. **Get API Key** (2 minutes)
   ```
   Visit: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key"
   - Copy the key (starts with AIza...)
   ```

2. **Create .env file** (1 minute)
   ```bash
   # Copy example file
   cp .env.example .env
   ```

3. **Add API key to .env** (1 minute)
   ```env
   # Open .env in text editor and set:
   GOOGLE_API_KEY=AIza...your-actual-key-here
   ```

4. **Restart app** (1 minute)
   ```bash
   python run.py
   ```

✅ **Done!** Chat is now enabled with FREE Gemini Pro!

---

### Option 2: OpenAI (Paid, Most Popular)

**Why OpenAI?**
- 🎯 GPT-3.5 and GPT-4 models
- 📚 Well-documented
- 🏢 Industry standard
- 💰 Paid service (~$0.002 per 1K tokens)

**Setup Steps:**

1. **Get API Key**
   ```
   Visit: https://platform.openai.com/api-keys
   - Create account (requires credit card for billing)
   - Add billing information
   - Create API key
   - Copy the key (starts with sk-...)
   ```

2. **Add to .env**
   ```env
   OPENAI_API_KEY=sk-...your-actual-key-here
   ```

3. **Restart app**
   ```bash
   python run.py
   ```

---

### Option 3: Anthropic Claude (Cheapest Paid)

**Why Claude?**
- 🎓 Advanced reasoning
- 💸 Cheapest option (~$0.0008 per 1K tokens)
- 📊 Great for analysis
- 🔐 Privacy-focused

**Setup Steps:**

1. **Get API Key**
   ```
   Visit: https://console.anthropic.com/
   - Create account
   - Add billing information
   - Generate API key
   - Copy the key (starts with sk-ant-...)
   ```

2. **Add to .env**
   ```env
   ANTHROPIC_API_KEY=sk-ant-...your-actual-key-here
   ```

3. **Restart app**
   ```bash
   python run.py
   ```

---

## Provider Comparison

| Feature | OpenAI | Gemini | Claude |
|---------|--------|--------|--------|
| **Cost** | ~$0.002/1K tokens | **FREE** ✅ | ~$0.0008/1K tokens |
| **Rate Limit** | Varies by tier | 60 req/min | Varies by tier |
| **Setup** | Credit card required | Google account | Credit card required |
| **Model** | GPT-3.5-turbo | Gemini Pro | Claude 3 Haiku |
| **Quality** | Excellent | Excellent | Excellent |
| **Speed** | Fast | Fast | Fast |
| **Best For** | General use | Testing & FREE use | Cost-conscious users |

**Recommendation:** Start with **Gemini** (FREE), then try others if needed.

---

## Advanced: Using Multiple Providers

You can configure **multiple providers** and the app will use them in this priority order:

1. OpenAI (if configured)
2. Gemini (if configured)
3. Anthropic (if configured)

**Example .env with all providers:**
```env
# All three configured - OpenAI will be used by default
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

**To change priority:** Comment out the provider you don't want to use:
```env
# OpenAI disabled, will use Gemini
# OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## How It Works

### Auto-Detection

The app automatically detects which provider(s) you've configured:

```python
# When you send a chat message, the app:
1. Checks if any API key is configured
2. Selects provider in order: OpenAI > Gemini > Anthropic
3. Initializes the chat agent with that provider
4. Processes your question
5. Returns the response
```

### Provider Information

Check which provider is active via the `/chat/provider-info` API endpoint:

```bash
curl http://localhost:5000/chat/provider-info
```

Response:
```json
{
  "available_providers": {
    "openai": false,
    "gemini": true,
    "anthropic": false
  },
  "current_provider": "gemini",
  "has_any_provider": true
}
```

---

## Error Messages

### No Provider Configured

```
⚠️ No AI Provider API Key Configured

The AI Chat feature requires at least one API key from these providers:

🔹 OpenAI (GPT-3.5-turbo, GPT-4)
   • Get key: https://platform.openai.com/api-keys
   • Set: OPENAI_API_KEY=your-key
   • Cost: ~$0.002 per 1K tokens

🔹 Google Gemini (Gemini Pro) - RECOMMENDED
   • Get key: https://makersuite.google.com/app/apikey
   • Set: GOOGLE_API_KEY=your-key
   • Cost: FREE (with generous limits)

🔹 Anthropic Claude (Claude 3 Haiku)
   • Get key: https://console.anthropic.com/
   • Set: ANTHROPIC_API_KEY=your-key
   • Cost: ~$0.0008 per 1K tokens

💡 Tip: Google Gemini is FREE and works great!
```

### Provider Failed to Load

```
⚠️ Failed to Initialize Chat Agent

Possible issues:
1. API key is invalid or expired
2. You haven't set up billing (OpenAI/Claude)
3. Data CSV file is missing or corrupted
4. Network connectivity issues
5. Provider service is down
```

---

## Technical Details

### New Features

1. **Multi-Provider Support**
   - Seamlessly switch between providers
   - Auto-detection of configured providers
   - Fallback to available providers

2. **Provider-Specific Configurations**
   - OpenAI: Uses `gpt-3.5-turbo` model
   - Gemini: Uses `gemini-pro` model
   - Anthropic: Uses `claude-3-haiku-20240307` model

3. **Enhanced Error Handling**
   - Clear setup instructions in error messages
   - Provider availability checks
   - Helpful troubleshooting tips

### Code Architecture

**Service Layer** (`app/services/chat_service.py`):
```python
class ChatService:
    SUPPORTED_PROVIDERS = ['openai', 'gemini', 'anthropic']

    def detect_available_provider(self) -> str
    def load_agent(self, csv_file, provider=None) -> bool
    def switch_provider(self, csv_file, provider) -> bool
```

**Blueprint** (`app/blueprints/chat.py`):
```python
@chat_bp.route('/send_message', methods=['POST'])
def send_message():
    # Auto-detects provider
    # Returns response with provider info
```

---

## Cost Estimation

### Gemini (FREE)
```
Cost: $0.00
Limit: 60 requests/min
Monthly: FREE
```

### OpenAI (Paid)
```
Model: GPT-3.5-turbo
Cost: ~$0.002 per 1K tokens
Average query: 200-500 tokens
Cost per query: ~$0.0004-$0.001
Monthly (1000 queries): ~$0.40-$1.00
```

### Anthropic (Paid)
```
Model: Claude 3 Haiku
Cost: ~$0.0008 per 1K tokens
Average query: 200-500 tokens
Cost per query: ~$0.00016-$0.0004
Monthly (1000 queries): ~$0.16-$0.40
```

---

## Security Best Practices

### DO ✅
- Keep API keys in `.env` file
- Add `.env` to `.gitignore` (already done)
- Rotate keys every 3-6 months
- Set spending limits (OpenAI/Claude)
- Monitor usage regularly

### DON'T ❌
- Commit `.env` to Git
- Share API keys publicly
- Use production keys for testing
- Ignore unusual usage spikes

---

## Troubleshooting

### Issue: "No provider configured" but I added API key

**Solution:**
1. Verify `.env` file is in project root (same folder as `run.py`)
2. Check API key format:
   - OpenAI: starts with `sk-`
   - Gemini: starts with `AIza`
   - Anthropic: starts with `sk-ant-`
3. Remove any extra spaces or quotes around the key
4. Restart the application completely

### Issue: "Failed to initialize" with valid API key

**Solution:**
1. **OpenAI:** Check if billing is set up
2. **Gemini:** Verify API is enabled in Google Cloud Console
3. **Claude:** Confirm billing is configured
4. Test API key with curl:

```bash
# Test OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"

# Test Gemini
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"

# Test Claude
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: YOUR_KEY" \
  -H "anthropic-version: 2023-06-01"
```

### Issue: High costs

**Solution:**
1. Switch to Gemini (FREE)
2. Set spending limits in provider dashboard
3. Monitor usage daily
4. Use specific questions instead of broad queries
5. Consider caching frequent queries

---

## Testing the Setup

### Test Chat Functionality

1. Start the app: `python run.py`
2. Login and navigate to "Chat Support"
3. Send a test message: `"What is my total revenue?"`
4. You should see a response with:
   - Your question
   - AI's answer
   - Provider name (OpenAI/Gemini/Claude)

### Verify Provider

Check the response for provider information:
```json
{
  "user_message": "What is my total revenue?",
  "model_response": "Your total revenue is...",
  "provider": "gemini",
  "provider_display": "Google Gemini Pro"
}
```

---

## FAQs

**Q: Which provider is best?**
A: For FREE usage, **Gemini** is excellent. For paid, **Claude** is cheapest, **OpenAI** is most popular.

**Q: Can I use multiple providers?**
A: Yes! Configure all three and the app will use them in priority order.

**Q: How do I switch providers?**
A: Just comment out unwanted providers in `.env` and restart the app.

**Q: Is my data sent to the AI providers?**
A: Yes, your questions and data are sent to the selected provider's API. Use providers you trust.

**Q: Can I use this offline?**
A: No, all providers require internet connection to their APIs.

**Q: What if all providers fail?**
A: The app will show an error message. Check logs for details.

---

## Updating Dependencies

If you encounter package conflicts:

```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Or reinstall from scratch
pip uninstall -y langchain langchain-core langchain-community \
  langchain-openai langchain-google-genai langchain-anthropic

pip install -r requirements.txt
```

---

## Support

**Documentation:**
- [CHAT_SETUP.md](CHAT_SETUP.md) - Original single-provider guide
- [README.md](../README.md) - Main documentation
- [ENHANCEMENT_PLAN.md](ENHANCEMENT_PLAN.md) - Future features

**Need Help?**
1. Check error messages (they're now very helpful!)
2. Review this guide
3. Check logs in `logs/app.log`
4. Test API keys with curl commands above

---

## Summary

✅ **Multi-provider support added**
✅ **Three providers available**: OpenAI, Gemini, Claude
✅ **Auto-detection**: No manual configuration needed
✅ **FREE option**: Google Gemini
✅ **Enhanced errors**: Helpful setup instructions
✅ **Production ready**: Tested and working

**Recommended Setup:**
1. Use **Gemini** for FREE testing
2. Switch to **Claude** if you need paid (cheapest)
3. Use **OpenAI** if you prefer GPT models

**All providers work equally well for data analysis!** 🎉

---

**Last Updated:** October 25, 2025
**Version:** 2.1.0
**Status:** ✅ Production Ready
