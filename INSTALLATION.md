# Installation & Setup Guide

This guide covers installing and launching the Automated LinkedIn Tech Post Generator on Windows, macOS, or Linux.

---

## Prerequisites

- **Python**: 3.10+ (Python 3.12 recommended)
- **Node.js**: v18+ (Node v25 supported)
- **Git**

---

## Step 1: Environment Configuration

Create a `.env` file in `backend/` or the root workspace:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=gemini-2.5-flash
TEMPERATURE=0.7
```

---

## Step 2: Backend Setup (Python / FastAPI)

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run unit tests to verify installation:
   ```bash
   pytest tests
   ```

5. Start the backend Uvicorn server:
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```
   *The backend will be running at `http://127.0.0.1:8001` with interactive API docs at `http://127.0.0.1:8001/docs`.*

---

## Step 3: Frontend Setup (React + Vite)

1. Open a new terminal window and navigate to `frontend`:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The React UI studio will open at `http://localhost:3000`.*

---

## Step 4: Verification Walkthrough

1. Open `http://localhost:3000` in your web browser.
2. Click **Fetch Trending News** to load ranked Hacker News stories.
3. Select your desired tone (**Professional**, **Founder**, **Developer**, **Investor**).
4. Click **Generate Post for Top Story**.
5. Preview the post caption, word count counter, dynamic hashtags, and attached image card.
6. Click **Copy Caption** to copy formatted text to your clipboard.
7. Click **Export** to download `.md`, `.html`, or `.json` artifacts.
