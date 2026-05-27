"""
Cliente para Confluence Cloud API
"""

import os
import requests
from requests.auth import HTTPBasicAuth


class ConfluenceClient:
    def __init__(self):
        self.base_url = f"https://{os.getenv('CONFLUENCE_DOMAIN')}/wiki/rest/api"
        self.auth = HTTPBasicAuth(
            os.getenv("CONFLUENCE_EMAIL"),
            os.getenv("CONFLUENCE_API_TOKEN")
        )
        self.headers = {"Accept": "application/json"}

    def get_page_content(self, page_id: str) -> str:
        """Obtiene el contenido de una página de Confluence."""
        url = f"{self.base_url}/content/{page_id}?expand=body.storage"
        response = requests.get(url, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data["body"]["storage"]["value"]

    def create_page(self, space_key: str, title: str, content: str, parent_id: str = None) -> str:
        """Crea una nueva página en Confluence y retorna su ID."""
        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]

        url = f"{self.base_url}/content"
        response = requests.post(url, json=payload, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return response.json()["id"]

    def update_page(self, page_id: str, title: str, content: str, version: int) -> bool:
        """Actualiza una página existente de Confluence."""
        payload = {
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }
        url = f"{self.base_url}/content/{page_id}"
        response = requests.put(url, json=payload, auth=self.auth, headers=self.headers)
        response.raise_for_status()
        return True
