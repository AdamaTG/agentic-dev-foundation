"""Exemple purement local : création de signalement, sans réseau ni stockage."""
from uuid import uuid4

def creer_signalement(description: str) -> dict[str, str]:
    if not isinstance(description, str) or not description.strip():
        raise ValueError("La description est obligatoire")
    return {"id": f"SIG-{uuid4().hex[:12].upper()}", "description": description.strip(), "statut": "nouveau"}
