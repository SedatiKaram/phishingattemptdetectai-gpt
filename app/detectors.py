from typing import List, Tuple
import re

SUSPECT_PATTERNS = [
    r"\bignore (all )?previous (rules|instructions)\b",
    r"\boverride(s|)? (policy|policies|rules)\b",
    r"\bact as (system|admin|developer)\b",
    r"\bdisregard\b",
    r"\bdeveloper mode\b",
]

def heuristic_injection_scan(text: str) -> Tuple[bool, List[str]]:
    hits = []
    for pat in SUSPECT_PATTERNS:
        if re.search(pat, text, flags=re.I):
            hits.append(pat)
    return (len(hits) > 0, hits)
