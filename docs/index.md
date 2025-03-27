# Korea Geovariable

Welcome to the Korea Geovariable documentation! This project provides tools for calculating spatial data over time for specific coordinates, known as geographic variables (geovariables). It supports most of the geographic variables defined in Eum et al.

## Overview

Korea Geovariable is designed to help researchers analyze the relationship between spatial characteristics and health by combining cohort health information with geographic variables. The project uses data from various sources including:

- Public Data Portal
- KTDB
- Other government agencies

All data has been reviewed and refined by the National Cancer Center's Fine Dust Research Team and loaded into a PostGIS database.

## Quick Start

1. **Prerequisites**
   - Python 3.11 or 3.12
   - Database account (contact dongook.son@gmail.com)
   - `uv` package manager

2. **Installation**
   ```bash
   git clone https://github.com/yourusername/korea-geovariable.git
   cd korea-geovariable
   uv sync
   ```

3. **Configuration**
   - Copy `.env.template` to `.env`
   - Fill in your database credentials

## Features

- Comprehensive geographic variable calculations
- Support for various data sources
- Efficient spatial data processing
- Integration with health cohort data
- PostGIS database integration

## Documentation Sections

- [Installation Guide](getting-started/installation.md) - Detailed setup instructions
- [Configuration](getting-started/configuration.md) - How to configure the project
- [Database Setup](getting-started/database-setup.md) - Database configuration
- [Basic Usage](usage/basic-usage.md) - Getting started with the library
- [Available Calculators](usage/calculators.md) - List of supported calculations
- [Examples](usage/examples.md) - Usage examples
- [API Reference](api/point-based-calculations.md) - Detailed API documentation

## Support

For support or questions, please contact:

- Email: [Han Jimin - 한지민](mailto:hangm0101@ncc.re.kr)
- Email: [Son Dongook - 손동욱](mailto:d@dou.so)
- GitHub Issues: [Project Issues](https://github.com/ncc-airhealth/korea-geovariable/issues)
