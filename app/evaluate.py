import json
from pathlib import Path
import asyncio
from typing import Dict
from app.pipeline import run_pipeline
from app.llm_client import get_llm_client

LABELS = {
    "benign1": "benign",
    "phish1": "phishing",
    "phish2": "phishing",
    "inject1": "suspicious",
    "inject2": "suspicious",
}

async def eval_all():
    llm = get_llm_client()
    preds, gold = [], []
    for line in Path("data/samples.jsonl").read_text(encoding="utf-8").splitlines():
        email = json.loads(line)
        result = await run_pipeline(llm, email)
        await asyncio.sleep(121) # rate limit
        preds.append(result.verdict if result.verdict else "suspicious")
        gold.append(LABELS[email["id"]])
    # basic scores
    correct = sum(p==g for p,g in zip(preds,gold))
    print(f"Accuracy: {correct}/{len(gold)} = {correct/len(gold):.2%}")
    from collections import Counter
    print("Confusion (gold -> pred):")
    print(Counter(zip(gold,preds)))

if __name__ == "__main__":
    asyncio.run(eval_all())
