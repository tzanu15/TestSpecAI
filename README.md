# TestSpecAI

TestSpecAI is a web application for creating standardized automotive test specifications using AI (NLP + Local LLM) with standardized Parameters and Generic Commands.

## Technology Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Database**: SQLite (dev), PostgreSQL 15+ with pgvector (prod)
- **AI Libraries**: Hugging Face Transformers, sentence-transformers
- **Document Processing**: python-docx, PyPDF2, openpyxl

### Frontend
- **Framework**: React.js 18+ with TypeScript
- **UI Library**: Ant Design Pro
- **State Management**: Zustand
- **Styling**: styled-components
- **Build Tool**: Vite
- **Testing**: Vitest + React Testing Library

### Infrastructure
- **Development**: Native Python venv + Node.js
- **Production**: Simple VPS/cloud instance with Nginx + systemd
- **No Docker, No CI/CD** (explicitly excluded)

## Project Structure

```
TestSpecAI/
├── backend/                    # FastAPI Backend
├── frontend/                  # React Frontend
├── .taskmaster/              # Task management
├── docs/                     # Project documentation
├── .cursor/                  # Cursor IDE configuration
└── README.md
```

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git
- VS Code (recommended)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TestSpecAI
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

5. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Detailed Setup Instructions

#### Backend Development

1. **Environment Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Database Setup**
   ```bash
   # Initialize Alembic (first time only)
   alembic init alembic

   # Create migration
   alembic revision --autogenerate -m "Initial migration"

   # Apply migration
   alembic upgrade head
   ```

5. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Development

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Environment Configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Run Development Server**
   ```bash
   npm run dev
   ```

4. **Run Tests**
   ```bash
   npm run test
   npm run test:ui
   npm run test:coverage
   ```

5. **Code Quality**
   ```bash
   npm run lint
   npm run lint:fix
   npm run format
   npm run type-check
   ```

### Development Scripts

#### Backend Scripts
```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=app

# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Database migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
alembic downgrade -1
```

#### Frontend Scripts
```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build

# Testing
npm run test         # Run tests
npm run test:ui      # Run tests with UI
npm run test:coverage # Run tests with coverage

# Code Quality
npm run lint         # Lint code
npm run lint:fix     # Fix linting issues
npm run format       # Format code
npm run type-check   # TypeScript type checking
```

### VS Code Setup

1. **Install Recommended Extensions**
   - Open VS Code in the project root
   - Install recommended extensions when prompted

2. **Python Interpreter**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Python: Select Interpreter"
   - Choose the virtual environment: `./backend/venv/Scripts/python.exe`

3. **Debugging**
   - Use the debug configurations in `.vscode/launch.json`
   - Press `F5` to start debugging
   - Available configurations:
     - Debug Backend (FastAPI)
     - Debug Frontend (Vite)
     - Debug Full Stack
     - Debug Tests

## Development Guidelines

- Follow the rules defined in `.cursor/rules/` directory
- Use async/await for all database operations
- Implement proper error handling and logging
- Write tests for all new functionality
- Follow TypeScript best practices for frontend code

## Development Guidelines

- Follow the rules defined in `.cursor/rules/` directory
- Use async/await for all database operations
- Implement proper error handling and logging
- Write tests for all new functionality
- Follow TypeScript best practices for frontend code
- Use proper type hints for Python code
- Follow PEP 8 style guide for Python
- Use ESLint and Prettier for frontend code formatting

## Code Style

### Python (Backend)
- Use Black for code formatting
- Use isort for import sorting
- Use flake8 for linting
- Use mypy for type checking
- Follow PEP 8 style guide

### TypeScript/React (Frontend)
- Use Prettier for code formatting
- Use ESLint for linting
- Use TypeScript strict mode
- Follow React best practices
- Use functional components with hooks

## Testing

### Backend Testing
- Write unit tests for all business logic
- Write integration tests for API endpoints
- Use pytest for testing framework
- Aim for 80%+ code coverage

### Frontend Testing
- Write unit tests for components
- Write integration tests for user flows
- Use Vitest and React Testing Library
- Aim for 70%+ code coverage

## Contributing

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Follow the established project structure**
4. **Write comprehensive tests**
5. **Update documentation as needed**
6. **Follow code style guidelines defined in the rules**
7. **Commit your changes**
   ```bash
   git commit -m "feat: add your feature description"
   ```
8. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Create a Pull Request**

### Commit Message Format
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `style:` for formatting changes
- `refactor:` for code refactoring
- `test:` for adding tests
- `chore:` for maintenance tasks

## Troubleshooting

### Common Issues

1. **Python Virtual Environment Issues**
   ```bash
   # Delete and recreate virtual environment
   rm -rf backend/venv
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Node.js Dependencies Issues**
   ```bash
   # Clear npm cache and reinstall
   cd frontend
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Database Connection Issues**
   - Check if the database server is running
   - Verify connection settings in `.env` file
   - Ensure database exists and user has proper permissions

4. **Port Already in Use**
   ```bash
   # Find process using port 8000
   lsof -i :8000  # Linux/Mac
   netstat -ano | findstr :8000  # Windows

   # Kill the process
   kill -9 <PID>  # Linux/Mac
   taskkill /PID <PID> /F  # Windows
   ```

## License

This project is proprietary software.
