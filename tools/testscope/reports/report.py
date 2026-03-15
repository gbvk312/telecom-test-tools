from rich.console import Console

console = Console()


def print_report(kpis, failures):

    console.print("\n[bold cyan]5G Test Summary[/bold cyan]\n")

    console.print("Total Events:", kpis["total_events"])
    console.print("Failures:", kpis["failures"])
    console.print("Success Rate:", kpis["success_rate"], "%")

    if failures:
        console.print("\n[bold red]Detected Issues[/bold red]")

        for f in failures:
            console.print("❌", f)
