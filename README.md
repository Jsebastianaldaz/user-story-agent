# 🤖 User Story Generator Agent

An AI-powered pipeline that automates the full product artifact lifecycle — from a Confluence spec to production-ready Jira epics, user stories, acceptance criteria, and sprint structure.

Built with [Claude claude-opus-4-5](https://www.anthropic.com/claude) + Confluence Cloud API + Jira Cloud API.

---

## 🧠 How It Works

The agent runs a **6-step sequential chain**, where each step produces structured JSON consumed by the next:

```
Confluence Spec
      │
      ▼
 [Step 1] Read spec from Confluence page
      │
      ▼
 [Step 2] Generate Epics  ← Claude claude-opus-4-5
      │
      ▼
 [Step 3] Decompose into User Stories  ← Claude claude-opus-4-5
      │
      ▼
 [Step 4] Generate Acceptance Criteria (Gherkin)  ← Claude claude-opus-4-5
      │
      ▼
 [Step 5] Build User Story Map + Release Plan  ← Claude claude-opus-4-5
      │
      ▼
 [Step 6] Push Epics + Stories to Jira
```

---

## 📦 Project Structure

```
user-story-agent/
├── src/
│   ├── agent.py            # Main pipeline orchestrator
│   ├── confluence_client.py # Confluence Cloud API wrapper
│   └── jira_client.py      # Jira Cloud API wrapper
├── docs/                   # Additional documentation
├── examples/               # Example inputs and outputs
├── CLAUDE.md               # Context file for Claude Code
├── .env.example            # Environment variables template
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/Jsebastianaldaz/user-story-agent.git
cd user-story-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Run the agent
```bash
python -m src.agent
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill in your credentials:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `CONFLUENCE_DOMAIN` | e.g. `your-company.atlassian.net` |
| `CONFLUENCE_EMAIL` | Your Atlassian email |
| `CONFLUENCE_API_TOKEN` | Confluence API token |
| `JIRA_DOMAIN` | e.g. `your-company.atlassian.net` |
| `JIRA_EMAIL` | Your Atlassian email |
| `JIRA_API_TOKEN` | Jira API token |
| `JIRA_PROJECT_KEY` | e.g. `EDP` |

---

## 💡 Usage Example

```python
from src.agent import run_pipeline

result = run_pipeline(
    initiative_title="Gift Cards Feature",
    confluence_page_id="YOUR_PAGE_ID",
    project_key="EDP"
)

print(f"Created {len(result['jira_artifacts'])} artifacts in Jira")
```

**Sample output:**
```
🚀 Iniciando pipeline para: Gift Cards Feature

📥 Paso 1: Leyendo spec desde Confluence...
🗂  Paso 2: Generando épicas...
📝 Paso 3: Descomponiendo en user stories...
✅ Paso 4: Generando criterios de aceptación...
🗺  Paso 5: Estructurando User Story Map...
📤 Paso 6: Creando artefactos en Jira...
  ✓ Épica creada: EDP-1
    ✓ Story creada: EDP-2
    ✓ Story creada: EDP-3
  ✓ Épica creada: EDP-4
    ✓ Story creada: EDP-5

✅ Pipeline completado. 5 artefactos creados en Jira.
```

---

## 🏗️ Built With

- [Anthropic Claude claude-opus-4-5](https://docs.anthropic.com/) — AI reasoning engine
- [Confluence Cloud REST API](https://developer.atlassian.com/cloud/confluence/rest/) — Spec intake
- [Jira Cloud REST API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/) — Artifact creation
- Python 3.11+

---

## 📄 License

MIT License — feel free to use, adapt, and build on top of this.

---

## 👤 Author

**Jaime Sebastián Aldaz Mora**
Head of Product & Engineering @ Fast-growing grocery e-commerce startup in LATAM
[LinkedIn](https://www.linkedin.com/in/jaime-sebasti%C3%A1n-aldaz-227a82112) · [GitHub](https://github.com/Jsebastianaldaz)
