# Contributing Guide

This guide explains how to contribute to the Korea Geovariable project.

For examples of our code style and API usage, see [Examples](../usage/examples.md) and [API Reference](../api/point-based-calculations.md).

## Getting Started

### Prerequisites

1. Python 3.11 or 3.12
2. Git
3. PostgreSQL with PostGIS
4. `uv` package manager

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/korea-geovariable.git
   cd korea-geovariable
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   uv sync
   ```

4. **Set Up Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Configure Environment Variables**
   ```bash
   cp .env.template .env
   # Edit .env with your database credentials
   ```

## Development Workflow

### 1. Create a New Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-fix-name
```

### 2. Make Changes

- Follow the [Code Style Guide](code-style.md)
- Write tests for new features
- Update documentation as needed

### 3. Run Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_point_based_calculations.py
```

### 4. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add new calculator for X"
```

### 5. Push Changes

```bash
git push origin feature/your-feature-name
```

### 6. Create Pull Request

1. Go to the project's GitHub page
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit the PR

## Code Style

### Python Style Guide

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Documentation Style

- Use Google style docstrings
- Include examples in docstrings
- Keep documentation up to date
- Use clear and concise language

### Git Commit Messages

Follow conventional commits:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

## Testing

### Writing Tests

1. Create test file in `tests/` directory
2. Use pytest fixtures for common setup
3. Test both success and failure cases
4. Include edge cases
5. Mock external dependencies

Example:
```python
import pytest
from point_based_calculations import PopulationCalculator, BufferSize

def test_population_calculator():
    calculator = PopulationCalculator(
        buffer_size=BufferSize.MEDIUM,
        year=2020
    )
    results = calculator.calculate()

    assert not results.empty
    assert 'tot_reg_cd' in results.columns
    assert 'POP_500' in results.columns

def test_invalid_year():
    with pytest.raises(ValueError):
        PopulationCalculator(
            buffer_size=BufferSize.MEDIUM,
            year=1999  # Invalid year
        )
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=.

# Run specific test file
python -m pytest tests/test_point_based_calculations.py

# Run tests with verbose output
python -m pytest -v
```

## Documentation

### Updating Documentation

1. Edit markdown files in `docs/` directory
2. Run documentation locally:
   ```bash
   mkdocs serve
   ```
3. Check documentation at http://127.0.0.1:8000

### Documentation Structure

- `index.md`: Project overview
- `getting-started/`: Installation and setup guides
- `usage/`: Usage guides and examples
- `api/`: API reference
- `development/`: Development guides

## Database Changes

### Adding New Tables

1. Create migration script in `scripts/` directory
2. Test migration locally
3. Update documentation
4. Include rollback instructions

Example:
```sql
-- Create new table
CREATE TABLE new_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add spatial index
CREATE INDEX idx_new_table_geom ON new_table USING GIST (geom);
```

## Release Process

### 1. Version Bump

```bash
# Update version in pyproject.toml
# Create release branch
git checkout -b release/v1.0.0
```

### 2. Update Changelog

Add changes to `CHANGELOG.md`:
```markdown
# Changelog

## [1.0.0] - 2024-03-27

### Added
- New feature X
- New calculator Y

### Changed
- Updated documentation
- Improved performance

### Fixed
- Bug in calculator Z
```

### 3. Create Release

1. Create tag:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```

2. Create GitHub release
3. Update documentation

## Getting Help

- Open an issue for bugs or feature requests
- Join discussions in GitHub Discussions
- Contact maintainers
   - [Han Jimin - 한지민](mailto:hangm0101@ncc.re.kr)
   - [Son Dongook - 손동욱](mailto:d@dou.so)

## Next Steps

1. Read the [Code Style Guide](code-style.md)
2. Check [Examples](../usage/examples.md) for usage patterns
3. Review [API Reference](../api/point-based-calculations.md)
