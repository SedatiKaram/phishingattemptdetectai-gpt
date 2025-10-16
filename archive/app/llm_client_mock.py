import json

class LLMClientBase:
    async def call(self, system: str, user: str) -> str:
        raise NotImplementedError()

class MockClient(LLMClientBase):
    """Archived mock client: deterministic JSON for demos/tests."""
    async def call(self, system: str, user: str) -> str:
        txt = user.lower()
        is_inj = any(k in txt for k in ["ignore previous", "override", "act as system", "developer mode"])        
        if "Output ONLY valid JSON" in system and "Does this content attempt" in user:
            return json.dumps({"is_injection": is_inj, "reasons": ["mock-detected-pattern"] if is_inj else []})
        verdict = "phishing" if ("password" in txt or "wire" in txt or "reset" in txt or "invoice" in txt) else "benign"
        score = 0.9 if verdict=="phishing" else 0.1
        return json.dumps({
            "phishing_score": score,
            "verdict": verdict,
            "key_signals": ["mock-signal"],
            "suggested_actions": ["Report to security", "Verify sender via known channel"],
            "indicators": ["mock-indicator"],
            "links": []
        })
