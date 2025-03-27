# Installation Guide

This guide will help you set up the Korea Geovariable project on your local machine.

## Prerequisites

Before you begin, ensure you have the following prerequisites installed:

1. **Python 3.11 or 3.12**
   - Download from [Python's official website](https://www.python.org/downloads/)
   - Verify installation:
     ```bash
     python --version
     ```

2. **uv Package Manager**
   - Install using pip:
     ```bash
     pip install uv
     ```
   - Verify installation:
     ```bash
     uv --version
     ```

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone https://github.com/ncc-airhealth/korea-geovariable
   cd korea-geovariable
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install Dependencies**
   ```bash
   uv sync
   ```

4. **Configure Environment Variables**
   ```bash
   # Copy the template file
   cp .env.template .env
   ```

   Edit the `.env` file with your database credentials:
   ```env
   DB_URL=postgresql://username:password@localhost:5432/database_name
   ```

   > **Note**: To obtain the database URL, please contact the system administrators:
   >
   > - [Han Jimin - 한지민](mailto:hangm0101@ncc.re.kr)
   > - [Son Dongook - 손동욱](mailto:d@dou.so)


5. **Verify Installation**
   ```bash
   # Run tests to verify installation
   python -m pytest tests/
   ```

## Common Issues and Solutions

### Database Connection Issues

If you encounter database connection issues:

1. Check database credentials in `.env` file

### Dependency Installation Issues

If `uv sync` fails:

1. Try updating uv:
   ```bash
   pip install --upgrade uv
   ```

2. Clear uv cache:
   ```bash
   uv cache clean
   ```

3. Try installing dependencies manually:
   ```bash
   pip install -r requirements.txt
   ```

## Next Steps

After installation, you can:

1. Read the [Configuration Guide](configuration.md) for detailed setup options
2. Check the [Database Setup Guide](database-setup.md) for database configuration
3. Start with [Basic Usage](../usage/basic-usage.md) to learn how to use the library
