# Usage Guide

This guide covers all commands and features available in the SLR Assessor CLI.

## Commands Overview

### `screen` - Automated Paper Screening

Use LLMs to automatically screen papers based on predefined QA criteria.

```bash
slr-assessor screen papers.csv --provider openai --output results.csv
```

**Options:**
- `--provider`: Choose LLM provider (`openai`, `gemini`, `anthropic`)
- `--model`: Specify model (e.g., `gpt-4`, `gemini-2.5-flash`)
- `--output`: Output CSV file path
- `--usage-report`: Save usage statistics to JSON file

**Examples:**
```bash
# Basic screening with OpenAI
slr-assessor screen papers.csv --provider openai --output results.csv

# With specific model and usage tracking
slr-assessor screen papers.csv \
  --provider gemini \
  --model gemini-2.5-flash \
  --output results.csv \
  --usage-report usage.json

# Using Anthropic Claude
slr-assessor screen papers.csv \
  --provider anthropic \
  --model claude-3-sonnet-20240229 \
  --output results.csv
```

### `process-human` - Process Human Evaluations

Process human evaluation data to standardize format and calculate decision scores.

```bash
slr-assessor process-human human_scores.csv --output processed_results.csv
```

**Input Format:**
Human evaluation CSV must include:
- `id`: Paper identifier
- `title`: Paper title
- `abstract`: Paper abstract
- `qa1_score`, `qa1_reason`: QA1 assessment (score: 0, 0.5, 1)
- `qa2_score`, `qa2_reason`: QA2 assessment
- `qa3_score`, `qa3_reason`: QA3 assessment
- `qa4_score`, `qa4_reason`: QA4 assessment

### `compare` - Compare Evaluations

Compare two evaluation datasets and generate concordance analysis.

```bash
slr-assessor compare results1.csv results2.csv --output conflict_report.json
```

**Features:**
- Cohen's Kappa calculation
- Conflict identification
- Agreement statistics
- Detailed disagreement analysis

### `estimate-cost` - Cost Estimation

Estimate the cost of screening before execution.

```bash
slr-assessor estimate-cost papers.csv --provider openai --model gpt-4
```

**Benefits:**
- Budget planning
- Model comparison
- Cost optimization
- Token usage prediction

### `analyze-usage` - Usage Analysis

Analyze saved usage reports from screening sessions.

```bash
slr-assessor analyze-usage usage.json
```

**Provides:**
- Total costs breakdown
- Token usage statistics
- Per-paper analysis
- Performance metrics

## Input Data Formats

### Papers CSV (for screening)

Required columns:
- `id`: Unique paper identifier
- `title`: Paper title
- `abstract`: Paper abstract

Example:
```csv
id,title,abstract
paper_001,"AI in Healthcare","This study explores the application of artificial intelligence..."
paper_002,"Machine Learning Models","We present novel machine learning approaches for..."
```

### Human Evaluations CSV

Required columns for human evaluation processing:
- `id`: Paper identifier
- `title`: Paper title  
- `abstract`: Paper abstract
- `qa1_score`: Score for QA1 (0, 0.5, or 1)
- `qa1_reason`: Reasoning for QA1 score
- `qa2_score`: Score for QA2 (0, 0.5, or 1)
- `qa2_reason`: Reasoning for QA2 score
- `qa3_score`: Score for QA3 (0, 0.5, or 1)
- `qa3_reason`: Reasoning for QA3 score
- `qa4_score`: Score for QA4 (0, 0.5, or 1)
- `qa4_reason`: Reasoning for QA4 score

## Output Formats

### Screening Results CSV

The output CSV includes:
- All original paper data
- QA scores and reasoning
- Total score and decision
- Token usage and cost information (when available)
- Model and provider information

### Usage Report JSON

Contains detailed session statistics:
```json
{
  "session_id": "uuid",
  "timestamp": "2025-06-28T10:00:00Z",
  "provider": "openai",
  "model": "gpt-4",
  "total_papers": 100,
  "successful_assessments": 98,
  "failed_assessments": 2,
  "total_cost": 15.75,
  "total_tokens": 125000,
  "average_cost_per_paper": 0.16
}
```

### Comparison Report JSON

Provides concordance analysis:
```json
{
  "cohen_kappa": 0.85,
  "agreement_percentage": 92.5,
  "total_comparisons": 100,
  "agreements": 92,
  "disagreements": 8,
  "conflicts": [...]
}
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Default settings
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4
```

### Supported Models

**OpenAI:**
- `gpt-4` (recommended for accuracy)
- `gpt-4-turbo`
- `gpt-3.5-turbo` (cost-effective)

**Google Gemini:**
- `gemini-2.5-flash` (recommended)
- `gemini-2.5-pro`

**Anthropic:**
- `claude-3-sonnet-20240229` (recommended)
- `claude-3-haiku-20240307` (cost-effective)
- `claude-3-opus-20240229` (highest accuracy)

## Best Practices

### Cost Optimization

1. **Use cost estimation** before large screening sessions
2. **Compare models** using small test sets
3. **Monitor usage** with tracking reports
4. **Choose appropriate models** based on accuracy needs vs cost

### Quality Assurance

1. **Validate inputs** before screening
2. **Review sample outputs** to ensure quality
3. **Use human evaluation** for critical decisions
4. **Compare multiple approaches** for important projects

### Workflow Recommendations

1. **Start small**: Test with 10-20 papers first
2. **Estimate costs**: Always run cost estimation for large datasets
3. **Track usage**: Save usage reports for analysis
4. **Validate results**: Spot-check LLM assessments
5. **Document decisions**: Keep records of model choices and rationale
