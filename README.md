# Kerala Farmer Assistance System (Krishi Sakhi)

## Project Description
Krishi Sakhi is an advanced AI-powered agricultural assistance platform designed specifically for farmers in Kerala. By leveraging generative AI, machine learning, and real-time data analysis, the system provides personalized farming advice, market price trends, weather forecasts, and direct connectivity to local agricultural officers. The application combines a robust Python Flask backend with a modern, responsive React frontend to deliver a seamless user experience.

---

## Project Details

### Problem Statement
Farmers in Kerala often struggle with unpredictable weather patterns, fluctuating market prices for cash crops (like Rubber, Coconut, and Spices), and limited access to timely expert advice. This project aims to bridge the information gap by democratizing access to expert agricultural knowledge and government support systems.

### Key Features
- **AI-Powered Assistant (Krishi Sakhi):** A context-aware chatbot powered by Google Gemini specifically trained on Kerala's agricultural calendar, capable of answering queries in English and Malayalam.
- **Smart Crop Recommendation:** Machine learning models to suggest optimal crops based on soil and weather conditions.
- **Market Intelligence:** Real-time checking of market prices for key Kerala crops (Rubber, Coconut, Paddy, Banana, Pepper) across different mandis.
- **Weather & Advisories:** Localized weather forecasts coupled with actionable farming advisories (e.g., when to apply fertilizer).
- **Officer Connect:** A direct channel for farmers to submit detailed queries to local Krishi Bhavans and Agricultural Officers.
- **Schemes & Subsidies:** Aggregated information on central and state government agricultural schemes (PM-KISAN, etc.).
- **Digital Farm Profile:** A comprehensive dashboard for farmers to manage their land details, crop history, and farming activities.

### Data Management
- **JSON-based Storage:** Uses a lightweight, efficient JSON file system for persisting farmer profiles, activity logs, and officer queries, ensuring easy portability and backup.
- **Machine Learning Models:** Integrates pre-trained `.pkl` models for crop recommendation and disease identification.

### Web Application
The solution features a dual-interface architecture:
- **Farmer Portal:** A mobile-responsive web app for farmers to access daily insights, chat with the AI, and manage their farm.
- **Backend API:** A RESTful Flask service that handles authentication, AI processing, and data retrieval.

---

## Tech Stack
- **Frontend:**
  - React 19 (Vite)
  - React Router DOM
  - Recharts (for data visualization)
  - React Icons
  - Marked (Markdown rendering)
- **Backend:**
  - Python Flask
  - Google Generative AI (Gemini)
  - PyTorch & Transformers (for translation/audio features)
  - ReportLab (PDF Report Generation)
  - Scikit-learn (ML Models)
  - Flask-CORS & Flask-Limiter
- **Data:**
  - JSON Flat-file Database

---

## Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/DCode-v05/Kerala-Farmer-Assistance.git
cd Kerala-Farmer-Assistance
```

### 2. Backend Setup
Navigate to the root directory and install Python dependencies.
```bash
# Create a virtual environment (optional but recommended)
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```
**Configuration:**
Create a `.env` file in the root directory and add your API keys:
```
GEMINI_API_KEY=your_google_gemini_key
SECRET_KEY=your_secret_key
```

### 3. Frontend Setup
Open a new terminal and navigate to the frontend directory.
```bash
cd frontend
npm install
```

### 4. Run the Application
**Start Backend:**
```bash
python app.py
# Server runs on http://127.0.0.1:5000
```

**Start Frontend:**
```bash
cd frontend
npm run dev
# App runs on http://localhost:5173
```

---

## Usage
- **Registration:** Create a new farmer profile with your land details.
- **Dashboard:** View your personalized weather and market summary.
- **Krishi Sakhi Chat:** Ask questions like "What is the price of Rubber today?" or "How to control pests in Coconut trees?".
- **Activity Log:** Record your daily farming activities (fertilizing, harvesting) for better tracking.

---

## Project Structure
```
Kerala-Farmer-Assistance/
│
├── app.py                      # Main Flask Backend Application
├── requirements.txt            # Python Dependencies
├── .env.example                # Environment variables template
├── data/                       # JSON Database Storage
│   ├── farmers.json
│   ├── land_details.json
│   ├── market_prices.json
│   └── ...
├── frontend/                   # React Frontend Application
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── *.pkl                       # Machine Learning Models (Crop, Disease)
├── *_service.py                # Business Logic Services (Weather, Market, etc.)
└── README.md                   # Project Documentation
```

---

## Contributing
Contributions are welcome to improve the lives of farmers!
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m "Add NewFeature"`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
