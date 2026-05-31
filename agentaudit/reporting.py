import os
import re

from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agentaudit.models import SuiteResult


def slugify(text: str) -> str:
    """Helper to convert suite name to file-friendly slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "_", text).strip("_")


def generate_terminal_report(suite_result: SuiteResult, verbose: bool = False, quiet: bool = False) -> None:
    """Prints a styled, highly scannable audit outcome to the command terminal.

    Args:
        suite_result: The SuiteResult to print.
        verbose: If True, outputs detailed assertion lines for all cases.
        quiet: If True, prints nothing.
    """
    if quiet:
        return

    console = Console()

    # Title Banner
    color = "green" if suite_result.status == "PASSED" else "red"
    console.print()
    console.print(
        Panel(
            f"[bold]AgentAudit Suite: [cyan]{suite_result.name}[/cyan][/bold]\n"
            f"[dim]{suite_result.description or 'No suite description provided.'}[/dim]",
            title="[bold]AgentAudit Report[/bold]",
            border_style=color,
            expand=False,
        )
    )

    # Metrics Table
    table = Table(show_header=True, header_style="bold magenta", border_style="dim")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    table.add_row("Total Cases", str(suite_result.total_cases))
    table.add_row("Passed Cases", f"[green]{suite_result.passed}[/green]")
    table.add_row("Failed Cases", f"[red]{suite_result.failed}[/red]" if suite_result.failed > 0 else "0")
    table.add_row("Accuracy", f"{suite_result.accuracy:.1f}%")

    if suite_result.safety_score is not None:
        table.add_row("Safety Score", f"[yellow]{suite_result.safety_score:.1f}%[/yellow]")
    else:
        table.add_row("Safety Score", "[dim]N/A[/dim]")

    table.add_row("Average Latency", f"{suite_result.average_latency:.0f}ms")
    table.add_row("Execution Duration", f"{suite_result.duration_seconds:.2f}s")

    status_color = "green" if suite_result.status == "PASSED" else "red"
    table.add_row("Suite Status", f"[bold {status_color}]{suite_result.status}[/bold {status_color}]")

    console.print(table)
    console.print()

    # Detailed failures block
    if suite_result.failed > 0:
        console.print("[bold red]Failed cases detail:[/bold red]")
        for case in suite_result.results:
            if not case.success:
                console.print(f" • [bold yellow]{case.id}[/bold yellow] (Latency: {case.latency_ms:.0f}ms)")
                for assertion in case.assertions:
                    if not assertion.success:
                        console.print(f"   [red]✗[/red] [dim]{assertion.name}[/dim]: {assertion.reason or 'Failed assertion'}")
        console.print()

    # Detailed pass list if verbose is active
    if verbose:
        console.print("[bold green]Passed cases detail:[/bold green]")
        for case in suite_result.results:
            if case.success:
                console.print(f" • [bold green]{case.id}[/bold green] (Latency: {case.latency_ms:.0f}ms)")
        console.print()


def generate_json_report(suite_result: SuiteResult, output_dir: str) -> str:
    """Saves raw suite run data into structured JSON format.

    Args:
        suite_result: The SuiteResult.
        output_dir: Directory where the file will be saved.

    Returns:
        The generated file path string.
    """
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(suite_result.name)
    file_path = os.path.join(output_dir, f"report_{slug}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(suite_result.model_dump_json(indent=2))

    return file_path


def generate_markdown_report(suite_result: SuiteResult, output_dir: str) -> str:
    """Generates a structured Markdown report file (ideal for CI and PR summaries).

    Args:
        suite_result: The SuiteResult.
        output_dir: Output directory.

    Returns:
        The generated file path string.
    """
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(suite_result.name)
    file_path = os.path.join(output_dir, f"report_{slug}.md")

    md = []
    md.append(f"# AgentAudit Evaluation Report: {suite_result.name}")
    md.append(f"*{suite_result.description or 'No suite description.'}*\n")

    # Status & High level metrics
    status_emoji = "✅" if suite_result.status == "PASSED" else "❌"
    md.append("## High-Level Summary")
    md.append(f"- **Suite Status**: {status_emoji} **{suite_result.status}**")
    md.append(f"- **Accuracy**: **{suite_result.accuracy:.1f}%** ({suite_result.passed}/{suite_result.total_cases} passed)")

    if suite_result.safety_score is not None:
        md.append(f"- **Safety Score**: **{suite_result.safety_score:.1f}%**")
    else:
        md.append("- **Safety Score**: N/A (no safety cases detected)")

    md.append(f"- **Average Latency**: {suite_result.average_latency:.0f}ms")
    md.append(f"- **Execution Duration**: {suite_result.duration_seconds:.2f}s")
    md.append(f"- **Target Type**: `{suite_result.target_type}`")
    md.append("")

    # Cases Table
    md.append("## Test Case Outcomes")
    md.append("| Test ID | Type | Outcome | Latency | Score | Hallucination Risk |")
    md.append("|---|---|---|---|---|---|")

    for case in suite_result.results:
        outcome = "✅ PASSED" if case.success else "❌ FAILED"
        case_type = "Safety" if case.is_safety_case else "Functional"
        risk = "🚨 Yes" if case.hallucination_risk else "🟢 None"
        md.append(
            f"| `{case.id}` | {case_type} | {outcome} | {case.latency_ms:.0f}ms | {case.score * 100:.0f}% | {risk} |"
        )
    md.append("")

    # Detailed Failures Section
    if suite_result.failed > 0:
        md.append("## Detailed Failures")
        for case in suite_result.results:
            if not case.success:
                md.append(f"### ❌ Case: `{case.id}`")
                md.append(f"- **Prompt Input**: `{case.input}`")
                md.append(f"- **AI Response**: `{case.output}`")
                if case.sources:
                    md.append(f"- **Retrieved Sources**: `{case.sources}`")
                md.append("- **Failed Assertions**:")
                for assertion in case.assertions:
                    if not assertion.success:
                        md.append(
                            f"  - 🔴 **`{assertion.name}`**: Expected `{assertion.expected}`, but got `{assertion.actual}`."
                        )
                        if assertion.reason:
                            md.append(f"    - *Reason*: {assertion.reason}")
                md.append("")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    return file_path


def generate_html_report(suite_result: SuiteResult, output_dir: str) -> str:
    """Generates a standalone, beautifully styled Glassmorphism HTML report.

    Args:
        suite_result: The SuiteResult.
        output_dir: Output directory.

    Returns:
        The generated file path string.
    """
    os.makedirs(output_dir, exist_ok=True)
    slug = slugify(suite_result.name)
    file_path = os.path.join(output_dir, f"report_{slug}.html")

    # Locate templates relative to the reporting module
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html.j2")

    # Render template using SuiteResult dict context or model instance directly
    html_content = template.render(suite_result=suite_result)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return file_path


def generate_all_reports(suite_result: SuiteResult, output_dir: str) -> dict[str, str]:
    """Generates and writes JSON, Markdown, and HTML reports all at once.

    Args:
        suite_result: The SuiteResult.
        output_dir: Directory where reports are saved.

    Returns:
        A dictionary mapping formats ("json", "md", "html") to absolute or relative file paths.
    """
    paths = {
        "json": generate_json_report(suite_result, output_dir),
        "md": generate_markdown_report(suite_result, output_dir),
        "html": generate_html_report(suite_result, output_dir),
    }

    # Also save a 'latest' symlink/copy for ease of access (e.g. 'latest_report.json')
    # This matches CLI behavior for generating summaries
    for fmt, path in paths.items():
        latest_path = os.path.join(output_dir, f"latest_report.{fmt}")
        try:
            with open(path, encoding="utf-8") as src:
                content = src.read()
            with open(latest_path, "w", encoding="utf-8") as dst:
                dst.write(content)
        except Exception:
            pass

    return paths
