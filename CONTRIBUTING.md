# Contributing to Weaver

## Development Setup

1. Clone the repository
2. Run setup script: `bash scripts/setup.sh`
3. Configure environment variables in `backend/.env` and `frontend/.env.local`
4. Start services (see README.md)

## Code Style

### Python (Backend)

- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Format with Black (if available)
- Lint with Flake8 (if available)

### TypeScript (Frontend)

- Follow Airbnb style guide
- Use functional components
- Prefer hooks over class components
- Format with Prettier (if available)

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Pull Request Process

1. Create a feature branch from `dev`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation if needed
6. Submit PR to `dev` branch
7. Wait for review and CI checks

## Commit Messages

Use conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Build/tooling changes

Example: `feat: add streaming support for query endpoint`

## Architecture Decisions

Major architectural changes should be discussed via GitHub issues before implementation.

## Questions?

Open an issue or contact the maintainers.

