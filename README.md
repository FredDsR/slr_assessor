# SLR Assessor CLI

A command-line interface tool designed to standardize and accelerate the paper screening process for Systematic Literature Reviews (SLRs) using Large Language Models.

## ✨ Features

- 🤖 **Automated Paper Screening**: Use LLMs (OpenAI, Gemini, Anthropic) for preliminary assessment
- 📋 **Standardized QA Protocol**: Consistent 4-point evaluation framework
- � **Prompt Versioning**: Multiple assessment approaches with version control and comparison
- �💰 **Cost Management**: Estimate and track token usage and costs
- 📊 **Concordance Analysis**: Calculate Cohen's Kappa and identify conflicts
- 🔍 **Traceability**: Structured CSV outputs with clear audit trails
- 🔧 **Multiple Providers**: Support for OpenAI, Google Gemini, and Anthropic

## 🚀 Quick Start

### Installation

```bash
# Clone and install
git clone <repository-url>
cd slr_assessor
uv venv && source .venv/bin/activate
uv pip install -e ".[all]"
```

### Configuration

Create `.env` file with your API keys:
```env
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### Basic Usage

```bash
# Estimate costs first
slr-assessor estimate-cost papers.csv --provider openai

# Screen papers
slr-assessor screen papers.csv --provider openai --output results.csv

# Compare evaluations
slr-assessor compare llm_results.csv human_results.csv --output analysis.json
```

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Installation Guide](docs/installation.md) | Detailed setup instructions and troubleshooting |
| [Usage Guide](docs/usage.md) | Complete command reference and examples |
| [QA Protocol](docs/qa-protocol.md) | Quality assurance questions and scoring system |
| [Specification](docs/SPECIFICATION.md) | Technical architecture and data models |
| [Cost Tracking](docs/cost_tracking.md) | Token usage and cost management features |

## 🎯 Quality Assurance Framework

The tool evaluates papers using 4 standardized questions:

1. **Study Objective Clarity**: Clear research questions/objectives?
2. **Practical Application**: Evidence of empirical results/applications?
3. **Challenge Context**: Contextualizes traditional/AI challenges?
4. **AI Integration**: Addresses AI-traditional knowledge integration?

**Decision Thresholds:**
- **Include**: ≥ 2.5 total score
- **Conditional**: 1.5-2.4 total score  
- **Exclude**: < 1.5 total score

## 📋 Input Format

Your CSV file needs these columns:
```csv
id,title,abstract
paper_001,"AI in Healthcare","This study explores..."
```

## 🛠️ Available Commands

| Command | Purpose |
|---------|---------|
| `screen` | Automated LLM-based paper screening |
| `process-human` | Process human evaluation data |
| `compare` | Compare two evaluation datasets |
| `estimate-cost` | Estimate screening costs before execution |
| `analyze-usage` | Analyze usage reports and costs |

## 🔧 Supported Models

- **OpenAI**: GPT-4, GPT-4-turbo, GPT-3.5-turbo
- **Google**: Gemini-2.5-flash, Gemini-2.5-pro
- **Anthropic**: Claude-3-sonnet, Claude-3-haiku, Claude-3-opus

## 📊 Example Workflow

```bash
# 1. Estimate costs for different models
slr-assessor estimate-cost papers.csv --provider openai --model gpt-4
slr-assessor estimate-cost papers.csv --provider gemini --model gemini-2.5-flash

# 2. Run screening with cost tracking
slr-assessor screen papers.csv \
  --provider openai \
  --output results.csv \
  --usage-report usage.json

# 3. Analyze costs and usage
slr-assessor analyze-usage usage.json

# 4. Compare with human evaluations
slr-assessor compare results.csv human_eval.csv --output comparison.json
```

## 📄 License

MIT License

---

**Need help?** Check the [Installation Guide](docs/installation.md) for detailed setup instructions or the [Usage Guide](docs/usage.md) for complete command documentation.
