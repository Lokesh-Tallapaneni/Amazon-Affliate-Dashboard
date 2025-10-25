# AI Chat Setup Guide

## Issue: "Chat agent not initialized. Please try again."

This error occurs when the OpenAI API key is not configured. The AI chat feature requires an OpenAI API key to function.

---

## Solution: Configure OpenAI API Key

### Option 1: Using .env File (Recommended)

1. **Get an OpenAI API Key**
   - Visit https://platform.openai.com/api-keys
   - Sign up or log in to your OpenAI account
   - Click "Create new secret key"
   - Copy the API key (you won't be able to see it again!)

2. **Create .env File**
   ```bash
   # Copy the example file
   cp .env.example .env
   ```

3. **Edit .env File**
   ```bash
   # Open .env in a text editor and update:
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

4. **Restart the Application**
   ```bash
   # Stop the server (Ctrl+C) and restart
   python run.py
   ```

### Option 2: Using Environment Variable

**Windows:**
```bash
set OPENAI_API_KEY=sk-your-actual-api-key-here
python run.py
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-actual-api-key-here
python run.py
```

---

## Testing the Chat

1. **Login to the application**
2. **Navigate to "Chat Support"**
3. **Upload your data file** (if not already uploaded)
4. **Ask a question**, for example:
   - "What is my total revenue?"
   - "Show me the top 5 products"
   - "What's the average order value?"

---

## Troubleshooting

### Error: "OpenAI API Key is not configured"
**Solution:** Follow the setup steps above to configure your API key.

### Error: "Failed to initialize chat agent - OpenAI API key is invalid"
**Possible causes:**
- API key is incorrect or expired
- You haven't added billing information to your OpenAI account
- The key doesn't have the necessary permissions

**Solution:**
1. Verify your API key at https://platform.openai.com/api-keys
2. Check if your OpenAI account has billing set up
3. Generate a new API key if needed

### Error: "Failed to initialize chat agent - Data CSV file is missing"
**Solution:**
1. Make sure you've logged in and uploaded the Excel file
2. The data.csv file should be created automatically
3. Check if the file exists in the project root

### Error: Network connectivity issues
**Solution:**
1. Check your internet connection
2. Verify you can access https://api.openai.com
3. Check if you're behind a firewall or proxy

---

## OpenAI API Pricing

**Note:** The chat feature uses the OpenAI API which has usage costs.

**Current Pricing (as of 2024):**
- GPT-3.5-turbo: ~$0.002 per 1K tokens
- Typical query: ~100-500 tokens
- Average cost per question: $0.0002 - $0.001

**Tips to minimize costs:**
1. Use specific questions instead of broad queries
2. Monitor your usage on the OpenAI dashboard
3. Set spending limits in your OpenAI account
4. Consider using the chat feature only when necessary

---

## Alternative: Free Testing

If you don't want to use OpenAI API, you can:

1. **Use the data table view** instead
   - Navigate to "Data View"
   - Use browser search (Ctrl+F) to find specific data
   - Filter by date range

2. **Export data to Excel**
   - Download the processed data
   - Use Excel's built-in analysis tools

3. **Disable the chat feature** (optional)
   - Comment out the chat route in `templates/dash.html`
   - Or hide it via CSS

---

## Security Best Practices

1. **Never commit .env file to Git**
   - Already in `.gitignore`
   - Never share your API key publicly

2. **Rotate your API key regularly**
   - Generate new keys every 3-6 months
   - Delete old keys from OpenAI dashboard

3. **Set spending limits**
   - Configure in OpenAI account settings
   - Get notifications at certain thresholds

4. **Monitor usage**
   - Check OpenAI dashboard regularly
   - Review unexpected spikes in usage

---

## Enhanced Error Messages (New!)

The chat feature now provides helpful error messages:

✅ **Before:** "Chat agent not initialized. Please try again."

✅ **After:** Detailed instructions including:
- What went wrong
- How to fix it
- Step-by-step setup guide
- Alternative solutions

---

## Support

If you continue to experience issues:

1. Check the application logs in `logs/app.log`
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure Flask is running in development mode for detailed error messages
4. Review the console output for specific error messages

---

**Last Updated:** October 25, 2025
**Status:** ✅ Enhanced error handling implemented
