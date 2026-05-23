# 🎧💬 SmartSupport: Intelligent Customer Support Agent 

SmartSupport is an AI-powered customer support agent that automatically categorizes incoming queries, detects sentiment, and routes each conversation to the right handler all in real time. No rigid decision trees, no hardcoded FAQs. Just a smart agent that knows when to troubleshoot, when to handle billing, and when to escalate.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1.2-1D9E75?logo=langchain&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama%203.3%2070B-E24B4A?logo=groq&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)



<img width="1408" height="768" alt="Smart Support" src="https://github.com/user-attachments/assets/5c6f2fcc-2c9d-4a28-87c4-7edc5e682016" />

---

## 📌 Overview

**SmartSupport** is a multi-node customer support agent built with:

- **LangGraph** for stateful, graph-based query routing
- **Groq** (Llama 3.3 70B) for fast, high-quality LLM inference
- **Streamlit** for a clean, zero-config chat interface

Paste your Groq API key, type a customer query, and the agent handles everything — classifying the issue, reading the sentiment, picking the right handler, and responding with context-aware, empathetic answers.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔑 **Bring-your-own key** | Enter your Groq API key in the sidebar, no `.env` or server config needed |
| 🗂 **Auto categorization** | Every query is classified as Technical, Billing, or General before routing |
| 💬 **Sentiment detection** | Positive, Neutral, or Negative, detected automatically on each message |
| 🔀 **Smart routing** | LangGraph conditional edges route to the right handler based on category + sentiment |
| 🚨 **Escalation logic** | Only Negative + Technical queries escalate, other frustrated users still get real help |
| 🤝 **Empathy-aware replies** | Negative-sentiment queries get an empathetic opening before the actual answer |
| 📊 **Live metadata badges** | Every response shows the detected category and sentiment inline |


---

## 🛠 Tools & Technologies

| Layer | Technology | Purpose |
|---|---|---|
| **UI** | Streamlit 1.45 | Chat interface, sidebar, session state |
| **LLM** | Groq · Llama 3.3 70B | Fast inference, categorization, response generation |
| **Orchestration** | LangGraph 1.2 | Stateful agent graph with conditional routing |

---

## 📁 Project Structure

```

├── .gitignore
├── README.md
├── SmartSupport_CustomerSupportAgent.ipynb
├── app.py
└── requirements.txt
```

---

## ⚡ Quick Start

### 1 · Clone the repo

```bash
git clone https://github.com/muqadasejaz/SmartSupport-Customer-Support-Agent
cd supportiq-agent
```

### 2 · Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Run the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

### 5 · Get a free Groq API key

Sign up at [console.groq.com](https://console.groq.com), go to **API Keys**, and click **Create API Key**. It is free.

---

## 🧭 How to Use

```
1. Enter your Groq API key in the sidebar
2. Type a customer query in the chat box
3. The agent categorizes the query and detects sentiment
4. You get a routed, context-aware response instantly
5. Category and sentiment badges appear under each response
6. Click "Clear chat" to start a fresh session
```

**Try these sample queries:**

- *"My app keeps crashing when I open the dashboard"* → Technical
- *"I was charged twice this month"* → Billing
- *"Do you offer live chat support?"* → General
- *"I've been trying to fix this for three days and nothing works"* → Escalated

---

## 🏗 Architecture

The diagram below shows how a user message flows through the agent graph:

```
User sends a message
│
▼
Streamlit (app.py)
Passes query into LangGraph workflow
│
▼
Node 1 · categorize
→ Classifies query as: Technical | Billing | General
│
▼
Node 2 · analyze_sentiment
→ Detects sentiment as: Positive | Neutral | Negative
│
▼
Conditional Router · route_query
→ Negative + Technical   →  escalate
→ Technical              →  handle_technical
→ Billing                →  handle_billing
→ General / fallback     →  handle_general
│
▼
Handler Node
→ Generates a context-aware, role-appropriate response
→ Adds empathetic opening if sentiment is Negative
│
▼
Streamlit renders response
→ Shows category + sentiment badges
→ Appends to chat history
```

### Why separate categorization and sentiment?

Treating them as two independent nodes gives the router a two-axis decision surface. A frustrated billing complaint and a frustrated technical crash look similar in raw text, but they need completely different handlers. Splitting the signals keeps the routing logic clean and extensible.

### Why only escalate Negative + Technical?

Escalating every negative-sentiment query is a common mistake — it leaves frustrated billing or general users with a dead-end message instead of actual help. Only Technical issues with negative sentiment genuinely benefit from a human review. Everything else gets a real LLM response with an empathetic tone.

---

## 🖥 GUI Preview

```
┌──────────────────────────────────────────────────────────────┐
│  🎧 Customer Support Agent                      sidebar      │
│  ──────────────────────────────────────────────────────────  │
│  ⚙️ Configuration                                            │
│  Groq API Key                                                │
│  [gsk_••••••••••••••••••••••••••]                           │
├──────────────────────────────────────────────────────────────┤
│                        main area                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  You: My app keeps crashing on file upload           │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  🔧 Technical          😐 Neutral                    │   │
│  │                                                      │   │
│  │  🤖 This sounds like a client-side upload error.    │   │
│  │     Here's what to try:                              │   │
│  │     1. Clear your browser cache and retry           │   │
│  │     2. Check the file size — the limit is 10MB      │   │
│  │     3. Try a different browser                      │   │
│  │     What file format are you uploading?             │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [ Describe your issue…                          Send ▶ ]   │
└──────────────────────────────────────────────────────────────┘
```

---

## ☁️ Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit — SmartSupport Agent"
git remote add origin https://github.com/muqadasejaz/SmartSupport-Customer-Support-Agent
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **New app**
3. Select your repository and set **Main file path** to `app.py`
4. Click **Deploy**

> 💡 **No secrets needed** users supply their own Groq API key through the sidebar UI.


---

## 📋 Requirements

```
streamlit>=1.45.0
langchain-core>=0.3.0
langchain-groq>=1.1.2
langgraph>=1.2.0
python-dotenv>=1.0.0
```

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 👤 Author

Muqadas Ejaz

BS Computer Science (AI Specialization)

AI/ML Engineer

Kaggle Grand Master

Data Science & Gen AI 

📫 Connect with me on [LinkedIn](https://www.linkedin.com/in/muqadasejaz/)  

🌐 GitHub: [github.com/muqadasejaz](https://github.com/muqadasejaz)

📬 Kaggle: [Kaggle Profile](https://www.kaggle.com/muqaddasejaz) 


----

## 📄 License

This project is licensed under the **MIT License**

⭐ If you find this project useful, don’t forget to star the repository!
