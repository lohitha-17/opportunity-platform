import re

def analyze_rfp(text: str) -> dict:
    
    # Extract NAICS code
    naics_match = re.search(r'NAICS[:\s#]*(\d{3,6})', text, re.IGNORECASE)
    naics_code = naics_match.group(1) if naics_match else "Not found"
    
    # Extract dollar amount
    dollar_match = re.search(
        r'\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?',
        text, re.IGNORECASE
    )
    dollar_amount = dollar_match.group(0) if dollar_match else "Not found"
    
    # Extract deadline
    deadline_match = re.search(
        r'(?:deadline|due date|response date|submit by|responses due)[:\s]+([A-Za-z]+\s+\d{1,2},?\s+\d{4}|\d{1,2}/\d{1,2}/\d{4})',
        text, re.IGNORECASE
    )
    deadline = deadline_match.group(1) if deadline_match else "Not found"
    
    # Extract state
    states = ["TX", "OK", "KS", "AR", "NM", "LA"]
    found_state = "Not found"
    for state in states:
        if state in text.upper():
            found_state = state
            break
    
    # Extract requirements
    requirements = []
    sentences = text.split('.')
    keywords = ['shall', 'must', 'required', 'experience', 'licensed', 'certified']
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in keywords):
            clean = sentence.strip()
            if len(clean) > 10:
                requirements.append(clean)
    
    # Generate summary
    words = text.split()
    summary = ' '.join(words[:50]) + '...' if len(words) > 50 else text
    
    # Auto scoring hints
    score_hints = []
    if naics_code in ["236", "237", "238"]:
        score_hints.append("NAICS code qualifies")
    if found_state in ["TX", "OK", "KS", "AR", "NM", "LA"]:
        score_hints.append("State is in footprint")
    if dollar_amount != "Not found":
        score_hints.append("Dollar amount found — verify $1M-$5M range")
    
    return {
        "summary": summary,
        "naics_code": naics_code,
        "dollar_amount": dollar_amount,
        "deadline": deadline,
        "state": found_state,
        "key_requirements": requirements[:4],
        "scoring_hints": score_hints,
        "recommendation": "Run through /score endpoint for full evaluation"
    }