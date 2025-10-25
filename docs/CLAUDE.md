# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based Amazon Affiliate Dashboard that analyzes affiliate performance data, provides ML-based product recommendations, and offers an AI chat interface for data exploration.

**Core Technologies:** Flask, pandas, scikit-learn, matplotlib, Amazon Product API (PAAPI), LangChain

## Development Commands

### Running the Application
```bash
python app.py
# Runs on http://0.0.0.0:5000 with debug mode enabled
```

### Alternative Launch (Windows)
```bash
run_app.vbs  # VBS script for Windows
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Architecture Overview

### Application Flow
1. **Authentication**: Users upload Amazon API credentials and affiliate earnings Excel file
2. **Data Processing**: Excel file parsed into multiple sheets (Fee-Earnings, Fee-DailyTrends, Fee-Orders, Fee-Tracking)
3. **ML Training**: Logistic Regression model trains on product names to predict returns
4. **Background Tasks**: Multiprocessing spawns product fetch process using Amazon PAAPI
5. **Dashboard**: Visualizations render based on date-filtered data
6. **Recommendations**: ML model predicts which fetched products are likely to have low returns

### Key Modules

**[app.py](app.py)** - Main Flask application
- Routes: `/login`, `/dash`, `/data`, `/get_recommendations`, `/chat`
- Session management for API credentials
- Coordinates all other modules

**[main.py](main.py)** - Data processing and visualization
- Generates 4 charts: main dashboard (bar+line combo), pie chart, category bar chart, returns chart
- Functions: `main()`, `main_dash()`, `pie_chart()`, `bar_chart()`, `returns()`, `max_adfee()`, `max_quantity()`
- All charts saved to `static/images/*.png`

**[ml.py](ml.py)** - Machine learning pipeline
- `model(name)`: Trains TF-IDF + Logistic Regression on product names vs returns
- `prediction(name)`: Applies model to fetched products, adds "result" column (0=low return risk, 1=high)
- Saves models to `cmodel_pkl` and `feature_extraction` pickle files

**[product_fetch.py](product_fetch.py)** - Amazon product scraping
- `gen_product(KEY, SECRET, TAG)`: Runs as background process
- Searches 24 predefined keywords, throttles at 1 req/sec
- Outputs to `product_details.xlsx` with sheet "Product_details"

**[aichat.py](aichat.py)** - LangChain CSV agent
- `load(file_name)`: Creates OpenAI-powered CSV agent on `data.csv`
- `chat(agent, prompt)`: Processes natural language queries about affiliate data
- **Note**: Requires `OPENAI_API_KEY` environment variable

### Data Files

**Input Files:**
- User uploads: `data.xlsx` (Amazon affiliate earnings export with sheets: Fee-Earnings, Fee-DailyTrends, Fee-Orders, Fee-Tracking)
- Generated: `data.csv` (converted from Fee-Earnings sheet for chat agent)

**Generated Files:**
- `product_details.xlsx`: Fetched Amazon products (2 sheets: Product_details, Results)
- `cmodel_pkl`, `feature_extraction`: Serialized ML models
- `static/images/{dash,piepic,barpic,returns}.png`: Dashboard charts

### Important Implementation Details

**Excel Processing Pattern:**
All modules use identical pattern for multi-sheet Excel parsing:
```python
file = pd.ExcelFile(name)
sheet_names = file.sheet_names
for sheet_name in sheet_names:
    sheet = file.parse(sheet_name)
    sheet.columns = sheet.iloc[0]  # First row becomes header
    globals()[sheet_name.replace("-","_")] = sheet
```

**Date Handling:**
- Dates extracted from Excel column headers via regex `r'\d{2}-\d{2}-\d{4}'`
- Format: "%m-%d-%Y" → "%Y-%m-%d"
- Dashboard defaults to last 30 days from end date

**Multiprocessing Lifecycle:**
- Product fetch process (`pf`) starts on successful login
- Checked via `pf.is_alive()` before showing recommendations
- Terminated on logout

**Session Security:**
- `app.secret_key = 'your_secret_key'` - Should be changed for production
- Session stores `logged_in` boolean flag

## Common Development Patterns

### Adding a New Route
All protected routes should check session:
```python
@app.route('/new_route')
def new_route():
    if 'logged_in' in session and session['logged_in']:
        # Route logic
        return render_template('template.html')
    else:
        return redirect(url_for('index'))
```

### Adding a New Visualization
1. Create function in [main.py](main.py) that accepts `(dataframe, from_date, to_date)`
2. Filter data: `df = df[(df['Date'] >= from_date) & (df['Date'] <= to_date)]`
3. Save figure: `plt.savefig(fname="static/images/filename.png", bbox_inches="tight")`
4. Return `True` on success
5. Call from `main()` function
6. Reference in [templates/dash.html](templates/dash.html)

### Working with Amazon PAAPI
- Throttling built into `AmazonApi(throttling=1)` - max 1 request/sec
- Country code: `"IN"` (India)
- Common exceptions: `RequestError` for invalid credentials
- Test credentials with `check()` function in [app.py](app.py:36-47)

## File Structure

```
.
├── app.py                    # Main Flask app
├── main.py                   # Data processing & charts
├── ml.py                     # ML model training/prediction
├── product_fetch.py          # Amazon product scraper
├── aichat.py                 # LangChain chat agent
├── requirements.txt          # Dependencies
├── run_app.vbs               # Windows launcher
├── templates/                # HTML templates
│   ├── index.html           # Login page
│   ├── dash.html            # Main dashboard
│   ├── excel_products.html  # Raw data table
│   ├── recommendations.html # ML-filtered products
│   └── chat.html            # AI chat interface
└── static/
    ├── images/              # Generated chart PNGs
    └── *.css                # Stylesheets
```

## Gotchas and Known Issues

1. **API Key Security**: [aichat.py:6](aichat.py#L6) has empty `OPENAI_API_KEY` - must be set via environment variable
2. **File Cleanup**: Logout attempts to delete files but uses `try/except` to suppress errors
3. **Global Variables**: Extensive use of `globals()` for sheet storage - not thread-safe
4. **Hardcoded Values**:
   - Secret key in [app.py:23](app.py#L23)
   - Keywords in [product_fetch.py:9](product_fetch.py#L9)
   - Test ASIN in [app.py:39](app.py#L39)
5. **Date Format Assumption**: Excel must have date range in first column header (e.g., "01-15-2024 to 02-14-2024")
6. **Deprecated openpyxl**: [ml.py:154](ml.py#L154) uses `get_sheet_by_name()` (deprecated, use `wb[sheet_name]`)
7. **No Database**: All data stored in Excel files, cleared on logout
