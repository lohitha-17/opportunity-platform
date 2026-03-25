from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date

app = FastAPI()

VALID_STATES = ["TX", "OK", "KS", "AR", "NM", "LA"]
VALID_NAICS = [236, 237, 238]
VALID_TYPES = ["source sought", "pre-solicitation"]

class Opportunity(BaseModel):
    name: str
    state: str
    naics_code: int
    opportunity_type: str
    dollar_amount: float
    calendar_days: int
    days_until_response: int
    sow_match: str

@app.post("/score")
def score_opportunity(opportunity: Opportunity):

    # Stage 1 — Hard Gates
    if opportunity.state not in VALID_STATES:
        return {
            "opportunity": opportunity.name,
            "result": "NO BID",
            "reason": f"State {opportunity.state} is outside our footprint"
        }

    if opportunity.naics_code not in VALID_NAICS:
        return {
            "opportunity": opportunity.name,
            "result": "NO BID",
            "reason": f"NAICS {opportunity.naics_code} is outside our scope"
        }

    if opportunity.opportunity_type.lower() not in VALID_TYPES:
        return {
            "opportunity": opportunity.name,
            "result": "NO BID",
            "reason": f"Opportunity type '{opportunity.opportunity_type}' not pursued"
        }

    # Stage 2 — Scoring
    score = 0

    # SOW match — 40 points
    if opportunity.sow_match.lower() == "strong":
        score += 40
    elif opportunity.sow_match.lower() == "partial":
        score += 20

    # Dollar magnitude — 30 points
    if 1000000 <= opportunity.dollar_amount <= 5000000:
        score += 30
    elif opportunity.dollar_amount < 1000000:
        score += 10

    # Calendar days — 20 points
    if opportunity.calendar_days >= 250:
        score += 20
    elif opportunity.calendar_days >= 150:
        score += 10

    # Response date — 10 points
    if opportunity.days_until_response >= 10:
        score += 10

    return {
        "opportunity": opportunity.name,
        "score": score,
        "result": "BID" if score >= 60 else "NO BID",
        "breakdown": {
            "sow_match": opportunity.sow_match,
            "dollar_amount": opportunity.dollar_amount,
            "calendar_days": opportunity.calendar_days,
            "days_until_response": opportunity.days_until_response
        }
    }