# Quick Start Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Amazon Product Advertising API credentials
- OpenAI API key (optional, for chat feature)

## Installation

### 1. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 2. Run Setup Script

```bash
# This creates directories and generates .env file
python setup.py
```

### 3. Configure Environment

Edit the `.env` file and add your credentials:

```env
# Required for login
AMAZON_API_KEY=your-amazon-api-key
AMAZON_SECRET_KEY=your-amazon-secret-key
AMAZON_ASSOCIATE_TAG=your-associate-tag

# Required for chat feature
OPENAI_API_KEY=your-openai-key

# Change this in production!
SECRET_KEY=your-generated-secret-key
```

### 4. Verify Installation

```bash
# Run verification script
python verify_refactoring.py
```

All checks should pass if dependencies are installed and structure is correct.

### 5. Run the Application

```bash
# Development mode
python run.py
```

Or with custom settings:

```bash
# Set environment
export FLASK_ENV=development  # or production
export FLASK_DEBUG=True

# Run
python run.py
```

### 6. Access the Application

Open your browser to: **http://localhost:5000**

## First Time Use

1. **Login Page**
   - Enter your Amazon API credentials
   - Upload your Amazon Affiliate earnings Excel file
   - Click Submit

2. **Dashboard**
   - View charts and analytics
   - Filter by date range
   - See top products

3. **Data View**
   - Browse all transactions in table format

4. **Recommendations**
   - Wait for product fetch to complete (~1-2 minutes)
   - View ML-filtered product recommendations

5. **Chat**
   - Ask questions about your data in natural language
   - Requires OPENAI_API_KEY to be set

## Troubleshooting

### ImportError: No module named 'xxx'

Solution: Install dependencies
```bash
pip install -r requirements.txt
```

### Charts not displaying

Solution: Ensure static/images directory exists
```bash
mkdir -p static/images
```

### Chat not working

Solution: Set OPENAI_API_KEY in .env file

### Login fails

Solution: Verify Amazon API credentials are correct

## Production Deployment

### Using Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

### Environment Variables for Production

```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export AMAZON_API_KEY=your-key
export AMAZON_SECRET_KEY=your-secret
export AMAZON_ASSOCIATE_TAG=your-tag
export OPENAI_API_KEY=your-openai-key
```

### Using systemd (Linux)

Create `/etc/systemd/system/affiliate-dashboard.service`:

```ini
[Unit]
Description=Amazon Affiliate Dashboard
After=network.target

[Service]
User=your-user
WorkingDirectory=/path/to/app
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 "app:create_app('production')"
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable affiliate-dashboard
sudo systemctl start affiliate-dashboard
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

Build and run:
```bash
docker build -t affiliate-dashboard .
docker run -p 5000:5000 --env-file .env affiliate-dashboard
```

## Next Steps

- Read [README_REFACTORED.md](README_REFACTORED.md) for detailed documentation
- Check [MIGRATION.md](MIGRATION.md) if migrating from old version
- See [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) for technical details

## Support

If you encounter issues:

1. Check logs in `logs/app.log`
2. Run verification: `python verify_refactoring.py`
3. Review error messages in console
4. Ensure all dependencies are installed

## Common Commands

```bash
# Setup
python setup.py

# Verify
python verify_refactoring.py

# Run (development)
python run.py

# Run (production)
gunicorn -w 4 "app:create_app('production')"

# Check dependencies
pip list | grep -i flask

# View logs
tail -f logs/app.log
```

## File Structure Overview

```
.
├── app/                  # Main application package
│   ├── blueprints/      # Route handlers
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── static/              # CSS, images
├── templates/           # HTML templates
├── config.py            # Configuration
├── run.py               # Entry point
├── .env                 # Environment variables (create from .env.example)
└── requirements.txt     # Dependencies
```

## Quick Reference

| Task | Command |
|------|---------|
| Install | `pip install -r requirements.txt` |
| Setup | `python setup.py` |
| Verify | `python verify_refactoring.py` |
| Run | `python run.py` |
| Test Login | Go to http://localhost:5000 |

---

**Ready to start?** Run `python setup.py` and follow the prompts!
