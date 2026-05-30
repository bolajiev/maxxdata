"""CLI for Maxx-agent."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from maxx_agent.orchestrator import MaxxAgent
from maxx_agent.paths import PLATFORM_ROOT, rag_parquet_path
from maxx_agent.public_datasets import export_hf_dataset, list_catalog

console = Console()


@click.group()
@click.version_option(package_name="maxx-agent")
def main() -> None:
    """Maxx agent runtime — chat, RAG, tools, public datasets."""


@main.command()
@click.option("--agent", default="coding", type=click.Choice(["coding", "research", "coder"]))
@click.option("--rag-version", default=None, help="maxxdata RAG version folder name")
@click.option("--workspace", default=None, type=click.Path(exists=True), help="Root for read_file")
@click.argument("message")
def chat(agent: str, rag_version: str | None, workspace: str | None, message: str) -> None:
    """Send one message to Maxx and print the reply."""
    ws = Path(workspace) if workspace else PLATFORM_ROOT
    agent_obj = MaxxAgent(agent, rag_version=rag_version, workspace=ws)
    if not agent_obj.rag.available:
        console.print("[yellow]Warning: no RAG index found. Run maxxdata chunk-rag + promote first.[/yellow]")
    reply = agent_obj.run(message)
    console.print(reply)


@main.command()
@click.option("--agent", default="coding", type=click.Choice(["coding", "research"]))
def status(agent: str) -> None:
    """Show RAG path and config status."""
    p = rag_parquet_path(agent)
    if p:
        console.print(f"[green]RAG[/green] {p}")
    else:
        console.print("[yellow]RAG not found. Expected maxxdata/data/serve/{agent}/rag/<version>/chunks.parquet[/yellow]")


@main.group()
def datasets() -> None:
    """Public Hugging Face datasets for training."""


@datasets.command("list")
def datasets_list() -> None:
    """List recommended public datasets."""
    table = Table(title="Public datasets (Hugging Face)")
    table.add_column("ID")
    table.add_column("HF repo")
    table.add_column("Use")
    for row in list_catalog():
        table.add_row(row["id"], row["hf"], row["use"])
    console.print(table)
    console.print("\nDoc: maxx-agent/docs/PUBLIC_DATASETS.md")


@datasets.command("pull")
@click.option("--hf", "hf_name", required=True, help="e.g. rajpurkar/squad")
@click.option("--out", default=None, help="Output JSONL path")
@click.option("--limit", default=200, type=int)
@click.option("--split", default="train")
def datasets_pull(hf_name: str, out: str | None, limit: int, split: str) -> None:
    """Download a sample slice to JSONL for fine-tuning."""
    from maxx_agent.paths import PUBLIC_DATA_DIR

    safe = hf_name.replace("/", "_")
    out_path = Path(out) if out else PUBLIC_DATA_DIR / f"{safe}_{limit}.jsonl"
    meta = export_hf_dataset(hf_name, out_path, split=split, limit=limit)
    console.print(f"[green]Saved {meta['rows']} rows[/green] -> {meta['out']}")


if __name__ == "__main__":
    main()
