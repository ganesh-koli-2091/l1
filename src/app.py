"""
Streamlit UI for the API Documentation Assistant.

Run:
    streamlit run src/app.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title="API Docs Assistant",
    page_icon="📚",
    layout="wide",
)

EXAMPLE_QUESTIONS = [
    "Which endpoint do I call to get a customer's full order history?",
    "How do I track a shipment after an order is placed?",
    "What endpoint handles customer registration?",
    "How do I check if a product is in stock before adding to cart?",
    "How do I refresh an expired JWT token?",
    "Which endpoint do I call to issue a refund?",
    "How do I search for products by keyword?",
    "What is the checkout flow — which endpoints do I call in order?",
    "How do I get the top-selling products for the last 30 days?",
    "How do I send an order confirmation email to a customer?",
]


@st.cache_resource(show_spinner="Loading assistant...")
def get_assistant():
    from query import APIDocsAssistant
    try:
        return APIDocsAssistant(), None
    except RuntimeError as e:
        return None, str(e)
    except EnvironmentError as e:
        return None, str(e)


def main() -> None:
    st.title("📚 Internal API Documentation Assistant")
    st.caption(
        "Ask plain-English questions about ShopCo's microservices APIs. "
        "Every answer cites the source endpoint."
    )

    with st.sidebar:
        st.header("Example questions")
        st.caption("Click any question to use it:")
        for q in EXAMPLE_QUESTIONS:
            if st.button(q, key=q, use_container_width=True):
                st.session_state["pending_question"] = q

        st.divider()
        st.header("About")
        st.markdown(
            "**Corpus:** 10 OpenAPI YAML specs + 4 architecture notes  \n"
            "**Retrieval:** ChromaDB + sentence-transformers (all-MiniLM-L6-v2)  \n"
            "**LLM:** Anthropic Claude claude-opus-4-5  \n"
            "**Context:** CLAUDE.md enforces structured, cited answers"
        )

    assistant, error = get_assistant()

    if error:
        st.error(f"**Setup required:** {error}")
        st.code(
            "# 1. Add your API key\ncp .env.example .env\n# edit .env and set ANTHROPIC_API_KEY\n\n"
            "# 2. Install dependencies\npip install -r requirements.txt\n\n"
            "# 3. Run ingestion\npython src/ingest.py\n\n"
            "# 4. Restart the app\nstreamlit run src/app.py",
            language="bash",
        )
        return

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Display chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander(f"📎 {len(msg['sources'])} source chunks retrieved"):
                    for i, src in enumerate(msg["sources"], 1):
                        meta = src["metadata"]
                        if meta.get("type") == "endpoint":
                            label = f"{meta.get('method')} {meta.get('path')} — {meta.get('source')}"
                        else:
                            label = f"{meta.get('title')} — {meta.get('source')}"
                        st.markdown(f"**[{i}] Score: {src['score']:.3f} | {label}**")
                        st.text(src["text"])

    # Handle sidebar button click
    pending = st.session_state.pop("pending_question", None)

    prompt = st.chat_input("Ask about any endpoint...") or pending

    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Searching documentation and generating answer..."):
                try:
                    result = assistant.query(prompt)
                    answer = result["answer"]
                    sources = result.get("sources", [])
                    llm_error = None
                except Exception as e:
                    answer = None
                    sources = []
                    llm_error = str(e)

            if llm_error:
                st.error(
                    "**LLM gateway error** — retrieval worked but the language model call failed.\n\n"
                    f"```\n{llm_error[:400]}\n```\n\n"
                    "**To fix:** The Perficient Portkey gateway (`@dsvertex/anthropic.claude-opus-4-8`) "
                    "is returning a Vertex AI 403. Contact your AI Academy team, or add your own "
                    "`ANTHROPIC_API_KEY` to `.env` and set `USE_DIRECT_ANTHROPIC=true`."
                )
                answer = "_Gateway unavailable — see error above._"
            else:
                st.markdown(answer)

            if sources:
                with st.expander(f"📎 {len(sources)} source chunks retrieved"):
                    for i, src in enumerate(sources, 1):
                        meta = src["metadata"]
                        if meta.get("type") == "endpoint":
                            label = f"{meta.get('method')} {meta.get('path')} — {meta.get('source')}"
                        else:
                            label = f"{meta.get('title')} — {meta.get('source')}"
                        st.markdown(f"**[{i}] Score: {src['score']:.3f} | {label}**")
                        st.text(src["text"])

        st.session_state["messages"].append({
            "role": "assistant",
            "content": answer,
            "sources": sources,
        })


if __name__ == "__main__":
    main()
