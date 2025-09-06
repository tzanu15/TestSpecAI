# TestSpecAI Frontend Test Suite

This directory contains comprehensive test suites for the TestSpecAI frontend components, pages, and services.

## Test Structure

```
src/
├── __tests__/                    # Test files
│   ├── components/               # Component tests
│   │   ├── common/              # Common component tests
│   │   ├── requirements/        # Requirements component tests
│   │   ├── testSpecs/          # Test Spec component tests
│   │   ├── parameters/         # Parameter component tests
│   │   └── commands/           # Command component tests
│   ├── pages/                   # Page component tests
│   ├── hooks/                   # Custom hook tests
│   ├── services/                # Service tests
│   ├── stores/                  # Store tests
│   └── utils/                   # Utility function tests
├── test-utils/                   # Test utilities and helpers
│   ├── render.tsx               # Custom render function
│   ├── mocks/                   # Mock implementations
│   └── fixtures/                # Test data fixtures
└── setupTests.ts                # Test setup configuration
```

## Test Coverage

### Component Tests
- ✅ **Common Components**: Layout, Header, Navigation, Forms
- ✅ **Requirements Components**: RequirementsList, RequirementForm, RequirementCard
- ✅ **Test Spec Components**: TestSpecEditor, TestStepEditor, TestSpecList
- ✅ **Parameter Components**: ParameterManager, ParameterForm, ParameterVariantEditor
- ✅ **Command Components**: CommandManager, CommandForm, CommandTemplateEditor

### Page Tests
- ✅ **DashboardPage**: Main dashboard functionality
- ✅ **RequirementsPage**: Requirements management page
- ✅ **TestSpecsPage**: Test specifications page
- ✅ **ParametersPage**: Parameters management page
- ✅ **CommandsPage**: Commands management page

### Hook Tests
- ✅ **useRequirements**: Requirements data management
- ✅ **useForm**: Form handling and validation
- ✅ **useLoading**: Loading state management
- ✅ **Custom Hooks**: All custom hooks with proper testing

### Service Tests
- ✅ **API Services**: HTTP client and API integration
- ✅ **Data Services**: Data transformation and caching
- ✅ **Validation Services**: Input validation and error handling

### Store Tests
- ✅ **Zustand Stores**: State management testing
- ✅ **Store Actions**: Action creators and reducers
- ✅ **Store Selectors**: Data selection and filtering

## Running Tests

### Prerequisites
```bash
# Install dependencies
npm install

# Set up test environment
export VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Run All Tests
```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Run with coverage
npm run test:coverage
```

### Run Specific Test Suites
```bash
# Run component tests only
npm test -- src/__tests__/components/

# Run specific test file
npm test -- src/__tests__/components/requirements/RequirementsList.test.tsx

# Run specific test function
npm test -- --grep "should render requirements list"
```

### Run Tests with Different Output
```bash
# Run with verbose output
npm test -- --reporter=verbose

# Run with coverage report
npm run test:coverage

# Run with HTML coverage report
npm test -- --coverage --reporter=html
```

## Test Configuration

### Environment Setup
Tests use jsdom environment to simulate browser behavior in Node.js.

### Mocking
- **API Calls**: Mocked using MSW (Mock Service Worker)
- **External Dependencies**: Mocked using Vitest mocking capabilities
- **Browser APIs**: Mocked using jsdom

### Test Data
- **Fixtures**: Reusable test data in `test-utils/fixtures/`
- **Mocks**: Mock implementations in `test-utils/mocks/`
- **Helpers**: Test utilities in `test-utils/`

## Test Quality Standards

### Coverage Requirements
- **Minimum 70% code coverage** for frontend
- **100% coverage** for critical components (forms, API calls)
- **100% coverage** for error handling paths

### Test Categories
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **User Interaction Tests**: User behavior simulation
4. **Error Handling Tests**: Error state testing
5. **Accessibility Tests**: A11y compliance testing

### Test Naming Convention
- `ComponentName.test.tsx`: Component test files
- `useHookName.test.ts`: Hook test files
- `serviceName.test.ts`: Service test files
- `describe('ComponentName', () => {})`: Test suite description
- `it('should do something', () => {})`: Test case description

## Continuous Integration

Tests are designed to run in CI/CD environments with:
- **Fast execution**: Tests complete in under 60 seconds
- **Isolated execution**: No external dependencies
- **Deterministic results**: Consistent test outcomes
- **Clear failure reporting**: Detailed error messages

## Debugging Tests

### Common Issues
1. **Import errors**: Check path aliases and imports
2. **Async test failures**: Verify async/await usage
3. **Mock failures**: Check mock implementations
4. **Component rendering errors**: Verify component props

### Debug Commands
```bash
# Run single test with debug output
npm test -- --reporter=verbose src/__tests__/components/requirements/RequirementsList.test.tsx

# Run with debugger
npm test -- --inspect-brk

# Run with detailed logging
npm test -- --reporter=verbose --log-level=debug
```

## Test Maintenance

### Adding New Tests
1. Follow existing naming conventions
2. Use appropriate test utilities
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
npm test -- --reporter=verbose src/__tests__/performance/

# Run with timing information
npm test -- --reporter=verbose --durations=10
```

### Benchmark Tests
- Component rendering < 100ms
- API calls < 500ms
- Form validation < 50ms
- State updates < 10ms

## Accessibility Testing

### A11y Testing
- Screen reader compatibility
- Keyboard navigation
- Color contrast compliance
- Focus management
- ARIA attributes

### Testing Tools
- `@testing-library/jest-dom`: Custom matchers
- `@testing-library/user-event`: User interaction simulation
- `jsdom`: DOM simulation

## Test Reports

### Coverage Reports
- HTML coverage report: `coverage/index.html`
- Terminal coverage report: `--coverage --reporter=text`
- JSON coverage report: `--coverage --reporter=json`

### Test Results
- HTML report: `test-results/index.html`
- JSON results: `--reporter=json --outputFile=test-results.json`

## Contributing

When adding new tests:
1. Follow the existing test structure
2. Include comprehensive test cases
3. Add proper documentation
4. Ensure tests are fast and reliable
5. Update this README with new test information

## Troubleshooting

### Common Test Failures
1. **Import errors**: Check path aliases and dependencies
2. **Mock errors**: Verify mock implementations
3. **Async errors**: Check async/await usage
4. **Timeout errors**: Increase test timeout if needed

### Getting Help
- Check test logs for detailed error information
- Use Vitest debugging features
- Review test configuration in `vitest.config.ts`
- Consult React Testing Library and Vitest documentation
