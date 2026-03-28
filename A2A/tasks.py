"""
tasks.py — Définition des 3 Tâches CrewAI du Système de Triage Médical

Tâches :
  1. Intake Task       — Analyse et structuration JSON par l'Agent 1
  2. Triage Task       — Évaluation stricte (ROUGE/VERT) par l'Agent 2
  3. Action & Alert Task — Exécution (Sheets/Email) par l'Agent 3
"""

from crewai import Task
from textwrap import dedent


def create_intake_task(agent, patient_data: dict) -> Task:
    """
    Crée la tâche d'accueil.
    Entrée : Données brutes du formulaire (patient_data).
    Sortie attendue : Un string formaté proprement avec ces infos.
    """
    return Task(
        description=dedent(
            f"""
            Voici les informations reçues d'un nouveau patient aux urgences :
            - Nom : {patient_data['nom']}
            - Âge : {patient_data['age']}
            - Email : {patient_data['email']}
            - Symptômes décrits : {patient_data['symptomes']}

            Ta mission :
            1. Lire et vérifier ces informations.
            2. Les structurer clairement pour l'expert médical.
            3. Produire un résumé JSON valide contenant ces 4 clés exactes : 
               'nom', 'age', 'email', 'symptomes'.
            """
        ),
        expected_output=(
            "Un bloc JSON valide contenant strictement les clés : "
            "'nom', 'age', 'email', 'symptomes' avec les valeurs du patient."
        ),
        agent=agent,
    )


def create_triage_task(agent) -> Task:
    """
    Crée la tâche de triage médical.
    Entrée implicite : Le JSON (ou texte) généré par la tâche précédente.
    Sortie attendue : Le mot "ROUGE" ou "VERT".
    """
    return Task(
        description=dedent(
            """
            L'agent d'accueil vient de te transmettre les données structurées d'un patient.
            Lis attentivement les symptômes décrits dans le texte précédent.

            Rappel strict de ta consigne :
            - Urgence CRITIQUE (douleur thoracique, sang, difficulté respiratoire grave, etc) = ROUGE
            - Urgence NON CRITIQUE (mal de tête, douleur légère, fièvre modérée, etc) = VERT

            Applique ton expertise de triage.
            """
        ),
        expected_output=(
            "UN SEUL ET UNIQUE MOT. Soit 'ROUGE', soit 'VERT'. "
            "Aucun autre texte, explication ou ponctuation."
        ),
        agent=agent,
    )


def create_action_task(agent, patient_data: dict) -> Task:
    """
    Crée la tâche de coordination et d'actions (Outils MCP).
    Entrée explicite : Données du patient + Entrée implicite (résultat ROUGE/VERT de Tâche 2).
    """
    return Task(
        description=dedent(
            f"""
            L'expert médical (Tâche précédente) a rendu son verdict. 
            Le niveau d'urgence est soit "ROUGE" soit "VERT".

            Données du patient à utiliser :
            - Nom : {patient_data['nom']}
            - Âge : {patient_data['age']}
            - Email : {patient_data['email']}
            - Symptômes : {patient_data['symptomes']}

            Actions obligatoires à exécuter MAINTENANT :
            1. Utilise l'outil `google_sheets_writer` pour enregistrer le patient avec 
               son niveau d'urgence (le résultat de la tâche précédente).
            2. SI (et seulement si) le niveau d'urgence est ROUGE, utilise ENSUITE l'outil 
               `email_alert_sender` pour envoyer une alerte critique.

            Ne termine pas cette tâche tant que l'enregistrement Google Sheets n'a pas été confirmé.
            """
        ),
        expected_output=(
            "Un rapport textuel confirmant que l'enregistrement Google Sheets a été effectué, "
            "et précisant si un email d'alerte a été envoyé (uniquement si ROUGE)."
        ),
        agent=agent,
    )
