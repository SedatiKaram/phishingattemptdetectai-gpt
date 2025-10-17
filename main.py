import asyncio, json, sys
from pathlib import Path
from rich import print as rprint
from app.llm_client import get_llm_client
from app.pipeline import run_pipeline
from app.metrics import compute_metrics

async def main():
    if len(sys.argv) < 2:
        rprint("[bold red]Usage:[/bold red] python main.py path/to/input.json[|l] [count] [out.jsonl]")
        sys.exit(1)

    inp = Path(sys.argv[1])
    # Optional numeric count (for JSONL), else optional output path
    count_arg = None
    out_arg = None
    if len(sys.argv) >= 3:
        try:
            count_arg = int(sys.argv[2])
        except ValueError:
            out_arg = sys.argv[2]
    if len(sys.argv) >= 4:
        out_arg = sys.argv[3]

    llm = get_llm_client()

    text = inp.read_text(encoding="utf-8")
    try:
        # Try single-JSON mode first
        obj = json.loads(text)
        if not isinstance(obj, dict):
            raise json.JSONDecodeError("Root is not an object", text, 0)
        result = await run_pipeline(llm, obj)
        rprint(result.model_dump())
        # Append to results and auto-update metrics
        outp = Path("out/results.jsonl")
        outp.parent.mkdir(parents=True, exist_ok=True)
        with open(outp, "a", encoding="utf-8") as f:
            f.write(result.model_dump_json())
            f.write("\n")
        try:
            items = []
            for ln in outp.read_text(encoding="utf-8").splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    items.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
            m = compute_metrics(items)
            metrics_path = Path("out/metrics.json")
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            metrics_path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            rprint({"metrics_file": str(metrics_path), **m})
        except Exception as e:
            rprint(f"[yellow]Metrics update skipped: {e}[/yellow]")
        return
    except json.JSONDecodeError:
        # Fallback: treat as JSONL (one JSON per line)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        if not lines:
            rprint("[yellow]No lines to process.[/yellow]")
            return
        total = len(lines)
        count = count_arg if (count_arg and count_arg > 0) else total
        count = min(count, total)
        outp = Path(out_arg) if out_arg else Path("out/results.jsonl")
        outp.parent.mkdir(parents=True, exist_ok=True)
        rprint(f"Analyzing {inp} (first {count} lines of {total}) -> {outp}")
        for i, line in enumerate(lines[:count], start=1):
            try:
                email = json.loads(line)
            except json.JSONDecodeError as e:
                rprint(f"[yellow]Skipping line {i}: invalid JSON ({e})[/yellow]")
                continue
            result = await run_pipeline(llm, email)
            with open(outp, "a", encoding="utf-8") as f:
                f.write(result.model_dump_json())
                f.write("\n")
            rprint({"line": i, **result.model_dump()})
        # Auto-update metrics after batch
        try:
            items = []
            for ln in outp.read_text(encoding="utf-8").splitlines():
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    items.append(json.loads(ln))
                except json.JSONDecodeError:
                    pass
            m = compute_metrics(items)
            metrics_path = Path("out/metrics.json")
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            metrics_path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
            rprint({"metrics_file": str(metrics_path), **m})
        except Exception as e:
            rprint(f"[yellow]Metrics update skipped: {e}[/yellow]")

if __name__ == "__main__":
    asyncio.run(main())
