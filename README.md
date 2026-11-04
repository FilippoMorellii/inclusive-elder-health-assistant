# Elder Health Assistant 🩺👵👴

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Telegram Bot API](https://img.shields.io/badge/python--telegram--bot-v21.6-0088cc.svg?logo=telegram&logoColor=white)](https://python-telegram-bot.org/)
[![AI Model](https://img.shields.io/badge/Google%20Gemini-2.5%20Flash-orange.svg?logo=google&logoColor=white)](https://ai.google.dev/)
[![Database](https://img.shields.io/badge/SQLAlchemy-SQLite-red.svg?logo=sqlite&logoColor=white)](https://www.sqlalchemy.org/)
[![Course](https://img.shields.io/badge/Course-Inclusive%20Digital%20Technologies-success.svg)](#about-the-project)
[![Academic Year](https://img.shields.io/badge/Academic%20Year-2025%2F2026-lightgrey.svg)](#team--credits)

> **An inclusive, accessible conversational assistant designed with and for older adults and their caregivers.**  
> Built as a university capstone project for the **Inclusive Digital Technologies** course (A.Y. 2025/2026) by team **Designed4U**.

---

## 📌 Table of Contents

- [Overview & The Challenge](#-overview--the-challenge)
- [The Inclusive Design Process](#-the-inclusive-design-process)
  - [Target Personas](#target-personas)
  - [Customer Journey Mapping](#customer-journey-mapping)
  - [Nielsen Usability Heuristics for Elderly Users](#nielsen-usability-heuristics-for-elderly-users)
  - [User Validation & TAM Evaluation](#user-validation--tam-evaluation)
- [Key Features](#-key-features)
- [System Architecture & Tech Stack](#-system-architecture--tech-stack)
- [Database Schema](#-database-schema)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Configuration (.env)](#-configuration-env)
- [Usage Guide](#-usage-guide)
- [Presentation & Assets](#-presentation--assets)
- [Team & Credits](#-team--credits)
- [Ethical & Medical Disclaimer](#-ethical--medical-disclaimer)

---

## 💡 Overview & The Challenge

As people age, polypharmacy (managing multiple medications daily) becomes frequent. However, existing health apps are often complex, feature-heavy, and not suited for elderly cognitive and visual ergonomics.

### Identified Exclusion Barriers:
1. **Cognitive Decline & Autonomy Loss**: Forgetting whether a pill was taken, leading to dangerous missed doses or accidental double dosages.
2. **Poor Leaflet Legibility**: Package leaflets ("bugiardini") feature microscopic fonts and convoluted pharmacological jargon that generate anxiety, confusion, and cognitive overload.
3. **Fragmented Organization**: Relying on uncoordinated paper notes, alarms, and mental reminders.
4. **The Caregiver Dilemma**: Family members and caregivers worry constantly and need to stay informed, yet over-monitoring can infringe on the older person's sense of dignity and independence.

### Our Solution:
**Elder Health Assistant** is a lightweight, accessible Telegram bot that transforms complex medication regimens into a friendly, barrier-free conversational experience. It bridges the gap between older adults and their caregivers through:
- Scheduled reminders with double-confirmation error prevention.
- One-click batch confirmations to eliminate notification fatigue.
- Automated escalation notifications to the caregiver if doses are missed.
- An AI-powered **Smart Leaflet** (using **Google Gemini 2.5 Flash**) that summarizes medicine leaflets into plain, friendly language and answers doubts under strict clinical guardrails.

---

## 🎨 The Inclusive Design Process

The project followed human-centered and participatory design methodologies.

### Target Personas
Based on semi-structured interviews with 4 older adults (ages 64–87, intermediate digital literacy):

| Persona | Demographics & Traits | Primary Barriers & Needs |
|---|---|---|
| **Concetta (72)** | Retired seamstress, habitual, self-reliant | Low vision, struggles with small print, values autonomy without feeling like a burden. |
| **Ettore (75)** | Retired teacher, sociable, forgetful | Loses track of medication details, needs structured reassurance and family support. |

### Customer Journey Mapping
We mapped the end-to-end journey across four phases:
1. **Prescription**: Doctor prescribes a new medication.
2. **Understanding**: Reading the leaflet, understanding posology and contraindications.
3. **Preparation**: Organizing schedules and pills.
4. **Administration**: Taking the medicine at the right time and recording intake.

### Nielsen Usability Heuristics for Elderly Users
Every interaction was audited against Jakob Nielsen's 10 Usability Heuristics and tailored for older adults:

- **Visibility of System Status (#1)**: Clear visual feedback such as *"AI is thinking..."* during leaflet processing and status tags for pending/confirmed medications.
- **Match Between System and Real World (#2)**: Natural conversational tone, plain Italian/English terms instead of technical jargon, and intuitive emojis (💊, ⏰, 👨‍👩‍👦).
- **User Control & Freedom (#3)**: Unobtrusive *Snooze* option (e.g. 15-minute delay) and easy cancellation workflows.
- **Error Prevention (#5)**: 
  - **Double Confirmation Workflow**: Prevents accidental button presses when confirming medication intake.
  - **Batch "Confirm All"**: Reduces alert fatigue for users taking multiple pills at once.
- **Recognition Rather Than Recall (#6)**: Persistent inline menus, pre-filled options, and list displays so users never have to memorize commands.
- **Aesthetic & Minimalist Design (#8)**: Elimination of visual clutter by dynamically disabling outdated inline keyboards, keeping interactive elements anchored within the thumb zone.
- **Help Users Recognize and Recover from Errors (#9)**: Forgiving time and dosage validators providing contextual format examples (e.g. `HH:MM`, `08:30`).

### User Validation & TAM Evaluation
Tested with 5 participants across 3 core task scenarios:
1. Setting up a daily medication reminder.
2. Consulting an AI leaflet for side effects.
3. Linking a family caregiver account.

Results evaluated through the **Technology Acceptance Model (TAM)** demonstrated high **Perceived Usefulness (avg. ~4.2 / 5)**, positive **Behavioral Intention (avg. ~3.9 / 5)**, and actionable qualitative insights that shaped future roadmaps (e.g., voice note support and Alexa integration).

---

## ⚡ Key Features

- ⏰ **Smart Medication Scheduler**: Daily reminders scheduled via Telegram's asynchronous `JobQueue` based on local timezone (`Europe/Rome`).
- 💊 **Dual-Confirmation & Batch Action**:
  - Individual pill confirmation or one-tap **"Confirm All"**.
  - Confirmation safety modal (*"Are you sure you took your medication?"*).
- 🤝 **Caregiver Connection & Safety Escalation**:
  - Secure 6-character alphanumeric pairing token (e.g. `M659Z2`).
  - Real-time escalation: If an elder fails to confirm a scheduled dose within `CAREGIVER_TIMEOUT_MINUTES`, the caregiver automatically receives an urgent alert with medication details.
  - Caregiver view: Caregivers can inspect the assisted person's active medication list remotely.
- 📖 **Smart AI Leaflet (Bugiardino Intelligente)**:
  - Powered by **Google Gemini 2.5 Flash**.
  - Generates plain-language summaries (uses, how to take, common side effects).
  - Quick action buttons for key points and posology.
  - Interactive Q&A with strict safety prompts (cautious pharmaceutical tone, disclaimers, medical doctor referral).
- 🌐 **Multilingual (i18n)**: Full native localization in **Italian** and **English**, switchable on the fly from the main menu.
- 🛡️ **UI Safety & State Hygiene**: Automatically neutralizes expired or superseded message keyboards to prevent out-of-order execution or duplicate database entries.

---

## 🛠 System Architecture & Tech Stack

```
                          ┌───────────────────────────┐
                          │   Elder & Caregiver Users │
                          └─────────────┬─────────────┘
                                        │
                                Telegram App
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │    python-telegram-bot    │
                          │   (Async Polling / Webhook│
                          │        + JobQueue)        │
                          └──────┬─────────────┬──────┘
                                 │             │
                    ┌────────────┘             └────────────┐
                    ▼                                       ▼
        ┌───────────────────────┐               ┌───────────────────────┐
        │   Google Gemini API   │               │   SQLAlchemy + SQLite │
        │   (gemini-2.5-flash)  │               │   elder_assistant.db  │
        │ Smart Patient Leaflet │               │ Users, Meds, Logs     │
        └───────────────────────┘               └───────────────────────┘
```

- **Language**: Python 3.11+
- **Bot Framework**: [`python-telegram-bot` v21.6](https://github.com/python-telegram-bot/python-telegram-bot) with `job-queue`
- **Generative AI**: [`google-genai`](https://pypi.org/project/google-genai/) (Gemini 2.5 Flash API)
- **Database & ORM**: [`SQLAlchemy`](https://www.sqlalchemy.org/) with SQLite
- **Web Server (Optional Webhook)**: [`Flask`](https://palletsprojects.com/p/flask/)
- **Configuration**: [`python-dotenv`](https://pypi.org/project/python-dotenv/)

---

## 🗄 Database Schema

The database consists of three relational models (`app/db.py`):

1. **`User`**:
   - `telegram_id` (Primary Key): Telegram unique user identifier.
   - `first_name`: User's display name.
   - `language`: Preferred language (`it` or `en`, default: `it`).
   - `caregiver_telegram_id`: ForeignKey / ID of the paired caregiver (if any).
   - `pairing_token`: Unique 6-character token for pairing.

2. **`Medication`**:
   - `id` (Primary Key): Auto-incrementing identifier.
   - `user_id`: ForeignKey referencing `User.telegram_id`.
   - `name`: Name of the medication (e.g. *Cardioaspirina*).
   - `dosage`: Prescribed dosage (e.g. *1 compressa*).
   - `time_to_take`: Time formatted as `HH:MM` (e.g. `08:30`).

3. **`MedicationLog`**:
   - `id` (Primary Key): Record identifier.
   - `medication_id`: ForeignKey referencing `Medication.id`.
   - `scheduled_time`: Timestamp of the scheduled dose.
   - `confirmed`: Boolean flag indicating if the elder confirmed intake.
   - `confirmed_at`: Timestamp of confirmation.
   - `caregiver_notified`: Boolean flag tracking whether an escalation alert was dispatched.

---

## 📁 Project Structure

```
elder-health-assistant/
├── app/
│   ├── handlers/
│   │   ├── __init__.py          # Handler exports and aggregation
│   │   ├── ai_leaflet.py        # Gemini AI smart leaflet assistant & Q&A
│   │   ├── caregiver.py         # Caregiver pairing, menu & escalation flow
│   │   ├── help.py              # Main menu and command help
│   │   ├── lista.py             # Medication list views (elder & caregiver)
│   │   ├── medication.py        # Add medication conversation handler
│   │   ├── modifica.py          # Edit and delete medication routines
│   │   ├── reminder.py          # Scheduled jobs, confirmations, snooze & escalation
│   │   └── start.py             # /start command & user onboarding
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── dosage_validators.py # Validation for dosage text input
│   │   ├── locales.py           # Bilingual dictionary (Italian & English)
│   │   ├── logger.py            # Centralized logging configuration
│   │   ├── time_validators.py   # HH:MM time format validation
│   │   └── ui.py                # Inline keyboard cleanup & active keyboard tracker
│   ├── config.py                # Environment variable loader & validations
│   ├── db.py                    # SQLAlchemy engine, declarative models & session
│   └── __init__.py
├── .env.example                 # Template for required environment variables
├── .gitignore                   # Comprehensive git ignore file
├── flask_app.py                 # Optional webhook runner for production (e.g. PythonAnywhere)
├── main.py                      # Main entrypoint (long-polling mode + job scheduler)
├── requirements.txt             # Python project dependencies
├── README.md                    # Project documentation
└── IDT - Elder Health Assistant - Final Presentation.pdf  # Academic presentation slides
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11 or higher
- A Telegram account and a bot token obtained from [@BotFather](https://t.me/BotFather)
- A Google Gemini API key obtained from [Google AI Studio](https://aistudio.google.com/)

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/elder-health-assistant.git
cd elder-health-assistant
```

### 2. Set Up a Virtual Environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the template file to `.env`:
```bash
cp .env.example .env
```
Edit `.env` with your preferred editor and insert your actual credentials:
```env
TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
GEMINI_API_KEY="your_gemini_api_key_here"
LOG_LEVEL="INFO"
CAREGIVER_TIMEOUT_MINUTES=15
```

---

## ⚙️ Configuration (.env)

| Variable | Type | Default | Description |
|---|---|---|---|
| `TELEGRAM_BOT_TOKEN` | String | *Required* | API token generated via Telegram's @BotFather. |
| `GEMINI_API_KEY` | String | *Required* | Google Gemini API key for the Smart Leaflet feature. |
| `LOG_LEVEL` | String | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `CAREGIVER_TIMEOUT_MINUTES` | Integer | `15` | Minutes to wait for medication confirmation before triggering caregiver escalation. |

---

## 💻 Usage Guide

### Running in Long-Polling Mode (Recommended for Development)
```bash
python main.py
```
*Expected log output:*
```
INFO - Starting Elder Health Assistant bot...
INFO - Reminder ripristinato user=... orario=08:30
INFO - Bot is running. Press Ctrl+C to stop.
INFO - Application started
```

### Running with Webhook (Flask Deployment)
For cloud hosting platforms like PythonAnywhere, Heroku, or VPS:
```bash
python flask_app.py
```

### Bot Commands & Navigation
- `/start` - Initial onboarding, registers user in database, presents welcome message.
- `/help` - Displays the main interactive navigation menu.
- `/lista` - Shows the user's active medication routine.
- **Interactive UI**:
  - 📋 **My Meds List**: View, add, edit, or delete scheduled medications.
  - 📖 **Smart Leaflet**: Ask Gemini for clear leaflet explanations or dosage guides.
  - 👨‍👩‍👦 **Caregiver Management**: Generate a 6-character connection code or enter a loved one's code.
  - 🌐 **Change Language**: Switch instantly between Italian and English.

---

## 📊 Presentation & Assets

The complete academic presentation detailing the research methodology, persona studies, journey maps, heuristics evaluation, and user testing metrics is included directly in this repository:

📄 **[Download / View Presentation PDF](./IDT%20-%20Elder%20Health%20Assistant%20-%20Final%20Presentation.pdf)**

---

## 👥 Team & Credits

Developed with ❤️ by **Team Designed4U**:

- **Giuseppe Anzillotti** - Computer Science Engineering
- **Susanna Lo Cascio** - Computer Science Engineering
- **Filippo Morelli** - Computer Science Engineering
- **Vincenzo Picone** - Computer Science Engineering
- **Gaia Scherini** - Digital and Interaction Design

*Course: Inclusive Digital Technologies — Academic Year 2025/2026*

---

## ⚖️ Ethical & Medical Disclaimer

> **Important**: This application was developed strictly for academic and research purposes within an Inclusive Design curriculum. The AI-powered Smart Leaflet relies on Large Language Model inference and must **never** replace professional medical advice, clinical diagnosis, or direct consultation with a qualified doctor or pharmacist. Always read the physical product packaging and follow your physician's instructions.
