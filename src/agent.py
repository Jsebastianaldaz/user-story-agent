"""
User Story Generator Agent
Pipeline de 6 pasos: Confluence → Épicas → User Stories → USM → Sprints → Jira
"""

import os
import json
from anthropic import Anthropic
from src.confluence_client import ConfluenceClient
from src.jira_client import JiraClient

client = Anthropic()
confluence = ConfluenceClient()
jira = JiraClient()


def run_pipeline(initiative_title: str, confluence_page_id: str, project_key: str):
    """
    Ejecuta el pipeline completo de generación de user stories.

    Args:
        initiative_title: Nombre de la iniciativa de producto
        confluence_page_id: ID de la página de Confluence con el spec
        project_key: Clave del proyecto en Jira (ej. "EDP")
    """
    print(f"\n🚀 Iniciando pipeline para: {initiative_title}\n")

    # ── PASO 1: Intake desde Confluence ─────────────────────────────
    print("📥 Paso 1: Leyendo spec desde Confluence...")
    spec = confluence.get_page_content(confluence_page_id)

    # ── PASO 2: Generación de Épicas ────────────────────────────────
    print("🗂  Paso 2: Generando épicas...")
    epics = generate_epics(initiative_title, spec)

    # ── PASO 3: Descomposición en User Stories ───────────────────────
    print("📝 Paso 3: Descomponiendo en user stories...")
    stories = generate_stories(epics, spec)

    # ── PASO 4: Criterios de Aceptación ─────────────────────────────
    print("✅ Paso 4: Generando criterios de aceptación...")
    stories_with_ac = generate_acceptance_criteria(stories)

    # ── PASO 5: User Story Map ───────────────────────────────────────
    print("🗺  Paso 5: Estructurando User Story Map...")
    usm = generate_usm(epics, stories_with_ac)

    # ── PASO 6: Push a Jira ─────────────────────────────────────────
    print("📤 Paso 6: Creando artefactos en Jira...")
    created = push_to_jira(project_key, epics, stories_with_ac)

    print(f"\n✅ Pipeline completado. {len(created)} artefactos creados en Jira.\n")
    return {
        "epics": epics,
        "stories": stories_with_ac,
        "usm": usm,
        "jira_artifacts": created,
    }


# ── PASO 2: ÉPICAS ──────────────────────────────────────────────────
def generate_epics(initiative: str, spec: str) -> list[dict]:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=2000,
        system="""Eres un Product Manager senior experto en metodologías ágiles.
Tu tarea es analizar un spec de producto y generar épicas bien definidas.
Responde SOLO con un JSON válido, sin texto adicional, con este formato:
[
  {
    "title": "Nombre de la épica",
    "description": "Descripción clara del alcance",
    "business_value": "Valor de negocio que aporta"
  }
]""",
        messages=[
            {
                "role": "user",
                "content": f"Iniciativa: {initiative}\n\nSpec:\n{spec}\n\nGenera las épicas necesarias."
            }
        ]
    )
    return json.loads(response.content[0].text)


# ── PASO 3: USER STORIES ─────────────────────────────────────────────
def generate_stories(epics: list[dict], spec: str) -> list[dict]:
    all_stories = []
    for epic in epics:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=3000,
            system="""Eres un Product Manager senior experto en escritura de user stories.
Genera user stories en formato: "Como [rol], quiero [acción], para [beneficio]".
Responde SOLO con JSON válido:
[
  {
    "epic_title": "Título de la épica padre",
    "title": "Título corto de la story",
    "user_story": "Como [rol], quiero [acción], para [beneficio]",
    "story_points": 3,
    "priority": "High|Medium|Low"
  }
]""",
            messages=[
                {
                    "role": "user",
                    "content": f"Épica: {epic['title']}\nDescripción: {epic['description']}\n\nSpec completo:\n{spec}\n\nGenera las user stories para esta épica."
                }
            ]
        )
        stories = json.loads(response.content[0].text)
        all_stories.extend(stories)
    return all_stories


# ── PASO 4: CRITERIOS DE ACEPTACIÓN ─────────────────────────────────
def generate_acceptance_criteria(stories: list[dict]) -> list[dict]:
    enriched = []
    for story in stories:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1000,
            system="""Eres un QA Lead experto en criterios de aceptación en formato Gherkin.
Responde SOLO con JSON válido:
{
  "acceptance_criteria": [
    "DADO [contexto], CUANDO [acción], ENTONCES [resultado esperado]"
  ],
  "definition_of_done": [
    "Criterio de done"
  ]
}""",
            messages=[
                {
                    "role": "user",
                    "content": f"User Story: {story['user_story']}\n\nGenera criterios de aceptación en formato Gherkin."
                }
            ]
        )
        ac_data = json.loads(response.content[0].text)
        enriched.append({**story, **ac_data})
    return enriched


# ── PASO 5: USER STORY MAP ───────────────────────────────────────────
def generate_usm(epics: list[dict], stories: list[dict]) -> dict:
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        system="""Eres un Product Manager experto en User Story Mapping.
Organiza las épicas y stories en releases/sprints priorizados.
Responde SOLO con JSON válido:
{
  "releases": [
    {
      "name": "MVP / Release 1",
      "goal": "Objetivo del release",
      "epics": [
        {
          "title": "Épica",
          "stories": ["story 1", "story 2"]
        }
      ]
    }
  ]
}""",
        messages=[
            {
                "role": "user",
                "content": f"Épicas: {json.dumps(epics)}\n\nStories: {json.dumps([s['title'] for s in stories])}\n\nCrea el User Story Map con releases priorizados."
            }
        ]
    )
    return json.loads(response.content[0].text)


# ── PASO 6: PUSH A JIRA ──────────────────────────────────────────────
def push_to_jira(project_key: str, epics: list[dict], stories: list[dict]) -> list[dict]:
    created = []

    for epic in epics:
        epic_key = jira.create_epic(
            project_key=project_key,
            title=epic["title"],
            description=epic["description"]
        )
        print(f"  ✓ Épica creada: {epic_key}")

        epic_stories = [s for s in stories if s["epic_title"] == epic["title"]]
        for story in epic_stories:
            story_key = jira.create_story(
                project_key=project_key,
                epic_key=epic_key,
                title=story["title"],
                user_story=story["user_story"],
                acceptance_criteria=story.get("acceptance_criteria", []),
                story_points=story.get("story_points", 3),
                priority=story.get("priority", "Medium")
            )
            print(f"    ✓ Story creada: {story_key}")
            created.append({"type": "story", "key": story_key})

        created.append({"type": "epic", "key": epic_key})

    return created


if __name__ == "__main__":
    run_pipeline(
        initiative_title="Gift Cards Feature",
        confluence_page_id=os.getenv("CONFLUENCE_PAGE_ID", "YOUR_PAGE_ID"),
        project_key=os.getenv("JIRA_PROJECT_KEY", "EDP")
    )
