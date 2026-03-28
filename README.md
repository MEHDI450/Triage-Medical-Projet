# 🏥 Système de Triage Médical Multi-Agents

Ce projet est une application web de triage médical autonome basée sur l'intelligence artificielle. Il utilise une architecture Agent-to-Agent (A2A) orchestrée par **CrewAI**, paramétrée avec le modèle cognitif **Gemini 2.5 Flash**, et dotée d'outils externes (Google Sheets, Gmail) simulant une intégration MCP (Model Context Protocol). L'interface utilisateur est développée avec **Streamlit**.

---

## 🏗 Architecture Multi-Agents

1. **Patient Intake Agent** : Collecte et structure les données du formulaire Streamlit sous forme de JSON robuste.
2. **Triage Evaluator Agent** : Expert médical qui analyse les symptômes et rend un verdict binaire strict : `ROUGE` ou `VERT`.
3. **Action & Alert Agent** : L'agent coordinateur qui enregistre tous les patients dans le registre Google Sheets et déclenche une alerte critique par Email si l'urgence est `ROUGE`.

---

## 🚀 Lancement Local — Étape par Étape

### 1. Prérequis
- **Python 3.10+** ou supérieur.
- Un compte **Google Cloud** pour l'accès aux APIs (Gemini & Sheets).
- Un accès à un compte **Gmail** pour l'envoi des alertes.

### 2. Installations des dépendances
Ouvrez votre terminal à la racine du projet et exécutez la commande suivante :
```bash
pip install -r requirements.txt
```

### 3. Configuration de l'environnement
Un fichier template nommé `.env.example` se trouve à la racine.
1. Créez une copie de ce fichier et nommez-la `.env`.
2. Complétez chaque variable à l'intérieur :

#### `GOOGLE_API_KEY`
Allez sur [Google AI Studio](https://aistudio.google.com/) et générez votre clé API.

#### Google Sheets 
1. Créez un projet sur la [Google Cloud Console](https://console.cloud.google.com/).
2. Activez l'API **Google Sheets API** et **Google Drive API**.
3. Créez des identifiants (Compte de service). Générez une nouvelle clé et téléchargez le fichier JSON.
4. Dans votre projet local, créez un dossier `credentials` et placez-y le JSON sous le nom `google_credentials.json`.
5. Ouvrez Google Sheets, créez un document vide.
6. **Important** : Partagez ce document avec l'adresse email du compte de service ("*@*.iam.gserviceaccount.com") en tant qu'**Éditeur**.
7. Copiez l'URL de votre Google Sheet et collez-la pour `GOOGLE_SHEET_URL` dans votre fichier `.env`.

#### Alertes Email (Gmail)
1. Activez la [Validation en deux étapes](https://myaccount.google.com/security) sur votre compte Google (SMTP_USER).
2. Rendez-vous dans **Mots de passe d'application** et créez-en un pour "Mail".
3. Récupérez le mot de passe de 16 caractères et mettez-le dans `SMTP_PASSWORD` dans le `.env`.

### 4. Démarrer l'application Streamlit

Une fois configuré, lancez le serveur Streamlit avec la commande suivante :
```bash
streamlit run app.py
```

Votre navigateur ouvrira automatiquement l'application sur [http://localhost:8501](http://localhost:8501).

---

## 🧪 Tests Rapides

- **Cas Vert (Non critique)** : _"Je me sens faible et j'ai des frissons légers depuis ce matin."_
  - _Résultat attendu_ : Enregistrement dans Google Sheets. (Pas d'email).
- **Cas Rouge (Critique)** : _"J'ai une douleur atroce dans la poitrine et mon bras gauche s'engourdit, je peine à respirer."_
  - _Résultat attendu_ : Alerte envoyée par e-mail et enregistrement dans Google Sheets.
