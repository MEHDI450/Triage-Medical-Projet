"""
app.py — Interface Web du Système de Triage Médical Multi-Agents
(Streamlit - Frontend Premium & Dynamique)
"""

import streamlit as st
import time
import uuid
import logging

# Configurer la journalisation de base
logging.basicConfig(level=logging.INFO)

# Importation de la vérification de configuration (charge le .env en premier)
from config import validate_config
# L'importation de CrewAI est décalée plus bas, après la validation de la configuration

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Triage Médical Intel IA",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- CSS / DESIGN PREMIUM ---
def set_custom_css():
    st.markdown(
        """
        <style>
        /* Thème sombre global de la page */
        .stApp {
            background-color: #0f1015;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
        }
        
        /* Conteneur principal style carte "glassmorphism" */
        .main-container {
            background: rgba(30, 41, 59, 0.7);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        
        /* Titre Header */
        h1 {
            background: -webkit-linear-gradient(45deg, #00f2fe, #4facfe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 0.5rem;
        }

        h3 {
            color: #94a3b8;
            font-weight: 500;
        }
        
        /* Bouton "Analyser" Premium */
        div.stButton > button {
            width: 100%;
            background-image: linear-gradient(to right, #4facfe 0%, #00f2fe 100%);
            color: white;
            font-weight: bold;
            font-size: 1.1rem;
            border-radius: 8px;
            border: none;
            padding: 0.75rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 242, 254, 0.4);
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 242, 254, 0.6);
            color: white;
            border-color: transparent;
        }
        div.stButton > button:active {
            transform: translateY(0px);
        }
        
        /* Style des zones d'alerte */
        .alert-rouge {
            background: linear-gradient(135deg, #7f1d1d, #ef4444);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            border: 2px solid #f87171;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.5);
            animation: pulse-red 2s infinite;
        }
        .alert-vert {
            background: linear-gradient(135deg, #14532d, #22c55e);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            font-size: 1.5rem;
            font-weight: bold;
            border: 2px solid #4ade80;
            box-shadow: 0 0 20px rgba(34, 197, 94, 0.4);
        }
        
        /* Animations */
        @keyframes pulse-red {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
            70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        
        /* Lignes de Status Streamlit Custom */
        .stStatus {
            background: rgba(15, 23, 42, 0.7) !important;
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

set_custom_css()

# --- INITIALISATION SESSION STATE ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- VALIDATION DE CONFIGURATION ---
config_errors = validate_config()

# HEADER
st.markdown("<h1>🏥 A2A Triage Médical Automatisé</h1>", unsafe_allow_html=True)
st.markdown("<h3>Orchestration Multi-Agents via CrewAI & Gemini 2.5</h3>", unsafe_allow_html=True)

if config_errors:
    st.error("🚨 Erreur de configuration détectée. L'application ne peut pas fonctionner.")
    for err in config_errors:
        st.warning(err)
    st.info("Vérifiez votre fichier `.env` à l'aide de `.env.example`.")
    st.stop()

# Importation de la fonction CrewAI (APRES la validation de configuration pour éviter le crash Pydantic si la clé est vide)
from A2A.crew import run_triage_crew

# --- FORMULAIRE PRINCIPAL ---
st.markdown('<div class="main-container">', unsafe_allow_html=True)

with st.form(key="patient_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        nom_patient = st.text_input("Nom Complet du Patient", placeholder="Ex: Jean Dupont")
        age_patient = st.number_input("Âge", min_value=0, max_value=120, value=35, step=1)
    with col2:
        email_patient = st.text_input("Email de Contact", placeholder="jean.dupont@email.com")

    symptomes = st.text_area(
        "Description des Symptômes (Précise le motif de la visite)",
        placeholder="Ex: Douleur vive à la poitrine depuis 30 minutes, difficulté à respirer... ou simplement un léger mal de tête.",
        height=150,
    )

    submit_button = st.form_submit_button("Lancer l'Analyse Multi-Agents 🚀")

st.markdown('</div>', unsafe_allow_html=True)

# --- EXÉCUTION DE L'ANALYSE ---
if submit_button:
    if not nom_patient or not symptomes:
        st.error("⚠️ Veuillez renseigner au minimum le nom et les symptômes.")
    else:
        patient_data = {
            "nom": nom_patient,
            "age": str(age_patient),
            "email": email_patient if email_patient else "Non fourni",
            "symptomes": symptomes,
            "id": str(uuid.uuid4())[:8],
        }

        # Expérience d'attente détaillée / Statut
        with st.status("🤖 Orchestration Multi-Agents en cours...", expanded=True) as status:
            
            st.write("🔄 **Agent 1** : Collecte et structuration des données...")
            time.sleep(1) # Simulation de UX
            
            st.write("⚕️ **Agent 2** : Évaluation stricte des symptômes par l'Expert Médical...")
            
            # Appel asynchrone / bloquant de la logique backend 
            try:
                niveau_urgence, raw_trace = run_triage_crew(patient_data)
                
                st.write(f"⚙️ **Agent 3** : Exécution des outils MCP (Google Sheets / Email)...")
                
                status.update(label="✅ Traitement Multi-Agents terminé !", state="complete", expanded=False)
                
                # --- AFFICHAGE DU RÉSULTAT ---
                st.markdown("---")
                if niveau_urgence == "ROUGE":
                    st.markdown(
                        f"""
                        <div class="alert-rouge">
                            🚨 URGENCE CRITIQUE (ROUGE)<br>
                            <span style="font-size: 1rem; font-weight:normal;">Un email a été envoyé à l'équipe, et le patient a été enregistré dans Google Sheets.</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif niveau_urgence == "VERT":
                    st.markdown(
                        f"""
                        <div class="alert-vert">
                            🟢 URGENCE NON CRITIQUE (VERT)<br>
                            <span style="font-size: 1rem; font-weight:normal;">Patient enregistré dans Google Sheets pour suivi standard.</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.error(f"⚠️ Erreur lors de l'analyse. Résumé reçu : {niveau_urgence}")
                
                # Afficher le résumé complet pour les "Logs" (Pour les développeurs et la transparence IA)
                with st.expander("Voir le rapport détaillé de l'Agent Coordinateur"):
                    st.write(raw_trace)
                
                # Sauvegarder dans l'historique
                st.session_state.history.insert(0, {
                    "nom": patient_data["nom"],
                    "symptomes": patient_data["symptomes"],
                    "urgence": niveau_urgence,
                    "date": time.strftime("%H:%M:%S")
                })
                
            except Exception as e:
                status.update(label="❌ Échec de l'analyse", state="error", expanded=True)
                st.error(f"Erreur technique : {e}")


# --- HISTORIQUE DE SESSION ---
if st.session_state.history:
    st.markdown("### 📋 Historique de Session")
    
    for h in st.session_state.history[:5]: # Mostrar los ultimos 5
        color = "#ef4444" if h["urgence"] == "ROUGE" else "#22c55e"
        icon = "🔴" if h["urgence"] == "ROUGE" else "🟢"
        
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.5); padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {color};">
                <strong>{icon} {h['nom']}</strong> - {h['date']}<br>
                <span style="color: #94a3b8; font-size: 0.9rem;">Symptômes: {h['symptomes'][:60]}...</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
