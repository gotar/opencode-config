# Python Project Structure

Guide to organizing Python projects with modern best practices, including `src` layout, package structure, and configuration files.

## Table of Contents

1. [Project Layouts](#project-layouts)
2. [src Layout vs Flat Layout](#src-layout-vs-flat-layout)
3. [Complete Project Structure](#complete-project-structure)
4. [pyproject.toml](#pyprojecttoml)
5. [Virtual Environments](#virtual-environments)
6. [Import Organization](#import-organization)
7. [Configuration Files](#configuration-files)

---

## Project Layouts

### When to Use Each Layout

| Layout | Use Case | Example |
|--------|----------|---------|
| **src Layout** | Python packages to be installed/installed | `requests`, `pandas` |
| **Flat Layout** | Simple scripts, not intended as packages | Utility scripts |
| **Mono Repository** | Multiple related packages | `numpy`, `scipy` |

---

## src Layout vs Flat Layout

### src Layout (Recommended for Packages)

**Structure**:
```
myproject/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
├── src/
│   └── myproject/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── main.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_main.py
│   └── test_utils.py
└── docs/
    ├── index.md
    └── api/
```

**Why src layout**:
- Prevents import confusion during development
- Ensures tests import from installed package, not source tree
- Better packaging behavior with tools like `setuptools_scm`
- Avoids namespace pollution
- Enables `pip install -e .` to work correctly

### Flat Layout (Simple Scripts)

**Structure**:
```
myscript/
├── pyproject.toml
├── README.md
├── script.py
├── module.py
└── tests/
    └── test_module.py
```

**When to use flat layout**:
- Single-file scripts or very simple projects
- Not planning to publish as a package
- Quick prototypes or experiments

---

## Complete Project Structure

### Full Modern Python Project

```
myproject/
│
├── pyproject.toml              # PEP 621 configuration (replaces setup.py/setup.cfg)
├── README.md                   # Project documentation
├── LICENSE                     # License file
├── CHANGELOG.md                # Version history
├── .gitignore                  # Git ignore patterns
├── .pre-commit-config.yaml      # Pre-commit hooks
├── .github/
│   └── workflows/
│       ├── ci.yml              # Continuous integration
│       └── release.yml         # Automated releases
│
├── src/                        # Source code (src layout)
│   └── myproject/
│       ├── __init__.py         # Package init
│       ├── __main__.py         # `python -m myproject`
│       ├── cli.py              # CLI entry points
│       ├── config.py           # Configuration
│       ├── main.py             # Main application code
│       ├── models.py           # Data models
│       ├── utils.py            # Utilities
│       └── api/
│           ├── __init__.py
│           ├── routes.py       # API routes
│           └── schemas.py      # Pydantic schemas
│
├── tests/                      # Tests (pytest)
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures
│   ├── test_main.py
│   ├── test_cli.py
│   ├── test_config.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py
│
├── docs/                       # Documentation (MkDocs/Sphinx)
│   ├── index.md
│   ├── installation.md
│   ├── usage.md
│   └── api/
│       └── main.md
│
├── data/                       # Static data (if any)
│   └── fixtures/
│       └── sample.json
│
├── scripts/                    # Utility scripts
│   ├── build.sh
│   └── migrate.py
│
└── .vscode/                    # VS Code settings
    ├── settings.json
    └── launch.json
```

---

## pyproject.toml

### Complete Example (PEP 621)

```toml
[build-system]
requires = ["hatchling", "setuptools-scm"]
build-backend = "hatchling.build"

[project]
name = "myproject"
dynamic = ["version"]
description = "A modern Python project"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "Author Name", email = "author@example.com"},
]
maintainers = [
    {name = "Maintainer Name", email = "maintainer@example.com"},
]

keywords = ["python", "example", "web"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "structlog>=23.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.10.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.23.0",
]
server = [
    "uvicorn>=0.24.0",
    "gunicorn>=21.0.0",
]
database = [
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.12.0",
]

[project.scripts]
myproject-cli = "myproject.cli:main"

[project.urls]
Homepage = "https://github.com/user/myproject"
Documentation = "https://myproject.readthedocs.io"
Repository = "https://github.com/user/myproject"
Issues = "https://github.com/user/myproject/issues"
Changelog = "https://github.com/user/myproject/blob/main/CHANGELOG.md"

[project.gui-scripts]
myproject-gui = "myproject.gui:main"

[tool.setuptools_scm]
write_to = "src/myproject/_version.py"
version_scheme = "release-branch-semver"

# Tool configurations
[tool.ruff]
line-length = 88
target-version = "py39"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "B", "C4"]
ignore = ["E501"]

[tool.ruff.lint.isort]
known-first-party = ["myproject"]

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
show_error_codes = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/myproject",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
asyncio_mode = "auto"

[tool.coverage.run]
source = ["src"]
branch = true
parallel = true

[tool.coverage.paths]
source = [
    "src/myproject",
    ".tox/*/lib/python*/site-packages/myproject",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "@abstractmethod",
]
precision = 2

[tool.black]
line-length = 88
target-version = ["py39", "py310", "py311", "py312"]
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

---

## Virtual Environments

### Using uv (Recommended)

```bash
# Create new project with uv
uv init myproject
cd myproject

# Create virtual environment
uv venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Add dependencies
uv add httpx pydantic

# Add dev dependencies
uv add --dev pytest pytest-cov mypy ruff

# Install from pyproject.toml
uv sync

# Run commands
uv run pytest
uv run myproject-cli
uv run python -m myproject

# Remove dependencies
uv remove httpx

# Update dependencies
uv lock --upgrade
```

### Using venv (Standard Library)

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Upgrade pip
python -m pip install --upgrade pip

# Install from pyproject.toml
pip install -e ".[dev,docs]"

# Freeze requirements
pip freeze > requirements.txt
```

### .gitignore for Python

```
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
PIPFILE.lock

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~
```

---

## Import Organization

### PEP 8 Import Order

```python
# Standard library imports
import asyncio
import os
from pathlib import Path
from typing import Optional, List, Dict

# Third-party imports
import httpx
from pydantic import BaseModel
from structlog import get_logger

# Local imports
from myproject.config import settings
from myproject.utils import calculate_sum

# Relative imports (within package)
from .models import User
from .api import routes
```

### __init__.py Patterns

```python
# src/myproject/__init__.py

"""
MyProject - A modern Python project.

Example usage:
    >>> from myproject import calculate_sum
    >>> calculate_sum([1, 2, 3])
    6
"""

__version__ = "1.0.0"

# Export public API
from myproject.main import calculate_sum, greet
from myproject.utils import helper_function

__all__ = [
    "calculate_sum",
    "greet",
    "helper_function",
]
```

---

## Configuration Files

### .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.6.0
    hooks:
      - id: mypy
        additional_dependencies:
          - pydantic>=2.0.0
          - types-all
```

### .vscode/settings.json

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "mypy.runUsingActiveInterpreter": true,
  "mypy.targets": ["src/"]
}
```

### .editorconfig

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.{py,pyi}]
indent_style = space
indent_size = 4

[*.{md,yml,yaml}]
indent_style = space
indent_size = 2

[*.{toml}]
indent_style = space
indent_size = 4

[Makefile]
indent_style = tab
```

---

## Best Practices

1. **Always use `src` layout for packages**: Better isolation and packaging
2. **Use `pyproject.toml`**: Modern PEP 621 standard
3. **Keep `__init__.py` simple**: Don't put complex logic there
4. **Organize by feature, not by layer**: Group related functionality
5. **Use `uv` for dependency management**: 10-100x faster than pip
6. **Add `.gitignore` early**: Don't accidentally commit artifacts
7. **Separate tests from source**: Clear separation of concerns
8. **Document public API**: Use `__all__` to define exports
