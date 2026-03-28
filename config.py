"""
config.py — Configuration centralisée du Système de Triage Médical
Charge toutes les variables d'environnement depuis .env
"""

import os
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env en forçant l'écrasement (utile pour Streamlit)
load_dotenv(override=True)

# ─────────────────────────────────────────────
#  GOOGLE / GEMINI LLM
# ─────────────────────────────────────────────
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
GEMINI_MODEL: str = "gemini-2.5-flash"  # Gemini 2.5 Flash

# ─────────────────────────────────────────────
#  GOOGLE SHEETS
# ─────────────────────────────────────────────
GOOGLE_CREDENTIALS_PATH: str = os.getenv(
    "GOOGLE_CREDENTIALS_PATH", "credentials/google_credentials.json"
)
GOOGLE_SHEET_URL: str = os.getenv("GOOGLE_SHEET_URL", "")
SHEET_NAME: str = "Registre_Triage"  # Nom de l'onglet dans le Sheet

# ─────────────────────────────────────────────
#  EMAIL (Gmail SMTP)
# ─────────────────────────────────────────────
SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER: str = os.getenv("SMTP_USER", "")
SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
ALERT_EMAIL: str = os.getenv("ALERT_EMAIL", "aitmouhaddachmouad22@gmail.com")

# ─────────────────────────────────────────────
#  VALIDATION AU DÉMARRAGE
# ─────────────────────────────────────────────
def validate_config() -> list[str]:
    """Retourne une liste d'erreurs de configuration (vide si tout est OK)."""
    errors = []
    if not GOOGLE_API_KEY:
        errors.append("❌ GOOGLE_API_KEY manquante dans le fichier .env")
    if not GOOGLE_SHEET_URL:
        errors.append("❌ GOOGLE_SHEET_URL manquante dans le fichier .env")
    if not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        errors.append(
            f"❌ Fichier credentials Google introuvable : {GOOGLE_CREDENTIALS_PATH}"
        )
    if not SMTP_USER or not SMTP_PASSWORD:
        errors.append("❌ Credentials SMTP (SMTP_USER / SMTP_PASSWORD) manquants")
    return errors
