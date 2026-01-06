# Drug Recovery Platform - Backend

Modular Flask microservices backend for drug recovery assistance platform with LLM agent and ML relapse prediction.

## 🏗 Architecture

```
backend/
├── shared/          # Shared utilities (database, logging, schemas)
├── Chat/            # LLM Agent service (Groq + LangChain + RAG)
├── Relapse/         # ML prediction service (XGBoost)
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Groq API key ([Get one here](https://console.groq.com))

### Setup

1. **Clone and navigate to backend:**
```bash
cd backend
```

2. **Create and configure environment:**
```bash
# Copy .env template
cp ../.env.example ../.env

# Edit .env and add your GROQ_API_KEY
# GROQ_API_KEY=gsk_...
```

3. **Initialize databases:**
```bash
# Create Chat databases
cd Chat/data
sqlite3 drugs.db < drugs.sql
sqlite3 history.db < history.sql
cd ../..
```

---

## 💬 Chat Service

Intelligent drug recovery assistant with RAG, web search, and tool calling. Features strict JSON validation, structured tool-call logging, and comprehensive safety guardrails.

### Key Features

- **LLM Agent:** Groq-powered conversational AI with tool calling
- **Response Validation:** Strict schema validation with safe fallbacks
- **Tool-Call Logging:** Structured JSON logging for debugging and monitoring
- **RAG (Retrieval-Augmented Generation):** Semantic search over drug database
- **Crisis Detection:** Automatic crisis override for emergency situations
- **No Tool Traces:** Clean responses - no tool metadata exposed to users
- **Vector Store:** FAISS for fast similarity search
- **Structured Logging:** JSON-lines format with request tracking

### Installation

```bash
cd Chat
pip install -r requirements.txt
```

### Run Development Server

```bash
python run.py
```

Service runs on `http://localhost:5001`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/chat` | Full agent execution (with validation & logging) |
| POST | `/chat/rag/query` | RAG-only retrieval |
| POST | `/chat/tools/drug_lookup` | Query drugs database |
| POST | `/chat/tools/history_lookup` | Query user history |
| POST | `/chat/websearch` | Web search only |
| POST | `/chat/ingest/drugs` | Build vector index |
| GET | `/chat/logs/tail?n=200` | Tail JSON-formatted logs |

### Example Requests

**Chat (Full Agent with Validation):**
```bash
curl -X POST http://localhost:5001/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are the risks of fentanyl?",
    "user_id": "user_001"
  }'
```

Response (always valid JSON):
```json
{
  "request_id": "uuid-v4",
  "status": "success",
  "data": {
    "response": {
      "summary": "Fentanyl is a potent synthetic opioid...",
      "risks": ["Respiratory depression", "Overdose potential", "Addiction risk"],
      "what_to_do": ["Consult healthcare provider", "Use naloxone if available"],
      "safety": {
        "urgent_signs": ["Difficulty breathing", "Loss of consciousness"],
        "hotlines": ["988", "1-800-662-4357"]
      }
    },
    "conversation_history": [...]
  },
  "error": null
}
```

**Drug Lookup:**
```bash
curl -X POST http://localhost:5001/chat/tools/drug_lookup \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "Oxycodone"}'
```

**Ingest Drugs (Build RAG Index):**
```bash
curl -X POST http://localhost:5001/chat/ingest/drugs
```

**View Tool-Call Logs:**
```bash
curl http://localhost:5001/chat/logs/tail?n=50
```

Logs include: `tool_name`, `args` (sanitized), `latency_ms`, `status`, `request_id`

---

## 🔁 Relapse Service

ML-based relapse time prediction using behavioral signals.

### Installation

```bash
cd Relapse
pip install -r requirements.txt
```

### Run Development Server

```bash
python run.py
```

Service runs on `http://localhost:5002`

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/relapse/predict` | Predict relapse time |
| POST | `/relapse/features` | Debug features |
| POST | `/relapse/train` | Train model |
| GET | `/relapse/model/info` | Model version + metrics |
| GET | `/relapse/logs/tail` | Tail logs |

### Example Requests

**Train Model (First Time):**
```bash
curl -X POST http://localhost:5002/relapse/train
```

**Predict Relapse:**
```bash
curl -X POST http://localhost:5002/relapse/predict \
  -H "Content-Type: application/json" \
  -d '{
    "days_clean": 35,
    "craving_scores": [3, 2, 4, 3, 2, 3, 2],
    "sleep_hours": [7, 6.5, 7, 8, 6, 7.5, 7],
    "trigger_events": [],
    "support_sessions": 3,
    "medication_adherence": {
      "doses_taken": 13,
      "doses_prescribed": 14
    }
  }'
```

**Debug Features:**
```bash
curl -X POST http://localhost:5002/relapse/features \
  -H "Content-Type: application/json" \
  -d '{
    "days_clean": 30,
    "craving_scores": [2, 3, 2],
    "sleep_hours": [7, 8, 6.5],
    "trigger_events": [],
    "support_sessions": 2,
    "medication_adherence": {"doses_taken": 10, "doses_prescribed": 10}
  }'
```
with tool calling
- **Response Validation:** All responses validated against required schema:
  - `summary` (str): Factual answer
  - `risks` (list): Associated risks
  - `what_to_do` (list): Recommended actions
  - `safety.urgent_signs` (list): Emergency warning signs
  - `safety.hotlines` (list): Crisis hotline numbers
- **Fallback Safety:** Invalid responses automatically replaced with safe defaults
- **Strict JSON Output:** Enforced JSON-only responses, no tool traces exposed
- **Tool-Call Logging:** Structured logging for each tool execution:
  - Tool name
  - Sanitized arguments (user_id redacted)
  - Latency in milliseconds
  - Success/error status
  - Request ID for tracing
- **Crisis Detection:** Automatic detection and override for emergency situations
- **RAG:** Semantic search over drug database
- **Tools:** 
  - `lookup_drug`: Query drugs database by name
  - `lookup_history`: Retrieve user's personal history
  - `rag_query`: Semantic search over knowledge base
  - `websearch_drug`: Web search fallback
- **Vector Store:** FAISS for fast similarity search
- **Structured Logging:** JSON-lines format with request correlation IDs

### Chat Service

Edit `Chat/config.py`:
- `LLM_MODEL`: Groq model to use
- `LLM_TEMPERATURE`: Response randomness (0-1)
- `RAG_TOP_K`: Number of RAG results
- `EMBEDDING_MODEL`: Sentence transformer model

### Relapse Service

Edit `Relapse/config.py`:
- `N_ESTIMATORS`: XGBoost trees
- `MAX_DEPTH`: Tree depth
- `LEARNING_RATE`: Training rate
- Feature windows (days)

---

## 📊 Features

### Chat Service Features

- **LLM Agent:** Groq-powered conversational AI
- **RAG:** Semantic search over drug database
- **Tools:** Drug lookup, history lookup, web search
- **Vector Store:** FAISS for fast similarity search
- **Structured Logging:** JSON-lines format

### Relapse Service Features

- **6 Engineered Features:**
  - `days_clean`: Days since last relapse
  - `craving_trend`: Rolling average craving score
  - `sleep_deviation`: Sleep pattern irregularity
  - `trigger_count`: Weekly trigger exposures
  - `support_sessions`: Therapy attendance
  - `medication_adherence`: % of doses taken

- **XGBoost Regressor:** Time-series prediction
- **Model Versioning:** Automatic version tracking
- **Risk Assessment:**logs/` directory in JSON-lines format.

### Chat Service Logging

Logs to `logs/chat.log` with entries for:
- **Request-level logs:** Every `/chat` endpoint call with full latency
- **Tool-call logs:** Each tool execution with:
  - Tool name and sanitized arguments
  - Execution latency in milliseconds
  - Success/error status
  - Request ID for correlation

Example log entry (tool call):
```json
{
  "ts": "2026-01-06T19:30:45.123456Z",
  "service": "chat",
  "request_id": "882e46b1-c2a8-40f6-9281-afbd12feccf1",
  "endpoint": "execute_tool",
  "tool": "lookup_drug",
  "status": "success",
  "latency_ms": 45.23,
  "args": {
    "drug_name": "Fentanyl"
  }
}
```

View logs:
```bash
# Chat logs (last 50 entries)
curl http://localhost:5001/chat/logs/tail?n=50
```

**Relapse Service:**
```bash
cd Relapse
gunicorn "app:create_app()" -w 4 --threads 8 -b 0.0.0.0:5002
```

---Automated Test Script

Run comprehensive test suite for Chat service:

```bash
# From backend directory
python test_chat_route.py
```

This runs 3 scenarios:
1. **Drug Query Test:** "What are the risks of fentanyl?" - Validates tool calls and JSON schema
2. **History Query Test:** "Can you summarize my progress?" - Verifies `lookup_history` integration with `user_id`
3. **Unknown Drug Test:** "What are the risks of Xylazine-XYZ?" - Confirms "Drug not found" response in proper JSON structure

Test output includes:
- ✅ Response schema validation
- ✅ JSON structure verification
- ✅ Required field presence checks
- ✅ Detailed error reporting

### Manual Test Chat Service

```bash
# Health check
curl http://localhost:5001/health

# Drug lookup
curl -X POST http://localhost:5001/chat/tools/drug_lookup \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "Cocaine"}'

# User history
curl -X POST http://localhost:5001/chat/tools/history_lookup \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'

# View recent tool-call logs
curl http://localhost:5001/chat/logs/tail?n=20
```

- Check that `logs/` directory exists or can be created

**Chat returns 500 error:**
- Check the error message in the response - often indicates missing fields or validation issues
- Review `logs/chat.log` for detailed error information
- Verify JSONLogger has permission to write to `logs/chat.log`

**Response validation failing:**
- Ensure LLM is returning valid JSON format
- Check `logs/chat.log` for tool execution errors
- Verify all tools (lookup_drug, lookup_history, etc.) are working correctly

**RAG not working:**
- Run ingestion endpoint first: `POST /chat/ingest/drugs`
- Check that `drugs.db` has records
- Verify FAISS can be imported: `pip install faiss-cpu`

**Test script failing:**
- Verify Chat service is running on `http://localhost:5001`
- Check service is healthy: `curl http://localhost:5001/health`
- Review error messages in test output for specific issues
- Check `logs/chat.log` for backend errors

**Relapse predictions failing:**
- Train model first: `POST /relapse/train`
- Check all required fields in prediction request
- Verify feature ranges are valid (e.g., adherence 0-100)

**Module import errors:**
- Ensure you're in the correct directory when running
- Check Python version: `python --version` (needs 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt`
- For JSONLogger issues, verify `shared/logging.py` exists and is importable
}

View logs:
```bash
# Chat logs
curl http://localhost:5001/chat/logs/tail?n=50

# Relapse logs
curl http://localhost:5002/relapse/logs/tail?n=50
```

---

## 🧪 Testing

### Test Chat Service

```bash
# Health check
curl http://localhost:5001/health

# Drug lookup
curl -X POST http://localhost:5001/chat/tools/drug_lookup \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "Cocaine"}'

# User history
curl -X POST http://localhost:5001/chat/tools/history_lookup \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_001"}'
```

### Test Relapse Service

```bash
# Health check
curl http://localhost:5002/health

# Train model
curl -X POST http://localhost:5002/relapse/train

# Get model info
curl http://localhost:5002/relapse/model/info

# Predict
curl -X POST http://localhost:5002/relapse/predict \
  -H "Content-Type: application/json" \
  -d '{
    "days_clean": 20,
    "craving_scores": [4, 5, 3, 4],
    "sleep_hours": [6, 5, 7, 6],
    "trigger_events": [{"days_ago": 2}],
    "support_sessions": 1,
    "medication_adherence": {"doses_taken": 8, "doses_prescribed": 10}
  }'
```

---

## 🛠 Troubleshooting

### Common Issues

**Chat service won't start:**
- Verify `GROQ_API_KEY` is set in `.env`
- Check databases exist: `Chat/data/drugs.db`, `Chat/data/history.db`
- Run SQL schemas to initialize databases

**RAG not working:**
- Run ingestion endpoint first: `POST /chat/ingest/drugs`
- Check that `drugs.db` has records
- Verify FAISS can be imported: `pip install faiss-cpu`

**Relapse predictions failing:**
- Train model first: `POST /relapse/train`
- Check all required fields in prediction request
- Verify feature ranges are valid (e.g., adherence 0-100)

**Module import errors:**
- Ensure you're in the correct directory when running
- Check Python version: `python --version` (needs 3.9+)
- Reinstall dependencies: `pip install -r requirements.txt`

---

## 📚 API Documentation

### Shared Response Schema

```python
{
  "request_id": str,      # UUID v4
  "status": str,          # "success" | "error"
  "data": any,           # Response payload (if success)
  "error": str | null    # Error message (if error)
}
```

### Feature Input Format (Relapse)

```python
{
  "days_clean": int,                              # Days since last relapse
  "craving_scores": list[float],                  # Daily scores (0-10)
  "sleep_hours": list[float],                     # Daily sleep hours
  "trigger_events": list[dict],                   # Events with 'days_ago'
  "support_sessions": int,                        # Weekly count
  "medication_adherence": {
    "doses_taken": int,
    "doses_prescribed": int
  }
}
```

---

## 🎯 Hackathon Ready

This implementation is:
- ✅ Fully isolated microservices
- ✅ Thread-safe with SQLite
- ✅ Production-ready with Gunicorn
- ✅ Structured logging for debugging
- ✅ Standardized API responses
- ✅ No coupling between services
- ✅ Ready for containerization (Docker)

---

## 📞 Support Resources

- **SAMHSA National Helpline:** 1-800-662-4357
- **Crisis Text Line:** Text HOME to 741741
- **National Suicide Prevention Lifeline:** 988

---

## 📄 License

Hackathon project - educational purposes only. Not for production medical use.
