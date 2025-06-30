# Backup Feature Documentation

## Overview

The backup feature provides persistent, resumable paper screening sessions. If processing is interrupted due to errors, network issues, or user intervention, you can resume exactly where you left off without losing already processed papers.

## How It Works

1. **Backup Creation**: When you specify `--backup-file`, the system creates a JSON backup file that stores:
   - Session metadata (provider, model, file paths)
   - All successfully processed papers and their evaluations
   - Progress tracking information
   - Usage statistics

2. **Automatic Resumption**: If a backup file exists, the system automatically:
   - Loads the previous session
   - Validates compatibility (same provider, model, input file)
   - Skips already processed papers
   - Continues from where it left off

3. **Error Handling**: If an error occurs during processing:
   - The backup is updated with all successfully processed papers
   - Processing stops gracefully
   - You can resume later using the same command

## Usage Examples

### Starting a New Session with Backup

```bash
slr-assessor screen papers.csv \
  --provider openai \
  --output results.csv \
  --backup-file backup_session.json
```

### Resuming from a Previous Session

```bash
# Same command - will automatically resume if backup exists
slr-assessor screen papers.csv \
  --provider openai \
  --output results.csv \
  --backup-file backup_session.json
```

### Different Backup Files for Different Experiments

```bash
# Experiment 1: OpenAI GPT-4
slr-assessor screen papers.csv \
  --provider openai \
  --model gpt-4 \
  --output results_gpt4.csv \
  --backup-file backup_gpt4.json

# Experiment 2: Gemini
slr-assessor screen papers.csv \
  --provider gemini \
  --model gemini-2.5-flash \
  --output results_gemini.csv \
  --backup-file backup_gemini.json
```

## Backup File Structure

The backup file contains:

```json
{
  "session_id": "unique-session-id",
  "start_time": "2025-06-30T10:00:00",
  "provider": "openai",
  "model": "gpt-4",
  "input_csv_path": "/path/to/papers.csv",
  "output_csv_path": "/path/to/results.csv",
  "total_papers": 100,
  "processed_papers": [
    {
      "id": "paper_001",
      "title": "Paper Title",
      "abstract": "Paper abstract...",
      "qa1_score": 1.0,
      "qa1_reason": "Clear objectives",
      // ... full evaluation results
    }
  ],
  "processed_paper_ids": ["paper_001", "paper_002", ...],
  "usage_tracker_data": {
    "total_papers_processed": 2,
    "successful_papers": 2,
    "failed_papers": 0,
    "total_cost": 0.05
  },
  "last_updated": "2025-06-30T10:15:00"
}
```

## Benefits

1. **Resilience**: Never lose progress due to interruptions
2. **Cost Efficiency**: Avoid reprocessing papers you've already paid for
3. **Flexibility**: Pause and resume sessions as needed
4. **Experimentation**: Run multiple backup sessions for different configurations
5. **Transparency**: Full audit trail of processing history

## Important Notes

- **Compatibility Check**: The system validates that backup sessions match the current command (same provider, model, input file)
- **Error Recovery**: Processing stops immediately on errors, allowing you to investigate and resume
- **Progress Tracking**: Real-time display of completion percentage when resuming
- **Final Output**: The final CSV contains ALL papers (both from backup and newly processed)

## Best Practices

1. **Use Descriptive Backup Names**: Include provider/model in the filename
2. **Keep Backups Safe**: Backup files contain your complete processing history
3. **Monitor Progress**: Check the console output for resumption information
4. **Handle Errors**: Investigate error messages before resuming to avoid repeated failures
