# CLAUDE.md — User Story Generator Agent

## Project Overview
This is an AI-powered pipeline that automates the full product artifact lifecycle:
from a Confluence spec → Epics → User Stories → Acceptance Criteria → User Story Map → Jira issues.

## Architecture
- **Language:** Python 3.11+
- **AI Model:** Claude claude-opus-4-5 via Anthropic SDK
- **Integrations:** Confluence Cloud API + Jira Cloud API
- **Pattern:** Sequential 6-step chain with JSON-structured outputs at each step

## Pipeline Steps
1. `get_page_content()` — Read spec from Confluence
2. `generate_epics()` — Claude generates epics from spec
3. `generate_stories()` — Claude decomposes each epic into user stories
4. `generate_acceptance_criteria()` — Claude adds Gherkin-format AC to each story
5. `generate_usm()` — Claude organizes stories into releases/sprints
6. `push_to_jira()` — Create epics and stories in Jira via REST API

## Key Constraints
- All Claude responses must be valid JSON (enforced via system prompt)
- Never hardcode credentials — always use environment variables from .env
- Each pipeline step must be independently testable
- Error handling must be explicit — no silent failures

## Output Format Standards
- Epics: `{ title, description, business_value }`
- Stories: `{ epic_title, title, user_story, story_points, priority, acceptance_criteria, definition_of_done }`
- USM: `{ releases: [{ name, goal, epics: [{ title, stories[] }] }] }`

## Environment
See `.env.example` for all required environment variables.
Run with: `python -m src.agent`
