# 🚀 Quick Start Guide

Get the Drug Recovery Platform backend running in 5 minutes!

## Prerequisites

- Python 3.9+
- pip
- Groq API key ([Get free key](https://console.groq.com))

---

## Setup Steps

### 1. Configure Environment

```bash
# Navigate to project root
cd "d:\Programming\AI\Hackathons\.Competitions\Drugs"

# Edit .env and add your Groq API key
# Open .env in your editor and set:
# GROQ_API_KEY=gsk_your_key_here
```

### 2. Initialize Databases

```bash
cd backend
python init_databases.py
```

This will create and populate:
- `Chat/data/drugs.db` (8 sample drugs)
- `Chat/data/history.db` (15 sample encounters)

### 3. Install Dependencies

**Chat Service:**
```powershell
cd Chat
pip install -r requirements.txt
cd ..
```

**Relapse Service:**
```powershell
cd Relapse
pip install -r requirements.txt
cd ..
```

### 4. Start Services

**Terminal 1 - Chat Service:**
```powershell
cd Chat
python run.py
```
🟢 Running on http://localhost:5001

**Terminal 2 - Relapse Service:**
```powershell
cd Relapse
python run.py
```
🟢 Running on http://localhost:5002

### 5. Test Services

**Terminal 3 - Run Tests:**
```powershell
cd backend
pip install requests  # If not already installed
python test_services.py
```

---

## Quick API Tests

### Chat Service

**Drug Lookup:**
```powershell
curl -X POST http://localhost:5001/chat/tools/drug_lookup `
  -H "Content-Type: application/json" `
  -d '{\"drug_name\": \"Oxycodone\"}'
```

**User History:**
```powershell
curl -X POST http://localhost:5001/chat/tools/history_lookup `
  -H "Content-Type: application/json" `
  -d '{\"user_id\": \"user_001\"}'
```

**Build RAG Index:**
```powershell
curl -X POST http://localhost:5001/chat/ingest/drugs
```

**RAG Query:**
```powershell
curl -X POST http://localhost:5001/chat/rag/query `
  -H "Content-Type: application/json" `
  -d '{\"query\": \"What are opioid withdrawal symptoms?\"}'
```

### Relapse Service

**Train Model:**
```powershell
curl -X POST http://localhost:5002/relapse/train
```

**Predict Relapse:**
```powershell
curl -X POST http://localhost:5002/relapse/predict `
  -H "Content-Type: application/json" `
  -d '{\"days_clean\": 35, \"craving_scores\": [3,2,4,3,2,3,2], \"sleep_hours\": [7,6.5,7,8,6,7.5,7], \"trigger_events\": [], \"support_sessions\": 3, \"medication_adherence\": {\"doses_taken\": 13, \"doses_prescribed\": 14}}'
```

**Model Info:**
```powershell
curl http://localhost:5002/relapse/model/info
```

---

## 🎯 What You Built

### Chat Service (Port 5001)
- ✅ Groq-powered LLM agent
- ✅ Drug database with 8 substances
- ✅ User history tracking (15 sample encounters)
- ✅ RAG (semantic search) with FAISS
- ✅ Web search fallback
- ✅ 8 REST endpoints
- ✅ JSON-lines structured logging

### Relapse Service (Port 5002)
- ✅ XGBoost time-series predictor
- ✅ 6 engineered behavioral features
- ✅ Risk assessment (low/moderate/high/critical)
- ✅ Model versioning and metrics
- ✅ 6 REST endpoints
- ✅ JSON-lines structured logging

---

## 📁 Project Structure

```
backend/
├── shared/              # Shared utilities
│   ├── db.py           # SQLite helper
│   ├── logging.py      # JSON logger
│   ├── schemas.py      # API response format
│   └── utils.py        # Common utilities
│
├── Chat/               # LLM Agent Service
│   ├── api/
│   │   └── routes.py   # 8 endpoints
│   ├── core/
│   │   ├── agent.py    # Groq orchestrator
│   │   ├── rag.py      # Vector search
│   │   ├── tools.py    # DB tools
│   │   └── websearch.py
│   ├── data/
│   │   ├── drugs.sql   # Drug schema + data
│   │   └── history.sql # History schema + data
│   ├── app.py          # Flask factory
│   ├── run.py          # Dev server
│   ├── config.py       # Constants
│   └── prompts.py      # LLM prompts
│
├── Relapse/            # ML Prediction Service
│   ├── api/
│   │   └── routes.py   # 6 endpoints
│   ├── core/
│   │   ├── features.py # Feature engineering
│   │   ├── model.py    # XGBoost predictor
│   │   ├── metrics.py  # Performance metrics
│   │   └── storage.py  # Model versioning
│   ├── app.py          # Flask factory
│   ├── run.py          # Dev server
│   ├── config.py       # Constants
│   └── prompts.py      # Disclaimers
│
├── init_databases.py   # DB setup script
├── test_services.py    # Test suite
└── README.md           # Full documentation
```

---

## 🔧 Troubleshooting

### "Module not found" errors
```powershell
# Ensure you're in the correct directory
cd backend/Chat  # or backend/Relapse
pip install -r requirements.txt
```

### "GROQ_API_KEY not found"
```powershell
# Check .env file in project root (not backend/)
cd ..
notepad .env
# Add: GROQ_API_KEY=gsk_your_key_here
```

### Databases not initialized
```powershell
cd backend
python init_databases.py
```

### RAG not working
```powershell
# Initialize vector index first
curl -X POST http://localhost:5001/chat/ingest/drugs
```

### Relapse predictions fail
```powershell
# Train model first
curl -X POST http://localhost:5002/relapse/train
```

---

## 🎓 Next Steps

1. **Customize Prompts:** Edit `Chat/prompts.py` and `Relapse/prompts.py`
2. **Add More Data:** Extend SQL files in `Chat/data/`
3. **Tune Model:** Adjust hyperparameters in `Relapse/config.py`
4. **Add Web Search:** Configure search API in `.env` and update `Chat/core/websearch.py`
5. **Production Deploy:** Use Gunicorn (see README.md)

---

## 📚 Documentation

- Full API docs: [backend/README.md](README.md)
- Architecture plan: [../plan.md](../plan.md)

---

## 🎉 You're Ready!

Both services are now running and ready for your hackathon project. Build an amazing frontend and win! 🏆

**Support Resources:**
- SAMHSA National Helpline: 1-800-662-4357
- Crisis Text Line: Text HOME to 741741
