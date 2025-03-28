# Release Process Guide

This guide explains the release process for the Korea Geovariable project.

## Release Types

### 1. Major Release (X.0.0)
- Breaking changes
- New features
- Significant updates
- Example: 1.0.0 → 2.0.0

### 2. Minor Release (0.X.0)
- New features (backwards compatible)
- Deprecation notices
- Example: 1.0.0 → 1.1.0

### 3. Patch Release (0.0.X)
- Bug fixes
- Documentation updates
- Example: 1.0.0 → 1.0.1

## Release Schedule

1. **Major Releases**
   - Every 6 months
   - Planned in advance
   - Requires migration guide

2. **Minor Releases**
   - Every 2 months
   - Feature-based
   - Requires documentation updates

3. **Patch Releases**
   - As needed
   - Bug fix based
   - Quick turnaround

## Release Checklist

### 1. Pre-Release Tasks

1. **Update Version**
   ```toml
   # pyproject.toml
   [project]
   version = "1.0.0"
   ```

2. **Update Changelog**
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

3. **Run Tests**
   ```bash
   # Run all tests
   python -m pytest

   # Run with coverage
   python -m pytest --cov=.

   # Run specific test suites
   python -m pytest tests/test_point_based_calculations.py
   ```

4. **Check Documentation**
   ```bash
   # Build documentation
   mkdocs build

   # Check for broken links
   mkdocs build --strict
   ```

5. **Update Dependencies**
   ```bash
   # Update dependencies
   uv pip install --upgrade -r requirements.txt

   # Check for security issues
   safety check
   ```

### 2. Release Tasks

1. **Create Release Branch**
   ```bash
   # Create and switch to release branch
   git checkout -b release/v1.0.0

   # Update version
   # Update changelog
   # Commit changes
   git add .
   git commit -m "chore: prepare release v1.0.0"
   ```

2. **Create Release Tag**
   ```bash
   # Create annotated tag
   git tag -a v1.0.0 -m "Release v1.0.0"

   # Push tag
   git push origin v1.0.0
   ```

3. **Create GitHub Release**
   - Go to GitHub repository
   - Click "Releases"
   - Click "Create a new release"
   - Select tag
   - Add release notes
   - Upload assets
   - Publish release

4. **Build Distribution**
   ```bash
   # Build wheel
   python -m build

   # Check distribution
   twine check dist/*
   ```

5. **Upload to PyPI**
   ```bash
   # Upload to PyPI
   twine upload dist/*
   ```

### 3. Post-Release Tasks

1. **Update Documentation**
   - Update version numbers
   - Add migration guide if needed
   - Update examples

2. **Announce Release**
   - Update project website
   - Send email to users
   - Post on social media

3. **Monitor Issues**
   - Watch for bug reports
   - Monitor performance
   - Track user feedback

## Release Notes Template

```markdown
# Release v1.0.0

## Overview
Brief description of the release.

## New Features
- Feature 1
- Feature 2
- Feature 3

## Breaking Changes
- Change 1
- Change 2
- Change 3

## Improvements
- Improvement 1
- Improvement 2
- Improvement 3

## Bug Fixes
- Fix 1
- Fix 2
- Fix 3

## Documentation
- Update 1
- Update 2
- Update 3

## Migration Guide
Instructions for upgrading from previous version.

## Contributors
List of contributors to this release.

## Support
Information about getting help and support.
```

## Emergency Releases

### 1. Critical Bug Fixes

1. **Identify Issue**
   - Confirm bug severity
   - Document impact
   - Plan fix

2. **Create Hotfix Branch**
   ```bash
   # Create hotfix branch
   git checkout -b hotfix/v1.0.1

   # Apply fix
   # Update version
   # Update changelog
   # Commit changes
   git add .
   git commit -m "fix: critical bug in X"
   ```

3. **Release Process**
   - Follow normal release steps
   - Expedite testing
   - Quick deployment

### 2. Security Fixes

1. **Security Assessment**
   - Identify vulnerability
   - Assess impact
   - Plan fix

2. **Create Security Branch**
   ```bash
   # Create security branch
   git checkout -b security/v1.0.2

   # Apply fix
   # Update version
   # Update changelog
   # Commit changes
   git add .
   git commit -m "security: fix vulnerability in X"
   ```

3. **Release Process**
   - Follow normal release steps
   - Security testing
   - Quick deployment

## Release Automation

### 1. GitHub Actions Workflow

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine

      - name: Build package
        run: python -m build

      - name: Check package
        run: twine check dist/*

      - name: Upload to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
        run: twine upload dist/*
```

### 2. Release Script

```python
#!/usr/bin/env python
"""Release script for Korea Geovariable."""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_command(command):
    """Run a shell command."""
    result = subprocess.run(
        command,
        shell=True,
        check=True,
        capture_output=True,
        text=True
    )
    return result.stdout

def main():
    """Main function."""
    # Get version
    version = sys.argv[1]

    # Create release branch
    run_command(f"git checkout -b release/v{version}")

    # Update version in pyproject.toml
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    content = content.replace(
        'version = "0.0.0"',
        f'version = "{version}"'
    )
    pyproject.write_text(content)

    # Update changelog
    changelog = Path("CHANGELOG.md")
    content = changelog.read_text()
    content = f"# Changelog\n\n## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n" + content
    changelog.write_text(content)

    # Commit changes
    run_command("git add .")
    run_command(f'git commit -m "chore: prepare release v{version}"')

    # Create tag
    run_command(f"git tag -a v{version} -m 'Release v{version}'")

    # Push changes
    run_command(f"git push origin release/v{version}")
    run_command(f"git push origin v{version}")

if __name__ == "__main__":
    main()
```

## Next Steps

1. Review the [Contributing Guide](contributing.md)
2. Check [Code Style Guide](code-style.md)
3. Review [Architecture Guide](architecture.md)
