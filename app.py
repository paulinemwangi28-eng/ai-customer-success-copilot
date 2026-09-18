"""
AI Customer Success & Sales Copilot
------------------------------------
A Streamlit web app that analyzes fictional customer data and produces
a Customer Success assessment: health score, churn risk, risk factors,
an action plan, product adoption analysis, and expansion opportunities.

100% transparent rule-based logic — no API keys, no black-box models.
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
        padding: 1.1rem; border-radius: 12px; text-align: center;
        border: 1px solid #e5e7eb; background: #ffffff; height: 100%;
    }
    .metric-label {font-size: 0.8rem; color: #6b7280; text-transform: uppercase;
                   letter-spacing: 0.05em;}
    .metric-value {font-size: 1.5rem; font-weight: 700;}
    .section-title {font-size: 1.15rem; font-weight: 600; margin-top: 1.4rem;}
</style>
""", unsafe_allow_html=True)

COLOR = {"green": "#16a34a", "amber": "#d97706", "red": "#dc2626", "blue": "#2563eb"}


# ----------------------------------------------------------------------------
# ANALYSIS ENGINE — transparent, rule-based, explainable
# ----------------------------------------------------------------------------

NEGATIVE_WORDS = ["frustrated", "angry", "cancel", "unacceptable", "disappointed",
                  "terrible", "worst", "refund", "not working", "broken", "upset",
                  "considering leaving", "competitor", "unhappy"]
POSITIVE_WORDS = ["love", "great", "amazing", "happy", "excellent", "thank",
                  "awesome", "fantastic", "helpful"]


def analyze_sentiment(message: str) -> str:
    """Keyword-based sentiment check. Empty or balanced messages -> neutral."""
    text = (message or "").lower()
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    if neg > pos:
        return "negative"
    if pos > neg:
        return "positive"
    return "neutral"


def analyze_customer(data: dict) -> dict:
    """
    Core engine. Each signal contributes weighted risk points (0-100+).
    Health Score = 100 - risk points. Every rule records a human-readable
    reason so the output is fully explainable.
    """
    risk_points = 0
    # Each factor: (text, weight) so we can rank the top drivers
    risk_factors = []

    # --- Product usage level (max 35 pts) ---
    usage = data["usage_level"]
    if usage == "Low":
        risk_points += 35
        risk_factors.append(("Low product usage — the customer may not be getting value from the product", 35))
    elif usage == "Medium":
        risk_points += 15
        risk_factors.append(("Moderate product usage — adoption is partial and could slip", 15))

    # --- Support tickets (max 25 pts) ---
    tickets = max(0, int(data["support_tickets"]))
    if tickets >= 6:
        risk_points += 25
        risk_factors.append((f"High support load ({tickets} tickets) — repeated issues erode trust", 25))
    elif tickets >= 3:
        risk_points += 12
        risk_factors.append((f"Elevated ticket volume ({tickets} tickets) — monitor resolution closely", 12))

    # --- Days since last activity (max 25 pts) ---
    inactive = max(0, int(data["days_inactive"]))
    if inactive >= 30:
        risk_points += 25
        risk_factors.append((f"No activity in {inactive} days — disengagement is a strong churn signal", 25))
    elif inactive >= 14:
        risk_points += 12
        risk_factors.append((f"{inactive} days since last activity — engagement is cooling", 12))

    # --- Message sentiment (max 15 pts) ---
    sentiment = analyze_sentiment(data["message"])
    if sentiment == "negative":
        risk_points += 15
        risk_factors.append(("Negative sentiment detected in the customer's latest message", 15))

    # --- Goal clarity (max 5 pts) ---
    goal = (data["goal"] or "").strip()
    if not goal:
        risk_points += 5
        risk_factors.append(("No documented customer goal — success cannot be measured or demonstrated", 5))

    # --- Health score (0-100) ---
    health_score = max(0, 100 - min(risk_points, 100))

    if health_score <= 50:
        health, churn, color = "At Risk", "High", COLOR["red"]
    elif health_score <= 75:
        health, churn, color = "Needs Attention", "Medium", COLOR["amber"]
    else:
        health, churn, color = "Healthy", "Low", COLOR["green"]

    # Rank top 3 risk factors by weight
    top_factors = [t for t, _ in sorted(risk_factors, key=lambda x: -x[1])][:3]
    if not top_factors:
        top_factors = ["No significant risk signals detected — the account appears stable"]

    # --- Score explanation ---
    if health == "Healthy":
        score_explanation = (f"Score {health_score}/100: strong usage and engagement with no major "
                             "negative signals. The customer appears to be realizing value.")
    elif health == "Needs Attention":
        score_explanation = (f"Score {health_score}/100: early warning signs — "
                             f"mainly driven by {top_factors[0].split('—')[0].strip().lower()}. "
                             "Proactive outreach now can prevent escalation.")
    else:
        score_explanation = (f"Score {health_score}/100: multiple compounding risk signals "
                             f"(top driver: {top_factors[0].split('—')[0].strip().lower()}). "
                             "Immediate, structured intervention is recommended.")

    # --- Churn driver explanation ---
    if churn == "Low":
        churn_driver = "Churn risk is low: engagement, sentiment, and support signals are all within healthy ranges."
    elif churn == "Medium":
        churn_driver = (f"Churn risk is medium, driven primarily by {len([f for f in risk_factors if f[1] >= 12])} "
                        "moderate signal(s). Unaddressed, these typically compound over 1-2 quarters.")
    else:
        churn_driver = ("Churn risk is high: several severe signals are present simultaneously — "
                        "accounts in this state have an elevated probability of non-renewal.")

    # --- Recommended CS action plan (3-5 steps, health-aware) ---
    plan = []
    name = data["company"]
    if health == "At Risk":
        plan.append(f"**Contact the customer within 48 hours** — acknowledge their concerns directly and personally.")
        plan.append("**Escalate internally** — brief a senior CSM or manager and align on a recovery plan.")
        if tickets > 0:
            plan.append(f"**Resolve support concerns** — review all {tickets} ticket(s), prioritize blockers, and share a resolution timeline.")
        if usage in ("Low", "Medium"):
            plan.append("**Provide targeted training** — run a hands-on session focused on the workflows tied to their goal.")
        plan.append("**Schedule a check-in within 1 week** — review progress against the recovery plan and confirm next milestones.")
    elif health == "Needs Attention":
        plan.append(f"**Send a proactive check-in to {name} this week** — share one resource that moves them toward their goal.")
        if tickets > 0:
            plan.append(f"**Close the loop on support** — confirm their {tickets} ticket(s) are resolved to satisfaction.")
        if usage in ("Low", "Medium"):
            plan.append("**Offer onboarding/training** — a 30-minute session on the features most relevant to their goal.")
        plan.append("**Schedule a check-in within 2 weeks** — track engagement and confirm usage is trending up.")
    else:
        plan.append(f"**Send a value recap to {name}** — highlight usage wins and progress toward their goal.")
        plan.append("**Schedule the next QBR** — review outcomes, set next-quarter goals, and strengthen the relationship.")
        plan.append("**Recommend relevant features** — introduce one advanced capability aligned to their goal.")
        plan.append("**Follow up within 30 days** — maintain momentum and watch for expansion signals.")

    # --- Product adoption analysis ---
    adoption_map = {
        "Low": ("Low",
                "Adoption is shallow. Focus on onboarding fundamentals: identify one high-value use case tied "
                "to their goal, deliver hands-on training, and set a simple weekly usage target."),
        "Medium": ("Moderate",
                   "Adoption is partial. Identify the team's most-used workflow and introduce the next most "
                   "valuable adjacent feature. Consider office hours or a tips newsletter to build habits."),
        "High": ("High",
                 "Adoption is strong — the product is embedded in their workflow. Protect it: share best "
                 "practices, invite them to a customer community, and explore advocacy (case study, referral)."),
    }
    adoption_level, adoption_advice = adoption_map[usage]

    # --- Expansion opportunity (conservative) ---
    if health == "Healthy" and usage == "High":
        expansion_type = "Upsell opportunity"
        expansion_text = ("The customer is healthy with deep adoption — a reasonable moment to discuss "
                          "additional seats, a higher tier, or premium features that support their goal.")
        expansion_next = "Next step: raise the topic naturally at the next QBR, anchored on achieved value."
    elif health == "Healthy":
        expansion_type = "Cross-sell opportunity (early)"
        expansion_text = ("The account is healthy. Rather than selling now, introduce one complementary "
                          "feature or add-on aligned to their goal to deepen value first.")
        expansion_next = "Next step: share a short walkthrough of the relevant feature; revisit commercial discussion next quarter."
    else:
        expansion_type = "No immediate opportunity"
        expansion_text = ("The account needs stabilization before any commercial conversation. "
                          "Selling now would damage trust.")
        expansion_next = "Next step: focus entirely on retention; reassess expansion once health returns to Healthy."

    # --- Suggested customer response (kept from v1, goal-safe) ---
    goal_text = goal if goal else "your goals"
    product = data["product"]
    if sentiment == "negative":
        reply = (f"Hi [Name], thank you for being honest with us — I'm sorry your experience with "
                 f"{product} hasn't met expectations. I've reviewed your account and I'm personally "
                 f"taking ownership of the issues you've raised. Could we schedule 20 minutes this week so I can "
                 f"understand what's blocking your goal of \"{goal_text}\" and put a plan in place?")
    elif health == "Healthy":
        reply = (f"Hi [Name], great to see the progress {name} is making with {product}! "
                 f"Your usage trends look strong. I'd love to show you a few capabilities other teams use to "
                 f"accelerate goals like \"{goal_text}\" — would a quick 15-minute walkthrough be useful?")
    else:
        reply = (f"Hi [Name], I wanted to check in on how things are going with {product}. "
                 f"I noticed a few areas where we can help you get closer to \"{goal_text}\". "
                 f"Would you be open to a short call this week to review and plan next steps?")

    return {
        "health_score": health_score, "health": health, "churn": churn, "color": color,
        "sentiment": sentiment, "score_explanation": score_explanation,
        "top_factors": top_factors, "churn_driver": churn_driver,
        "plan": plan, "adoption_level": adoption_level, "adoption_advice": adoption_advice,
        "expansion_type": expansion_type, "expansion_text": expansion_text,
        "expansion_next": expansion_next, "reply": reply, "goal": goal_text,
    }


# ----------------------------------------------------------------------------
# UI — INPUT FORM (left) & RESULTS (right)
# ----------------------------------------------------------------------------

st.markdown('<p class="main-header">🤖 AI Customer Success & Sales Copilot</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Analyze fictional customer accounts and get an instant, explainable '
            'health score, churn risk, action plan, and expansion guidance.</p>', unsafe_allow_html=True)

left, right = st.columns([1, 1.4], gap="large")

with left:
    st.markdown("### 📋 Customer Information")
    with st.form("customer_form"):
        company_in = st.text_input("Customer / Company Name", value="Acme Corp")
        product_in = st.text_input("Product", value="CloudSync Pro")
        goal_in = st.text_area("Customer Goal", value="Reduce manual reporting time by 50%", height=80)
        usage_in = st.select_slider("Product Usage Level", options=["Low", "Medium", "High"], value="Medium")
        tickets_in = st.number_input("Number of Support Tickets (last 90 days)", min_value=0, max_value=500, value=2)
        inactive_in = st.number_input("Days Since Last Activity", min_value=0, max_value=730, value=5)
        message_in = st.text_area("Latest Customer Message",
            value="Things are going okay, but we're still figuring out some of the reporting features.",
            height=120)
        submitted = st.form_submit_button("🔍 Analyze Customer", use_container_width=True)

    st.caption("⚠️ Demo app — use fictional customer data only.")

    with st.expander("📖 How This Works (Methodology)"):
        st.markdown("""
This app uses **transparent, rule-based logic** — not a machine-learning model.

**Health Score (0–100):** starts at 100; points are subtracted for risk signals:
- Low product usage: −35 · Medium usage: −15
- 6+ support tickets: −25 · 3–5 tickets: −12
- 30+ days inactive: −25 · 14–29 days: −12
- Negative message sentiment: −15 (keyword-based check)
- No documented customer goal: −5

**Status thresholds:** ≥76 Healthy · 51–75 Needs Attention · ≤50 At Risk

Churn risk (Low/Medium/High), the action plan, adoption guidance, and expansion
recommendations all derive from the same signals — every conclusion links back to
an input you can see and adjust.
        """)

with right:
    if submitted:
        # Edge-case handling: sanitize inputs before analysis
        data = {
            "company": (company_in or "").strip() or "the customer",
            "product": (product_in or "").strip() or "the product",
            "goal": goal_in or "",
            "usage_level": usage_in,
            "support_tickets": tickets_in,
            "days_inactive": inactive_in,
            "message": message_in or "",
        }
        r = analyze_customer(data)

        st.markdown(f"### 📊 Analysis for {data['company']}")

        # ---- Top dashboard cards ----
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Health Score</div>
                <div class="metric-value" style="color:{r['color']}">{r['health_score']}/100</div></div>""",
                unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Health Status</div>
                <div class="metric-value" style="color:{r['color']}">{r['health']}</div></div>""",
                unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Churn Risk</div>
                <div class="metric-value" style="color:{r['color']}">{r['churn']}</div></div>""",
                unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="metric-card">
                <div class="metric-label">Product Adoption</div>
                <div class="metric-value" style="color:{COLOR['blue']}">{r['adoption_level']}</div></div>""",
                unsafe_allow_html=True)

        st.progress(r["health_score"] / 100, text=f"Health Score: {r['health_score']}/100")
        st.caption(r["score_explanation"])

        # ---- Churn risk explanation ----
        st.markdown('<p class="section-title">🔥 Churn Risk Analysis</p>', unsafe_allow_html=True)
        st.write(r["churn_driver"])
        st.markdown("**Top risk factors:**")
        for f in r["top_factors"]:
            st.markdown(f"- {f}")

        # ---- Customer goal ----
        st.markdown('<p class="section-title">🎯 Customer Goal</p>', unsafe_allow_html=True)
        st.write(r["goal"])

        # ---- Action plan ----
        st.markdown('<p class="section-title">✅ Recommended Customer Success Action Plan</p>', unsafe_allow_html=True)
        for i, step in enumerate(r["plan"], 1):
            st.markdown(f"{i}. {step}")

        # ---- Product adoption ----
        st.markdown('<p class="section-title">📈 Product Adoption</p>', unsafe_allow_html=True)
        st.markdown(f"**Level: {r['adoption_level']}**")
        st.write(r["adoption_advice"])

        # ---- Suggested response ----
        st.markdown('<p class="section-title">✉️ Suggested Customer Response</p>', unsafe_allow_html=True)
        st.info(r["reply"])

        # ---- Expansion ----
        st.markdown('<p class="section-title">💰 Expansion Opportunity</p>', unsafe_allow_html=True)
        st.markdown(f"**{r['expansion_type']}**")
        st.write(r["expansion_text"])
        st.caption(r["expansion_next"])
    else:
        st.markdown("### 📊 Analysis")
        st.markdown(
            "<div style='padding:3rem; text-align:center; color:#9ca3af; border:2px dashed #e5e7eb; "
            "border-radius:12px;'>Fill in the customer details and click "
            "<b>Analyze Customer</b> to see the assessment here.</div>",
            unsafe_allow_html=True)
