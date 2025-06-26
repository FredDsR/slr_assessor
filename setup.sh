#!/bin/bash

# SLR Assessor Setup Script using uv

echo "Setting up SLR Assessor CLI..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Initialize uv project (creates venv and installs dependencies)
echo "Initializing uv project..."
uv sync

# Ask user which LLM providers to install
echo ""
echo "Which LLM providers would you like to install? (y/n for each)"

read -p "OpenAI (recommended): " install_openai
if [[ $install_openai == [Yy]* ]]; then
    uv add openai
fi

read -p "Google Gemini: " install_gemini  
if [[ $install_gemini == [Yy]* ]]; then
    uv add google-generativeai
fi

read -p "Anthropic Claude: " install_anthropic
if [[ $install_anthropic == [Yy]* ]]; then
    uv add anthropic
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file and add your API keys before using the tool."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API keys"
echo "2. Activate the environment: source .venv/bin/activate" 
echo "3. Test the installation: uv run slr-assessor --help"
echo ""
echo "Example usage:"
echo "uv run slr-assessor screen examples/sample_papers.csv --provider openai --output results.csv"
