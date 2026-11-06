import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import anthropic


def read_url_content(url):
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Error reading {url}: {e}")
        return None


# (cheap model, advanced model) for each LLM
MODELS = {
    "OpenAI": ("gpt-5-mini", "gpt-5"),
    "Anthropic (Claude)": ("claude-haiku-5-5", "claude-sonnet-5-5"),
    "Google (Gemini)": ("gemini-2.5-flash", "gemini-2.5-pro"),
}
SECRET_NAMES = {
    "OpenAI": "OPENAI_API_KEY",
    "Anthropic (Claude)": "ANTHROPIC_API_KEY",
    "Google (Gemini)": "GEMINI_API_KEY",
}


def ask_llm(provider, model, prompt):
    key = st.secrets.get(SECRET_NAMES[provider])
    if not key:
        raise ValueError(f"No key found in secrets for {provider}.")

    if provider == "OpenAI":
        client = OpenAI(api_key=key)
    elif provider == "Google (Gemini)":
        # Gemini offers an OpenAI-compatible endpoint
        client = OpenAI(
            api_key=key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
    else:
        client = anthropic.Anthropic(api_key=key)
        reply = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return reply.content[0].text

    reply = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return reply.choices[0].message.content


st.title("URL Summarizer")

# URL at the top of the screen (not the sidebar)
url = st.text_input("Enter a web page URL", placeholder="https://example.com/article")

# Sidebar options
st.sidebar.header("Options")
summary_type = st.sidebar.radio(
    "Summary type",
    ["Summarize in 100 words", "Summarize in 2 paragraphs", "Summarize in 5 bullet points"],
)
language = st.sidebar.selectbox("Output language", ["English", "French", "Spanish", "German"])
provider = st.sidebar.selectbox("LLM", list(MODELS.keys()))
use_advanced = st.sidebar.checkbox("Use advanced model")

cheap_model, advanced_model = MODELS[provider]
model = advanced_model if use_advanced else cheap_model
st.sidebar.caption(f"Model: {model}")

if url:
    document = read_url_content(url)
    if not document:
        st.error("Could not read that URL. Check the link and try again.")
        st.stop()

    prompt = (
        f"Here is the text of a web page:\n\n{document[:100000]}\n\n---\n\n"
        f"{summary_type}. Write the summary in {language}."
    )

    try:
        with st.spinner(f"Asking {model}..."):
            answer = ask_llm(provider, model, prompt)
        st.subheader(f"Summary ({provider}, {model})")
        st.write(answer)
    except Exception as e:
        st.error(f"Problem with {provider}: the key may be missing/invalid or the model name isn't available. Details: {e}")
