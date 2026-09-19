# EcoSort AI – Intelligent Waste Segregation & Recycling Assistant

B.Tech CSE AI project aligned with **UN SDG 12 – Responsible Consumption and Production**.

## Problem statement

Households and campuses struggle to segregate waste correctly. EcoSort AI helps users **identify items**, check **recyclability**, and follow **safe disposal guidance** using AI and a small local knowledge base—without training custom ML models on historical datasets.

## Target users

- Students and residents learning waste segregation  
- Campus sustainability clubs  
- Demo audiences for AI + sustainability projects  

## Why AI?

Natural language and documents are unstructured. Large language models (IBM Granite) plus RAG over uploaded guidelines provide flexible answers, entity extraction, and summarization that rule-only apps cannot cover.

## Features

| Feature | Description |
|--------|-------------|
| Dashboard | Stats from local browser history, quick actions |
| Text waste analyzer | Structured JSON analysis + entity extraction |
| Image analyzer | Upload JPG/PNG/WEBP; vision provider interface + demo fallback |
| AI chat | EcoSort system prompt + agent routing |
| Document RAG | PDF/TXT/DOCX → ChromaDB → Granite answer with sources |
| Summarization | Key rules and warnings from uploaded docs |
| Agentic workflow | Routes to analyze_text_waste, search_documents, etc. |
| History | localStorage view / delete / clear |
| Responsible AI | Disclaimers, demo mode transparency, safe hazardous guidance |

## Architecture

```
React (Vite) ──REST──► Flask API
                          ├── granite_service (IBM watsonx / demo)
                          ├── rag_service (ChromaDB)
                          ├── image_service (vision interface)
                          ├── entity_service
                          └── agent_service
```

## Technologies

- **Frontend:** React, TypeScript, Vite, Tailwind CSS  
- **Backend:** Python, Flask  
- **Vector store:** ChromaDB (local persistent)  
- **AI:** IBM Granite on watsonx.ai (optional); deterministic demo mode  

## Environment variables

Copy `backend/.env.example` to `backend/.env`:

```env
IBM_WATSONX_API_KEY=
IBM_WATSONX_PROJECT_ID=
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
IBM_GRANITE_MODEL=ibm/granite-3-8b-instruct
DEMO_MODE=true
FLASK_PORT=5000
MAX_UPLOAD_MB=10
```

- **`DEMO_MODE=true`:** Always use local deterministic responses (default for college demo).  
- **`DEMO_MODE=false`** and valid IBM credentials:** Live Granite calls.

API keys never reach the frontend.

## Installation

### Backend

```powershell
cd C:\Users\ayush\Projects\ecosort-ai
python -m venv backend\.venv
backend\.venv\Scripts\activate
pip install -r backend\requirements.txt
```

### Frontend

```powershell
cd C:\Users\ayush\Projects\ecosort-ai\frontend
npm install
```

## How to run

**Terminal 1 – Backend:**

```powershell
cd C:\Users\ayush\Projects\ecosort-ai
backend\.venv\Scripts\activate
python backend\app.py
```

**Terminal 2 – Frontend:**

```powershell
cd C:\Users\ayush\Projects\\frontend
npm run dev
```

Open **http://localhost:5173**. The Vite dev server proxies `/api` to Flask on port **5000**.

## Demo mode

When demo mode is active, the UI shows:

**Demo Mode – IBM Granite API is not connected.**

Responses come from `backend/services/demo_data.py` (deterministic, labeled demo).

## IBM API configuration

1. Create a watsonx.ai project and API key.  
2. Set `IBM_WATSONX_*` variables in `backend/.env`.  
3. Set `DEMO_MODE=false`.  
4. Restart Flask.

## Sample test cases (text analyzer)

| Input | Expected category (demo) |
|-------|--------------------------|
| plastic bottle | Recyclable |
| banana peel | Organic Waste |
| old newspaper | Dry Waste |
| broken mobile phone | E-Waste |
| used battery | Hazardous Waste |
| glass bottle | Recyclable |
| food container | Dry Waste |

Run backend tests:

```powershell
python backend\tests\test_demo_waste.py
```

## API endpoints

- `GET /api/health`  
- `POST /api/analyze-text`  
- `POST /api/analyze-image`  
- `POST /api/chat`  
- `POST /api/upload-document`  
- `POST /api/search-document`  
- `POST /api/summarize-document`  
- `POST /api/extract-entities`  
- `POST /api/agent-route`  

## RAG pipeline

Document → text extraction (pypdf / docx / txt) → chunking → ChromaDB embedding → similarity search → Granite (or demo) answer with **source filename**.

If context does not contain the answer:

`I could not find this information in the uploaded documents.`

## Prompt engineering

- Waste analysis: JSON-only schema with category enum and safety constraints.  
- Chat: EcoSort system prompt (10 responsibility rules in code).  
- RAG: Answer strictly from retrieved chunks.  

## Future improvements

- Connect watsonx multimodal or dedicated vision API in `GraniteVisionProvider`  
- Multilingual UI  
- Export history as CSV  
- OAuth-free cloud deploy templates  

## License

Academic / demonstration use for CSE AI coursework.
