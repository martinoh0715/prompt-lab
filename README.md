# PromptLab 🧪

> Version control and A/B testing platform for AI prompts

**Live Demo → [prompt-lab-ui.vercel.app](https://prompt-lab-ui.vercel.app/)**

---

## What is PromptLab?

When building AI-powered products, the quality of your output depends heavily on how you write your system prompt. But most teams rely on gut feeling to decide which prompt is "better."

PromptLab fixes that. It gives AI teams a way to version control their prompts (like Git), run head-to-head A/B experiments, and automatically score AI responses using GPT-4o — so the best prompt wins on data, not instinct.

---

## Features

- 📋 **Prompt Version Control** — Save and track multiple versions of your system prompt with commit messages
- 🤖 **Multi-Bot Support** — Manage prompts for multiple AI assistants from a single dashboard
- 🧪 **A/B Experiments** — Compare two prompt versions head-to-head with configurable traffic splits
- ⚡ **Live Testing** — Run real test questions and get AI responses instantly
- 🏆 **Auto Scoring** — GPT-4o automatically scores every response (1–5) on helpfulness, clarity, and empathy
- 📊 **Winner Declaration** — Data-backed winner declared based on average scores
- 🗑️ **Version Management** — Roll back, delete, or activate any prompt version

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js |
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| AI Scoring | OpenAI GPT-4o |
| Deployment | Railway (backend) + Vercel (frontend) |

---

## Screenshots

### Hero & Dashboard
![PromptLab Dashboard](https://prompt-lab-ui.vercel.app/)

### A/B Experiment Results
- Professional tone (v1) → **3.75/5**
- Empathetic tone (v2) → **4.12/5** 🏆

---

## Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key

### Backend

```bash
# Clone the repo
git clone https://github.com/martinoh0715/prompt-lab
cd prompt-lab

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key
echo "OPENAI_API_KEY=your-key-here" > .env

# Start the server
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`
API docs at `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd prompt-lab-ui
npm install
npm start
```

Frontend runs at `http://localhost:3000`

---

## Project Structure

```
prompt-lab/
├── main.py              # FastAPI server + API endpoints
├── database.py          # Database models (SQLAlchemy)
├── prompt_registry.py   # Prompt version management
├── experiment.py        # A/B experiment engine
├── analyzer.py          # OpenAI API + auto scoring
└── requirements.txt

prompt-lab-ui/
└── src/
    └── App.js           # React dashboard
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prompts` | List all bots |
| POST | `/prompts` | Create new prompt version |
| GET | `/prompts/{name}/versions` | Get all versions of a prompt |
| DELETE | `/prompts/{name}/{version}` | Delete a prompt version |
| POST | `/experiments` | Create new experiment |
| GET | `/experiments` | List all experiments |
| POST | `/experiments/{id}/test` | Run a test |
| GET | `/experiments/{id}/results` | Get experiment results |

---

## Author

**Martin Oh**
- Starting MAS-CS @ UPenn, Fall 2025
- B.B.A. Business @ Emory University
- [LinkedIn](https://www.linkedin.com/in/martinoh0715)
- [GitHub](https://github.com/martinoh0715)
