# 🎓 LearnBot — AI-Powered Course Content Simplification Agent

[![IBM watsonx.ai](https://img.shields.io/badge/IBM-watsonx.ai-blue?logo=ibm)](https://www.ibm.com/products/watsonx-ai)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)](https://getbootstrap.com/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://python.org)

**LearnBot** is a production-ready, AI-powered web application that simplifies complex academic content using **IBM watsonx.ai** and the **IBM Granite 3.0 8B Instruct** model. It features a full RAG (Retrieval-Augmented Generation) pipeline, adaptive multi-level learning, and a modern glassmorphism UI.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Document Upload** | PDF, DOCX, TXT support with drag-and-drop |
| 📋 **Paste Text** | Process text directly without uploading |
| 🤖 **RAG Pipeline** | FAISS + sentence-transformers for grounded answers |
| 🎓 **Adaptive Levels** | Beginner / Intermediate / Expert proficiency modes |
| 🌍 **Analogies & Examples** | Real-world examples for every concept |
| ❓ **Practice Questions** | Auto-generated quizzes and Q&A |
| 📊 **Dashboard** | Learning stats, progress tracking, subject distribution |
| 🕐 **History** | Full learning history with re-ask functionality |
| ⚙️ **Settings** | Proficiency, subject, and connection testing |
| 🌙 **Dark Mode** | Full dark/light mode toggle |
| 📱 **Mobile Responsive** | Fully responsive Bootstrap 5 design |
| 🔧 **Agent Instructions** | Centralized customization module |

---

## 🏗️ Project Structure

```
course_simplifier/
├── run.py                          # Development entry point
├── wsgi.py                         # Production WSGI entry point
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variable template
├── .env                            # Your credentials (DO NOT commit)
│
└── app/
    ├── __init__.py                 # Flask application factory
    │
    ├── core/
    │   ├── agent_instructions.py   # ⭐ CUSTOMIZE AGENT HERE
    │   ├── watsonx_client.py       # IBM watsonx.ai wrapper
    │   └── rag_engine.py           # RAG pipeline (FAISS + sentence-transformers)
    │
    ├── routes/
    │   ├── main.py                 # Home + About
    │   ├── chat.py                 # Chat API + page
    │   ├── upload.py               # Document upload + paste
    │   ├── dashboard.py            # Learner dashboard
    │   ├── history.py              # Learning history
    │   └── settings.py             # Settings + connection test
    │
    ├── templates/
    │   ├── base.html               # Base layout (navbar, footer, dark mode)
    │   ├── home.html               # Landing page
    │   ├── chat.html               # Chat interface
    │   ├── upload.html             # Document upload page
    │   ├── dashboard.html          # Learner dashboard
    │   ├── history.html            # Learning history
    │   ├── settings.html           # Settings page
    │   └── about.html              # About page
    │
    ├── static/
    │   ├── css/style.css           # Custom styles (glassmorphism, dark mode, animations)
    │   ├── js/
    │   │   ├── app.js              # Global utilities (dark mode, toast, fetch wrapper)
    │   │   ├── chat.js             # Chat interface logic
    │   │   ├── upload.js           # Upload & paste logic
    │   │   └── settings.js         # Settings page logic
    │   └── uploads/                # Document upload directory
    │
    └── utils/
        └── __init__.py
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- pip
- IBM Cloud account with watsonx.ai access

### 1. Clone / Download the project

```bash
cd course_simplifier
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
IBM_API_KEY=your_ibm_cloud_api_key
IBM_PROJECT_ID=your_watsonx_project_id
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
FLASK_SECRET_KEY=your-strong-random-secret-key
```

### 5. Run the application

```bash
python run.py
```

Open your browser at **http://localhost:5000**

---

## 🔑 Getting IBM watsonx.ai Credentials

### IBM Cloud API Key
1. Go to [IBM Cloud Console](https://cloud.ibm.com)
2. Navigate to **Manage → Access (IAM) → API Keys**
3. Click **Create an IBM Cloud API Key**
4. Copy the key and paste it in `.env` as `IBM_API_KEY`

### watsonx.ai Project ID
1. Go to [IBM watsonx.ai](https://dataplatform.cloud.ibm.com/wx/home)
2. Create a new project or open an existing one
3. Go to **Project → Manage → General**
4. Copy the **Project ID** and paste it in `.env` as `IBM_PROJECT_ID`

---

## 🤖 Customizing the Agent (`agent_instructions.py`)

All agent behavior is controlled from `app/core/agent_instructions.py`. No code changes needed elsewhere.

```python
# ── Change the agent's name and persona
AGENT_NAME = "LearnBot"
AGENT_PERSONA = "You are LearnBot, a friendly AI tutor..."

# ── Change tone: "formal" | "conversational" | "encouraging" | "Socratic"
AGENT_TONE = "encouraging"

# ── Change teaching style: "direct" | "analogical" | "Socratic" | "constructivist"
TEACHING_STYLE = "analogical"

# ── Customize depth per proficiency level
PROFICIENCY_INSTRUCTIONS = {
    "Beginner":     "Use very simple language (Grade 6–8 reading level)...",
    "Intermediate": "Use moderate technical vocabulary...",
    "Expert":       "Use full technical vocabulary...",
}

# ── Add/remove subjects
SUPPORTED_SUBJECTS = ["Computer Science", "Mathematics", ...]

# ── Modify response format
RESPONSE_FORMAT = """
## 📘 Summary
## 🔑 Key Concepts & Definitions
## 💡 Explanation
...
"""

# ── Edit safety rules
SAFETY_RULES = "1. Never generate harmful content..."
```

---

## ⚙️ Configuration Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `IBM_API_KEY` | IBM Cloud API key | Required |
| `IBM_PROJECT_ID` | watsonx.ai project ID | Required |
| `IBM_WATSONX_URL` | watsonx.ai endpoint URL | `https://us-south.ml.cloud.ibm.com` |
| `GRANITE_MODEL_ID` | Model ID to use | `ibm/granite-3-8b-instruct` |
| `MAX_NEW_TOKENS` | Max response length in tokens | `1024` |
| `TEMPERATURE` | Generation temperature (0.0–1.0) | `0.7` |
| `FLASK_SECRET_KEY` | Flask session secret | Required |
| `MAX_CONTENT_LENGTH` | Max file size in bytes | `16777216` (16 MB) |

---

## 🏭 Production Deployment

### Option 1: Gunicorn (Linux/macOS)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

### Option 2: IBM Cloud Code Engine

1. **Create a `Procfile`**:
   ```
   web: gunicorn -w 2 -b 0.0.0.0:$PORT wsgi:app
   ```

2. **Deploy via IBM Cloud CLI**:
   ```bash
   ibmcloud login
   ibmcloud ce project create --name learnbot
   ibmcloud ce app create \
     --name learnbot \
     --image icr.io/your-namespace/learnbot \
     --env IBM_API_KEY=xxx \
     --env IBM_PROJECT_ID=xxx \
     --env FLASK_SECRET_KEY=xxx
   ```

### Option 3: Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "wsgi:app"]
```

```bash
docker build -t learnbot .
docker run -p 8000:8000 --env-file .env learnbot
```

### Option 4: IBM Cloud Foundry

1. Create `manifest.yml`:
   ```yaml
   applications:
     - name: learnbot
       memory: 512M
       instances: 1
       command: gunicorn -w 2 -b 0.0.0.0:$PORT wsgi:app
   ```

2. Deploy:
   ```bash
   ibmcloud cf push
   ```

---

## 🔧 Architecture Overview

```
User Browser
    │
    ▼
Flask Application (run.py / wsgi.py)
    │
    ├── Routes (Blueprints)
    │     ├── /           → Home + About
    │     ├── /chat/      → Chat API + UI
    │     ├── /upload/    → Document processing API
    │     ├── /dashboard/ → Learning stats
    │     ├── /history/   → Session history
    │     └── /settings/  → Preferences + health check
    │
    ├── Core Modules
    │     ├── agent_instructions.py  → System prompt builder
    │     ├── watsonx_client.py      → IBM Granite API calls
    │     └── rag_engine.py          → Document parsing + FAISS indexing
    │
    └── Static Assets
          ├── Bootstrap 5.3 (CDN)
          ├── Bootstrap Icons (CDN)
          ├── marked.js (Markdown rendering, CDN)
          └── Custom CSS + JS (local)
```

### RAG Pipeline Flow

```
Upload Document
    │
    ▼
Parse (PyPDF2 / python-docx / plain text)
    │
    ▼
Chunk (400 words, 80-word overlap)
    │
    ▼
Embed (sentence-transformers: all-MiniLM-L6-v2)
    │
    ▼
Index (FAISS IndexFlatL2, per-session)
    │
User Query ──► Embed Query ──► FAISS Search ──► Top-5 Chunks
                                                      │
                                                      ▼
                                              IBM Granite LLM
                                                      │
                                                      ▼
                                             Structured Response
```

---

## 🧪 Testing the Connection

1. Navigate to **Settings → Test Connection**
2. The app will attempt a lightweight API call to confirm credentials
3. Or use the health endpoint: `GET /chat/health`

---

## 📦 Dependencies

```
Flask==3.0.3                  # Web framework
Flask-Session==0.8.0          # Server-side sessions
python-dotenv==1.0.1          # .env file loading
ibm-watsonx-ai==1.1.2         # IBM watsonx.ai SDK
PyPDF2==3.0.1                 # PDF parsing
python-docx==1.1.2            # DOCX parsing
sentence-transformers==3.0.1  # Text embeddings for RAG
faiss-cpu==1.8.0              # Vector similarity search
numpy==1.26.4                 # Numerical operations
Werkzeug==3.0.3               # WSGI utilities
gunicorn==22.0.0              # Production WSGI server
chardet==5.2.0                # Encoding detection
tiktoken==0.7.0               # Token counting
```

---

## 🛡️ Security Notes

- **Never commit `.env`** — it contains your IBM API key. Add `.env` to `.gitignore`.
- Use a strong, random `FLASK_SECRET_KEY` in production.
- File uploads are validated by extension and size before processing.
- The agent is instructed never to reproduce copyrighted material verbatim or complete live exam questions.

---

## 🤝 Contributing & Extending

- **Add a new subject**: Edit `SUPPORTED_SUBJECTS` and `SUBJECT_NOTES` in `agent_instructions.py`.
- **Change response format**: Edit `RESPONSE_FORMAT` in `agent_instructions.py`.
- **Swap the model**: Set `GRANITE_MODEL_ID=ibm/granite-13b-chat-v2` in `.env`.
- **Persist sessions to a database**: Replace Flask's in-memory session with SQLAlchemy or Redis.
- **Add authentication**: Add Flask-Login and a user model.

---

## 📄 License

MIT License — free to use, modify, and distribute.
