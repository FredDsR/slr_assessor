"""CLI command definitions using Typer."""

import json
from typing import Optional

import typer
from rich.console import Console
from rich.progress import track
from dotenv import load_dotenv

from .models import EvaluationResult
from .core.evaluator import create_evaluation_result
from .core.comparator import compare_evaluations
from .llm.providers import create_provider, parse_llm_response
from .llm.prompt import format_assessment_prompt
from .utils.io import (
    read_papers_from_csv,
    read_human_evaluations_from_csv,
    read_evaluations_from_csv,
    write_evaluations_to_csv,
)

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
    api_key: Optional[str] = typer.Option(
        None, "--api-key", help="API key for LLM provider"
    ),
):
    """Screen papers using an LLM provider."""
    try:
        # Read papers from CSV
        console.print(f"[blue]Reading papers from {input_csv}...[/blue]")
        papers = read_papers_from_csv(input_csv)
        console.print(f"[green]Found {len(papers)} papers to screen[/green]")

        # Create LLM provider
        console.print(f"[blue]Initializing {provider} provider...[/blue]")
        llm_provider = create_provider(provider, api_key)

        # Process each paper
        evaluations = []
        for paper in track(papers, description="Screening papers..."):
            try:
                # Format prompt
                prompt = format_assessment_prompt(paper.abstract)

                # Get LLM assessment
                response = llm_provider.get_assessment(prompt)
                assessment = parse_llm_response(response)

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
                )

            except Exception as e:
                # Create evaluation with error
                console.print(f"[red]Error processing paper {paper.id}: {str(e)}[/red]")
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
                )

            evaluations.append(evaluation)

        # Write results to CSV
        console.print(f"[blue]Writing results to {output}...[/blue]")
        write_evaluations_to_csv(evaluations, output)

        # Summary
        include_count = sum(1 for e in evaluations if e.decision == "Include")
        exclude_count = sum(1 for e in evaluations if e.decision == "Exclude")
        conditional_count = sum(
            1 for e in evaluations if e.decision == "Conditional Review"
        )
        error_count = sum(1 for e in evaluations if e.error is not None)

        console.print("\n[green]✓ Screening complete![/green]")
        console.print(
            f"Results: {include_count} Include, {conditional_count} Conditional Review, {exclude_count} Exclude"
        )
        if error_count > 0:
            console.print(
                f"[yellow]⚠ {error_count} papers had processing errors[/yellow]"
            )

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


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
        raise typer.Exit(1)


@app.command()
def compare(
    evaluation_file_1: str = typer.Argument(..., help="Path to first evaluation CSV"),
    evaluation_file_2: str = typer.Argument(..., help="Path to second evaluation CSV"),
    output: Optional[str] = typer.Option(
        None, "-o", "--output", help="Path to save detailed conflict report JSON"
    ),
):
    """Compare two evaluation files and report conflicts."""
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
        raise typer.Exit(1)
