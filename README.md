<div align="center">

# 🎓 Mentora AI

### Your Personal AI Computer Science Teacher

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5-FF6F00?style=for-the-badge&logo=databricks&logoColor=white)](https://www.trychroma.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com)

An intelligent, full-stack AI teaching assistant that uses **Retrieval-Augmented Generation (RAG)** to deliver personalized computer science education. Powered by real CS50 lecture transcripts, it teaches concepts from scratch using analogies, the Socratic method, and interactive code examples.

[**Live Demo**](https://mentora-ai.onrender.com) · [**Report Bug**](https://github.com/vigneshselvanV/Mentora-AI/issues) · [**Request Feature**](https://github.com/vigneshselvanV/Mentora-AI/issues)

---

</div>

## ✨ Features

<table>
<tr>
<td width="50%">

### 🧠 AI-Powered Teaching
- **RAG Pipeline** — Retrieves relevant content from 60+ CS50 lecture transcripts before generating responses
- **Dual Mode System** — Automatically detects casual conversation vs. technical questions
- **Socratic Method** — Guides students to discover answers rather than giving them directly
- **Analogy-First Approach** — Every technical concept starts with a real-world analogy

</td>
<td width="50%">

### 📊 Learning Dashboard
- **Progress Tracking** — Questions asked, topics explored, learning streaks
- **Quiz Mode** — AI-generated quizzes with configurable difficulty and question count
- **Learning Paths** — AI-generated step-by-step roadmaps for any learning goal
- **Saved Notes** — Bookmark and export important answers

</td>
</tr>
<tr>
<td width="50%">

### 🔐 Authentication System
- **Secure Signup/Login** — PBKDF2-HMAC-SHA256 password hashing with random salts
- **Token-Based Auth** — HMAC-signed tokens with 7-day expiry
- **Demo Account** — Try the app instantly without registration
- **User Profiles** — Personalized experience with persistent data

</td>
<td width="50%">

### 🎨 Modern UI/UX
- **Dark & Light Themes** — Smooth theme switching with persistent preference
- **Glassmorphism Design** — Frosted glass effects with backdrop blur
- **Responsive Layout** — Works seamlessly on desktop and mobile
- **Micro-Animations** — Typing indicators, slide-ups, and smooth transitions

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (HTML/CSS/JS)                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │  Chat UI  │  │ Progress │  │  Quiz    │  │ Learning Path │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬───────┘   │
│       └──────────────┴─────────────┴───────────────┘           │
│                          REST API                               │
├─────────────────────────────────────────────────────────────────┤
│                     FASTAPI BACKEND                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Auth Module   │  │ User Data    │  │   RAG Pipeline      │   │
│  │ (HMAC tokens) │  │ (SQLite)     │  │                     │   │
│  └──────────────┘  └──────────────┘  │  Question ──►        │   │
│                                       │  Embedding ──►       │   │
│                                       │  Vector Search ──►   │   │
│                                       │  Context + LLM ──►   │   │
│                                       │  Response            │   │
│                                       └─────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ ChromaDB          │  │ Sentence          │  │ OpenRouter   │  │
│  │ (Vector Store)    │  │ Transformers      │  │ (LLM API)   │  │
│  │ 60+ lectures      │  │ all-MiniLM-L6-v2  │  │ Free Models │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | Async API server |
| **AI/LLM** | OpenRouter API | Language model inference (free-tier models) |
| **Embeddings** | Sentence Transformers (`all-MiniLM-L6-v2`) | Semantic text encoding |
| **Vector DB** | ChromaDB | Persistent vector storage & similarity search |
| **Database** | SQLite | User accounts & progress data |
| **Auth** | PBKDF2-HMAC-SHA256 + HMAC tokens | Secure authentication |
| **Frontend** | Vanilla HTML/CSS/JS | No framework dependencies |
| **Styling** | CSS Variables + Glassmorphism | Dark/light theme system |
| **Deployment** | Render / Vercel | Production hosting |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **pip** (Python package manager)
- An **[OpenRouter API key](https://openrouter.ai/)** (free tier available)

### 1. Clone the Repository

```bash
git clone https://github.com/vigneshselvanV/Mentora-AI.git
cd Mentora-AI
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
OPENROUTER_API_KEY=your-openrouter-key-here
MODEL_NAME=meta-llama/llama-3.3-70b-instruct:free
SECRET_KEY=your-super-secret-key-min-32-chars
DEMO_EMAIL=demo@mentora.ai
DEMO_PASSWORD=Demo1234
```

> **💡 Tip:** Generate a secure `SECRET_KEY` by running:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 5. Run the Application

```bash
python main.py
```

The server starts at **http://localhost:8000**

| Route | Description |
|-------|-------------|
| `/` | Login / Signup page |
| `/app` | Main application (requires authentication) |
| `/health` | API health check |

---

## 📁 Project Structure

```
Mentora-AI/
├── main.py                 # FastAPI app entry point + all routes
├── auth.py                 # Password hashing, token creation/verification
├── database.py             # SQLite ORM — users, sessions, progress
├── models.py               # Pydantic request/response schemas
├── requirements.txt        # Python dependencies
├── render.yaml             # Render deployment config
├── vercel.json             # Vercel rewrite rules
├── .env.example            # Environment variable template
├── .gitignore              # Git ignore rules
│
├── backend/
│   ├── config.py           # Environment config & model list
│   ├── embeddings.py       # Sentence Transformer embedding service
│   ├── vectorstore.py      # ChromaDB vector store wrapper
│   ├── prompts.py          # System prompts & teaching methodology
│   └── rag.py              # RAG pipeline — retrieve, augment, generate
│
├── frontend/
│   ├── login.html          # Auth page (sign in / sign up / demo)
│   ├── index.html          # Main app (chat, progress, quiz, paths, notes)
│   └── assets/             # Static assets
│
├── transcripts/            # 60+ CS50 lecture transcripts (knowledge base)
│   ├── CS50x 2024 - Lecture 0 - Scratch.txt
│   ├── CS50x 2025 - Lecture 1 - C.txt
│   ├── CS50P - Lecture 8 - Object-Oriented Programming.txt
│   └── ... (62 transcripts total)
│
└── chroma_db/              # Pre-built vector embeddings (committed to git)
```

---

## 🧪 How the RAG Pipeline Works

```
Student Question
       │
       ▼
┌─────────────────┐
│ Casual Detection │ ─── Is it a greeting/casual chat?
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
   YES        NO
    │         │
    ▼         ▼
 Casual    ┌──────────────────┐
 Response  │ Generate Embedding│
           │ (all-MiniLM-L6-v2)│
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Vector Search     │
           │ (ChromaDB top-5)  │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ Build Prompt with │
           │ Retrieved Context │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ LLM Generation   │
           │ (OpenRouter API)  │
           └────────┬─────────┘
                    │
                    ▼
           Teaching Response
           + Source Citations
```

**Teaching Methodology (built into the system prompt):**

1. 🤝 Warm acknowledgment
2. 🌍 Real-world analogy (understandable by a 10-year-old)
3. 📝 Plain English explanation, layer by layer
4. 💻 Code example with line-by-line breakdown
5. 📌 One-sentence summary
6. ❓ Socratic follow-up question

---

## 🌐 Deployment

### Deploy to Render

The project includes a [`render.yaml`](render.yaml) for one-click deployment:

1. Push your code to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Web Service**
3. Connect your GitHub repository
4. Set environment variables:
   - `OPENROUTER_API_KEY`
   - `SECRET_KEY`
5. Deploy!

> The `chroma_db/` directory with pre-built vectors is committed to the repository, so the knowledge base works immediately on deployment.

### Deploy Frontend to Vercel (Optional)

The [`vercel.json`](vercel.json) configuration handles routing for the static frontend if you want to deploy it separately.

---

## 🔑 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/health` | ❌ | Health check + vector DB stats |
| `POST` | `/auth/signup` | ❌ | Create new account |
| `POST` | `/auth/login` | ❌ | Sign in to existing account |
| `POST` | `/auth/logout` | ❌ | Logout (client-side token clear) |
| `GET` | `/auth/me` | ✅ | Get current user profile |
| `POST` | `/chat` | ✅ | Send a question, get AI response |
| `GET` | `/user/data` | ✅ | Retrieve saved progress |
| `POST` | `/user/data` | ✅ | Save user progress |
| `GET` | `/` | ❌ | Serve login page |
| `GET` | `/app` | ❌ | Serve main application |

---

## 📸 Screenshots

> Add screenshots of your app here by placing images in the repository and using:
> ```markdown
> ![Login Page](screenshots/login.png)
> ![Chat Interface](screenshots/chat.png)
> ![Quiz Mode](screenshots/quiz.png)
> ![Progress Dashboard](screenshots/progress.png)
> ```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions

- 🌍 Multi-language support
- 📱 Progressive Web App (PWA) support
- 🎙️ Voice input/output
- 📈 Advanced analytics dashboard
- 🔗 Integration with more course content
- 🧪 Unit and integration tests

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👨‍💻 Author

**Vignesh Selvan V**

- GitHub: [@vigneshselvanV](https://github.com/vigneshselvanV)

---

<div align="center">

### ⭐ If you found this project helpful, please give it a star!

Built with ❤️ and a passion for education

</div>
