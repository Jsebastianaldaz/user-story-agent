"""
Cliente para Jira Cloud API
"""

import os
import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    def __init__(self):
        self.base_url = f"https://{os.getenv('JIRA_DOMAIN')}/rest/api/3"
        self.auth = HTTPBasicAuth(
            os.getenv("JIRA_EMAIL"),
            os.getenv("JIRA_API_TOKEN")
        )
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_epic(self, project_key: str, title: str, description: str) -> str:
        """Crea una épica en Jira y retorna su key (ej. EDP-1)."""
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
                },
                "issuetype": {"name": "Epic"},
                "customfield_10011": title  # Epic Name field
            }
        }
        response = requests.post(
            f"{self.base_url}/issue",
            json=payload,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["key"]

    def create_story(
        self,
        project_key: str,
        epic_key: str,
        title: str,
        user_story: str,
        acceptance_criteria: list[str],
        story_points: int = 3,
        priority: str = "Medium"
    ) -> str:
        """Crea una user story vinculada a una épica y retorna su key."""
        ac_text = "\n".join([f"• {ac}" for ac in acceptance_criteria])
        full_description = f"{user_story}\n\n*Criterios de Aceptación:*\n{ac_text}"

        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": title,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [{"type": "paragraph", "content": [{"type": "text", "text": full_description}]}]
                },
                "issuetype": {"name": "Story"},
                "priority": {"name": priority},
                "story_points": story_points,
                "customfield_10014": epic_key,  # Epic Link field
            }
        }
        response = requests.post(
            f"{self.base_url}/issue",
            json=payload,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["key"]

    def create_sprint(self, board_id: str, name: str, goal: str) -> int:
        """Crea un sprint en un board de Jira y retorna su ID."""
        payload = {
            "name": name,
            "goal": goal,
            "originBoardId": board_id
        }
        response = requests.post(
            f"https://{os.getenv('JIRA_DOMAIN')}/rest/agile/1.0/sprint",
            json=payload,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["id"]

    def move_issues_to_sprint(self, sprint_id: int, issue_keys: list[str]) -> bool:
        """Mueve issues a un sprint específico."""
        payload = {"issues": issue_keys}
        response = requests.post(
            f"https://{os.getenv('JIRA_DOMAIN')}/rest/agile/1.0/sprint/{sprint_id}/issue",
            json=payload,
            auth=self.auth,
            headers=self.headers
        )
        response.raise_for_status()
        return True
