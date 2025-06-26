# SLR Assessor CLI

A command-line interface tool designed to standardize and accelerate the paper screening process for Systematic Literature Reviews (SLRs) using Large Language Models.

## Features

- **Automated Paper Screening**: Use LLMs for preliminary assessment
- **Standardized QA Protocol**: Consistent evaluation across LLM and human assessments
- **Traceability**: Structured CSV outputs with clear audit trails
- **Concordance Analysis**: Calculate Cohen's Kappa and identify conflicts
- **Multiple LLM Providers**: Support for OpenAI, Google Gemini, and Anthropic

## Installation

### Using uv (recommended)

```bash
# Clone the repository
git clone <repository-url>
cd slr_assessor

# Create environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Install with specific LLM provider support
uv pip install -e ".[openai]"     # For OpenAI
uv pip install -e ".[gemini]"     # For Google Gemini
uv pip install -e ".[anthropic]"  # For Anthropic
uv pip install -e ".[all]"        # For all providers
```

## Configuration

Create a `.env` file in the project root with your API keys:

```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Usage

### Screen Papers with LLM

```bash
slr-assessor screen papers.csv --provider openai --output results.csv
```

### Process Human Evaluations

```bash
slr-assessor process-human human_scores.csv --output processed_results.csv
```

### Compare Evaluations

```bash
slr-assessor compare results1.csv results2.csv --output conflict_report.json
```

## Input CSV Format

### For `screen` command:
- `id`: Unique paper identifier
- `title`: Paper title
- `abstract`: Paper abstract

### For `process-human` command:
- `id`: Unique paper identifier
- `title`: Paper title
- `abstract`: Paper abstract
- `qa1_score`, `qa1_reason`: Score (0, 0.5, 1) and reason for QA1
- `qa2_score`, `qa2_reason`: Score (0, 0.5, 1) and reason for QA2
- `qa3_score`, `qa3_reason`: Score (0, 0.5, 1) and reason for QA3
- `qa4_score`, `qa4_reason`: Score (0, 0.5, 1) and reason for QA4

## Quality Assurance Questions

1. **QA1**: Does the abstract clearly present the study's objective, research question, or central focus?
2. **QA2**: Does the abstract provide any indication of a practical application or an empirical result?
3. **QA3**: Does the abstract contextualize the challenge faced by the traditional community or by the application of AI?
4. **QA4**: Does the abstract directly address the integration of AI with traditional communities/knowledge?

## Decision Thresholds

- **Include**: total_score ≥ 2.5
- **Conditional Review**: 1.5 ≤ total_score < 2.5
- **Exclude**: total_score < 1.5

## License

MIT License
