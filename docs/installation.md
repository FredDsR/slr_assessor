# Installation Guide

This guide provides detailed installation instructions for the SLR Assessor CLI tool.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: At least 1GB RAM
- **Storage**: 100MB for installation

## Installation Methods

### Method 1: Using uv (Recommended)

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that provides the best experience.

#### Install uv (if not already installed)

```bash
# On Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Install SLR Assessor

```bash
# Clone the repository
git clone <repository-url>
cd slr_assessor

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Install with LLM Provider Support

Choose the providers you need:

```bash
# For OpenAI only
uv pip install -e ".[openai]"

# For Google Gemini only  
uv pip install -e ".[gemini]"

# For Anthropic only
uv pip install -e ".[anthropic]"

# For all providers
uv pip install -e ".[all]"
```

### Method 2: Using pip

```bash
# Clone the repository
git clone <repository-url>
cd slr_assessor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
pip install -e .

# Install with provider support
pip install -e ".[all]"
```

### Method 3: Using conda

```bash
# Create conda environment
conda create -n slr-assessor python=3.11
conda activate slr-assessor

# Clone and install
git clone <repository-url>
cd slr_assessor
pip install -e ".[all]"
```

## Configuration

### API Keys Setup

Create a `.env` file in the project root directory:

```bash
# Navigate to project directory
cd slr_assessor

# Create .env file
touch .env
```

Add your API keys to the `.env` file:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Google Gemini API Key
GOOGLE_API_KEY=your_google_api_key_here

# Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Set defaults
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4
```

### Obtaining API Keys

#### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an account or sign in
3. Navigate to "API Keys"
4. Create a new secret key
5. Copy the key to your `.env` file

#### Google Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Navigate to "Get API Key"
4. Create a new API key
5. Copy the key to your `.env` file

#### Anthropic API Key
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Navigate to "API Keys"
4. Create a new key
5. Copy the key to your `.env` file

## Verification

### Test Installation

Run the built-in test to verify everything is working:

```bash
python test_installation.py
```

This will check:
- Package installation
- Dependencies
- API key configuration
- Basic functionality

### Test CLI Commands

```bash
# Check if CLI is installed
slr-assessor --help

# Test with sample data
slr-assessor screen examples/sample_papers.csv --provider openai --output test_results.csv
```

## Troubleshooting

### Common Issues

#### 1. Command not found: `slr-assessor`

**Solution:**
- Ensure virtual environment is activated
- Reinstall with: `pip install -e .`
- Check if `~/.local/bin` is in your PATH

#### 2. API Key errors

**Solution:**
- Verify `.env` file exists in project root
- Check API key format (no extra spaces/quotes)
- Ensure API key is valid and has sufficient credits

#### 3. Import errors

**Solution:**
- Install with provider extras: `pip install -e ".[all]"`
- Check Python version compatibility
- Reinstall dependencies

#### 4. Permission errors

**Solution:**
- Use virtual environment
- On Linux/macOS: Check file permissions
- On Windows: Run as administrator if needed

### Getting Help

If you encounter issues:

1. **Check the logs**: Enable verbose logging with `--verbose` flag
2. **Verify configuration**: Run `test_installation.py`
3. **Check dependencies**: Run `pip list` to see installed packages
4. **Update packages**: Try `pip install -e ".[all]" --upgrade`

## Development Installation

For development work:

```bash
# Clone with development dependencies
git clone <repository-url>
cd slr_assessor

# Install in development mode
uv pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Uninstallation

To remove the package:

```bash
# Uninstall the package
pip uninstall slr-assessor

# Remove virtual environment
rm -rf .venv  # On Windows: rmdir /s .venv
```

## Next Steps

After installation:

1. **Read the Usage Guide**: See `docs/usage.md` for detailed command instructions
2. **Review QA Protocol**: Check `docs/qa-protocol.md` to understand the evaluation criteria
3. **Try Examples**: Use the sample data in `examples/` to test functionality
4. **Estimate Costs**: Run cost estimation before large screening sessions

## Updates

To update to the latest version:

```bash
# Navigate to project directory
cd slr_assessor

# Pull latest changes
git pull origin main

# Update installation
uv pip install -e ".[all]" --upgrade
```
