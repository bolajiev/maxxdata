"""Inventory status: catalog summary and gap hints."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

from rich.console import Console
from rich.table import Table

from maxxdata.paths import INVENTORY_DIR, DATA_DIR

console = Console()


def run_inventory_status() -> None:
    catalog = INVENTORY_DIR / "catalog.csv"
    table = Table(title="Maxxdata Catalog")
    table.add_column("ID")
    table.add_column("Agent")
    table.add_column("Product")
    table.add_column("Version")
    table.add_column("Rows")

    if catalog.exists():
        with catalog.open(encoding="utf-8") as f:
            for row in csv.DictReader(f):
                table.add_row(
                    row.get("id", ""),
                    row.get("agent", ""),
                    row.get("product", ""),
                    row.get("version", ""),
                    row.get("row_count", ""),
                )
    else:
        table.add_row("(empty)", "-", "-", "-", "-")

    console.print(table)

    # Scan serve/ for versions not in catalog
    serve = DATA_DIR / "serve"
    by_agent: dict[str, list[str]] = defaultdict(list)
    if serve.exists():
        for agent_dir in serve.iterdir():
            if not agent_dir.is_dir():
                continue
            for product_dir in agent_dir.iterdir():
                if not product_dir.is_dir():
                    continue
                for ver in product_dir.iterdir():
                    if ver.is_dir():
                        by_agent[agent_dir.name].append(f"{product_dir.name}/{ver.name}")

    console.print("\n[bold]Served datasets on disk:[/bold]")
    if by_agent:
        for agent, paths in sorted(by_agent.items()):
            console.print(f"  {agent}: {', '.join(paths)}")
    else:
        console.print("  (none yet — run pipeline through promote)")

    gaps = INVENTORY_DIR / "gaps.md"
    if gaps.exists():
        console.print(f"\n[bold]Gaps file:[/bold] {gaps}")
        console.print(gaps.read_text(encoding="utf-8")[:1500])
