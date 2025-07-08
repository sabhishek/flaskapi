import os
import requests
from typing import Optional

ARGO_URL = os.getenv("ARGOCD_URL", "http://argocd.example.com")
ARGO_TOKEN = os.getenv("ARGOCD_TOKEN")


def _headers():
    return {"Authorization": f"Bearer {ARGO_TOKEN}"} if ARGO_TOKEN else {}


def trigger_sync(app_name: str):
    url = f"{ARGO_URL}/api/v1/applications/{app_name}/sync"
    r = requests.post(url, headers=_headers(), json={})
    r.raise_for_status()
    return r.json()


def get_app_status(app_name: str) -> Optional[dict]:
    url = f"{ARGO_URL}/api/v1/applications/{app_name}"
    r = requests.get(url, headers=_headers())
    if r.status_code == 200:
        return r.json()
    return None
