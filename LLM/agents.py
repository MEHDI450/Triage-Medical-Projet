"""
agents.py — Définition des 3 Agents CrewAI du Système de Triage Médical

Agents :
  1. patient_intake_agent    — Collecte et structure les données patient
  2. triage_evaluator_agent  — Expert médical : décision ROUGE/VERT
  3. action_alert_agent      — Coordinateur : Google Sheets + Email
"""

import os
from crewai import Agent, LLM

import config
from MCP.tools import GoogleSheetsWriterTool, EmailAlertTool

# ─────────────────────────────────────────────────────────────────────────────
# Initialisation du LLM Gemini 2.5 Flash via l'interface native CrewAI
# ─────────────────────────────────────────────────────────────────────────────

# LiteLLM (utilisé par CrewAI) lit la variable d'environnement GEMINI_API_KEY
os.environ["GEMINI_API_KEY"] = config.GOOGLE_API_KEY

llm = LLM(
    model=f"gemini/{config.GEMINI_MODEL}",
    api_key=config.GOOGLE_API_KEY,
    temperature=0.1
)

# ─────────────────────────────────────────────────────────────────────────────
# Instanciation des outils
# ─────────────────────────────────────────────────────────────────────────────

sheets_tool = GoogleSheetsWriterTool()
email_tool = EmailAlertTool()


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1 : Patient Intake Agent (Agent d'Accueil)
# ─────────────────────────────────────────────────────────────────────────────

def create_intake_agent() -> Agent:
    """
    Crée l'agent d'accueil patient.
    Rôle : Recevoir et structurer les données brutes du formulaire Streamlit
           en un JSON propre et validé pour le pipeline suivant.
    """
    return Agent(
        role="Agent d'Accueil Patient",
        goal=(
            "Récupérer les informations du patient depuis le formulaire, "
            "les valider et les structurer dans un format JSON propre et standardisé "
            "prêt à être analysé par l'expert médical."
        ),
        backstory=(
            "Tu es un agent d'accueil médical expert en collecte et structuration de données. "
            "Tu travailles à l'entrée d'un service d'urgences et ton rôle est d'enregistrer "
            "avec précision les informations des patients qui se présentent. "
            "Tu es rigoureux, bienveillant et tu t'assures que chaque information est "
            "correctement structurée avant de la transmettre aux médecins."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
    )


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2 : Triage Evaluator Agent (Expert Médical)
# ─────────────────────────────────────────────────────────────────────────────

def create_triage_agent() -> Agent:
    """
    Crée l'agent expert médical de triage.
    Rôle : Analyser strictement les symptômes et répondre uniquement ROUGE ou VERT.
    """
    return Agent(
        role="Expert Médical de Triage",
        goal=(
            "Analyser les symptômes du patient et déterminer le niveau d'urgence. "
            "Répondre UNIQUEMENT par 'ROUGE' ou 'VERT', sans aucun autre texte."
        ),
        backstory=(
            "Tu es un expert médical de triage avec 20 ans d'expérience aux urgences. "
            "Tu es formé aux protocoles internationaux de triage (START, Manchester). "
            "Ta règle absolue : si les symptômes indiquent une urgence critique "
            "(douleur au thorax, sang, difficulté à respirer, perte de conscience, "
            "accident vasculaire, brûlures graves), tu réponds UNIQUEMENT 'ROUGE'. "
            "Pour tout autre symptôme moins urgent, tu réponds UNIQUEMENT 'VERT'. "
            "Tu ne donnes JAMAIS d'explication, JAMAIS de conseil médical, "
            "JAMAIS d'autre texte que le mot ROUGE ou VERT."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=2,  # Limité pour forcer une réponse directe
    )


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3 : Action & Alert Agent (Agent Coordinateur)
# ─────────────────────────────────────────────────────────────────────────────

def create_coordinator_agent() -> Agent:
    """
    Crée l'agent coordinateur d'actions.
    Rôle : Exécuter les actions post-triage via les outils Google Sheets et Email.
    """
    return Agent(
        role="Agent Coordinateur d'Actions Médicales",
        goal=(
            "Exécuter les actions requises après le triage : "
            "1) Toujours enregistrer le patient dans Google Sheets. "
            "2) Envoyer un email d'alerte critique UNIQUEMENT si le niveau est ROUGE."
        ),
        backstory=(
            "Tu es le coordinateur du système de triage médical automatisé. "
            "Tu as accès à deux outils puissants : l'enregistrement dans Google Sheets "
            "et l'envoi d'emails d'alerte. "
            "Ton protocole est strict : "
            "- TOUJOURS utiliser google_sheets_writer pour chaque patient. "
            "- Utiliser email_alert_sender SEULEMENT si le niveau d'urgence est ROUGE. "
            "- Ne jamais envoyer d'email pour les cas VERT. "
            "Tu es responsable de la traçabilité et de la réactivité du service."
        ),
        llm=llm,
        tools=[sheets_tool, email_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )
