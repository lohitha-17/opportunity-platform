# Opportunity Platform

A FastAPI microservice for automated federal contracting bid/no-bid evaluation.

## What it does
Automatically evaluates federal contracting opportunities and recommends 
BID or NO BID based on real business criteria — eliminating manual evaluation.

## How it works

### Stage 1 — Hard Gates (automatic NO BID if any fail)
- Footprint: TX, OK, KS, AR, NM, LA only
- NAICS codes: 236, 237, 238 only
- Opportunity type: Source Sought or Pre-Solicitation only

### Stage 2 — Weighted Scoring
| Factor | Weight |
|---|---|
| SOW match (strong/partial/weak) | 40 points |
| Dollar magnitude ($1M–$5M) | 30 points |
| Calendar days (>250 days) | 20 points |
| Response date (>10 days out) | 10 points |

Score ≥ 60 → **BID** | Score < 60 → **NO BID**

## Tech Stack
- Python
- FastAPI
- Pydantic
- Uvicorn

## Run locally
```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

## API Docs
Visit `http://127.0.0.1:8000/docs` for interactive Swagger documentation.

## Next Steps
- PostgreSQL database for persistent storage
- Kafka pipeline for real-time federal opportunity ingestion
- AWS Lambda deployment
- CI/CD via GitHub Actions
