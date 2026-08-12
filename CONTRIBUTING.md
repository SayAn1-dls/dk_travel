# Contributing to Wanderly

Thank you for your interest in contributing to Wanderly! This guide will help you get started.

## 🚀 Getting Started

### 1. Fork & Clone

```bash
git clone https://github.com/<your-username>/dk_travel.git
cd dk_travel
```

### 2. Set Up Development Environment

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

**Frontend:**
```bash
cd frontend
npm install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## 📋 Development Workflow

1. **Pick an issue** — Check the [Issues](https://github.com/SayAn1-dls/dk_travel/issues) tab for open tasks
2. **Write code** — Follow the existing code style and patterns
3. **Write tests** — All new features should include test coverage
4. **Run linting** — Ensure your code passes lint checks
5. **Commit** — Use [Conventional Commits](https://www.conventionalcommits.org/) format
6. **Push & PR** — Open a Pull Request against `main`

## 📝 Commit Convention

We follow Conventional Commits:

| Prefix | Usage |
|--------|-------|
| `feat:` | New feature |
| `fix:` | Bug fix |
| `docs:` | Documentation changes |
| `style:` | Code style (formatting, semicolons) |
| `refactor:` | Code restructuring |
| `test:` | Adding or updating tests |
| `chore:` | Maintenance tasks |
| `perf:` | Performance improvements |
| `ci:` | CI/CD changes |

### Examples

```
feat: add hotel search filtering by star rating
fix: resolve currency conversion rounding error
docs: update API documentation for reviews endpoint
test: add unit tests for itinerary planner
```

## 🧪 Running Tests

```bash
# Backend
cd backend && pytest --tb=short -v

# Frontend
cd frontend && npm test
```

## 🎨 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints for function signatures
- Use docstrings for public functions and classes
- Max line length: 100 characters

### JavaScript/React (Frontend)
- Use functional components with hooks
- Follow ESLint configuration
- Use Prettier for formatting
- Prefer named exports for components

## 🐛 Reporting Bugs

Please use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) when filing issues.

Include:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Screenshots if applicable
- Environment details (OS, browser, Node/Python version)

## 💡 Feature Requests

We love ideas! Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

## 📜 Code of Conduct

By contributing, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## ❓ Questions?

Open a [Discussion](https://github.com/SayAn1-dls/dk_travel/discussions) or reach out to the maintainers.

---

Thank you for helping make Wanderly better! 🌍
