# Amazon Affiliate Dashboard - Production Ready

A Flask-based analytics dashboard for Amazon Affiliate marketers with ML-powered product recommendations and AI-driven data exploration.

## Features

- **Analytics Dashboard**: Visualize earnings, clicks, orders, and trends
- **ML Recommendations**: Predict product return likelihood using Logistic Regression
- **AI Chat**: Natural language queries about your affiliate data using LangChain
- **Product Discovery**: Automated product fetching from Amazon Product API
- **Date Filtering**: Analyze data for custom date ranges
- **Category Insights**: Pie charts and bar charts for category distribution

## Architecture

This is a production-ready refactored version with:

- **Modular Blueprints**: Organized routes by feature (auth, dashboard, data, etc.)
- **Service Layer**: Business logic separated from routes
- **Configuration Management**: Environment-based settings
- **Comprehensive Logging**: Track application behavior
- **Input Validation**: Secure user input handling
- **Error Handling**: Graceful failure recovery
- **PEP8 Compliant**: Clean, maintainable code

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Amazon Product Advertising API credentials
- OpenAI API key (for chat feature)
- Amazon Affiliate earnings Excel export

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Good
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the application:
```bash
python run.py
```

6. Open browser to http://localhost:5000

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Amazon Product Advertising API
AMAZON_API_KEY=your-api-key
AMAZON_SECRET_KEY=your-secret-key
AMAZON_ASSOCIATE_TAG=your-tag

# OpenAI API (for chat)
OPENAI_API_KEY=your-openai-key

# Logging
LOG_LEVEL=INFO
```

### Configuration Environments

- **Development**: Debug enabled, verbose logging
- **Testing**: Isolated testing environment
- **Production**: Security hardened, optimized settings

Switch environments:
```bash
export FLASK_ENV=production
python run.py
```

## Project Structure

```
app/
├── blueprints/           # Route handlers
│   ├── auth.py          # Login/logout
│   ├── dashboard.py     # Main dashboard
│   ├── data.py          # Data tables
│   ├── recommendations.py
│   └── chat.py          # AI chat
├── services/            # Business logic
│   ├── data_processor.py
│   ├── ml_service.py
│   ├── product_service.py
│   ├── amazon_api.py
│   └── chat_service.py
└── utils/               # Helpers
    ├── validators.py
    ├── helpers.py
    └── decorators.py
```

## Usage

### 1. Login

1. Navigate to http://localhost:5000
2. Enter your Amazon API credentials:
   - API Key
   - Secret Key
   - Associate Tag
3. Upload your Amazon Affiliate earnings Excel file
4. Click Submit

### 2. Dashboard

View your affiliate performance:
- **Main Chart**: Ad fees, clicks, and orders over time
- **Category Pie Chart**: Distribution of products by category
- **Category Bar Chart**: Item counts by category
- **Returns Chart**: Product returns by category
- **Top Products**: Highest earning products
- **Top Quantity**: Most ordered products

Filter by date range using the date pickers.

### 3. View Data

Click "View Data" to see a detailed table of all your affiliate transactions.

### 4. Product Recommendations

The system automatically fetches products from Amazon API in the background. Once complete:

1. Click "Get Recommendations"
2. View ML-filtered products with low return risk
3. Products are sorted and randomized for variety

### 5. AI Chat

Ask questions about your data in natural language:

1. Click "Chat"
2. Type questions like:
   - "What's my total revenue?"
   - "Which category has the most returns?"
   - "Show me products shipped in January"
3. Get AI-powered answers

## API Reference

### Routes

| Route | Method | Description | Auth Required |
|-------|--------|-------------|---------------|
| `/` | GET | Redirect to login | No |
| `/login` | GET | Display login page | No |
| `/submit` | POST | Process login | No |
| `/logout` | POST | Logout and cleanup | Yes |
| `/dash` | GET, POST | Main dashboard | Yes |
| `/data` | GET | View data table | Yes |
| `/get_recommendations` | GET | ML product recommendations | Yes |
| `/chat` | GET | Chat interface | Yes |
| `/send_message` | POST | Send chat message | Yes |

### Services API

```python
from app.services import DataProcessor, MLService, ProductService

# Data Processing
processor = DataProcessor(config)
max_fee, max_qty = processor.process_data(file_path, from_date, to_date)

# ML Operations
ml_service = MLService(config)
ml_service.train_model(file_path)
ml_service.predict_returns(file_path)

# Product Fetching
product_service = ProductService(config)
product_service.fetch_products(api_key, secret_key, tag)
```

## Machine Learning

### Model: Logistic Regression

- **Input**: Product names (TF-IDF vectorized)
- **Output**: Return probability (0 = low risk, 1 = high risk)
- **Training**: Automatic on login using your historical data
- **Metrics**: Accuracy, precision, recall, F1-score logged

### Recommendation Logic

1. Fetch products from Amazon API (24 keyword searches)
2. Extract product names
3. Apply trained model
4. Filter products predicted as low-return-risk
5. Display randomized results

## Deployment

### Development

```bash
python run.py
```

### Production (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

### With Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/app/static;
    }
}
```

### Environment Variables

For production, set these securely:
```bash
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
export AMAZON_API_KEY=...
export OPENAI_API_KEY=...
```

## Logging

Logs are written to:
- Console (stdout)
- `logs/app.log` (rotating, 10MB max, 5 backups)

Log levels:
- **DEBUG**: Detailed diagnostic info
- **INFO**: General information messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical issues

Configure via `LOG_LEVEL` environment variable.

## Security

### Implemented Measures

- Environment-based configuration
- Session cookie security (HTTP-only, secure, SameSite)
- Input validation on all user inputs
- File upload size limits and extension checking
- Error messages don't expose internals
- Credentials stored in environment, not code
- CSRF protection via Flask sessions

### Recommendations

- Use HTTPS in production
- Set strong `SECRET_KEY`
- Restrict file upload directory permissions
- Enable Flask-Session with Redis/database for production
- Implement rate limiting
- Add user authentication beyond API credentials

## Performance

### Optimizations

- Matplotlib Agg backend (non-interactive, faster)
- Lazy service initialization
- Background product fetching (multiprocessing)
- Efficient pandas operations
- Rotating log files prevent disk fill

### Scaling

- Use Gunicorn with multiple workers
- Implement caching (Redis)
- Offload ML training to background workers (Celery)
- Use CDN for static files
- Database instead of Excel for large datasets

## Troubleshooting

### Common Issues

**Import errors:**
- Ensure you're in the project root
- Check virtual environment is activated

**Charts not showing:**
- Verify `static/images/` exists and is writable
- Check matplotlib backend is 'Agg'

**Chat not working:**
- Verify `OPENAI_API_KEY` is set and valid
- Check CSV file is generated from Excel

**Product fetch hangs:**
- Amazon API has rate limits (1 req/sec enforced)
- Check API credentials are valid

**Login fails:**
- Verify Amazon API credentials
- Check uploaded file is valid Excel format

## Development

### Running Tests

```bash
# Set testing environment
export FLASK_ENV=testing

# Run tests (add test files as needed)
python -m pytest tests/
```

### Adding New Features

1. Create service in `app/services/`
2. Add routes to appropriate blueprint
3. Update configuration if needed
4. Add tests
5. Update documentation

### Code Style

- Follow PEP8 (enforced)
- Use type hints where appropriate
- Document functions with docstrings
- Log important operations
- Handle exceptions gracefully

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following code style
4. Add tests
5. Submit pull request

## License

[Your License Here]

## Acknowledgments

- Flask framework
- Amazon Product Advertising API
- scikit-learn
- LangChain
- OpenAI

## Support

For issues and questions:
- Check `logs/app.log`
- Review [MIGRATION.md](MIGRATION.md) for migration details
- Open an issue on GitHub

## Changelog

### Version 2.0.0 (Refactored)

- Complete modular refactoring
- Blueprint architecture
- Service layer pattern
- Configuration management
- Comprehensive logging
- Input validation
- Error handling
- PEP8 compliance
- Production-ready deployment

### Version 1.0.0 (Legacy)

- Monolithic Flask app
- Basic functionality
- See legacy `app.py` for reference
