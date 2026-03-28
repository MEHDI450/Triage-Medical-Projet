"""
tools.py — Outils MCP du Système de Triage Médical
Simule l'approche Model Context Protocol via CrewAI BaseTool

Outils disponibles :
  1. GoogleSheetsWriterTool  — Écrit une ligne dans le registre Google Sheets
  2. EmailAlertTool          — Envoie un email d'alerte critique via Gmail SMTP
"""

import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Type

import gspread
from google.oauth2.service_account import Credentials
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

import config

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GOOGLE SHEETS TOOL
# ─────────────────────────────────────────────────────────────────────────────

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_HEADERS = [
    "Horodatage",
    "Nom_Patient",
    "Age",
    "Email_Patient",
    "Symptomes",
    "Niveau_Urgence",
    "Statut_Robot",
]


class GoogleSheetsInput(BaseModel):
    """Schéma d'entrée pour l'outil Google Sheets."""

    nom_patient: str = Field(..., description="Nom complet du patient")
    age: str = Field(..., description="Âge du patient")
    email_patient: str = Field(..., description="Email du patient")
    symptomes: str = Field(..., description="Description des symptômes")
    niveau_urgence: str = Field(..., description="ROUGE ou VERT")


class GoogleSheetsWriterTool(BaseTool):
    """
    Outil MCP — Google Sheets
    ─────────────────────────
    Ajoute une ligne de registre dans le Google Sheet de triage médical.
    Crée l'onglet et les en-têtes si nécessaires.
    """

    name: str = "google_sheets_writer"
    description: str = (
        "Enregistre les données d'un patient dans le registre Google Sheets. "
        "Utilise cet outil pour chaque patient traité, que l'urgence soit ROUGE ou VERT."
    )
    args_schema: Type[BaseModel] = GoogleSheetsInput

    def _run(
        self,
        nom_patient: str,
        age: str,
        email_patient: str,
        symptomes: str,
        niveau_urgence: str,
    ) -> str:
        """Exécute l'écriture dans Google Sheets."""
        try:
            # Authentification via compte de service
            creds = Credentials.from_service_account_file(
                config.GOOGLE_CREDENTIALS_PATH, scopes=SHEETS_SCOPES
            )
            client = gspread.authorize(creds)

            # Ouvrir le spreadsheet
            sheet_doc = client.open_by_url(config.GOOGLE_SHEET_URL)

            # Obtenir ou créer l'onglet
            try:
                worksheet = sheet_doc.worksheet(config.SHEET_NAME)
            except gspread.WorksheetNotFound:
                worksheet = sheet_doc.add_worksheet(
                    title=config.SHEET_NAME, rows=1000, cols=len(SHEET_HEADERS)
                )
                # Ajouter les en-têtes
                worksheet.append_row(SHEET_HEADERS)
                logger.info("Onglet '%s' créé avec les en-têtes.", config.SHEET_NAME)

            # Vérifier si les en-têtes existent (première ligne)
            first_row = worksheet.row_values(1)
            if not first_row or first_row[0] != "Horodatage":
                worksheet.insert_row(SHEET_HEADERS, index=1)

            # Préparer la nouvelle ligne
            horodatage = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [
                horodatage,
                nom_patient,
                str(age),
                email_patient,
                symptomes,
                niveau_urgence.upper(),
                "Traité par Agents IA",
            ]

            # Ajouter la ligne au sheet
            worksheet.append_row(new_row)

            result = (
                f"✅ Enregistrement réussi dans Google Sheets.\n"
                f"   Patient : {nom_patient} | Urgence : {niveau_urgence.upper()} | "
                f"Horodatage : {horodatage}"
            )
            logger.info(result)
            return result

        except FileNotFoundError:
            error_msg = (
                f"❌ Fichier credentials Google introuvable : {config.GOOGLE_CREDENTIALS_PATH}. "
                "Vérifiez votre configuration."
            )
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Erreur Google Sheets : {type(e).__name__}: {e}"
            logger.error(error_msg)
            return error_msg


# ─────────────────────────────────────────────────────────────────────────────
# 2. EMAIL ALERT TOOL
# ─────────────────────────────────────────────────────────────────────────────


class EmailAlertInput(BaseModel):
    """Schéma d'entrée pour l'outil Email."""

    nom_patient: str = Field(..., description="Nom complet du patient")
    age: str = Field(..., description="Âge du patient")
    symptomes: str = Field(..., description="Description des symptômes")
    niveau_urgence: str = Field(..., description="ROUGE — niveau d'urgence critique")


class EmailAlertTool(BaseTool):
    """
    Outil MCP — Gmail SMTP
    ──────────────────────
    Envoie un email d'alerte critique UNIQUEMENT pour les patients ROUGE.
    N'utilise PAS cet outil pour les patients VERT.
    """

    name: str = "email_alert_sender"
    description: str = (
        "Envoie un email d'alerte critique à l'équipe médicale. "
        "N'utilise cet outil QUE lorsque le niveau d'urgence est ROUGE. "
        "Ne l'utilise JAMAIS pour les cas VERT."
    )
    args_schema: Type[BaseModel] = EmailAlertInput

    def _run(
        self,
        nom_patient: str,
        age: str,
        symptomes: str,
        niveau_urgence: str,
    ) -> str:
        """Envoie l'email d'alerte via Gmail SMTP."""
        # Sécurité : ne jamais envoyer si pas ROUGE
        if niveau_urgence.upper() != "ROUGE":
            return "⚠️ Email non envoyé : le niveau d'urgence n'est pas ROUGE."

        try:
            # Construire le message HTML
            subject = f"🚨 ALERTE URGENCE CRITIQUE — Patient : {nom_patient}"
            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background: #1a1a2e; color: #e0e0e0; padding: 30px;">
              <div style="max-width: 600px; margin: 0 auto; background: #16213e; border-radius: 12px;
                          border: 2px solid #e74c3c; padding: 30px;">
                <h1 style="color: #e74c3c; text-align: center;">
                  🚨 ALERTE URGENCE CRITIQUE
                </h1>
                <hr style="border-color: #e74c3c;">
                <table style="width: 100%; border-collapse: collapse;">
                  <tr>
                    <td style="padding: 10px; font-weight: bold; color: #aaa;">Nom du Patient</td>
                    <td style="padding: 10px; color: #fff; font-size: 1.1em;">{nom_patient}</td>
                  </tr>
                  <tr style="background: #0f3460;">
                    <td style="padding: 10px; font-weight: bold; color: #aaa;">Âge</td>
                    <td style="padding: 10px; color: #fff;">{age} ans</td>
                  </tr>
                  <tr>
                    <td style="padding: 10px; font-weight: bold; color: #aaa;">Symptômes</td>
                    <td style="padding: 10px; color: #ff6b6b; font-style: italic;">{symptomes}</td>
                  </tr>
                  <tr style="background: #0f3460;">
                    <td style="padding: 10px; font-weight: bold; color: #aaa;">Niveau d'Urgence</td>
                    <td style="padding: 10px;">
                      <span style="background: #e74c3c; color: white; padding: 4px 12px;
                                   border-radius: 20px; font-weight: bold;">
                        🔴 ROUGE — CRITIQUE
                      </span>
                    </td>
                  </tr>
                </table>
                <hr style="border-color: #e74c3c; margin-top: 20px;">
                <p style="color: #e74c3c; text-align: center; font-weight: bold; font-size: 1.1em;">
                  ⚠️ ACTION IMMÉDIATE REQUISE — Ce patient nécessite une prise en charge d'urgence.
                </p>
                <p style="color: #888; font-size: 0.8em; text-align: center;">
                  Message généré automatiquement par le Système de Triage Médical IA<br>
                  {datetime.now().strftime("%d/%m/%Y à %H:%M:%S")}
                </p>
              </div>
            </body>
            </html>
            """

            # Construire l'email MIME
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = config.SMTP_USER
            msg["To"] = config.ALERT_EMAIL
            msg.attach(MIMEText(html_body, "html", "utf-8"))

            # Envoyer via Gmail SMTP avec TLS
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.sendmail(config.SMTP_USER, config.ALERT_EMAIL, msg.as_string())

            result = (
                f"✅ Email d'alerte critique envoyé avec succès.\n"
                f"   Destinataire : {config.ALERT_EMAIL}\n"
                f"   Patient : {nom_patient} | Urgence : ROUGE"
            )
            logger.info(result)
            return result

        except smtplib.SMTPAuthenticationError:
            error_msg = (
                "❌ Erreur d'authentification SMTP. "
                "Vérifiez SMTP_USER et SMTP_PASSWORD dans votre .env. "
                "Utiliser un 'App Password' Gmail, pas votre mot de passe habituel."
            )
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"❌ Erreur envoi email : {type(e).__name__}: {e}"
            logger.error(error_msg)
            return error_msg
