import sys, json
from pathlib import Path
from statistics import mean
from rich import print as rprint

#Loads results from JSONL file, skipping invalid lines 


def load_jsonl(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Results file not found: {path}")
    items = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as e:
            rprint(f"[yellow]Skipping line {i}: invalid JSON ({e})[/yellow]")
    return items


def compute_metrics(items):
    total = len(items)
    if total == 0:
        return {
            "total": 0,
            "phishing": 0,
            "suspicious": 0,
            "benign": 0,
            "injection_count": 0,
            "injection_rate": 0.0,
            "avg_phishing_score": None,
        }

    verdicts = [it.get("verdict") for it in items]
    phishing = sum(v == "phishing" for v in verdicts)
    suspicious = sum(v == "suspicious" for v in verdicts)
    benign = sum(v == "benign" for v in verdicts)
    injection_count = sum(bool(it.get("is_injection")) for it in items)
    scores = [it.get("phishing_score") for it in items if isinstance(it.get("phishing_score"), (int, float))]
    avg_score = round(mean(scores), 4) if scores else None

    return {
        "total": total,
        "phishing": phishing,
        "suspicious": suspicious,
        "benign": benign,
        "injection_count": injection_count,
        "injection_rate": round(injection_count / total, 4),
        "avg_phishing_score": avg_score,
    }


def main():
    # Usage: python -m app.metrics [results.jsonl] [metrics.json]
    results_path = Path(sys.argv[1]) if len(sys.argv) >= 2 else Path("out/results.jsonl")
    metrics_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path("out/metrics.json")

    items = load_jsonl(results_path)
    m = compute_metrics(items)

    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

    rprint({"metrics_file": str(metrics_path), **m})


if __name__ == "__main__":
    main()

