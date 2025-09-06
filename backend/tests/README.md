# TestSpecAI Backend Test Suite

This directory contains comprehensive test suites for the TestSpecAI backend API endpoints and services.

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_api/                      # API endpoint tests
│   ├── test_requirements_api.py   # Requirements API tests (Task 6)
│   ├── test_test_specs_api.py     # Test Specifications API tests (Task 7)
│   ├── test_parameters_api.py     # Parameters API tests (Task 8)
│   └── test_commands_api.py       # Commands API tests (Task 9)
├── test_models/                   # Database model tests
├── test_crud/                     # CRUD operation tests
├── test_services/                 # Service layer tests
└── test_utils/                    # Utility function tests
```

## Test Coverage

### Task 6 - Requirements API Tests
- ✅ **CRUD Operations**: Create, Read, Update, Delete requirements
- ✅ **Category Management**: CRUD operations for requirement categories
- ✅ **Validation**: Input validation and error handling
- ✅ **Pagination**: Pagination support for large datasets
- ✅ **Search & Filtering**: Search by title, filter by category
- ✅ **Metadata Support**: JSON metadata handling
- ✅ **Error Handling**: 404, 422, 409 error responses

### Task 7 - Test Specifications API Tests
- ✅ **CRUD Operations**: Create, Read, Update, Delete test specifications
- ✅ **Test Steps Management**: CRUD operations for test steps
- ✅ **Functional Areas**: Support for UDS, Communication, ErrorHandler, CyberSecurity
- ✅ **Requirement Relationships**: Link test specs to requirements
- ✅ **Command Integration**: Test steps with command references
- ✅ **Validation**: Template validation and parameter checking
- ✅ **Error Handling**: Comprehensive error response testing

### Task 8 - Parameters API Tests
- ✅ **CRUD Operations**: Create, Read, Update, Delete parameters
- ✅ **Parameter Variants**: Manufacturer-specific parameter values
- ✅ **Category Management**: Parameter category CRUD operations
- ✅ **Validation**: Parameter name format, variant consistency
- ✅ **Search & Filtering**: Advanced search capabilities
- ✅ **Error Handling**: Validation and conflict error handling

### Task 9 - Commands API Tests
- ✅ **CRUD Operations**: Create, Read, Update, Delete generic commands
- ✅ **Command Categories**: CRUD operations for command categories
- ✅ **Template Validation**: Command template syntax validation
- ✅ **Parameter Integration**: Command-parameter relationship validation
- ✅ **Search & Filtering**: Advanced search with multiple filters
- ✅ **Usage Validation**: Prevent deletion of commands in use
- ✅ **Error Handling**: Comprehensive validation and error responses

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Set up test database
export TEST_DATABASE_URL="sqlite+aiosqlite:///./test.db"
```

### Run All Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

### Run Specific Test Suites
```bash
# Run API tests only
pytest tests/test_api/

# Run specific API test file
pytest tests/test_api/test_requirements_api.py

# Run specific test function
pytest tests/test_api/test_requirements_api.py::test_create_requirement
```

### Run Tests with Different Output
```bash
# Run with detailed output
pytest -v -s

# Run with coverage report
pytest --cov=app --cov-report=term-missing

# Run with HTML coverage report
pytest --cov=app --cov-report=html
```

## Test Configuration

### Database Configuration
Tests use a separate SQLite database (`test.db`) to avoid interfering with development data.

### Fixtures
- `client`: AsyncClient for making HTTP requests
- `db_session`: Database session for test data setup
- `sample_requirement_data`: Sample requirement data for testing
- `sample_test_spec_data`: Sample test specification data

### Test Data Management
Each test creates its own test data and cleans up after itself to ensure test isolation.

## Test Quality Standards

### Coverage Requirements
- **Minimum 80% code coverage** for backend
- **100% coverage** for critical paths (API endpoints, validation)
- **100% coverage** for error handling paths

### Test Categories
1. **Happy Path Tests**: Normal operation scenarios
2. **Validation Tests**: Input validation and error cases
3. **Edge Case Tests**: Boundary conditions and unusual inputs
4. **Integration Tests**: Cross-component interactions
5. **Error Handling Tests**: Error response validation

### Test Naming Convention
- `test_<action>_<entity>`: Basic CRUD operations
- `test_<action>_<entity>_<condition>`: Conditional operations
- `test_<action>_<entity>_validation`: Validation tests
- `test_<action>_<entity>_error`: Error handling tests

## Continuous Integration

Tests are designed to run in CI/CD environments with:
- **Fast execution**: Tests complete in under 30 seconds
- **Isolated execution**: No external dependencies
- **Deterministic results**: Consistent test outcomes
- **Clear failure reporting**: Detailed error messages

## Debugging Tests

### Common Issues
1. **Database connection errors**: Check TEST_DATABASE_URL
2. **Import errors**: Ensure PYTHONPATH includes project root
3. **Async test failures**: Verify pytest-asyncio is installed

### Debug Commands
```bash
# Run single test with debug output
pytest -v -s tests/test_api/test_requirements_api.py::test_create_requirement

# Run with pdb debugger
pytest --pdb tests/test_api/test_requirements_api.py

# Run with detailed logging
pytest -v -s --log-cli-level=DEBUG
```

## Test Maintenance

### Adding New Tests
1. Follow existing naming conventions
2. Use appropriate fixtures
3. Include both positive and negative test cases
4. Add proper assertions and error checking
5. Update this README if adding new test categories

### Updating Tests
1. Maintain backward compatibility
2. Update test data as needed
3. Ensure all tests pass after changes
4. Update documentation for new test scenarios

## Performance Testing

### Load Testing
```bash
# Run performance tests
pytest tests/test_performance/

# Run with timing information
pytest --durations=10
```

### Benchmark Tests
- API response time < 100ms for simple operations
- Database queries < 50ms for single entity operations
- Bulk operations < 500ms for 100+ items

## Security Testing

### Input Validation
- SQL injection prevention
- XSS prevention
- CSRF protection
- Input sanitization

### Authentication & Authorization
- API key validation
- Role-based access control
- Session management
- Rate limiting

## Test Reports

### Coverage Reports
- HTML coverage report: `htmlcov/index.html`
- Terminal coverage report: `--cov-report=term-missing`
- XML coverage report: `--cov-report=xml`

### Test Results
- JUnit XML: `--junitxml=test-results.xml`
- JSON results: `--json-report --json-report-file=test-results.json`

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Include comprehensive test cases
3. Add proper documentation
4. Ensure tests are fast and reliable
5. Update this README with new test information

## Troubleshooting

### Common Test Failures
1. **Database locks**: Ensure test database is not in use
2. **Import errors**: Check Python path and dependencies
3. **Async errors**: Verify async/await usage
4. **Timeout errors**: Increase test timeout if needed

### Getting Help
- Check test logs for detailed error information
- Use pytest debugging features
- Review test configuration in `conftest.py`
- Consult FastAPI and pytest documentation
