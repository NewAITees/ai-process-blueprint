# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Process Blueprint is a template management system providing structured work procedures to AI assistants via HTTP API and MCP (Model Context Protocol) interfaces. Templates are stored as Markdown files with YAML frontmatter.

## Commands

### Development Setup
```bash
./setup_env.sh                    # Environment setup with uv
source .venv/bin/activate         # Activate virtual environment
```

### Server Operations  
```bash
./start_server.sh                 # Start development server (preferred)
uvicorn app.main:app --reload     # Alternative direct start
python run.py                     # Simple startup script
```

### Testing
```bash
./run_tests.sh                    # Full test suite with coverage (preferred)
pytest                           # Simple test run
pytest --cov=app                  # Coverage reporting
pytest tests/test_specific.py     # Run specific test file
```

### Code Quality
```bash
black app tests                   # Code formatting
isort app tests                   # Import sorting  
flake8 app tests                  # Linting
mypy app                          # Type checking
```

### Docker Operations
```bash
docker-compose up -d              # Production deployment
docker-compose up --build        # Rebuild and start containers
```

## Architecture

### Layered Design
- **Interface Layer** (`app/api/`, `app/mcp/`): FastAPI HTTP endpoints and MCP tools
- **Business Logic** (`app/core/services.py`): TemplateService with validation and business rules
- **Data Access** (`app/data/repository.py`): FileSystemTemplateRepository with abstract interface

### Key Patterns
- **Repository Pattern**: `TemplateRepository` interface with file-based implementation
- **Service Layer**: `TemplateService` handles business logic and validation  
- **Dependency Injection**: FastAPI's DI system manages service instantiation
- **Dual Interface**: Both HTTP API and MCP tools for different use cases

### Template Storage Format
Templates are Markdown files with YAML frontmatter in the `templates/` directory:
```markdown
---
title: "Template Title"
description: "Template description"  
username: "creator"
created_at: "2025-01-01T00:00:00Z"
updated_at: "2025-01-01T00:00:00Z"
---

# Template Content
Markdown content here...
```

### API Structure
- `GET /api/templates` - List templates with pagination/filtering
- `GET /api/templates/{title}` - Retrieve specific template
- `POST /api/templates` - Create new template
- `PUT /api/templates/{title}` - Update existing template  
- `DELETE /api/templates/{title}` - Delete template

### MCP Tools
- `get_template`, `list_templates`, `register_template`, `update_template`, `delete_template`

## Configuration

Environment variables (via `.env` or system):
- `PORT`: Server port (default: 8080)
- `TEMPLATE_DIR`: Template storage path
- `DEBUG`: Development mode toggle
- `ENABLE_MCP`/`ENABLE_HTTP`: Interface toggles
- `LOG_LEVEL`: Logging verbosity

## Testing Strategy

- **Unit Tests**: Service and repository layer (`tests/unit/`)
- **Integration Tests**: API endpoints (`tests/integration/`)
- **Fixtures**: Test data and temporary directories in `conftest.py`
- **Async Support**: Full async/await testing with pytest-asyncio

## Package Management

Prefer `uv` over Poetry for dependency management. The project supports both:
- `uv sync` for uv-based setup
- `poetry install` for Poetry-based setup