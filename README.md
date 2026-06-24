# Kerala Farmer Assistance — Krishi Sakhi

**A full-stack agriculture assistant for Kerala farmers: an AI advisor that talks back in Malayalam, reads leaf photos for disease, tracks the farm, and pulls live market and weather data into one dashboard.**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) ![React](https://img.shields.io/badge/React_19-61DAFB?style=flat&logo=react&logoColor=black) ![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white) ![Google Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-8E75B2?style=flat&logo=googlegemini&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white) ![Hugging Face](https://img.shields.io/badge/Transformers-FFD21E?style=flat&logo=huggingface&logoColor=black) ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikitlearn&logoColor=white)

## Overview

Krishi Sakhi ("farming friend") is an assistant built around a simple idea: a farmer in Kerala should be able to ask a question in Malayalam, by voice, and get a useful answer about their own crops, their local market price, and what to do this week — without juggling five different apps and English-only government portals.

The app started as a Smart-India-Hackathon-style project and grew into a full system. The backend is a Flask service (`app.py`, ~2,800 lines, 41 REST endpoints) wired to Google Gemini for chat and a set of Hugging Face speech models for the Malayalam voice pipeline. The frontend is a React 19 + Vite single-page app with about 18 screens — dashboard, chat, weather, market analysis, pest detection, schemes, ask-an-officer, community, activity log, financials, knowledge hub and profile.

It targets the concrete problems Kerala farmers actually deal with: cash crops like rubber, coconut, paddy, pepper and banana whose mandi prices swing week to week; monsoon-driven weather that decides when you can spray or harvest; and expert advice that's hard to reach in your own language. The app pulls real market data from `data.gov.in` (with an AGMARKNET scrape as fallback), real forecasts from Open-Meteo, and runs every farmer-facing reply through Gemini so it can answer in English or Malayalam.

## Key Features

- **Krishi Sakhi AI chat** — a Gemini 2.5 Flash chatbot grounded in a Kerala agriculture context (crop calendar, local crops, Krishi Bhavan system). Answers in English or Malayalam, renders Markdown in the UI.
- **Malayalam voice in and out** — record a question in Malayalam, get a spoken Malayalam answer back. Full speech-to-text → translate → reason → translate → text-to-speech pipeline, plus a one-shot "complete pipeline" endpoint.
- **Plant disease detection from a photo** — upload a leaf image and get a diagnosis, severity, and treatment steps. The in-app service uses Gemini's vision model; the repo also ships a standalone MobileNetV2 plant-disease classifier (`plant_disease.py`) using a Hugging Face image-classification pipeline.
- **Disease report PDFs** — generate a downloadable ReportLab PDF of a diagnosis with recommendations.
- **Smart crop recommendation** — feed in soil (N, P, K, pH) and climate (temperature, humidity, rainfall) values and get crop suggestions from a pickled scikit-learn model, with a rule-based fallback if the model can't load.
- **Market intelligence** — current prices for key Kerala commodities across mandis, 7-day-style trend analysis, and AI-written advisories on whether to hold or sell. Source order: `data.gov.in` API → AGMARKNET HTML scrape → seeded JSON.
- **Weather and advisories** — current conditions, forecast, and farming advisories (e.g. spray/fertilize timing) computed from Open-Meteo data and a climate-probability model.
- **Smart activity tracker** — log farm activities (fertilizing, harvesting, spraying), get suggested and upcoming activities, an activity plan, activity analysis, and dismissible smart reminders.
- **Ask an Officer** — submit detailed queries to local Krishi Bhavans / agricultural officers, optionally forwarded by email (SendGrid).
- **Schemes and subsidies** — aggregated central and state scheme info (PM-KISAN and others).
- **Farm profile and dashboard** — register as a farmer, store land details and crop history, and get a personalized dashboard summary.
- **Community feed** — farmer posts and shared updates.
- **Auth and rate limiting** — session-based login/register with hashed credentials, HTTP-only cookies, and Flask-Limiter throttling (200 requests/hour default).

## How It Works

The system is split into a Flask API, a React SPA, and a layer of focused Python service modules. The Flask app is the orchestrator; each domain has its own service file that the routes call into.

### Backend orchestration (`app.py`)

`app.py` boots Flask with CORS locked to the dev frontends, sets up Flask-Limiter, configures session cookies, and lazily initializes the heavy pieces so the server still starts if a dependency is missing:

- Gemini is configured from `GEMINI_API_KEY` as `gemini-2.5-flash`; if the key is absent, AI features degrade instead of crashing.
- The translation service is initialized at startup inside a try/except so the app boots even when the audio stack (torch, torchaudio, ffmpeg) isn't present.
- "Enhanced" services (`FarmProfileService`, `SmartActivityTracker`) are imported behind a feature flag.

Data lives in plain JSON files under `data/` (`farmers.json`, `land_details.json`, `market_prices.json`, `weather_snapshot.json`, `activities.json`, `officer_queries.json`), guarded by a thread `Lock` for safe concurrent writes. There's no external database — the flat-file store keeps the project portable and easy to seed.

The 41 routes are grouped by domain: auth (`/api/login`, `/api/register`, `/api/check-session`), chat (`/api/chat`), market (`/api/market-prices`, `/api/market-prices/trends`, `/api/market-prices/advisory`), weather (`/api/weather`, `/api/weather/forecast`, `/api/weather/advisory`), activities and reminders, crop recommendations, disease detection (`/api/detect-plant-disease`, `/api/generate-disease-report`), and the voice pipeline (`/api/voice/*`, `/api/translate-*`).

### Malayalam voice pipeline (`translation_service.py`)

This is the most involved part. On init it loads four Hugging Face models onto GPU if available, else CPU:

- **`facebook/seamless-m4t-v2-large`** — SeamlessM4T v2 for speech/text translation between Malayalam and English.
- **`facebook/mms-tts-mal`** — a VITS text-to-speech model that produces Malayalam audio.
- **`gvs/wav2vec2-large-xlsr-malayalam`** — a specialized Malayalam speech-to-text model.
- **Whisper** — as an additional speech recognition path.

Audio is handled with torchaudio / soundfile / pydub, with scipy used for resampling and light denoising. Every audio dependency is wrapped so a missing FFmpeg or codec disables voice gracefully rather than taking the server down. The flow for a spoken question: record → STT (wav2vec2/Whisper) → translate to English (SeamlessM4T) → Gemini answer → translate back to Malayalam → MMS-TTS audio → served via `/api/voice/get-response-audio`.

### Disease detection (`disease_identification_service.py` + `plant_disease.py`)

The live service base64-encodes the uploaded image and sends it to Gemini with a structured prompt asking for disease name, severity, causes and treatment, in the requested language, with a rule-based fallback analysis if Gemini is unavailable. Results can be turned into a formatted PDF via ReportLab. Separately, `plant_disease.py` is a small reference script that runs the `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification` MobileNetV2 model through a `transformers` image-classification pipeline.

### Crop recommendation (`crop_recommendation_service.py`)

On startup it tries a list of pickle files in priority order (`crop_model_new.pkl`, `crop_model_joblib.pkl`, `recommender.pkl`, `recommender_joblib.pkl`) and uses the first that loads. Given soil and climate parameters it returns crop suggestions; if no model loads it falls back to a rule-based recommender so the endpoint always answers.

### Market and weather services

`market_service.py` queries the `data.gov.in` mandi-price resource, falls back to scraping the AGMARKNET Kerala search page with BeautifulSoup, and uses Gemini to write the human-readable advisory on top of the numbers. `weather_service.py` calls Open-Meteo's free forecast API and derives sunny/rainy/cloudy probabilities and a climate summary that feeds the farming advisories.

### Frontend (`frontend/`)

A React 19 + Vite SPA. Routing is `react-router-dom` v7, charts are `recharts`, icons are `react-icons`, and chat/advisory Markdown is rendered with `marked`. Pages map onto the API: `Dashboard`, `Chat`, `Weather`, `MarketAnalysis`/`Marketplace`, `PestDetection`, `Schemes`, `AskOfficer`, `Community`, `Activities`, `Financials`, `KnowledgeHub`, `MyProfile`, `Future` and `Login`. Shared components include a `Sidebar`, `Topbar`, `VoiceInput` (records and posts Malayalam audio), `TranslationWidget`, `ChatWidget` and a `ProtectedRoute` gate backed by a `UserContext`.

## Tech Stack

- **Languages:** Python, JavaScript, CSS, HTML
- **Backend:** Flask, Flask-CORS, Flask-Limiter, python-dotenv
- **Frontend:** React 19, Vite, react-router-dom, recharts, react-icons, marked
- **AI / ML:** Google Generative AI (Gemini 2.5 Flash), PyTorch + torchaudio, Hugging Face Transformers (SeamlessM4T v2, MMS-TTS / VITS, wav2vec2-XLSR Malayalam, Whisper, MobileNetV2), scikit-learn
- **Audio:** librosa, soundfile, pydub, sentencepiece, scipy
- **Data sources / services:** data.gov.in (mandi prices), AGMARKNET (scrape fallback), Open-Meteo (weather), SendGrid (officer email)
- **Docs / utilities:** ReportLab (PDF), BeautifulSoup4, requests, pandas, numpy, Pillow
- **Storage:** JSON flat files (no external DB)

## Getting Started

### Prerequisites

- Python 3.12 or 3.13
- Node.js 18+ and npm
- A Google Gemini API key
- For voice features: a working PyTorch install and FFmpeg on PATH (optional — the app runs without them, voice is just disabled)

### Installation

```bash
git clone https://github.com/DCode-v05/Kerala-Farmer-Assistance.git
cd Kerala-Farmer-Assistance

# Backend
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

Copy the env template and fill in your keys:

```bash
cp .env.example .env
```

```
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_here
LOG_LEVEL=INFO
# optional
SENDGRID_API_KEY=...
OFFICER_FORWARD_EMAIL=officer@example.com
PORT=5000
```

### Running

```bash
# Terminal 1 — backend (http://127.0.0.1:5000)
python app.py

# Terminal 2 — frontend (http://localhost:5173)
cd frontend
npm run dev
```

The first run that touches voice will download the Hugging Face models (SeamlessM4T v2 alone is multi-GB), so expect a wait the first time.

## Usage

- **Register** a farmer profile with your land and crop details, then log in.
- **Dashboard** shows your personalized weather and market summary.
- **Chat** with Krishi Sakhi — for example "What is the price of rubber today?" or "How do I control pests on my coconut trees?" — in English or Malayalam.
- **Voice** — tap the mic, ask in Malayalam, and get a spoken Malayalam answer.
- **Pest detection** — upload a leaf photo to get a diagnosis and treatment, and export it as a PDF.
- **Activities** — log what you did on the farm and let the tracker suggest and remind you of what's next.
- **Ask an Officer** — send a detailed query to your local Krishi Bhavan.

## Project Structure

```
Kerala-Farmer-Assistance/
├── app.py                              # Flask backend — 41 REST routes, JSON store, Gemini wiring
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variable template
├── translation_service.py              # Malayalam STT/TTS/translate (SeamlessM4T, MMS-TTS, wav2vec2, Whisper)
├── disease_identification_service.py   # Leaf-image disease analysis via Gemini + PDF report
├── plant_disease.py                    # Standalone MobileNetV2 disease classifier (HF pipeline)
├── crop_recommendation_service.py      # sklearn crop model with rule-based fallback
├── market_service.py                   # data.gov.in + AGMARKNET scrape + Gemini advisories
├── weather_service.py                  # Open-Meteo forecast + climate-probability advisories
├── smart_activity_tracker.py           # Activity suggestions, plans, smart reminders
├── farm_profile_service.py             # Farmer/land profile logic
├── auth_service.py                     # Session auth, hashing
├── crop_model_joblib.pkl / recommender.pkl   # Pickled ML models
├── data/                               # JSON "database"
│   ├── farmers.json
│   ├── land_details.json
│   ├── market_prices.json
│   ├── weather_snapshot.json
│   ├── activities.json
│   └── officer_queries.json
├── frontend/                           # React 19 + Vite SPA
│   └── src/
│       ├── pages/                      # ~18 screens (Dashboard, Chat, Weather, PestDetection, ...)
│       ├── components/                 # Sidebar, Topbar, VoiceInput, ChatWidget, TranslationWidget
│       ├── contexts/UserContext.jsx
│       └── App.jsx
└── README.md
```

---

## Contact

**Portfolio:** [Denistan](https://www.denistan.me)<br>
**LinkedIn:** [Denistan](https://www.linkedin.com/in/denistanb)<br>
**GitHub:** [DCode-v05](https://github.com/DCode-v05)<br>
**LeetCode:** [Denistan_B](https://leetcode.com/u/Denistan_B)<br>
**Email:** [denistanb05@gmail.com](mailto:denistanb05@gmail.com)

Made with ❤️ by **Denistan B**
