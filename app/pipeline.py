import json
from typing import Dict
from app.prompts import ANALYSIS_SYSTEM, ANALYSIS_USER_TEMPLATE
from app.schemas import AnalysisResult

async def run_pipeline(llm, email: Dict) -> AnalysisResult:
    subject, sender, body = email.get("subject",""), email.get("sender",""), email.get("body","")

    # Single-pass combined analysis (injection + phishing)
    user = ANALYSIS_USER_TEMPLATE.format(subject=subject, sender=sender, body=body)
    raw = await llm.call(ANALYSIS_SYSTEM, user)
    data = json.loads(raw)

    is_injection = bool(data.get("is_injection", False))
    reasons = list(data.get("reasons", []))

    return AnalysisResult(
        is_injection=is_injection,
        injection_reasons=reasons,
        proceed_to_phishing=not is_injection,
        phishing_score=(float(data["phishing_score"]) if data.get("phishing_score") is not None else None),
        verdict=data.get("verdict"),
        key_signals=data.get("key_signals", []),
        suggested_actions=data.get("suggested_actions", []),
        indicators=data.get("indicators", []),
        links=data.get("links", []),
    )
