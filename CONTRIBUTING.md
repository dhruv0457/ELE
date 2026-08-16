# Contributing to ELE Agent

Thank you for your interest in contributing to ELE Agent! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/ele-agent/ele-agent/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (OS, Python/Node versions)

### Suggesting Features

1. Check existing issues and discussions
2. Create a feature request issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests and linting
5. Commit with clear messages
6. Push to your fork
7. Open a pull request

## Development Setup

### Backend (Python)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

### Web (Next.js)

```bash
cd web
npm install
```

### Desktop (Electron)

```bash
cd desktop
npm install
```

### CLI (Textual)

```bash
cd cli
pip install -e .
pip install -r requirements-dev.txt
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Run `ruff check .` and `mypy .` before committing
- Max line length: 100 characters

### TypeScript/React

- Use functional components with hooks
- Follow ESLint config
- Run `npm run lint` and `npm run type-check` before committing
- Use Tailwind CSS for styling

### Git Commits

Use conventional commits:

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
```
feat(agent): add parallel LLM orchestration
fix(voice): resolve wake word detection issue
docs(api): update WebSocket event documentation
```

## Testing

### Backend

```bash
cd backend
python -m pytest tests/ -v --cov=app
```

### Frontend

```bash
cd web
npm run test
```

### Desktop

```bash
cd desktop
npm run test
```

### CLI

```bash
cd cli
python -m pytest tests/ -v
```

## Plugin Development

### Python Plugin

```python
# manifest.json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "version": "1.0.0",
  "entry_point": "main.py",
  "permissions": ["file:read", "file:write"]
}
```

```python
# main.py
class MyPlugin:
    async def initialize(self, context):
        self.config = context.get("config", {})

    async def my_hook(self, data):
        return {"result": "done"}

async def initialize(context):
    return MyPlugin()
```

### JSON Plugin

Create a `manifest.json` with hooks referencing shell commands.

## Architecture Guidelines

- **Backend**: Modular design with clear separation of concerns
- **Frontend**: Component-based, state management with Zustand
- **Desktop**: Secure IPC bridge via preload script
- **CLI**: Textual-based TUI with reactive UI

## Documentation

- Update relevant docs in `docs/` for any user-facing changes
- Add docstrings for new public APIs
- Include examples for new features

## Release Process

1. Maintainers create release branch
2. Version bump in `pyproject.toml` and `package.json` files
3. Changelog updated
4. Tagged release triggers CI/CD
5. Artifacts published to GitHub Releases

## Getting Help

- [GitHub Discussions](https://github.com/ele-agent/ele-agent/discussions)
- [Discord](https://discord.gg/ele-agent)
- Email: contributors@ele-agent.dev

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Release notes
- Project README

Thank you for contributing to ELE Agent!