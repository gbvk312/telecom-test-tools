# Contributing to Telecom Test Toolkit

First off, thank you for considering contributing to the Telecom Test Toolkit! 

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/telecom-test-tools.git
   cd telecom-test-tools
   ```
3. **Set up your environment**: We recommend using a virtual environment.
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -e ".[all,dev]"
   ```
4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

## Development Workflow

1. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and ensure that all tests pass:
   ```bash
   pytest
   ```
3. Formatting and linting will run automatically when you commit your changes via `pre-commit`. Ensure there are no warnings.
4. Push your branch to GitHub and open a Pull Request against the `main` branch.

## Issue Tracking

We use GitHub Issues to track bugs and features. Before creating a new issue, please search existing issues to see if it has already been reported.

Thank you for your contributions!
