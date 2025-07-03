from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# === CONFIGURATION ===
API_KEY = os.getenv("TENWEB_API_KEY", "your-10web-api-key")
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

class SiteRequest(BaseModel):
    business_name: str
    business_description: str
    business_type: str
    contact_email: str = ""
    contact_phone: str = ""

@app.post("/generate-site")
async def generate_site(req: SiteRequest):
    subdomain = req.business_name.lower().replace(" ", "") + "88"

    # Step 1: create website
    create_url = "https://api.10web.io/v1/hosting/website"
    create_payload = {
        "subdomain": subdomain,
        "region": "asia-east1-a",
        "site_title": req.business_name,
        "admin_username": subdomain,
        "admin_password": "StrongP@ssw0rd",
        "is_demo": 0
    }

    create_resp = requests.post(create_url, json=create_payload, headers=HEADERS)
    if create_resp.status_code != 201:
        raise HTTPException(status_code=500, detail=f"Failed to create site: {create_resp.text}")

    website_id = create_resp.json()["data"]["website_id"]

    # Step 2: generate AI site
    generate_url = "https://api.10web.io/v1/ai/generate_site"
    generate_payload = {
        "website_id": website_id,
        "business_type": req.business_type,
        "business_name": req.business_name,
        "business_description": req.business_description
    }

    generate_resp = requests.post(generate_url, json=generate_payload, headers=HEADERS)
    if generate_resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Failed to generate AI site: {generate_resp.text}")

    preview_url = generate_resp.json().get("preview_url", "Check your 10Web dashboard")

    return {"status": "success", "preview_url": preview_url}

# === To run locally ===
# uvicorn main:app --reload

# === To deploy to Vercel ===
# Rename this file to `api/generate-site.py` and deploy to Vercel
