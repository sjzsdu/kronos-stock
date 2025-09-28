# Kronos Stock Prediction System - AI Coding Instructions

## Architecture Overview

This is a modern Flask + HTMX stock prediction system with a modular architecture. The system uses PyTorch models for stock price prediction and provides both web UI and REST API interfaces.

## Recommended Technology Stack

When developing for this system, use these preferred technologies:

### Core Framework
- **Flask** - Lightweight Python web framework with blueprint architecture
- **HTMX** - Modern JavaScript alternative for dynamic web interactions
- **TailwindCSS** - Utility-first CSS framework for responsive UI design

### Data Processing & ML
- **PyTorch** - Deep learning framework for stock prediction models
- **pandas** - Data manipulation and analysis library
- **numpy** - Numerical computing and array operations
- **china_stock_data** - Chinese stock market data provider

### Visualization & UI
- **Plotly** - Interactive charts and financial data visualization
- **FontAwesome** - Icon library for consistent UI elements
- **Bootstrap** (legacy) - CSS framework (being migrated to TailwindCSS)

### Development Tools
- **pytest** - Testing framework with custom markers
- **Flask-Migrate** - Database migration management
- **SQLAlchemy** - ORM for database operations

### Deployment
- **Docker** - Containerization for consistent environments
- **SQLite/MySQL** - Database engines (SQLite for dev, MySQL for production)

Always use these technologies when extending functionality to maintain consistency with the existing codebase.

### Key Architectural Patterns

**Application Factory Pattern**: The Flask app is created via `create_app()` in `app/__init__.py`, not directly instantiated. Always use this pattern when extending the application.

**Service Layer Pattern**: Business logic lives in `app/services/` not in routes:
- `model_service.py` - AI model loading/management 
- `prediction_service.py` - Stock prediction workflow
- `stock_service.py` - Stock data fetching/validation

**Blueprint Architecture**: Features are organized as blueprints:
- `app/api/` - REST API endpoints (`/api/*`)
- `app/views/` - HTMX views and main pages
- `app/config/` - Menu/UI configuration

## Critical Developer Workflows

### Running the Application
```bash
python run.py  # NOT python app.py (old pattern)
```
- Starts on port 5001 by default
- Uses `FLASK_CONFIG` environment variable (development/production/testing)
- Auto-loads `kronos-mini` model on startup

### Model Management
Models are stored in `models/` directory with three variants:
- `kronos-mini` - Fast, lightweight (~100MB)
- `kronos-small` - Balanced performance (~500MB) 
- `kronos-base` - Best accuracy (~1GB)

Model loading is CPU-only by design (see `model_service.py:65` where device is forced to "cpu").

### Testing
```bash
./run_tests.sh  # Preferred method
pytest          # Direct pytest
```
Test configuration in `pytest.ini` with markers: `slow`, `integration`, `unit`, `api`.

## Project-Specific Conventions

### Stock Code Validation
Stock codes are validated and normalized in `stock_service.py`. Always use 6-digit format (e.g., "000001" not "1").

### Prediction Results Storage
Predictions are saved as JSON files in `results/` with naming pattern:
`prediction_{stock_code}_{timestamp}.json`

### Configuration Management
- `config.py` defines environment-specific configs
- Model paths and parameters in `Config.AVAILABLE_MODELS`
- Default prediction params: lookback=30, pred_len=5, temperature=0.7

### HTMX Integration
- Templates use HTMX for dynamic updates
- Component templates in `app/templates/components/`
- Menu system defined in `app/config/menu.py`
- Custom template filters like `format_datetime` in `app/__init__.py`

## Integration Points

### Model Loading Pipeline
1. `model_service.py` imports from `model/` directory
2. Uses `KronosTokenizer`, `Kronos`, `KronosPredictor` classes
3. Paths are dynamically added to `sys.path` in `_setup_paths()`

### Prediction Workflow
1. Validate stock code → `stock_service.validate_stock_code()`
2. Fetch historical data → `stock_service.get_stock_data()`
3. Prepare data for model → `prediction_service.predict_stock()`
4. Generate trading day timestamps → `_generate_future_trading_dates()`
5. Save results → JSON files in `results/`

### Database Integration
- Uses SQLAlchemy with Flask-Migrate
- SQLite for dev, MySQL for production
- Models defined in `app/models/`

## Development Environment

### Docker Setup
- Multi-stage build optimized for Python 3.12
- Health check on `/api/health`
- Non-root user `appuser` (currently commented out)
- Entry point via `docker-entrypoint.sh`

### Dependencies
- Core: Flask, PyTorch, pandas, numpy
- UI: HTMX (included via CDN in templates)
- Testing: pytest with custom markers
- Deployment: Docker, CORS configured

## Common Gotchas

1. **Model Import Path Issues**: The `model/` directory is dynamically added to `sys.path`. If models don't load, check `_setup_paths()` in `model_service.py`.

2. **CPU-Only Inference**: All model operations are forced to CPU (`device="cpu"`). Don't attempt GPU acceleration without architecture changes.

3. **Trading Day Logic**: Prediction dates skip weekends/holidays via `_generate_future_trading_dates()`. Don't use simple date arithmetic.

4. **HTMX Response Format**: Views expecting HTMX should return partial HTML templates, not full pages or JSON (unless specifically handling API calls).

5. **Bootstrap CSS**: Uses template-first approach - always test UI changes in the actual web interface, not just API responses.