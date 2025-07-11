"""CLI command definitions using Typer."""

import json
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import track

from .core.comparator import compare_evaluations
from .core.evaluator import create_evaluation_result
from .llm.prompt import format_assessment_prompt
from .llm.providers import create_provider, parse_llm_response
from .models import EvaluationResult
from .utils.backup import BackupManager
from .utils.cost_calculator import (
    estimate_screening_cost,
)
from .utils.io import (
    read_evaluations_from_csv,
    read_human_evaluations_from_csv,
    read_papers_from_csv,
    write_evaluations_to_csv,
)
from .utils.usage_tracker import UsageTracker

# Load environment variables
load_dotenv()

app = typer.Typer(
    name="slr-assessor",
    help="A CLI tool for standardizing and accelerating paper screening in Systematic Literature Reviews using LLMs",
    no_args_is_help=True,
)
console = Console()


@app.command()
def screen(
    input_csv: str = typer.Argument(..., help="Path to input CSV file with papers"),
    provider: str = typer.Option(
        ..., "-p", "--provider", help="LLM provider (openai, gemini, anthropic)"
    ),
    output: str = typer.Option(
        ..., "-o", "--output", help="Path to save evaluation results CSV"
    ),
    prompt_version: str = typer.Option(
        "v1.0", "--prompt-version", help="Prompt version to use"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Specific model to use (optional)"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="API key for LLM provider"
    ),
    usage_report: Optional[str] = typer.Option(
        None, "--usage-report", help="Path to save usage report JSON"
    ),
    backup_file: Optional[str] = typer.Option(
        None,
        "--backup-file",
        help="Path to backup file for persistent processing (resumes from previous session)",
    ),
):
    """Screen papers using an LLM provider with specified prompt version."""
    try:
        # Initialize prompt manager
        from .llm.prompt_manager import PromptManager
        prompt_manager = PromptManager()

        # Validate prompt version
        try:
            prompt_manager.get_version(prompt_version)
        except ValueError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(f"[blue]Available versions: {[v.version for v in prompt_manager.list_versions()]}[/blue]")
            raise typer.Exit(1)

        console.print(f"[blue]Using prompt version: {prompt_version}[/blue]")

        # Read papers from CSV
        console.print(f"[blue]Reading papers from {input_csv}...[/blue]")
        papers = read_papers_from_csv(input_csv)
        console.print(f"[green]Found {len(papers)} papers to screen[/green]")

        # Create LLM provider
        console.print(f"[blue]Initializing {provider} provider...[/blue]")
        llm_provider = create_provider(provider, api_key, model)

        # Initialize usage tracker
        if not model:
            model = getattr(llm_provider, "model", "unknown")
        tracker = UsageTracker(provider, model or "unknown")

        # Initialize backup manager if backup file is specified
        backup_manager = None
        all_evaluations = []

        if backup_file:
            console.print(
                f"[blue]Initializing backup manager with {backup_file}...[/blue]"
            )
            backup_manager = BackupManager(backup_file)
            backup_manager.load_or_create_session(
                provider=provider,
                model=model or "unknown",
                input_csv_path=input_csv,
                output_csv_path=output,
                total_papers=len(papers),
            )

            # Get already processed papers
            processed_papers = backup_manager.get_processed_papers()
            all_evaluations.extend(processed_papers)

            # Get remaining papers to process
            remaining_papers = backup_manager.get_remaining_papers(papers)

            if len(processed_papers) > 0:
                progress_info = backup_manager.get_progress_info()
                failed_count = progress_info.get("failed", 0)
                console.print(
                    f"[green]Resuming from backup: {progress_info['processed']}/{progress_info['total']} papers completed ({progress_info['percentage']:.1f}%)[/green]"
                )
                if failed_count > 0:
                    console.print(
                        f"[yellow]⚠ {failed_count} papers failed previously and will be retried[/yellow]"
                    )

            papers_to_process = remaining_papers
        else:
            papers_to_process = papers

        # Process each paper
        if len(papers_to_process) == 0:
            console.print("[green]✓ All papers already processed![/green]")
        else:
            console.print(
                f"[blue]Processing {len(papers_to_process)} remaining papers...[/blue]"
            )

            for paper in track(papers_to_process, description="Screening papers..."):
                try:
                    # Format prompt using prompt manager
                    prompt = prompt_manager.format_prompt(prompt_version, paper.abstract)

                    # Get LLM assessment with token usage
                    response, token_usage = llm_provider.get_assessment(prompt)
                    assessment = parse_llm_response(response)

                    # Track usage
                    tracker.add_usage(token_usage)

                    # Convert to evaluation result
                    qa_scores = {}
                    qa_reasons = {}
                    for qa_item in assessment.assessments:
                        qa_id = qa_item.qa_id.lower()
                        qa_scores[qa_id] = qa_item.score
                        qa_reasons[qa_id] = qa_item.reason

                    evaluation = create_evaluation_result(
                        paper_id=paper.id,
                        title=paper.title,
                        abstract=paper.abstract,
                        qa_scores=qa_scores,
                        qa_reasons=qa_reasons,
                        llm_summary=assessment.overall_summary,
                        prompt_version=prompt_version,
                        prompt_hash=prompt_manager.get_prompt_hash(prompt_version),
                    )

                    # Add token usage to evaluation
                    evaluation.token_usage = token_usage

                    # Add to evaluations list
                    all_evaluations.append(evaluation)

                    # Save to backup if enabled
                    if backup_manager:
                        backup_manager.add_processed_paper(evaluation)

                        # Update usage tracker data in backup
                        report = tracker.get_report()
                        backup_manager.update_usage_tracker_data(
                            {
                                "total_papers_processed": report.total_papers_processed,
                                "successful_papers": report.successful_papers,
                                "failed_papers": report.failed_papers,
                                "total_input_tokens": report.total_input_tokens,
                                "total_output_tokens": report.total_output_tokens,
                                "total_cost": float(report.total_cost),
                            }
                        )

                except Exception as e:
                    # Create evaluation with error
                    console.print(
                        f"[red]Error processing paper {paper.id}: {str(e)}[/red]"
                    )
                    tracker.add_failure()

                    evaluation = EvaluationResult(
                        id=paper.id,
                        title=paper.title,
                        abstract=paper.abstract,
                        qa1_score=0.0,
                        qa1_reason="Error during processing",
                        qa2_score=0.0,
                        qa2_reason="Error during processing",
                        qa3_score=0.0,
                        qa3_reason="Error during processing",
                        qa4_score=0.0,
                        qa4_reason="Error during processing",
                        total_score=0.0,
                        decision="Exclude",
                        error=str(e),
                        prompt_version=prompt_version,
                        prompt_hash=prompt_manager.get_prompt_hash(prompt_version),
                    )

                    all_evaluations.append(evaluation)

                    # Update usage tracker data in backup but DO NOT mark paper as processed
                    # Failed papers should be retried in subsequent runs
                    if backup_manager:
                        backup_manager.add_failed_paper(evaluation)
                        report = tracker.get_report()
                        backup_manager.update_usage_tracker_data(
                            {
                                "total_papers_processed": report.total_papers_processed,
                                "successful_papers": report.successful_papers,
                                "failed_papers": report.failed_papers,
                                "total_input_tokens": report.total_input_tokens,
                                "total_output_tokens": report.total_output_tokens,
                                "total_cost": float(report.total_cost),
                            }
                        )
                        console.print(
                            "[yellow]⚠ Backup updated. Failed paper will be retried on resume:[/yellow]"
                        )
                        console.print(
                            f"[yellow]  slr-assessor screen {input_csv} --provider {provider} --output {output} --backup-file {backup_file}[/yellow]"
                        )

                    console.print(
                        f"[red]Stopping due to error in paper {paper.id}[/red]"
                    )
                    raise typer.Exit(1) from e

        # Finish tracking
        tracker.finish_session()

        # Write results to CSV
        console.print(f"[blue]Writing results to {output}...[/blue]")
        write_evaluations_to_csv(all_evaluations, output)

        # Summary
        include_count = sum(1 for e in all_evaluations if e.decision == "Include")
        exclude_count = sum(1 for e in all_evaluations if e.decision == "Exclude")
        conditional_count = sum(
            1 for e in all_evaluations if e.decision == "Conditional Review"
        )
        error_count = sum(1 for e in all_evaluations if e.error is not None)

        console.print("\n[green]✓ Screening complete![/green]")
        console.print(
            f"Results: {include_count} Include, {conditional_count} Conditional Review, {exclude_count} Exclude"
        )
        if error_count > 0:
            console.print(
                f"[yellow]⚠ {error_count} papers had processing errors[/yellow]"
            )

        # Print usage summary
        tracker.print_summary(console)

        # Save usage report if requested
        if usage_report:
            tracker.save_report(usage_report)
            console.print(f"[blue]💾 Usage report saved to {usage_report}[/blue]")

        # Clean up backup file if all papers processed successfully
        if backup_manager and len(papers_to_process) > 0 and error_count == 0:
            progress_info = backup_manager.get_progress_info()
            if progress_info["processed"] >= progress_info["total"]:
                console.print(
                    f"[green]✓ All papers processed successfully. Backup preserved at: {backup_file}[/green]"
                )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e


@app.command()
def process_human(
    input_csv: str = typer.Argument(..., help="Path to human evaluation CSV file"),
    output: str = typer.Option(
        ..., "-o", "--output", help="Path to save processed evaluation CSV"
    ),
):
    """Process human evaluations into standard format."""
    try:
        # Read human evaluations
        console.print(f"[blue]Reading human evaluations from {input_csv}...[/blue]")
        evaluations = read_human_evaluations_from_csv(input_csv)
        console.print(f"[green]Processed {len(evaluations)} evaluations[/green]")

        # Write standardized results
        console.print(f"[blue]Writing standardized results to {output}...[/blue]")
        write_evaluations_to_csv(evaluations, output)

        # Summary
        include_count = sum(1 for e in evaluations if e.decision == "Include")
        exclude_count = sum(1 for e in evaluations if e.decision == "Exclude")
        conditional_count = sum(
            1 for e in evaluations if e.decision == "Conditional Review"
        )

        console.print("\n[green]✓ Processing complete![/green]")
        console.print(
            f"Results: {include_count} Include, {conditional_count} Conditional Review, {exclude_count} Exclude"
        )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e


@app.command()
def compare(
    evaluation_file_1: str = typer.Argument(..., help="Path to first evaluation CSV"),
    evaluation_file_2: str = typer.Argument(..., help="Path to second evaluation CSV"),
    output: Optional[str] = typer.Option(
        None, "-o", "--output", help="Path to save detailed conflict report JSON"
    ),
):
    """Compare two evaluation results and report conflicts."""
    try:
        # Read evaluation files
        console.print(f"[blue]Reading evaluations from {evaluation_file_1}...[/blue]")
        eval1 = read_evaluations_from_csv(evaluation_file_1)

        console.print(f"[blue]Reading evaluations from {evaluation_file_2}...[/blue]")
        eval2 = read_evaluations_from_csv(evaluation_file_2)

        # Compare evaluations
        console.print("[blue]Comparing evaluations...[/blue]")
        conflict_report = compare_evaluations(eval1, eval2)

        # Print summary to console
        console.print("\n[bold]Comparison Results:[/bold]")
        console.print(f"Papers compared: {conflict_report.total_papers_compared}")
        console.print(f"Conflicts found: {conflict_report.total_conflicts}")
        console.print(f"Cohen's Kappa: {conflict_report.cohen_kappa_score:.3f}")

        # Interpret Kappa score
        kappa = conflict_report.cohen_kappa_score
        if kappa < 0:
            interpretation = "Poor (worse than random)"
        elif kappa < 0.2:
            interpretation = "Slight"
        elif kappa < 0.4:
            interpretation = "Fair"
        elif kappa < 0.6:
            interpretation = "Moderate"
        elif kappa < 0.8:
            interpretation = "Substantial"
        else:
            interpretation = "Almost perfect"

        console.print(f"Agreement level: {interpretation}")

        if conflict_report.conflicts:
            console.print("\n[yellow]Top 5 conflicts:[/yellow]")
            for i, conflict in enumerate(conflict_report.conflicts[:5]):
                console.print(
                    f"{i + 1}. Paper {conflict.id}: {conflict.decision_1} vs {conflict.decision_2} "
                    f"(score diff: {conflict.score_difference:.1f})"
                )

        # Save detailed report if requested
        if output:
            console.print(f"[blue]Saving detailed report to {output}...[/blue]")
            with open(output, "w") as f:
                json.dump(conflict_report.model_dump(), f, indent=2)
            console.print(f"[green]✓ Detailed report saved to {output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e


@app.command()
def estimate_cost(
    input_csv: str = typer.Argument(..., help="Path to input CSV file with papers"),
    provider: str = typer.Option(
        ..., "-p", "--provider", help="LLM provider (openai, gemini, anthropic)"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", help="Specific model to use (optional)"
    ),
):
    """Estimate screening costs for papers with an LLM provider."""
    try:
        # Read papers from CSV
        console.print(f"[blue]Reading papers from {input_csv}...[/blue]")
        papers = read_papers_from_csv(input_csv)
        console.print(f"[green]Found {len(papers)} papers to estimate[/green]")

        # Use first abstract as sample for estimation
        sample_abstract = (
            papers[0].abstract
            if papers
            else "Sample abstract for AI and traditional medicine research."
        )

        # Get default model if not specified
        if not model:
            default_models = {
                "openai": "gpt-4",
                "gemini": "gemini-2.5-flash",
                "anthropic": "claude-3-sonnet-20240229",
            }
            model = default_models.get(provider, "gpt-4")

        # Generate cost estimate
        console.print(
            f"[blue]Calculating cost estimate for {provider}/{model}...[/blue]"
        )
        estimate = estimate_screening_cost(
            len(papers), sample_abstract, provider, model
        )

        # Display results in a nice table
        from rich.table import Table

        table = Table(title=f"Cost Estimate for {provider}/{model}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Papers", str(estimate.total_papers))
        table.add_row(
            "Est. Input Tokens/Paper", f"{estimate.estimated_input_tokens_per_paper:,}"
        )
        table.add_row(
            "Est. Output Tokens/Paper",
            f"{estimate.estimated_output_tokens_per_paper:,}",
        )
        table.add_row("Total Estimated Tokens", f"{estimate.estimated_total_tokens:,}")
        table.add_row(
            "Input Cost per 1K tokens", f"${estimate.cost_per_input_token:.6f}"
        )
        table.add_row(
            "Output Cost per 1K tokens", f"${estimate.cost_per_output_token:.6f}"
        )
        table.add_row("", "")  # Separator
        table.add_row(
            "Estimated Total Cost",
            f"[bold green]${estimate.estimated_total_cost:.4f} USD[/bold green]",
        )
        table.add_row(
            "Cost per Paper",
            f"${estimate.estimated_total_cost / estimate.total_papers:.4f} USD",
        )

        console.print(table)

        # Show warning about estimates
        console.print(
            "\n[yellow]⚠️  Note: This is an estimate based on a sample abstract. Actual costs may vary.[/yellow]"
        )
        console.print(
            "[yellow]   Factors affecting cost: abstract length, response complexity, model efficiency.[/yellow]"
        )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e


@app.command()
def analyze_usage(
    usage_report: str = typer.Argument(..., help="Path to usage report JSON file"),
):
    """Analyze a usage report and display detailed statistics."""
    try:
        from rich.table import Table

        from .utils.usage_tracker import load_usage_report

        # Load the report
        console.print(f"[blue]Loading usage report from {usage_report}...[/blue]")
        report = load_usage_report(usage_report)

        # Basic info table
        info_table = Table(title="Session Information")
        info_table.add_column("Attribute", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Session ID", report.session_id)
        info_table.add_row("Provider/Model", f"{report.provider}/{report.model}")
        info_table.add_row("Start Time", report.start_time)
        info_table.add_row("End Time", report.end_time or "In Progress")
        info_table.add_row(
            "Duration", _calculate_duration(report.start_time, report.end_time)
        )

        console.print(info_table)

        # Processing stats table
        stats_table = Table(title="Processing Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="white")

        stats_table.add_row("Total Papers", str(report.total_papers_processed))
        stats_table.add_row("Successful", str(report.successful_papers))
        stats_table.add_row("Failed", str(report.failed_papers))
        if report.total_papers_processed > 0:
            success_rate = (
                report.successful_papers / report.total_papers_processed
            ) * 100
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%")

        console.print(stats_table)

        # Token usage table
        token_table = Table(title="Token Usage")
        token_table.add_column("Type", style="cyan")
        token_table.add_column("Total", style="white")
        token_table.add_column("Per Paper", style="white")

        token_table.add_row(
            "Input Tokens",
            f"{report.total_input_tokens:,}",
            f"{report.total_input_tokens / max(report.successful_papers, 1):.0f}",
        )
        token_table.add_row(
            "Output Tokens",
            f"{report.total_output_tokens:,}",
            f"{report.total_output_tokens / max(report.successful_papers, 1):.0f}",
        )
        token_table.add_row(
            "Total Tokens",
            f"{report.total_tokens:,}",
            f"{report.average_tokens_per_paper:.0f}",
        )

        console.print(token_table)

        # Cost table
        if report.total_cost > 0:
            cost_table = Table(title="Cost Analysis")
            cost_table.add_column("Metric", style="cyan")
            cost_table.add_column("Amount (USD)", style="green")

            cost_table.add_row("Total Cost", f"${report.total_cost:.4f}")
            cost_table.add_row(
                "Cost per Paper",
                f"${report.total_cost / max(report.successful_papers, 1):.4f}",
            )
            cost_table.add_row(
                "Cost per 1K Tokens",
                f"${(report.total_cost / max(report.total_tokens, 1)) * 1000:.4f}",
            )

            console.print(cost_table)
        else:
            console.print(
                "[yellow]Cost information not available in this report[/yellow]"
            )

        # Paper breakdown if there are any individual usages
        if report.paper_usages:
            console.print(
                "\n[bold]Individual Paper Analysis (showing first 10):[/bold]"
            )
            paper_table = Table()
            paper_table.add_column("Paper #", style="cyan")
            paper_table.add_column("Input", style="white")
            paper_table.add_column("Output", style="white")
            paper_table.add_column("Total", style="white")
            paper_table.add_column("Cost", style="green")

            for i, usage in enumerate(report.paper_usages[:10], 1):
                cost_str = (
                    f"${usage.estimated_cost:.4f}" if usage.estimated_cost else "N/A"
                )
                paper_table.add_row(
                    str(i),
                    str(usage.input_tokens),
                    str(usage.output_tokens),
                    str(usage.total_tokens),
                    cost_str,
                )

            console.print(paper_table)

            if len(report.paper_usages) > 10:
                console.print(
                    f"[dim]... and {len(report.paper_usages) - 10} more papers[/dim]"
                )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e


@app.command()
def list_prompts():
    """List all available prompt versions."""
    from .llm.prompt_manager import PromptManager

    prompt_manager = PromptManager()

    built_in_versions = prompt_manager.get_built_in_versions()
    custom_versions = prompt_manager.get_custom_versions()

    if built_in_versions:
        console.print("\n[bold green]Built-in Prompt Versions:[/bold green]")
        for version in built_in_versions:
            console.print(f"  [bold]{version.version}[/bold] - {version.name}")
            console.print(f"    {version.description}")
            console.print(f"    Created: {version.created_date}")
            console.print(f"    Hash: {prompt_manager.get_prompt_hash(version.version)}")

    if custom_versions:
        console.print("\n[bold blue]Custom Prompt Versions:[/bold blue]")
        for version in custom_versions:
            console.print(f"  [bold]{version.version}[/bold] - {version.name}")
            console.print(f"    {version.description}")
            console.print(f"    Created: {version.created_date}")
            console.print(f"    Hash: {prompt_manager.get_prompt_hash(version.version)}")

    if not built_in_versions and not custom_versions:
        console.print("[yellow]No prompt versions found[/yellow]")


@app.command()
def show_prompt(
    version: str = typer.Argument(..., help="Prompt version to display"),
    show_template: bool = typer.Option(False, "--template", help="Show full prompt template")
):
    """Show details of a specific prompt version."""
    from .llm.prompt_manager import PromptManager

    try:
        prompt_manager = PromptManager()
        prompt_version = prompt_manager.get_version(version)

        console.print(f"\n[bold]Prompt Version: {prompt_version.version}[/bold]")
        console.print(f"Name: {prompt_version.name}")
        console.print(f"Description: {prompt_version.description}")
        console.print(f"Created: {prompt_version.created_date}")
        console.print(f"Active: {'Yes' if prompt_version.is_active else 'No'}")
        console.print(f"Hash: {prompt_manager.get_prompt_hash(version)}")

        console.print("\n[bold]Assessment Questions:[/bold]")
        for qa_key, question in prompt_version.qa_questions.items():
            console.print(f"  {qa_key}: {question}")

        if show_template:
            console.print("\n[bold]Prompt Template:[/bold]")
            console.print(f"[dim]{prompt_version.template}[/dim]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def compare_prompts(
    input_csv: str = typer.Argument(..., help="Path to input CSV with papers"),
    provider: str = typer.Option(..., "-p", "--provider", help="LLM provider"),
    prompt_version_1: str = typer.Option(..., "--prompt1", help="First prompt version"),
    prompt_version_2: str = typer.Option(..., "--prompt2", help="Second prompt version"),
    output_dir: str = typer.Option(..., "-o", "--output-dir", help="Directory to save comparison results"),
    sample_size: Optional[int] = typer.Option(None, "--sample", help="Number of papers to compare (for testing)"),
    model: Optional[str] = typer.Option(None, "--model", help="Specific model to use"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key for LLM provider"),
):
    """Compare screening results using two different prompt versions."""
    from pathlib import Path
    import tempfile

    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Read and optionally sample papers
        papers = read_papers_from_csv(input_csv)
        if sample_size and sample_size < len(papers):
            papers = papers[:sample_size]
            console.print(f"[blue]Using sample of {sample_size} papers for comparison[/blue]")

        # Create temporary files for intermediate results
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp1, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp2:

            temp1_path = temp1.name
            temp2_path = temp2.name

        try:
            # Screen with first prompt
            console.print(f"[blue]Screening with prompt version {prompt_version_1}...[/blue]")
            result1_path = output_path / f"results_{prompt_version_1}.csv"

            # Run screen command programmatically for first prompt
            screen(
                input_csv=input_csv,
                provider=provider,
                output=str(result1_path),
                prompt_version=prompt_version_1,
                model=model,
                api_key=api_key,
                usage_report=None,
                backup_file=None
            )

            # Screen with second prompt
            console.print(f"[blue]Screening with prompt version {prompt_version_2}...[/blue]")
            result2_path = output_path / f"results_{prompt_version_2}.csv"

            # Run screen command programmatically for second prompt
            screen(
                input_csv=input_csv,
                provider=provider,
                output=str(result2_path),
                prompt_version=prompt_version_2,
                model=model,
                api_key=api_key,
                usage_report=None,
                backup_file=None
            )

            # Compare results
            console.print(f"[blue]Comparing prompt versions...[/blue]")
            comparison_path = output_path / f"comparison_{prompt_version_1}_vs_{prompt_version_2}.json"

            # Run compare command programmatically
            compare(
                evaluation1_csv=str(result1_path),
                evaluation2_csv=str(result2_path),
                output=str(comparison_path)
            )

            console.print(f"[green]✓ Prompt comparison complete![/green]")
            console.print(f"Results saved in: {output_path}")

        finally:
            # Clean up temporary files
            import os
            try:
                os.unlink(temp1_path)
                os.unlink(temp2_path)
            except:
                pass

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)

def _calculate_duration(start_time: str, end_time: Optional[str]) -> str:
    """Calculate duration between start and end times."""
    try:
        from datetime import datetime

        start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if end_time:
            end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
            duration = end - start

            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)

            if hours > 0:
                return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            elif minutes > 0:
                return f"{int(minutes)}m {int(seconds)}s"
            else:
                return f"{int(seconds)}s"
        else:
            return "In Progress"
    except:
        return "Unknown"
