"""
crew.py — Orchestration du Système de Triage Multi-Agents.
Définit la 'Crew' qui exécute séquentiellement les tâches des agents.
"""

from crewai import Crew, Process
import logging

from LLM.agents import (
    create_intake_agent,
    create_triage_agent,
    create_coordinator_agent,
)
from A2A.tasks import (
    create_intake_task,
    create_triage_task,
    create_action_task,
)

logger = logging.getLogger(__name__)


def run_triage_crew(patient_data: dict) -> tuple[str, str]:
    """
    Assemble les agents et les tâches, et lance l'exécution de la Crew.
    Retourne l'état de l'urgence (ROUGE/VERT) et la trace d'exécution pour l'interface.
    """
    logger.info("⚡ Lancement de la Crew de Triage Médical...")

    # 1. Instancier les Agents
    intake_agent = create_intake_agent()
    triage_agent = create_triage_agent()
    coordinator_agent = create_coordinator_agent()

    # 2. Instancier les Tâches
    intake_task = create_intake_task(intake_agent, patient_data)
    triage_task = create_triage_task(triage_agent)
    action_task = create_action_task(coordinator_agent, patient_data)

    # 3. Créer la Crew
    # Mode séquentiel : Intake -> Triage -> Action
    triage_crew = Crew(
        agents=[intake_agent, triage_agent, coordinator_agent],
        tasks=[intake_task, triage_task, action_task],
        process=Process.sequential,
        verbose=True,
    )

    # 4. Exécuter le processus
    try:
        # Lance la Crew
        result = triage_crew.kickoff()

        # Extraire le niveau d'urgence évalué par l'Agent 2
        # La sortie de TriageTask (Tâche 2) est l'évaluation ROUGE/VERT
        niveau_urgence = triage_task.output.raw.strip().upper()
        
        # S'assurer qu'il s'agit bien de ROUGE ou VERT, sinon fallback à un message d'erreur d'analyse
        if "ROUGE" in niveau_urgence:
            niveau_urgence = "ROUGE"
        elif "VERT" in niveau_urgence:
            niveau_urgence = "VERT"
        else:
            niveau_urgence = f"ERREUR_ANALYSE: {niveau_urgence}"

        # Rapport final
        trace = result.raw
        logger.info(f"✅ Exécution de la Crew terminée. Urgence : {niveau_urgence}")

        return niveau_urgence, trace

    except Exception as e:
        error_msg = f"❌ Erreur critique lors de l'exécution des agents : {str(e)}"
        logger.error(error_msg)
        return "ERREUR", error_msg
