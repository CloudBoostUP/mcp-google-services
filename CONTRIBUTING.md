# Contributing to Google Services MCP Server

Thank you for your interest in contributing to the Google Services MCP Server! We welcome contributions from the community and appreciate your help in making this project better.

## 🎯 How to Contribute

### Types of Contributions

We welcome several types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Submit bug fixes or new features
- **Documentation**: Improve our documentation
- **Testing**: Help us test the software
- **Examples**: Share usage examples and tutorials

### Getting Started

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/mcp-google-services.git
   cd mcp-google-services
   ```

2. **Set Up Development Environment**
   ```bash
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8 style guidelines
- **Formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for code linting
- **Type Hints**: Use type hints for better code documentation
- **Docstrings**: Follow Google docstring format

### Testing

- **Write Tests**: Include tests for new functionality
- **Test Coverage**: Maintain good test coverage
- **Test Types**: Write unit tests, integration tests, and end-to-end tests
- **Test Commands**:
  ```bash
  # Run all tests
  pytest
  
  # Run with coverage
  pytest --cov=mcp_google_services
  
  # Run specific test file
  pytest tests/test_services/test_gmail/
  ```

### Documentation

- **README Updates**: Update README.md for significant changes
- **API Documentation**: Document new API endpoints and tools
- **Code Comments**: Add clear comments for complex logic
- **Type Hints**: Use type hints to improve code documentation

## 🚀 Submitting Changes

### Pull Request Process

1. **Create a Pull Request**
   - Use a clear, descriptive title
   - Reference any related issues
   - Provide a detailed description

2. **Pull Request Template**
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests pass locally
   - [ ] New tests added for new functionality
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] Tests added/updated
   ```

3. **Code Review Process**
   - All submissions require review
   - Address feedback promptly
   - Keep PRs focused and small when possible

### Commit Messages

Use clear, descriptive commit messages:

```bash
# Good examples
feat: add Gmail backup functionality
fix: resolve authentication timeout issue
docs: update API documentation
test: add unit tests for Drive API client

# Bad examples
fix stuff
update
changes
```

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Environment**: Python version, OS, dependencies
- **Steps to Reproduce**: Clear, numbered steps
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error messages and stack traces
- **Additional Context**: Any other relevant information

### Feature Requests

For feature requests, please include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Other solutions you've considered
- **Additional Context**: Any other relevant information

## 🔧 Development Setup

### Prerequisites

- Python 3.8 or higher
- Google Cloud Project with APIs enabled
- Git
- Virtual environment (recommended)

### Local Development

```bash
# Clone and setup
git clone https://github.com/CloudBoostUP/mcp-google-services.git
cd mcp-google-services

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Configuration

```bash
# Copy example configuration
cp config/config.example.json config/config.json

# Set up Google API credentials
# Place your credentials.json in config/ directory
```

## 📚 Resources

### Documentation

- [API Documentation](docs/api.md)
- [Setup Guide](docs/setup.md)
- [Service Documentation](docs/services/)
- [Troubleshooting](docs/troubleshooting.md)

### External Resources

- [Google API Documentation](https://developers.google.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python Best Practices](https://docs.python-guide.org/)

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the golden rule

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **Discussions**: For questions and general discussion
- **Website**: [cloudboostup.com](https://cloudboostup.com)

## 🏆 Recognition

Contributors will be recognized in:

- **CONTRIBUTORS.md**: List of all contributors
- **Release Notes**: Credit for significant contributions
- **Documentation**: Attribution for documentation contributions

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Google Services MCP Server!** 🚀

[Back to Repository](https://github.com/CloudBoostUP/mcp-google-services) • [Website](https://cloudboostup.com)
