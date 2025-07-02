# Software Specification: SLR Assessor CLI (v2)

## 1\. Overview and Goals

**SLR Assessor** is a command-line interface (CLI) tool designed to standardize and accelerate the paper screening process for Systematic Literature Reviews (SLRs). It leverages Large Language Models (LLMs) for preliminary assessment while providing robust tools for human evaluation and concordance analysis.

The primary goals of this software are:

  * **Automation:** Drastically reduce the manual effort of initial paper screening using a configurable LLM.
  * **Standardization:** Enforce a consistent Quality Assurance (QA) protocol across both LLM and human evaluations.
  * **Traceability:** Generate structured, machine-readable CSV outputs for every step, ensuring a clear audit trail.
  * **Analysis:** Provide quantitative insights into reviewer agreement by identifying conflicts and calculating Cohen's Kappa statistic.
  * **Modularity & Extensibility:** Be LLM-agnostic and built with a clean, modular architecture for future maintenance and expansion.

## 2\. Core Concepts & Data Models (Pydantic)

The system's data structures will be strictly defined and validated using Pydantic models.

### `Paper`

Represents a single paper to be screened. Read from the input CSV.

```pydantic
from typing import List, Literal, Optional
from pydantic import BaseModel

class Paper(BaseModel):
    id: str
    title: str
    abstract: str
```

### `QAResponseItem`

Represents the assessment for a single QA question as returned by the LLM.

```pydantic
class QAResponseItem(BaseModel):
    qa_id: str
    question: str
    score: Literal[0, 0.5, 1]
    reason: str
```

### `LLMAssessment`

Defines the complete, structured JSON object expected from the LLM provider.

```pydantic
class LLMAssessment(BaseModel):
    assessments: List[QAResponseItem]
    overall_summary: str
```

### `EvaluationResult`

The final, processed result for a single paper, whether evaluated by an LLM or a human. This is the canonical structure for each row in the output evaluation CSVs.

```pydantic
class EvaluationResult(BaseModel):
    # Paper Details
    id: str
    title: str
    abstract: str

    # Individual Scores & Reasons
    qa1_score: float
    qa1_reason: str
    qa2_score: float
    qa2_reason: str
    qa3_score: float
    qa3_reason: str
    qa4_score: float
    qa4_reason: str

    # Calculated Totals
    total_score: float
    decision: Literal["Include", "Exclude", "Conditional Review"]

    # Metadata
    llm_summary: Optional[str] = None # Only for LLM evaluations
    error: Optional[str] = None # To log any processing errors
```

### `ConflictReport`

The output structure for the `compare` command.

```pydantic
class Conflict(BaseModel):
    id: str
    decision_1: str
    decision_2: str
    total_score_1: float
    total_score_2: float
    score_difference: float

class ConflictReport(BaseModel):
    total_papers_compared: int
    total_conflicts: int
    cohen_kappa_score: float
    conflicts: List[Conflict]
```

## 3\. System Architecture

The application will be organized into a modular structure to ensure separation of concerns.

### Directory Structure

```
slr_assessor/
├── cli.py             # CLI command definitions (Typer)
├── main.py            # Entry point for the CLI application
├── models.py          # Pydantic data models
├── core/
│   ├── evaluator.py   # Core logic for scoring and decision making
│   └── comparator.py  # Logic for comparing evaluations and calculating Kappa
├── llm/
│   ├── providers.py     # Abstraction layer and concrete LLM provider integrations
│   ├── prompt.py        # Core prompt utilities (deprecated - kept for compatibility)
│   ├── prompt_manager.py # Prompt versioning management system
│   └── prompts/         # Directory containing versioned prompt templates
│       ├── __init__.py
│       ├── v1_0_default.py
│       ├── v1_1_enhanced.py
│       └── v2_0_experimental.py
└── utils/
    └── io.py          # CSV reading and writing utilities
.env                   # For storing API keys
pyproject.toml         # Project metadata and dependencies
```

### Component Responsibilities

  * `cli.py`: Defines the CLI commands (`screen`, `process-human`, `compare`) using `Typer`. Handles user input (arguments, options) and orchestrates calls to the core logic.
  * `models.py`: Contains all Pydantic models listed in Section 2.
  * `evaluator.py`: Contains the function to calculate `total_score` and determine the `decision` based on the QA rules. This logic is shared between the `screen` and `process-human` commands.
  * `comparator.py`: Implements the logic for the `compare` command. It will identify conflicts based on the defined rules and use `scikit-learn` to calculate Cohen's Kappa.
  * `llm/providers.py`:
      * Defines a base protocol/abstract class `LLMProvider` with a single method: `get_assessment(prompt: str) -> str`.
      * Contains concrete implementations for different providers (e.g., `OpenAIProvider`, `GoogleGeminiProvider`) that inherit from `LLMProvider`.
      * A factory function will select the provider based on the user's CLI option.
  * `llm/prompt_manager.py`: Manages prompt versioning system, loading built-in and custom prompt versions.
  * `llm/prompts/`: Directory containing versioned prompt templates with built-in versions (v1.0, v1.1, v2.0).
  * `llm/prompt.py`: Legacy prompt utilities (maintained for backward compatibility).
  * `utils/io.py`: Contains helper functions to read data from an input CSV into a list of `Paper` models and to write a list of `EvaluationResult` models to an output CSV.

## 4\. Command-Line Interface (CLI) Specification

The tool will be invoked as `slr-assessor`.

### Use Case 1: `screen` Command

  * **Purpose:** Screens a list of papers from a CSV file using a chosen LLM.
  * **Usage:**
    ```bash
    slr-assessor screen <INPUT_CSV> \
        --provider [openai|gemini|anthropic] \
        --output <OUTPUT_CSV> \
        --prompt-version <VERSION> \
        --api-key <YOUR_API_KEY>
    ```
  * **Arguments:**
      * `INPUT_CSV`: Path to the input CSV file. Expected columns: `id`, `title`, `abstract`.
  * **Options:**
      * `--provider, -p`: (Required) The LLM provider to use.
      * `--output, -o`: (Required) Path to save the resulting evaluation CSV.
      * `--prompt-version`: The prompt version to use (defaults to v1.0).
      * `--api-key`: The API key for the LLM provider. **If not provided, the tool must look for a corresponding environment variable (e.g., `OPENAI_API_KEY`).**
  * **Output:**
      * A CSV file at the specified output path, with columns matching the `EvaluationResult` model.
      * A progress bar in the console showing the screening progress.

### Use Case 2: `process-human` Command

  * **Purpose:** Processes a CSV of human-provided scores and reasons into the standard evaluation format.
  * **Usage:**
    ```bash
    slr-assessor process-human <INPUT_CSV> --output <OUTPUT_CSV>
    ```
  * **Arguments:**
      * `INPUT_CSV`: Path to the human evaluation CSV. Expected columns: `id`, `title`, `abstract`, `qa1_score`, `qa1_reason`, `qa2_score`, `qa2_reason`, `qa3_score`, `qa3_reason`, `qa4_score`, `qa4_reason`.
  * **Options:**
      * `--output, -o`: (Required) Path to save the standardized evaluation CSV.
  * **Output:**
      * A CSV file with the same format as the `screen` command's output, with `total_score` and `decision` calculated.

### Use Case 3: `compare` Command

  * **Purpose:** Compares two evaluation files, reports conflicts, and calculates the Cohen's Kappa score.
  * **Usage:**
    ```bash
    slr-assessor compare <EVALUATION_FILE_1> <EVALUATION_FILE_2> --output <REPORT_FILE>
    ```
  * **Arguments:**
      * `EVALUATION_FILE_1`: Path to the first evaluation CSV (from LLM or human).
      * `EVALUATION_FILE_2`: Path to the second evaluation CSV.
  * **Options:**
      * `--output, -o`: (Optional) Path to save a detailed JSON conflict report.
  * **Output:**
      * **Console:** A summary report printed to standard output, including the total number of conflicts and the Cohen's Kappa score.
      * **Report File:** If `--output` is provided, a JSON file is created containing the detailed `ConflictReport` data.

### Use Case 4: `list-prompts` Command

  * **Purpose:** Lists all available prompt versions (built-in and custom).
  * **Usage:**
    ```bash
    slr-assessor list-prompts
    ```
  * **Output:**
      * **Console:** Displays a formatted list of all available prompt versions with their metadata.

### Use Case 5: `show-prompt` Command

  * **Purpose:** Shows detailed information about a specific prompt version.
  * **Usage:**
    ```bash
    slr-assessor show-prompt <VERSION>
    ```
  * **Arguments:**
      * `VERSION`: The prompt version to display (e.g., v1.0, v1.1, v2.0).
  * **Output:**
      * **Console:** Displays detailed information about the prompt version including name, description, creation date, and assessment questions.

### Use Case 6: `compare-prompts` Command

  * **Purpose:** Compares screening results using two different prompt versions.
  * **Usage:**
    ```bash
    slr-assessor compare-prompts <PAPERS_CSV> \
        --prompt1 <VERSION1> \
        --prompt2 <VERSION2> \
        --provider <PROVIDER> \
        --output <OUTPUT_CSV>
    ```
  * **Arguments:**
      * `PAPERS_CSV`: Path to the input CSV file with papers to screen.
  * **Options:**
      * `--prompt1`: First prompt version to use for comparison.
      * `--prompt2`: Second prompt version to use for comparison.
      * `--provider`: LLM provider to use for both screenings.
      * `--output, -o`: Path to save the comparison report CSV.
  * **Output:**
      * **Console:** Summary of differences between the two prompt versions.
      * **Report File:** CSV file containing side-by-side results and conflict analysis.

## 5\. Key Logic & Business Rules

  * **Scoring Logic:**
      * `total_score` is the sum of `qa1_score`, `qa2_score`, `qa3_score`, and `qa4_score`. The range is 0-4.
  * **Decision Thresholds:**
      * `total_score >= 2.5` -\> "Include"
      * `1.5 <= total_score < 2.5` -\> "Conditional Review"
      * `total_score < 1.5` -\> "Exclude"
  * **Conflict Definition:** A conflict between two evaluations for the same `id` is defined as:
      * The `decision` value is different (e.g., "Include" vs. "Exclude").
      * OR the absolute difference between `total_score_1` and `total_score_2` is `≥ 1.0`.
  * **Cohen's Kappa Calculation:**
      * The calculation will be performed on the `decision` column.
      * The `scikit-learn` library (`sklearn.metrics.cohen_kappa_score`) must be used.
      * Papers present in one file but not the other (based on `id`) should be ignored for the calculation.

## 6. LLM Prompt Versioning System

The system uses a versioned prompt management approach to support different assessment strategies and enable prompt evolution while maintaining backwards compatibility.

### Prompt Versions

Each prompt version is defined by:
- **Version ID**: Semantic version identifier (e.g., v1.0, v1.1, v2.0)
- **Name**: Human-readable name for the prompt
- **Description**: Brief description of the prompt's purpose or improvements
- **Creation Date**: When the prompt version was created
- **Assessment Questions**: The specific QA questions used
- **Template**: The complete prompt template

### Built-in Prompt Versions

- **v1.0 (Default)**: Original SLR assessment prompt for AI-traditional community integration studies
- **v1.1 (Enhanced)**: Improved prompt with clearer criteria and scoring guidelines
- **v2.0 (Experimental)**: Cultural-participatory focus with emphasis on community aspects

### Prompt Template Structure

All prompt versions follow this general structure to ensure consistent JSON output:

```text
You are a meticulous academic researcher tasked with conducting a quality assessment of a research paper based solely on its abstract. Your evaluation must strictly follow the provided Quality Assurance (QA) criteria.

**Instructions:**
1. Read the abstract below carefully.
2. For each of the QA questions, provide a score and a brief, one-sentence reason for that score.
3. The score for each question MUST be one of these three values: **1** (satisfies), **0.5** (partially satisfies), or **0** (does not satisfy).
4. Your entire response must be a single, valid JSON object, with no text before or after it.

**Abstract to Evaluate:**
"""
{abstract_text}
"""

**Assessment Questions:**
{qa_questions}

**JSON Output Structure:**
{json_structure}
```

### Prompt Versioning Benefits

- **Reproducibility**: Track which prompt version was used for each evaluation
- **Comparison**: Compare results across different prompt versions
- **Evolution**: Improve prompts while maintaining backwards compatibility
- **Customization**: Support for custom prompt versions alongside built-in ones

## 7\. Dependencies & Environment

  * **Python Version:** 3.9+
  * **Key Libraries:**
      * `typer`: For the CLI.
      * `pydantic`: For data modeling and validation.
      * `pandas`: For all CSV I/O operations.
      * `scikit-learn`: For calculating Cohen's Kappa.
      * `python-dotenv`: For managing environment variables.
      * Provider-specific SDKs (e.g., `openai`, `google-genai`) to be installed as optional dependencies.
  * **Environment:**
      * API keys should be managed via a `.env` file in the project's root directory. The tool should be pre-configured to look for variables like `OPENAI_API_KEY`, `GOOGLE_API_KEY`, etc.
