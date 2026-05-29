"""CLI entrypoint for maxxdata pipeline."""

from __future__ import annotations

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(package_name="maxxdata")
def main() -> None:
    """Maxxdata dataset pipeline."""


@main.command()
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True, help="Batch id e.g. batch_001")
def ingest(agent: str, batch: str) -> None:
    """Ingest raw documents from config sources."""
    from maxxdata.stages.ingest import run_ingest

    meta = run_ingest(agent, batch)
    console.print(f"[green]Ingested {meta['doc_count']} docs[/green] (errors: {len(meta.get('errors', []))})")


@main.command()
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
def clean(agent: str, batch: str) -> None:
    """Clean and deduplicate raw documents."""
    from maxxdata.stages.clean import run_clean

    meta = run_clean(agent, batch)
    console.print(
        f"[green]Cleaned[/green] {meta['out_count']}/{meta['in_count']} "
        f"(rejected {meta['reject_count']})"
    )


@main.command()
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
def validate(agent: str, batch: str) -> None:
    """Validate cleaned documents."""
    from maxxdata.stages.validate import run_validate

    meta = run_validate(agent, batch)
    console.print(
        f"[green]Validated[/green] {meta['validated_count']} "
        f"(rejected {meta['reject_count']})"
    )


@main.command()
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
@click.option("--note", default="", help="Approval note")
def approve(agent: str, batch: str, note: str) -> None:
    """Approve batch after reviewing rejects (required for chunk-rag, label, promote)."""
    from maxxdata.stages.approve import run_approve

    result = run_approve(agent, batch, note)
    console.print(f"[green]Approved[/green] -> {result['flag']}")


@main.command("chunk-rag")
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
def chunk_rag_cmd(agent: str, batch: str) -> None:
    """Build RAG chunks (requires approve)."""
    from maxxdata.stages.chunk_rag import run_chunk_rag

    meta = run_chunk_rag(agent, batch)
    console.print(f"[green]RAG chunks[/green] {meta['chunk_count']} -> {meta['path']}")


@main.command()
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
@click.option(
    "--types",
    default="sft,instructions,tool_calling,trajectories,multi_agent",
    help="sft,instructions,tool_calling,trajectories,multi_agent (aliases: tools,if)",
)
@click.option("--max-docs", default=None, type=int, help="Limit docs for LLM labeling")
def label(agent: str, batch: str, types: str, max_docs: int | None) -> None:
    """Generate FT drafts via DeepSeek (requires approve)."""
    from maxxdata.stages.label import run_label

    type_list = [t.strip() for t in types.split(",") if t.strip()]
    meta = run_label(agent, batch, types=type_list, max_docs=max_docs)
    console.print(
        f"[green]Labeled[/green] sft={meta.get('sft_count', 0)} if={meta.get('instructions_count', 0)} "
        f"tools={meta.get('tool_calling_count', 0)} traj={meta.get('trajectories_count', 0)} "
        f"multi={meta.get('multi_agent_count', 0)} (docs={meta['docs_labeled']}, errors={meta['errors']})"
    )


@main.command()
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
@click.option("--version", required=True, help="Version tag e.g. 2026.05.29.1")
def promote(agent: str, batch: str, version: str) -> None:
    """Promote serve-bound to data/serve/<agent>/<product>/<version>/."""
    from maxxdata.stages.promote import run_promote

    result = run_promote(agent, batch, version)
    for product, path in result.items():
        console.print(f"[green]Promoted {product}[/green] -> {path}")


@main.command("pipeline")
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", default="batch_001")
@click.option("--version", default="2026.05.29.1")
@click.option("--skip-label", is_flag=True, help="Skip DeepSeek labeling")
@click.option("--max-docs", default=3, type=int)
def run_pipeline(
    agent: str,
    batch: str,
    version: str,
    skip_label: bool,
    max_docs: int,
) -> None:
    """Run full pipeline through promote (auto-approves — review rejects first in production)."""
    from maxxdata.stages.approve import run_approve
    from maxxdata.stages.chunk_rag import run_chunk_rag
    from maxxdata.stages.clean import run_clean
    from maxxdata.stages.ingest import run_ingest
    from maxxdata.stages.inventory import run_inventory_status
    from maxxdata.stages.label import run_label
    from maxxdata.stages.promote import run_promote
    from maxxdata.stages.validate import run_validate

    meta = run_ingest(agent, batch)
    console.print(f"[green]Ingested {meta['doc_count']} docs[/green]")
    meta = run_clean(agent, batch)
    console.print(f"[green]Cleaned[/green] {meta['out_count']}/{meta['in_count']}")
    meta = run_validate(agent, batch)
    console.print(f"[green]Validated[/green] {meta['validated_count']}")
    console.print("[yellow]Review data/process/.../rejects.csv (pipeline auto-approves)[/yellow]")
    run_approve(agent, batch, note="pipeline auto")
    meta = run_chunk_rag(agent, batch)
    console.print(f"[green]RAG chunks[/green] {meta['chunk_count']}")
    if not skip_label:
        meta = run_label(agent, batch, types=["sft", "instructions"], max_docs=max_docs)
        console.print(f"[green]Labeled[/green] sft={meta['sft_count']} if={meta['instructions_count']}")
    result = run_promote(agent, batch, version)
    for product, path in result.items():
        console.print(f"[green]Promoted {product}[/green] -> {path}")
    run_inventory_status()


@main.command("seed-if")
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--batch", required=True)
def seed_if(agent: str, batch: str) -> None:
    """Load instruction-following seed JSONL (no API). Requires approve."""
    from maxxdata.stages.seed_ft import run_seed_ft

    counts = run_seed_ft(agent, batch, types=["instructions"])
    console.print(f"[green]Seeded IF[/green] instructions={counts.get('instructions', 0)}")
    console.print("Run: python -m maxxdata promote --agent ... --version ...")


@main.command("export-hf")
@click.option("--agent", required=True, type=click.Choice(["coding", "research"]))
@click.option("--version", required=True, help="Promoted version under data/serve/")
def export_hf(agent: str, version: str) -> None:
    """Export each serve file to exports/hf/<agent>-<type>-<version>/ for HF upload."""
    from maxxdata.stages.export_hf import run_export_hf

    folders = run_export_hf(agent, version)
    if not folders:
        console.print("[yellow]Nothing to export. Run promote first.[/yellow]")
        return
    for path in folders:
        console.print(f"[green]Exported[/green] {path}")


@main.group()
def inventory() -> None:
    """Inventory commands."""


@inventory.command("status")
def inventory_status() -> None:
    """Show catalog and served datasets."""
    from maxxdata.stages.inventory import run_inventory_status

    run_inventory_status()


if __name__ == "__main__":
    main()
