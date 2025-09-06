# TestSpecAI Backend Development Guide

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Linux/Mac
source venv/bin/activate
```

### 2. Start Development Server
```bash
# Option 1: Using PowerShell script
.\start_dev.ps1

# Option 2: Using batch file
start_dev.bat

# Option 3: Using Python script
python start_dev.py

# Option 4: Direct uvicorn command
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir app
```

### 3. Access the Application
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 🧪 Running Tests

### Prerequisites
1. **Backend server must be running** (see above)
2. **Virtual environment must be activated**
3. **All dependencies must be installed**

### Test Commands
```bash
# Run all tests
python run_tests.py

# Run tests with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file tests/test_api/test_requirements_api.py

# Run tests in parallel
python run_tests.py --parallel

# Run tests with verbose output
python run_tests.py --verbose
```

### Test Structure
```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_api/                # API endpoint tests
│   ├── test_requirements_api.py
│   ├── test_test_specs_api.py
│   ├── test_parameters_api.py
│   └── test_commands_api.py
└── README.md                # Test documentation
```

## 🔧 Development Workflow

### 1. Start Development Environment
```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start backend server
.\start_dev.ps1
```

### 2. Make Changes
- Edit code in `app/` directory
- Server will auto-reload on changes
- Check http://localhost:8000/docs for API changes

### 3. Run Tests
```bash
# Run tests after making changes
python run_tests.py --coverage
```

### 4. Check Code Quality
```bash
# Format code
black app/

# Sort imports
isort app/

# Check for issues
flake8 app/
mypy app/
```

## 📁 Project Structure
```
backend/
├── app/                     # Main application code
│   ├── api/                # API endpoints
│   ├── crud/               # Database operations
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   └── utils/              # Utility functions
├── tests/                  # Test files
├── venv/                   # Virtual environment
├── requirements.txt        # Python dependencies
├── pytest.ini             # Pytest configuration
├── run_tests.py           # Test runner script
├── start_dev.py           # Development server script
├── start_dev.ps1          # PowerShell startup script
├── start_dev.bat          # Batch startup script
└── start_dev.sh           # Shell startup script
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Virtual Environment Not Activated
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: Activate virtual environment first
```bash
.\venv\Scripts\Activate.ps1
```

#### 2. Dependencies Not Installed
**Error**: `ModuleNotFoundError: No module named 'pytest'`
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Database Connection Issues
**Error**: `sqlalchemy.exc.OperationalError`
**Solution**: Check database configuration in `.env` file

#### 4. Port Already in Use
**Error**: `OSError: [Errno 98] Address already in use`
**Solution**: Kill existing process or use different port
```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 5. Test Fixtures Not Working
**Error**: `AttributeError: 'async_generator' object has no attribute 'add'`
**Solution**: Check `conftest.py` configuration and ensure pytest-asyncio is installed

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-AsyncIO Documentation](https://pytest-asyncio.readthedocs.io/)
