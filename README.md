# 🦠 Epidemic Predict Pro
### 👨‍💻 Developed by Priyanshu Soni  
*A specialized Health-Tech solution for predictive pandemic modeling and mobility-driven outbreak analysis.*

---

## 📌 Project Overview
**Epidemic Predict Pro** is a sophisticated, full-stack AI platform designed to solve one of the biggest challenges in modern healthcare: **predicting infectious disease outbreaks before they peak**.

By integrating high-quality epidemiological data from **Johns Hopkins University (JHU)** with **Google Global Mobility Reports**, the system models how human movement (Retail, Transit, Workplace, Residential) directly influences viral transmission.

---

## 🌐 Live Prototype & Deployment
The application follows a **Microservices Architecture** for scalability and performance:

- 🚀 **Frontend Dashboard:** Hosted on Vercel Edge Network for ultra-fast global UI delivery  
- ⚙️ **AI Backend API:** Hosted on Render Compute for Machine Learning inference  

🔗 **Live Demo:**  
https://epidemic-predict-ai-git-main-jais-projects-833fe4a0.vercel.app/

> ⚠️ Note: Backend may take ~60 seconds to wake up after inactivity.

---

## ☁️ System Architecture
- **Frontend (Vercel):**
  - React 19 + Vite
  - Global CDN → instant UI loading

- **Backend (Render):**
  - FastAPI server
  - 100+ trained XGBoost models
  - SQLite3 database

---

## ✨ Core Features
- 🌍 **AI-Powered Risk Map**  
  Dynamic global choropleth map showing 14-day outbreak risk predictions  

- ⏱️ **Global Time Machine**  
  Replay pandemic history (2020–2023) and compare predictions vs real data  

- 🎛️ **What-If Scenario Simulator**  
  Adjust mobility (e.g., reduce transit by 50%) and instantly see predicted outcomes  

- 📊 **XGBoost Feature Importance**  
  Transparent AI showing which mobility factor drives spread in each region  

---

## 🧠 AI & Data Science Methodology

This system uses a **Multivariate Time Series approach**:

- **Algorithm Used:** XGBoost Regressor (XGBRegressor)  
- **Multivariate Modeling:** Uses mobility variables instead of only past cases  
- **14-Day Incubation Lag:** Matches real-world virus incubation period  
- **Log Transformation:** Normalizes population differences  
- **7-Day Rolling Average:** Removes noisy reporting fluctuations  

---

## 🛠️ Backend Workflow (Pipeline)

### 🧩 Stage 1: `train_model.py`
- Data preprocessing (JHU + Google Mobility)
- Feature engineering
- Train 100+ country-specific models
- Save models as `.pkl`

### 📚 Stage 2: `seed_db.py`
- Populate SQLite database (`epidemic_data.db`)
- Fast and portable storage

### 🔗 Stage 3: `main.py`
- FastAPI backend
- Real-time ML inference
- API endpoints for frontend

---

## 📦 Tech Stack

### 🎨 Frontend
- React 19 (Vite)  
- Leaflet.js  
- Recharts  
- Axios  

### ⚙️ Backend
- Python 3.9+  
- FastAPI  
- Uvicorn  

### 🧠 AI / ML
- XGBoost  
- Scikit-Learn  
- Pandas  
- NumPy  

### 🗄️ Database
- SQLite3  

---

## 🚀 Installation & Setup

### 🔧 Prerequisites
- Python 3.9+  
- Node.js 18+  
- Git  

---

### 1️⃣ Clone Repository
```bash
git clone https://github.com/priy0767/EpidemicPredictAI.git
cd EpidemicPredictAI
```

---

## ⚙️ Backend Setup (IMPORTANT)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Train models & prepare database
python train_model.py
python seed_db.py

# 🚀 Start Backend Server
uvicorn main:app --reload
```

✅ Backend runs on: http://localhost:8000  

---

## 🎨 Frontend Setup (IMPORTANT)

```bash
cd frontend
npm install --legacy-peer-deps

# 🚀 Start Frontend
npm run dev
```

✅ Frontend runs on: http://localhost:5173  

---

## 🧪 How It Works (Simple Flow)
1. Frontend sends user inputs (mobility sliders)
2. FastAPI backend processes request
3. XGBoost models generate predictions
4. Results are returned and visualized instantly

---

## 🏆 Hackathon Project
Built for **Health-Tech Hackathon**  
Focused on real-world epidemic prediction and decision-making tools.

---

## 👨‍💻 Author
**Priyanshu Soni**

---

## ⭐ Support
If you found this project useful, consider giving it a ⭐ on GitHub!
