Phishing Attempt Detector (LLM‑powered)

Overview
- Single‑pass LLM pipeline that analyzes emails for both prompt‑injection attempts and phishing risk.
- Works on one JSON email or many via JSONL. Appends results to `out/results.jsonl` and auto‑updates `out/metrics.json`.

Quickstart (Windows)
- python -m venv .venv
- Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
- .\.venv\Scripts\Activate.ps1
- pip install -U pip -r requirements.txt
- Create `.env` with your API key:
  - LLM_API_KEY=sk-...
  - optional: LLM_MODEL=gpt-4o-mini, LLM_BASE_URL=https://api.openai.com/v1

Inputs
- JSON email object with fields: `subject`, `sender`, `body` (optional: `links`, `raw_headers`).
- Or JSONL where each line is one such JSON email.

Usage
- Single JSON:
  - python main.py data/email1.json
- JSONL: all lines or first N lines; appends to `out/results.jsonl` and prints full per‑line result:
  - python main.py data/samples.jsonl
  - python main.py data/samples.jsonl 25
  - custom output file: python main.py data/samples.jsonl 25 out/run1.jsonl
- Convert EML to JSON first (optional):
  - python -m app.eml_to_json C:\path\to\email.eml .\out\email.json

Outputs
- Per email (Pydantic model in JSON):
  - `is_injection` (bool), `reasons` (list)
  - `phishing_score` (0..1), `verdict` in {phishing, suspicious, benign}
  - `key_signals`, `suggested_actions`, `indicators`, `links`
- Files:
  - `out/results.jsonl` — one JSON per analyzed email
  - `out/metrics.json` — auto‑updated summary after each run

Evaluate (Precision/Recall on 100+ emails)
- Prepare a labels JSONL file aligned line‑by‑line with your `out/results.jsonl`.
  - Each line must contain a field `label` (or `gold`/`verdict`) with one of: `phishing`, `suspicious`, `benign` (optionally `injection` if you use that label).
- Run the metrics module with labels to compute class counts and precision/recall/F1:
  - python -m app.metrics out/results.jsonl out/metrics.json data/evaluation_100.jsonl
- The report includes:
  - totals, class counts, injection rate, average phishing score
  - confusion matrix, per‑class precision/recall/F1, micro‑F1, macro‑F1

Model & API
- OpenAI‑compatible chat endpoint; set `LLM_API_KEY` in `.env`.
- Optional: `LLM_MODEL` and `LLM_BASE_URL` to point to compatible providers.

Design Notes (Simplified)
- One LLM call combines injection detection and phishing risk assessment.
- Minimal CLI: if the input isn’t parseable as a single JSON, it’s treated as JSONL.
- Metrics can be run standalone and support optional labels for PR/F1.

