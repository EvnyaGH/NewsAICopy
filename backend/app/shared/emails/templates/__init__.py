# app/shared/emails/templates/__init__.py
from pathlib import Path
from datetime import datetime

TEMPLATES_DIR = Path(__file__).parent

def render_verify_email(verification_link: str) -> str:
    html = (TEMPLATES_DIR / "verify_email.html").read_text()
    return (
        html.replace("{{verification_link}}", verification_link)
            .replace("{{year}}", str(datetime.now().year))
    )
