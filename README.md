# 🤖 AI Customer Success & Sales Copilot

A Streamlit web application that helps Customer Success professionals quickly assess
customer health, churn risk, and next best actions from simple account inputs.

> **Portfolio demo project** — uses fictional customer data only. No real integrations.

## ✨ Features

Enter basic customer information:

- Customer/company name
- Product
- Customer goal
- Product usage level (Low / Medium / High)
- Number of support tickets
- Days since last activity
- Latest customer message

Click **Analyze Customer** and get:

1. **Customer Health** — Healthy / Needs Attention / At Risk
2. **Churn Risk** — Low / Medium / High
3. **Risk Factors** — explainable reasons behind the score
4. **Customer Goal** — echoed for context
5. **Product Adoption Assessment**
6. **Recommended Next Action**
7. **Suggested Customer Response** — ready-to-edit message template
8. **Expansion / Cross-sell Opportunity**

## 🧠 How It Works

The analysis engine is **rule-based and fully transparent** (`analyze_customer()` in `app.py`):

- Each input (usage, tickets, inactivity, message sentiment) contributes weighted points
  to a risk score (0–100).
- Every rule that fires adds a human-readable risk factor, so results are explainable.
- Thresholds map the score to health status and churn risk:
  - `< 25` → Healthy / Low risk
  - `25–49` → Needs Attention / Medium risk
  - `>= 50` → At Risk / High risk
- Message sentiment is detected with a small keyword lexicon (positive/negative words).

No API keys, no external services — runs completely offline.

## 🚀 Getting Started

```bash
# 1. Clone or download this project
cd cs-copilot

# 2. (Recommended) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`.

## 📁 Project Structure

```
cs-copilot/
├── app.py             # Entire application: UI + analysis engine
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## 🛣️ Roadmap (future versions)

- [ ] LLM-powered analysis (OpenAI/Anthropic) for richer, personalized recommendations
- [ ] CSV batch analysis of multiple accounts
- [ ] Analysis history saved to a local database (SQLite)
- [ ] CRM/support-tool integrations (HubSpot, Zendesk)

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) — web app framework
- Python 3.9+
