from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, OpportunityRecord, create_tables
from sam_integration import fetch_opportunities
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
create_tables()

def get_db():

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
@app.get("/fetch-opportunities")
def get_sam_opportunities(naics_code: str = "237", limit: int = 10):
    return fetch_opportunities(naics_code=naics_code, limit=limit)

@app.post("/auto-score")
def auto_score_from_sam(
    naics_code: str = "237",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    # Step 1 — Fetch from SAM.gov
    sam_data = fetch_opportunities(naics_code=naics_code, limit=limit)
    
    results = []
    
    for opp in sam_data.get("opportunities", []):
        # Step 2 — Build opportunity object
        state = opp.get("state") or "TX"
        opp_type = opp.get("type", "").lower()
        
        if "presolicitation" in opp_type:
            opp_type = "pre-solicitation"
        elif "sources sought" in opp_type:
            opp_type = "source sought"

        # Step 3 — Run through hard gates
        if state not in VALID_STATES:
            results.append({
                "title": opp.get("title"),
                "state": state,
                "result": "NO BID",
                "reason": f"State {state} outside footprint"
            })
            continue

        if opp_type not in VALID_TYPES:
            results.append({
                "title": opp.get("title"),
                "state": state,
                "result": "NO BID",
                "reason": f"Type '{opp_type}' not pursued"
            })
            continue

        # Step 4 — Score it
        score = 0
        dollar = opp.get("dollar_amount", 2000000)

        if 1000000 <= dollar <= 5000000:
            score += 30
        score += 40  # assume strong SOW match for auto-scoring
        score += 20  # assume enough calendar days
        score += 10  # assume enough response time

        result = "BID" if score >= 60 else "NO BID"

        # Step 5 — Save to database
        record = OpportunityRecord(
            name=opp.get("title", "Unknown"),
            state=state,
            naics_code=int(naics_code),
            opportunity_type=opp_type,
            dollar_amount=dollar,
            calendar_days=300,
            days_until_response=15,
            sow_match="strong",
            score=score,
            result=result
        )
        db.add(record)
        db.commit()

        results.append({
            "title": opp.get("title"),
            "state": state,
            "score": score,
            "result": result
        })

    return {
        "total_processed": len(results),
        "results": results
    }
@app.get("/")
def home():
    return {"message": "Opportunity Platform is running"}

@app.get("/opportunities")
def get_opportunities(db: Session = Depends(get_db)):
    records = db.query(OpportunityRecord).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "state": r.state,
            "naics_code": r.naics_code,
            "opportunity_type": r.opportunity_type,
            "dollar_amount": r.dollar_amount,
            "score": r.score,
            "recommendation": r.result
        }
        for r in records
    ]

@app.post("/score")
def score_opportunity(opportunity: Opportunity, db: Session = Depends(get_db)):

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

    if opportunity.sow_match.lower() == "strong":
        score += 40
    elif opportunity.sow_match.lower() == "partial":
        score += 20

    if 1000000 <= opportunity.dollar_amount <= 5000000:
        score += 30
    elif opportunity.dollar_amount < 1000000:
        score += 10

    if opportunity.calendar_days >= 250:
        score += 20
    elif opportunity.calendar_days >= 150:
        score += 10

    if opportunity.days_until_response >= 10:
        score += 10

    result = "BID" if score >= 60 else "NO BID"

    # Save to database
    record = OpportunityRecord(
        name=opportunity.name,
        state=opportunity.state,
        naics_code=opportunity.naics_code,
        opportunity_type=opportunity.opportunity_type,
        dollar_amount=opportunity.dollar_amount,
        calendar_days=opportunity.calendar_days,
        days_until_response=opportunity.days_until_response,
        sow_match=opportunity.sow_match,
        score=score,
        result=result
    )
    db.add(record)
    db.commit()

    return {
        "opportunity": opportunity.name,
        "score": score,
        "result": result,
        "breakdown": {
            "sow_match": opportunity.sow_match,
            "dollar_amount": opportunity.dollar_amount,
            "calendar_days": opportunity.calendar_days,
            "days_until_response": opportunity.days_until_response
        }
    }