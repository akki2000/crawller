# AI Chatbot Backend (Auto-Crawl)

A minimal FastAPI backend for a chatbot that answers user questions based on live content crawled from a given website. Uses Google's Gemini API to generate answers.

## Features

- Crawls a target website (up to `max_pages`).
- Aggregates readable content.
- Sends content + user question to Gemini for response.
- Returns AI-generated answer.

## Setup

```bash
git clone https://github.com/akki2000/crawller.git
cd yourrepo
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with your Gemini API key:

```
GEMINI_API_KEY=your_api_key_here
```

## Run

```bash
uvicorn main:app --reload
```

## API

### `POST /chat`

**Payload:**

```json
{
  "start_url": "https://example.com",
  "max_pages": 50,
  "question": "What services does this company provide?"
}
```

**Response:**

```json
{
  "answer": "AI-generated response based on site content."
}
```

### `GET /health`

Returns basic status.

---

Built with ❤️ by Akash Verma

