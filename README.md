# Amazon Affiliate Dashboard - Enhanced Edition

A production-ready Flask application for analyzing Amazon affiliate performance with advanced analytics, ML-based recommendations, and AI-powered chat interface.


---

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file (optional, or use form inputs):
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=your-openai-key-here
```

### 3. Run Application

```bash
python run.py
```

Application will be available at `http://localhost:5000`

---

## Features

### Core Features (Existing)
- ✅ User authentication with Amazon API credentials
- ✅ Excel file upload and processing (5 sheets supported)
- ✅ Interactive dashboard with date filtering
- ✅ Multiple visualizations (line, pie, bar charts)
- ✅ ML-based product recommendations
- ✅ AI chat interface for data queries
- ✅ Product data table with search/filter

### NEW: Advanced Analytics
- ✅ **Conversion Rate Analysis** - Track daily conversion trends, identify best/worst days
- ✅ **Device Performance** - Analyze revenue and engagement by device type
- ✅ **Link Type Analysis** - Compare performance across different link types
- ✅ **Returns Analysis** - Deep dive into return patterns and financial impact
- ✅ **Seller Comparison** - Amazon vs 3rd Party performance metrics
- ✅ **Analytics Overview** - Unified dashboard with quick stats

---

## Project Structure

```
Good/
├── app/
│   ├── blueprints/          # Route handlers
│   │   ├── auth.py          # Login/logout
│   │   ├── dashboard.py     # Main dashboard
│   │   ├── data.py          # Data table view
│   │   ├── recommendations.py # ML recommendations
│   │   ├── chat.py          # AI chat
│   │   └── analytics.py     # NEW - Analytics dashboards
│   ├── services/            # Business logic
│   │   ├── amazon_api.py    # Amazon API wrapper
│   │   ├── chat_service.py  # LangChain chat
│   │   ├── data_processor.py # Data processing
│   │   ├── ml_service.py    # ML model
│   │   ├── product_service.py # Product fetching
│   │   └── analytics_service.py # NEW - Analytics calculations
│   └── utils/               # Utilities
├── templates/
│   ├── index.html           # Login page
│   ├── dash.html            # Main dashboard
│   ├── data.html            # Data table
│   ├── recommendations.html # ML recommendations
│   ├── chat.html            # AI chat
│   └── analytics/           # NEW - 6 analytics templates
├── static/
│   └── images/              # Generated charts
├── config.py                # Configuration
├── run.py                   # Application entry point
└── requirements.txt         # Dependencies
```

---


## Analytics Features

### 1. Conversion Rate Analysis
**Route:** `/analytics/conversion`

Track daily conversion rates, identify trends, and optimize marketing strategies.

**Metrics:**
- Average conversion rate
- Best/worst performing days
- Trend direction (up/down/stable)
- Total clicks and orders

### 2. Device Performance
**Route:** `/analytics/devices`

Understand how different devices contribute to revenue.

**Metrics:**
- Revenue by device type
- Orders per device
- Return rates by device
- Device performance comparison

### 3. Link Type Analysis
**Route:** `/analytics/link-types`

Compare performance across different affiliate link types.

**Metrics:**
- Revenue by link type
- Conversion rates
- ROI calculations
- Click efficiency

### 4. Returns Analysis
**Route:** `/analytics/returns`

Deep insights into return patterns and financial impact.

**Metrics:**
- Overall return rate
- Returns by category
- Top returned products
- Revenue lost to returns

### 5. Seller Performance
**Route:** `/analytics/sellers`

Compare Amazon vs 3rd Party seller performance.

**Metrics:**
- Revenue distribution
- Return rate comparison
- Performance by seller type

### 6. Analytics Overview
**Route:** `/analytics/overview`

Unified dashboard with quick stats from all categories.

---

## Technology Stack

**Backend:**
- Flask 3.0.0
- Python 3.11+
- pandas 2.1.4
- scikit-learn 1.3.2
- LangChain (AI chat)

**Visualization:**
- matplotlib 3.8.2
- seaborn 0.13.0 (NEW)

**APIs:**
- Amazon Product Advertising API
- OpenAI API (chat feature)

**Production:**
- Gunicorn 21.2.0
- Nginx (recommended)

---

## Usage

### 1. Login
- Enter Amazon API credentials (Key, Secret, Tag)
- Upload affiliate earnings Excel file (5 sheets)

### 2. Main Dashboard
- View summary statistics
- Filter by date range
- View multiple chart types

### 3. Analytics
- Click "Analytics" in navigation
- Choose from 5 analytics dashboards
- View detailed insights and charts

### 4. Recommendations
- ML model predicts low-return products
- View recommended products to promote

### 5. AI Chat
- Ask natural language questions
- Get insights from your data

---

## Performance

**Benchmarks:**
- Page load time: < 3 seconds
- Analytics calculations: < 1 second
- Chart generation: < 200ms per chart
- API response time: < 500ms

**Supported Data:**
- Up to 1000s of orders
- Full year of daily trends
- Multiple tracking IDs
- All product categories

---

## Security

✅ Session-based authentication
✅ Protected routes with @login_required
✅ Input validation and sanitization
✅ Error handling prevents information leakage
✅ Secure file uploads
✅ Environment-based configuration
✅ HTTPS recommended for production

---

## Known Limitations

1. **Data Persistence**
   - Files cleared on logout
   - No database (uses Excel files)
   - Consider PostgreSQL for large scale

2. **Real-time Updates**
   - Charts generated on request
   - No auto-refresh
   - Consider Redis caching

3. **Excel Format**
   - Requires specific Amazon format
   - 5 sheets expected
   - Headers must match Amazon export

---

## Troubleshooting

### Common Issues

**Issue: Import errors**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

**Issue: Charts not displaying**
```bash
# Solution: Check static/images folder exists
mkdir -p static/images
```

**Issue: Login fails**
```bash
# Solution: Verify Amazon API credentials
# Check api_credentials.txt or form inputs
```

**Issue: Test failures**
```bash
# Solution: Ensure data file exists
# Copy sample Excel file to project root
```

---

## License

Proprietary - All rights reserved

---
