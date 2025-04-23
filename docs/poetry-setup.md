# Poetry Setup for NetPrism

This document outlines the steps to set up Poetry for the NetPrism project.

## Prerequisites

- Python 3.10 or later
- Poetry 1.7.1 or later

## Installation

If you don't have Poetry installed, follow these steps:

### On Windows:
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### On macOS/Linux:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure Poetry is in your PATH.

## Project Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd netprism
```

2. Install dependencies:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

## Working with Poetry

- Add a new dependency:
```bash
poetry add <package-name>
```

- Add a development dependency:
```bash
poetry add --group dev <package-name>
```

- Update dependencies:
```bash
poetry update
```

- Run a command within the virtual environment:
```bash
poetry run <command>
```

For example, to run Django server:
```bash
poetry run python manage.py runserver
```

## Next Steps

After setup, continue with the Django project setup as outlined in the project documentation. 