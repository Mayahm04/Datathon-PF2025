# LawLytics
> Repository for the submission to the **Datathon PolyFinances 2025**.  

## 🚀 Project Summary
This project builds a data‑driven solution to a finance‑oriented challenge posed during the datathon: real‑world financial / market / investment / risk problem solved with engineering, data science and AI techniques. The repository contains code, data pipelines, models, a web interface (or dashboard) and deployment instructions.  

## IMPORTANT NOTE
To run this project, you need API Keys for the following : X (Twitter), Reddit, NewsApi.ai
In the root directory, you need 3 .env files. Here are the names and how they should be structured:

api_news.env
```
API_KEY="YOUR_API_KEY"
```

api_reddit.env
```
CLIENT_ID="YOUR_CLIENT_ID"
SECRET="YOUR_SECRET"
USER_AGENT="YOUR_USER_AGENT"
```

api_x.env
```
BEARER_TOKEN="YOUR_BEARER_TOKEN"
```


## 📦 Repository Structure
```
/ (root)
├── data/                   ← data
├── react-app/              ← Frontend /  UI code
├── requirements.txt        ← Python dependencies
├── server/                 ← Backend / Server code
├── api_x.env               ← X Api's key
├── api_reddit.env          ← Reddit Api's key
├── api_news.env            ← NewsApi Api's key
└── README.md               ← this file
```

## 🛠️ Getting Started
Follow these steps to get the project running locally:

### 1. Clone the repository
```bash
git clone https://github.com/YannToukam/datathon-polyfinances-2025.git
cd datathon-polyfinances-2025
```

### 2. Install dependencies
Ensure you have Python 3.11+ (or as specified) and optionally Docker.
Open the server folder in a terminal and run this command:
```bash
pip install -r requirements.txt
```

Ensure you have npm 11.6+
Open the react-app folder in a terminal and run this command:
```bash
npm i
```

### 3. Launch the server
Open the server folder in a terminal and run this command: 
```bash
python app.py
```

### 4. Launch the website
Open the react-app folder in a terminal and run this command:
```bash
npm run dev
```