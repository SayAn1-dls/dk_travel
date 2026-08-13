# Testing Guide

## Backend Tests

Run the backend test suite:

```bash
cd backend
pytest tests/ -v --cov=app
```

### Unit Tests
- Located in `backend/tests/unit/`
- Test individual functions and classes

### Integration Tests
- Located in `backend/tests/integration/`
- Test API endpoints and database interactions

## Frontend Tests

```bash
cd frontend
npm test -- --coverage
```

### Component Tests
- Use React Testing Library
- Located alongside components in `__tests__/` directories

## CI/CD

Tests run automatically on every pull request via GitHub Actions.
