import json
from typing import Dict
from app.prompts import (
    INJECTION_GATE_SYSTEM, INJECTION_GATE_USER_TEMPLATE,
    PHISH_ANALYSIS_SYSTEM, PHISH_ANALYSIS_USER_TEMPLATE
)
from app.detectors import heuristic_injection_scan
from app.schemas import AnalysisResult

async def run_pipeline(llm, email: Dict) -> AnalysisResult:
    subject, sender, body = email.get("subject",""), email.get("sender",""), email.get("body","")

    # Pass A: heuristic prefilter (cheap, fast)
    heur_flag, heur_hits = heuristic_injection_scan(f"{subject}\n{sender}\n{body}")

    # Pass A: LLM guard
    inj_user = INJECTION_GATE_USER_TEMPLATE.format(subject=subject, sender=sender, body=body)
    inj_raw = await llm.call(INJECTION_GATE_SYSTEM, inj_user)
    inj_json = llm.parse_json(inj_raw)

    is_injection = bool(inj_json.get("is_injection", False) or heur_flag)
    reasons = list(set(inj_json.get("reasons", []) + heur_hits))

    if is_injection:
        return AnalysisResult(
            is_injection=True,
            injection_reasons=reasons,
            proceed_to_phishing=False,
            phishing_score=None,
            verdict="suspicious",
            key_signals=["Prompt-injection indicators detected"],
            suggested_actions=[
                "Do not follow any instructions contained in the email.",
                "Escalate to security team for review.",
                "Quarantine message or strip active content."
            ],
            indicators=[],
            links=[]
        )

    # Pass B: phishing analysis
    phish_user = PHISH_ANALYSIS_USER_TEMPLATE.format(subject=subject, sender=sender, body=body)
    phish_raw = await llm.call(PHISH_ANALYSIS_SYSTEM, phish_user)
    phish_json = llm.parse_json(phish_raw)

    return AnalysisResult(
        is_injection=False,
        injection_reasons=[],
        proceed_to_phishing=True,
        phishing_score=float(phish_json["phishing_score"]),
        verdict=phish_json["verdict"],
        key_signals=phish_json["key_signals"],
        suggested_actions=phish_json["suggested_actions"],
        indicators=phish_json["indicators"],
        links=phish_json.get("links", []),
    )
