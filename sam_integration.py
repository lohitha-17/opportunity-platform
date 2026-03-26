import requests
import os
from dotenv import load_dotenv

load_dotenv()

SAM_API_KEY = os.getenv("SAM_API_KEY")

MOCK_OPPORTUNITIES = [
    {
        "title": "Highway Construction Project - Dallas TX",
        "naics_code": "237",
        "posted_date": "2026-03-01",
        "response_deadline": "2026-04-15",
        "description": "Construction of highway infrastructure in Dallas TX area",
        "type": "Presolicitation",
        "organization": "Dept of Transportation",
        "state": "TX"
    },
    {
        "title": "Building Construction - Oklahoma City OK",
        "naics_code": "236",
        "posted_date": "2026-03-10",
        "response_deadline": "2026-04-20",
        "description": "Federal building construction project in Oklahoma City",
        "type": "Sources Sought",
        "organization": "GSA",
        "state": "OK"
    },
    {
        "title": "Bridge Renovation - New York NY",
        "naics_code": "237",
        "posted_date": "2026-03-15",
        "response_deadline": "2026-04-10",
        "description": "Bridge renovation project in New York",
        "type": "Presolicitation",
        "organization": "Dept of Transportation",
        "state": "NY"
    }
]

def fetch_opportunities(naics_code: str = "237", limit: int = 10):
    url = "https://api.sam.gov/opportunities/v2/search"
    
    params = {
        "api_key": SAM_API_KEY,
        "limit": limit,
        "postedFrom": "03/26/2025",
        "postedTo": "03/26/2026",
        "naicsCode": naics_code,
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        print(f"SAM API unavailable, using mock data")
        filtered = [o for o in MOCK_OPPORTUNITIES 
                   if o["naics_code"] == naics_code][:limit]
        return {
            "total_found": len(filtered),
            "source": "mock_data",
            "opportunities": filtered
        }
    
    data = response.json()
    opportunities = []
    
    for opp in data.get("opportunitiesData", []):
        opportunities.append({
            "title": opp.get("title"),
            "naics_code": opp.get("naicsCode"),
            "posted_date": opp.get("postedDate"),
            "response_deadline": opp.get("responseDeadLine"),
            "description": opp.get("description", "")[:500],
            "type": opp.get("type"),
            "organization": opp.get("organizationName"),
            "state": opp.get("officeAddress", {}).get("state")
        })
    
    return {
        "total_found": data.get("totalRecords", 0),
        "source": "sam.gov",
        "opportunities": opportunities
    }