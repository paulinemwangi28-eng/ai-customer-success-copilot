"""
AI Customer Success & Sales Copilot
------------------------------------
A Streamlit web app that analyzes fictional customer data and produces
a Customer Success health assessment: health status, churn risk,
risk factors, recommended next actions, and expansion opportunities.

100% rule-based logic — no API keys or external services required.
"""

import streamlit as st

# ----------------------------------------------------------------------------
# PAGE CONFIG & STYLING
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Customer Success Copilot",
    page_icon="🤖",
    layout="wide",
)

st.markdown("""
<style>
    .main-header {font-size: 2.2rem; font-weight: 700; margin-bottom: 0;}
    .sub-header {color: #6b7280; margin-top: 0.2rem; margin-bottom: 1.5rem;}
    .metric-card {
        padding: 1.2rem; border-radius: 12px; text-align: center;
        border: 1px solid #e5e7eb; background: #ffffff;
    }
    .metric-label {font-size: 0.85rem; color: #6b7280; text-transform: uppercase;
                   letter-spacing: 0.05em;}
    .metric-value {font-size: 1.6rem; font-weight: 700;}
    .section-title {font-size: 1.15rem; font-weight: 600; margin-top: 1.2rem;}
    .badge {display: inline-block; padding: 2px 10px; border-radius: 999px;
            font-size: 0.8rem; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

COLOR = {"green": "#16a34a", "amber": "#d97706", "red": "#dc2626", "blue": "#2563eb"}


# ----------------------------------------------------------------------------
# ANALYSIS ENGINE (rule-based, explainable — great for portfolio discussions)
# ----------------------------------------------------------------------------

NEGATIVE_WORDS = ["frustrated", "angry", "cancel", "unacceptable", "disappointed",
                  "terrible", "worst", "refund", "not working", "broken", "upset",
                  "considering leaving", "competitor", "unhappy"]
POSITIVE_WORDS = ["love", "great", "amazing", "happy", "excellent", "thank",
                  "awesome", "fantastic", "helpful"]


def analyze_sentiment(message: str) -> str:
    """Very small keyword-based sentiment check on the customer message."""
    text = message.lower()
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    if neg > pos:
        return "negative"
    if pos > neg:
        return "positive"
    return "neutral"


def analyze_customer(data: dict) -> dict:
    """
    Core scoring logic. Each input contributes points to a risk score (0–100+).
    Every rule appends a human-readable reason so results are explainable.
    """
    risk_points = 0
    risk_factors = []

    # --- Product usage level (weight: up to 35 pts) ---
    usage = data["usage_level"]
    if usage == "Low":
        risk_points += 35
        risk_factors.append("Low product usage — the customer may not be getting value from the product")
    elif usage == "Medium":
        risk_points += 15
        risk_factors.append("Moderate product usage — adoption is partial and could slip")

    # --- Support tickets (weight: up to 25 pts) ---
    tickets = data["support_tickets"]
    if tickets >= 6:
        risk_points += 25
        risk_factors.append(f"High support load ({tickets} tickets) — repeated issues erode trust")
    elif tickets >= 3:
        risk_points += 12
        risk_factors.append(f"Elevated ticket volume ({tickets} tickets) — monitor issue resolution closely")

    # --- Days since last activity (weight: up to 25 pts) ---
    inactive = data["days_inactive"]
    if inactive >= 30:
        risk_points += 25
        risk_factors.append(f"No activity in {inactive} days — disengagement is a strong churn signal")
    elif inactive >= 14:
        risk_points += 12
        risk_factors.append(f"{inactive} days since last activity — engagement is cooling")

    # --- Message sentiment (weight: up to 15 pts) ---
    sentiment = analyze_sentiment(data["message"])
    if sentiment == "negative":
        risk_points += 15
        risk_factors.append("Negative sentiment detected in the customer's latest message")

    if not risk_factors:
        risk_factors.append("No significant risk signals detected — account appears stable")

    # --- Derive health & churn risk from the score ---
    if risk_points >= 50:
        health, churn, color = "At Risk", "High", COLOR["red"]
    elif risk_points >= 25:
        health, churn, color = "Needs Attention", "Medium", COLOR["amber"]
    else:
        health, churn, color = "Healthy", "Low", COLOR["green"]

    # --- Product adoption assessment ---
    adoption_map = {
        "Low": "The customer is only scratching the surface. Focus on onboarding, quick wins, and training to drive habit-forming usage.",
        "Medium": "The customer uses the product regularly but likely hasn't adopted advanced features. Identify the next most valuable feature for their goal.",
        "High": "Strong adoption — the product is embedded in their workflow. This account is a candidate for case studies, referrals, and expansion.",
    }

    # --- Recommended next action ---
    if health == "At Risk":
        next_action = (f"Schedule an urgent check-in call with {data['company']} within 48 hours. "
                       "Acknowledge their concerns, review open support tickets, and agree on a recovery plan "
                       "tied to their goal. Loop in a senior CSM or manager.")
    elif health == "Needs Attention":
        next_action = (f"Send a proactive check-in to {data['company']} this week. Share one tip or resource "
                       "that helps them progress toward their goal, and offer a short call to remove blockers.")
    else:
        next_action = (f"Send a value recap to {data['company']}: highlight usage wins and progress toward their goal. "
                       "Book the next QBR and explore expansion.")

    # --- Suggested customer response (template) ---
    if sentiment == "negative":
        reply = (f"Hi [Name], thank you for being honest with us — I'm sorry your experience with "
                 f"{data['product']} hasn't met expectations. I've reviewed your account and I'm personally "
                 f"taking ownership of the issues you've raised. Could we schedule 20 minutes this week so I can "
                 f"understand what's blocking your goal of \"{data['goal']}\" and put a plan in place?")
    elif health == "Healthy":
        reply = (f"Hi [Name], great to see the progress {data['company']} is making with {data['product']}! "
                 f"Your usage trends look strong. I'd love to show you a few capabilities other teams use to "
                 f"accelerate goals like \"{data['goal']}\" — would a quick 15-minute walkthrough be useful?")
    else:
        reply = (f"Hi [Name], I wanted to check in on how things are going with {data['product']}. "
                 f"I noticed a few areas where we can help you get closer to \"{data['goal']}\". "
                 f"Would you be open to a short call this week to review and plan next steps?")

    # --- Expansion / cross-sell opportunity ---
    if health == "Healthy" and usage == "High":
        expansion = ("Strong candidate for expansion: propose additional seats, a higher tier, or adjacent "
                     "products. Also ask for a referral or case study participation.")
    elif health == "Healthy":
        expansion = ("Potential to grow usage first: introduce one advanced feature aligned to their goal. "
                     "Revisit upsell once adoption deepens.")
    elif health == "Needs Attention":
        expansion = ("Hold off on selling — stabilize value first. Once health improves, explore features "
                     "that support their stated goal.")
    else:
        expansion = ("No expansion motion right now. Focus entirely on retention and rebuilding trust.")

    return {
        "health": health, "churn": churn, "color": color,
        "risk_score": risk_points, "risk_factors": risk_factors,
        "sentiment": sentiment, "adoption": adoption_map[usage],
        "next_action": next_action, "reply": reply, "expansion": expansion,
    }


# ----------------------------------------------------------------------------
# UI — INPUT FORM (left) & RESULTS (right)
# ----------------------------------------------------------------------------

st.markdown('<p class="main-header">🤖 AI Customer Success & Sales Copilot</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyze fictional customer accounts and get an instant health assessment, '
            'churn risk, and recommended next actions.</p>', unsafe_allow_html=True)

left, right = st.columns([1, 1.4], gap="large")

with left:
    st.markdown("### 📋 Customer Information")
    with st.form("customer_form"):
        company = st.text_input("Customer / Company Name", value="Acme Corp")
        product = st.text_input("Product", value="CloudSync Pro")
        goal = st.text_area("Customer Goal", value="Reduce manual reporting time by 50%", height=80)
        usage_level = st.select_slider("Product Usage Level", options=["Low", "Medium", "High"], value="Medium")
        support_tickets = st.number_input("Number of Support Tickets (last 90 days)", min_value=0, max_value=50, value=2)
        days_inactive = st.number_input("Days Since Last Activity", min_value=0, max_value=365, value=5)
        message = st.text_area("Latest Customer Message",
            value="Things are going okay, but we're still figuring out some of the reporting features.",
            height=120)
        submitted = st.form_submit_button("🔍 Analyze Customer", use_container_width=True)

    st.caption("⚠️ Demo app — use fictional customer data only.")

with right:
    if submitted:
        data = {"company": company, "product": product, "goal": goal,
                "usage_level": usage_level, "support_tickets": support_tickets,
                "days_inactive": days_inactive, "message": message}
        r = analyze_customer(data)

        st.markdown(f"### 📊 Analysis for {company}")

        # Top metric cards
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Customer Health</div>
                <div class="metric-value" style="color:{r['color']}">{r['health']}</div></div>""",
                unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Churn Risk</div>
                <div class="metric-value" style="color:{r['color']}">{r['churn']}</div></div>""",
                unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Message Sentiment</div>
                <div class="metric-value" style="color:{COLOR['blue']}">{r['sentiment'].title()}</div></div>""",
                unsafe_allow_html=True)

        st.progress(min(r["risk_score"], 100) / 100, text=f"Risk score: {r['risk_score']}/100")

        st.markdown('<p class="section-title">⚠️ Risk Factors</p>', unsafe_allow_html=True)
        for f in r["risk_factors"]:
            st.markdown(f"- {f}")

        st.markdown('<p class="section-title">🎯 Customer Goal</p>', unsafe_allow_html=True)
        st.write(goal)

        st.markdown('<p class="section-title">📈 Product Adoption Assessment</p>', unsafe_allow_html=True)
        st.write(r["adoption"])

        st.markdown('<p class="section-title">✅ Recommended Next Action</p>', unsafe_allow_html=True)
        st.success(r["next_action"])

        st.markdown('<p class="section-title">✉️ Suggested Customer Response</p>', unsafe_allow_html=True)
        st.info(r["reply"])

        st.markdown('<p class="section-title">💰 Expansion / Cross-sell Opportunity</p>', unsafe_allow_html=True)
        st.write(r["expansion"])
    else:
        st.markdown("### 📊 Analysis")
        st.markdown(
            "<div style='padding:3rem; text-align:center; color:#9ca3af; border:2px dashed #e5e7eb; "
            "border-radius:12px;'>Fill in the customer details and click "
            "<b>Analyze Customer</b> to see the assessment here.</div>",
            unsafe_allow_html=True)
