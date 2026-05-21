import streamlit as st
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="🎧💬",
    layout="centered"
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")
    groq_api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_..."
    )
    st.caption("Get your key at [console.groq.com](https://console.groq.com)")

    st.divider()


# ── State ─────────────────────────────────────────────────────────────────────
class State(TypedDict):
    query: str
    category: str
    sentiment: str
    response: str

# ── Build agent (cached per API key) ─────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def build_agent(api_key: str):
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
        api_key=api_key
    )

    # ── Nodes ─────────────────────────────────────────────────────────────────
    def categorize(state: State) -> State:
        prompt = ChatPromptTemplate.from_template("""
You are an expert customer support routing system.

Classify the user query into exactly ONE category:
- Technical: bugs, errors, performance, login issues, crashes, product functionality
- Billing: payment issues, refunds, subscriptions, invoices, charges
- General: FAQs, business info, greetings, account questions, anything else

Rules:
- Respond with ONLY one word: Technical, Billing, or General
- No explanations

Customer Query:
{query}
""")
        result = (prompt | llm).invoke({"query": state["query"]}).content.strip().lower()
        category_map = {"technical": "Technical", "billing": "Billing", "general": "General"}
        category = category_map.get(result, "General")  # fallback to General
        return {**state, "category": category}

    def analyze_sentiment(state: State) -> State:
        prompt = ChatPromptTemplate.from_template("""
You are a sentiment analysis engine for customer support.

Analyze the sentiment of the following message.

Return ONLY one label:
- Positive (happy, satisfied, thankful)
- Neutral (informational, simple question)
- Negative (angry, frustrated, urgent complaint)

Rules:
- Single word only: Positive, Neutral, or Negative
- No explanations

Customer Query:
{query}
""")
        result = (prompt | llm).invoke({"query": state["query"]}).content.strip().lower()
        sentiment_map = {"positive": "Positive", "neutral": "Neutral", "negative": "Negative"}
        sentiment = sentiment_map.get(result, "Neutral")
        return {**state, "sentiment": sentiment}

    def handle_technical(state: State) -> State:
        prompt = ChatPromptTemplate.from_template("""
You are a senior technical support engineer.

Your job:
- Diagnose the issue clearly
- Provide step-by-step troubleshooting
- Be concise but complete
- Ask a follow-up question if more info is needed
- Avoid vague or generic responses

{empathy_note}

Customer Issue:
{query}

Response format:
- Short diagnosis
- Steps to fix
- Optional follow-up question
""")
        empathy = "The customer seems frustrated — start with a brief empathetic acknowledgment before the diagnosis." if state["sentiment"] == "Negative" else ""
        response = (prompt | llm).invoke({"query": state["query"], "empathy_note": empathy}).content
        return {**state, "response": response}

    def handle_billing(state: State) -> State:
        prompt = ChatPromptTemplate.from_template("""
You are a billing support specialist.

Your responsibilities:
- Clearly explain billing-related issues
- Help with refunds, invoices, subscriptions, or charges
- Provide actionable next steps
- Maintain a professional and reassuring tone

{empathy_note}

Customer Issue:
{query}

Response should include:
- Clear explanation
- What the user should do next
- Mention escalation to billing team if the issue is complex
""")
        empathy = "The customer is frustrated — open with a brief, genuine acknowledgment of their frustration before addressing the issue." if state["sentiment"] == "Negative" else ""
        response = (prompt | llm).invoke({"query": state["query"], "empathy_note": empathy}).content
        return {**state, "response": response}

    def handle_general(state: State) -> State:
        prompt = ChatPromptTemplate.from_template("""
You are a helpful customer support assistant.

Your job:
- Answer general questions clearly and directly
- Keep responses short but useful
- If unsure, guide the user to the right support channel

{empathy_note}

Customer Query:
{query}
""")
        empathy = "The customer seems unhappy — acknowledge their concern briefly before answering." if state["sentiment"] == "Negative" else ""
        response = (prompt | llm).invoke({"query": state["query"], "empathy_note": empathy}).content
        return {**state, "response": response}

    def escalate(state: State) -> State:
        # Only truly unresolvable: Negative + Technical
        return {
            **state,
            "response": (
                "I'm really sorry you're dealing with this — that sounds genuinely frustrating. "
                "I've escalated your case to a senior technical agent who will review it with priority. "
                "You should hear back within a few hours.\n\n"
                "**In the meantime**, could you share any error messages or screenshots? "
                "That will help the agent get to the bottom of this faster."
            )
        }

    def route_query(state: State) -> str:
        # Only escalate for Negative + Technical — other combos still get LLM help
        if state["sentiment"] == "Negative" and state["category"] == "Technical":
            return "escalate"
        elif state["category"] == "Technical":
            return "handle_technical"
        elif state["category"] == "Billing":
            return "handle_billing"
        else:
            return "handle_general"

    # ── Graph ──────────────────────────────────────────────────────────────────
    workflow = StateGraph(State)
    workflow.add_node("categorize", categorize)
    workflow.add_node("analyze_sentiment", analyze_sentiment)
    workflow.add_node("handle_technical", handle_technical)
    workflow.add_node("handle_billing", handle_billing)
    workflow.add_node("handle_general", handle_general)
    workflow.add_node("escalate", escalate)

    workflow.add_edge(START, "categorize")
    workflow.add_edge("categorize", "analyze_sentiment")
    workflow.add_conditional_edges(
        "analyze_sentiment",
        route_query,
        {
            "handle_technical": "handle_technical",
            "handle_billing": "handle_billing",
            "handle_general": "handle_general",
            "escalate": "escalate"
        }
    )
    workflow.add_edge("handle_technical", END)
    workflow.add_edge("handle_billing", END)
    workflow.add_edge("handle_general", END)
    workflow.add_edge("escalate", END)

    return workflow.compile()


def run_query(agent, query: str) -> Dict[str, str]:
    result = agent.invoke({"query": query})
    return {
        "category": result["category"],
        "sentiment": result["sentiment"],
        "response": result["response"]
    }


# ── Main UI ───────────────────────────────────────────────────────────────────
st.title("🎧💬 Customer Support Agent")
st.caption("Ask your question · We'll handle the rest")

if not groq_api_key:
    st.info("Add your Groq API key in the sidebar to get started.")
    st.stop()

# Validate key format loosely
if not groq_api_key.startswith("gsk_"):
    st.warning("That doesn't look like a valid Groq key. It should start with `gsk_`.")
    st.stop()

try:
    agent = build_agent(groq_api_key)
except Exception as e:
    st.error(f"Failed to initialize agent: {e}")
    st.stop()

# ── Chat history ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "meta" in msg:
            col1, col2 = st.columns(2)
            category_colors = {"Technical": "🔧", "Billing": "💳", "General": "💬"}
            sentiment_colors = {"Positive": "😊", "Neutral": "😐", "Negative": "😤"}
            col1.caption(f"{category_colors.get(msg['meta']['category'], '❓')} {msg['meta']['category']}")
            col2.caption(f"{sentiment_colors.get(msg['meta']['sentiment'], '❓')} {msg['meta']['sentiment']}")
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
if query := st.chat_input("Describe your issue..."):
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Run agent
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = run_query(agent, query)

                category_colors = {"Technical": "🔧", "Billing": "💳", "General": "💬"}
                sentiment_colors = {"Positive": "😊", "Neutral": "😐", "Negative": "😤"}

                col1, col2 = st.columns(2)
                col1.caption(f"{category_colors.get(result['category'], '❓')} {result['category']}")
                col2.caption(f"{sentiment_colors.get(result['sentiment'], '❓')} {result['sentiment']}")

                st.markdown(result["response"])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["response"],
                    "meta": {"category": result["category"], "sentiment": result["sentiment"]}
                })

            except Exception as e:
                err = f"Something went wrong: {e}"
                st.error(err)
                st.session_state.messages.append({"role": "assistant", "content": err})

# Clear chat button
if st.session_state.messages:
    if st.button("Clear chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()
