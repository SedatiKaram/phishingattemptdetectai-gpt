from pydantic import BaseModel
from typing import List, Optional

class LinkInfo(BaseModel):
    text: str
    href: str

class AnalysisResult(BaseModel):
    is_injection: bool
    injection_reasons: List[str] = []
    proceed_to_phishing: bool
    phishing_score: Optional[float] = None  # 0..1
    verdict: Optional[str] = None           # "phishing"|"suspicious"|"benign"
    key_signals: List[str] = []
    suggested_actions: List[str] = []
    indicators: List[str] = []              # e.g., domains, senders, btc addresses
    links: List[LinkInfo] = []
