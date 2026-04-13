Got it — you want **clean, continuous README content (no separated blocks, no IDs, no breaks)**. Just copy everything below 👇

---

# 🚀 Agentic Multi-PDF RAG System

### Next.js + Gemini + Endee (Production-Ready)

An **Agentic Retrieval-Augmented Generation (RAG) system** that enables users to upload multiple PDFs, index them into a vector database, and interact with them using **context-aware AI reasoning** powered by **Gemini 1.5 Pro**.

Built with a modern full-stack architecture and a sleek UI inspired by developer portfolios.

---

## ✨ Features

* 📄 Upload and process multiple PDFs
* 🔍 Semantic search using vector embeddings
* 🧠 Agentic reasoning with conversation memory
* 🤖 Powered by Gemini 1.5 Pro (Google AI Studio)
* ⚡ FastAPI backend with efficient chunking + embedding
* 💾 Endee Vector DB (Docker-based local storage)
* 🎨 Beautiful UI with animations (Framer Motion)
* 💬 ChatGPT-like conversational interface
* 📚 Source-grounded answers with citations (file + page)

---

## 🧱 Tech Stack

### Frontend

* Next.js 14 (App Router)
* Tailwind CSS
* Framer Motion
* React Markdown

### Backend

* FastAPI
* google-generativeai
* PyMuPDF (PDF parsing)
* sentence-transformers (MiniLM-L6-v2)

### Database

* Endee Vector Database (Docker)

---

## 📁 Project Structure

```
project-root/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
└── endee-data/   # Vector DB persistent storage
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```
git clone https://github.com/Vijay-1469/Project--vector.git
cd Project--Vector
```

---

### 2. Environment Variables

Create `backend/.env`

```
GEMINI_API_KEY=your_google_ai_studio_api_key_here
ENDEE_HOST=localhost
ENDEE_PORT=8080
```

---

### 3. Run Endee (Vector Database)

```
docker run \
  --ulimit nofile=100000:100000 \
  -p 8080:8080 \
  -v ./endee-data:/data \
  --name endee-server \
  --restart unless-stopped \
  endeeio/endee-server:latest
```

Endee runs at: [http://localhost:8080](http://localhost:8080)

---

### 4. Backend Setup (FastAPI)

```
cd backend
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend runs at: [http://localhost:8000](http://localhost:8000)

---

### 5. Frontend Setup (Next.js)

```
cd frontend
npm install
npm run dev
```

Frontend runs at: [http://localhost:3000](http://localhost:3000)

---
