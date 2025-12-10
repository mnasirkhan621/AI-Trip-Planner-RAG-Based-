# AI Trip Planner Agent

An AI-powered travel planning API built with FastAPI, LangChain, and Google Gemini. The agent generates detailed trip itineraries using RAG (Retrieval-Augmented Generation) with ChromaDB for context.

## Features

- 🗺️ **AI Trip Planning**: Generate detailed day-by-day itineraries
- 🔍 **RAG-Powered**: Uses ChromaDB to retrieve relevant travel information
- ⚡ **Fast API**: Built with FastAPI for high performance
- 🤖 **Google Gemini**: Powered by Gemini 2.5 Flash model
- 🐳 **Docker Ready**: Containerized for easy deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Google API Key (for Gemini)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-trip-planner
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### `GET /`
Health check endpoint.

### `POST /plan_trip`
Generate a trip itinerary.

**Request Body:**
```json
{
  "query": "Plan a 2-day trip to Paris"
}
```

**Response:**
```json
{
  "title": "2-Day Trip to Paris",
  "total_cost": null,
  "days": [
    {
      "day": 1,
      "city": "Paris",
      "activities": [...]
    }
  ]
}
```

### Interactive Documentation
Visit `http://localhost:8000/docs` for Swagger UI.

## Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### Production Deployment
```bash
docker-compose -f docker-compose.yml up -d
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_API_KEY` | Google Gemini API Key | Yes |

## Project Structure

```
ai-trip-planner/
├── app/
│   ├── __init__.py
│   ├── api.py          # FastAPI routes
│   ├── agent.py        # LangChain agent logic
│   ├── models.py       # Pydantic models
│   └── rag.py          # RAG retriever
├── data/
│   └── chroma_db/      # Vector database (generated)
├── scripts/
│   └── ingest_data.py  # Data ingestion script
├── main.py             # Application entry point
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md           # This file
```

## License

MIT License
