# Contribution Guide

## Code Standards

### Python

- **Python 3.13+**: Use latest Python features (pattern matching, generics)
- **Type Hints**: All functions must have type annotations
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Line Length**: Maximum 120 characters
- **Docstrings**: Google-style docstrings for all public functions

### TypeScript

- **Strict Mode**: Always use TypeScript strict mode
- **Naming**: `camelCase` for functions/variables, `PascalCase` for components/types
- **Line Length**: Maximum 120 characters
- **Imports**: Use absolute imports (`@/components/...`)

## Development Workflow

### 1. Branch Strategy

```
main          Production-ready code
├── develop   Integration branch
│   ├── feature/*   New features
│   ├── fix/*       Bug fixes
│   └── refactor/*  Code refactoring
```

### 2. Commit Convention

```
type(scope): description

Types: feat, fix, docs, refactor, test, chore, perf, security
Scope:  auth, marketplace, payments, core, frontend, docs, etc.

Examples:
  feat(auth): add Google OAuth login
  fix(payments): resolve currency rounding error
  docs(api): update endpoint documentation
```

### 3. Pull Request Process

1. Create feature/fix branch from `develop`
2. Implement changes following code standards
3. Add/update tests
4. Run linters and type checkers
5. Create PR with description of changes
6. Wait for review approval
7. Merge to `develop`

## Testing Requirements

### Backend

- Unit tests for all services and repositories
- Integration tests for API endpoints
- Minimum 80% code coverage
- Use `pytest-asyncio` for async tests

### Frontend

- Component tests for UI components
- Integration tests for page flows
- TypeScript strict mode enforced

## Code Review Checklist

- [ ] Code follows project coding standards
- [ ] Type annotations are complete and correct
- [ ] Tests are added and passing
- [ ] No security vulnerabilities introduced
- [ ] Performance implications considered
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate (not excessive, not missing)
- [ ] No hardcoded secrets or configuration
- [ ] API changes are documented
- [ ] Database migrations are backward compatible

## Security Guidelines

- Never commit secrets, API keys, or passwords
- Use parameterized queries (SQLAlchemy ORM)
- Validate all user input (Pydantic/Zod)
- Apply principle of least privilege
- Log security events (failed logins, unauthorized access)
- Report vulnerabilities to security@tsbl.com
