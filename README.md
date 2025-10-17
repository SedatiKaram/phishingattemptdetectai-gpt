# Phishing_Attempt_Detector — LLM-Powered Email Phishing Analyzer + With Prompt Injection Defense

[![Project: PhishingAttemptDetectAI](https://img.shields.io/badge/project-phishing--detector-blue)](https://github.com/SedatiKaram/phishingattemptdetectai-gpt)
[![Language: Python](https://img.shields.io/badge/language-Python-3776AB)](https://www.python.org)

> A lightweight, demo that analyzes emails with an LLM to detect prompt-injection and phishing risk, then logs per-email analysis and aggregated evaluation metrics.

---

## Why this matters
Phishing remains the most common initial access vector in real-world breaches. This project demonstrates how to combine an LLM-based analyst with an evaluation pipeline that produces verifiable metrics (precision / recall / F1) over a labeled dataset — the kind of practical tooling interviewers love to see in an entry-level security / ML role.

---

## Project highlights
- Single-pass LLM pipeline: injection detection + phishing risk scoring in one analysis call.
- Supports single JSON email objects and JSONL (one JSON per line). Outputs a per-email JSON model and an aggregated metrics file.
- Evaluation mode computes class counts, confusion matrix, precision/recall/F1 and writes `out/metrics.json`.

---

**Metrics snapshot (analyzed email list)**

![Overview diagram placeholder](out/diagram_overview.png)  

**Metrics snapshot ()**

![Metrics snapshot placeholder](out/metrics_snapshot.png)  

---

## Where to look

1. **Per-email output**: `out/results.jsonl` — one JSON object per analyzed email with fields like `is_injection`, `phishing_score`, `verdict`, `key_signals`, `indicators`, and `links`.
2. **Evaluation report**: `out/metrics.json` — contains totals, confusion matrix counts, per-class precision/recall/F1, micro/macro F1 and average phishing score. This is the main proof you evaluated the model on labeled data.
3. **Sample dataset**: `data/evaluation_100.jsonl` — JSONL file with one email per line for reproducible testing. 
