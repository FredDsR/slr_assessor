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
- `--backup-file`: Enable persistent processing with backup file
- `--prompt-version`: Select prompt template version (e.g., `v1.0`, `v1.1`, `v2.0`)

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

# With backup for persistent processing (resumes automatically if interrupted)
slr-assessor screen papers.csv \
  --provider openai \
  --output results.csv \
  --backup-file session_backup.json

# Using Anthropic Claude
slr-assessor screen papers.csv \
  --provider anthropic \
  --model claude-3-sonnet-20240229 \
  --output results.csv

# Using specific prompt version
slr-assessor screen papers.csv \
  --provider openai \
  --output results.csv \
  --prompt-version v2.0

# Advanced usage with all options
slr-assessor screen papers.csv \
  --provider gemini \
  --model gemini-2.5-flash \
  --output results.csv \
  --prompt-version v1.1 \
  --usage-report usage.json \
  --backup-file session_backup.json
```

**💾 Backup Feature:**
- Use `--backup-file` to enable persistent processing
- Automatically resumes from previous session if interrupted
- Saves progress after each successfully processed paper
- Never lose work due to errors, network issues, or interruptions
- See [Backup Feature Guide](backup_feature.md) for detailed documentation

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
- Prompt version comparison and tracking

### `list-prompts` - List Available Prompt Versions

Display all available prompt template versions.

```bash
slr-assessor list-prompts
```

**Output:**
- Version identifier
- Description
- Creation date
- Hash for verification

### `show-prompt` - Display Prompt Template

Show the full content of a specific prompt version.

```bash
slr-assessor show-prompt v1.1
```

**Features:**
- Full prompt template display
- Version metadata
- Usage guidelines

### `compare-prompts` - Compare Prompt Versions

Compare two prompt template versions side by side.

```bash
slr-assessor compare-prompts v1.0 v2.0
```

**Features:**
- Side-by-side comparison
- Difference highlighting
- Version metadata comparison

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
- Prompt version and hash for traceability

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
  "metadata": {
    "comparison_id": "uuid",
    "timestamp": "2025-06-28T10:00:00Z",
    "dataset1_info": {
      "filename": "results1.csv",
      "prompt_version": "v1.0"
    },
    "dataset2_info": {
      "filename": "results2.csv", 
      "prompt_version": "v1.1"
    }
  },
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

## Prompt Versioning

The SLR Assessor supports multiple prompt template versions, allowing you to:
- Compare different assessment approaches
- Maintain consistency across evaluations
- Track prompt evolution over time
- Ensure reproducible results

### Available Prompt Versions

**v1.0 - Default**
- Basic QA assessment format
- Standard reasoning structure
- Stable and well-tested

**v1.1 - Enhanced**
- Improved reasoning guidance
- Better structured responses
- Enhanced clarity for complex papers

**v2.0 - Experimental**
- Advanced assessment criteria
- Detailed reasoning requirements
- Optimized for nuanced evaluations

### Using Prompt Versions

```bash
# List available prompt versions
slr-assessor list-prompts

# Use specific version for screening
slr-assessor screen papers.csv --prompt-version v1.1 --output results.csv

# View prompt template
slr-assessor show-prompt v2.0

# Compare two prompt versions
slr-assessor compare-prompts v1.0 v2.0
```

### Prompt Version Tracking

All evaluation results include prompt version metadata:
- Version identifier (e.g., "v1.1")
- Template hash for verification
- Creation timestamp
- Full traceability in comparison reports

### Best Practices for Prompt Versioning

1. **Start with v1.0** for initial assessments
2. **Test newer versions** on small datasets first
3. **Document version choices** for reproducibility
4. **Compare results** across versions when needed
5. **Use consistent versions** within the same study

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
2. **Choose prompt version**: Select appropriate version for your needs
3. **Estimate costs**: Always run cost estimation for large datasets
4. **Track usage**: Save usage reports for analysis
5. **Validate results**: Spot-check LLM assessments
6. **Document decisions**: Keep records of model and prompt version choices
7. **Compare approaches**: Test different prompt versions when needed
