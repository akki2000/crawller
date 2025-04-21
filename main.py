import os
from dotenv import load_dotenv
load_dotenv()

import asyncio
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google import genai
from google.genai import types

# ----- Configure Gemini API -----
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("Please set the GEMINI_API_KEY environment variable.")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# ----- FastAPI App -----
app = FastAPI(title="AI Chatbot Backend (Auto‑Crawl)")

class ChatRequest(BaseModel):
    start_url: str
    max_pages: int = 50
    question: str

# ----- Site Crawler -----
async def crawl_site(start_url: str, max_pages: int = 50) -> List[Dict]:
    visited: Set[str] = set()
    to_visit: List[str] = [start_url]
    docs: List[Dict] = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
        except Exception:
            continue

        visited.add(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator=" ")
        docs.append({"content": text, "source": url})

        base = urlparse(start_url).netloc
        for link in soup.find_all('a', href=True):
            href = urljoin(url, link['href'])
            if urlparse(href).netloc == base and href not in visited:
                to_visit.append(href)

    return docs

# ----- Chat Endpoint (Auto‑Crawl) -----
@app.post("/chat")
async def api_chat(req: ChatRequest):
    # 1. Crawl site
    docs = await crawl_site(req.start_url, req.max_pages)
    if not docs:
        raise HTTPException(status_code=400, detail="Failed to crawl the site or no content found.")

    # 2. Compile site content (with source markers)
    compiled = [f"Source: {doc['source']}\n{doc['content']}" for doc in docs]
    site_text = "\n\n".join(compiled)
    # Truncate if too long
    if len(site_text) > 50000:
        site_text = site_text[:50000]

    # 3. Build prompt for Gemini
    prompt = (
        "You are a helpful assistant. Use the following website content to answer the question."
        f"\n\n{site_text}\n\nQuestion: {req.question}\nAnswer:"
    )

    # 4. Call Gemini to generate the answer
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            max_output_tokens=512,
            temperature=0.2
        )
    )

    return {"answer": response.text}

# ----- Health Check -----
@app.get("/health")
def health_check():
    return {"status": "ok"}

# ----- Run Server & Environment Setup -----
# Before starting the server, set your Gemini API key:
#   export GEMINI_API_KEY="your_api_key_here"
# Or include it in a .env file.
# Start the server:
#   uvicorn ai_chatbot_backend:app --host 0.0.0.0 --port 8000 --reload