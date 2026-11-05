import streamlit as st
from openai import OpenAI, AuthenticationError
from pypdf import PdfReader

# 1. Add a title so we know this is Lab 2
st.title("Lab 2 - PDF Summarizer")
st.write("Upload a PDF and get a summary of it.")

# 2. Get the OpenAI API key from Streamlit secrets.
#    Locally it comes from .streamlit/secrets.toml (which is NOT in Git).
#    On Streamlit Cloud it comes from the app's Settings -> Secrets.
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("No OpenAI API key found. Add OPENAI_API_KEY to your Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# 3. Sidebar options
st.sidebar.header("Summary options")

summary_type = st.sidebar.selectbox(
    "Type of summary",
    [
        "Summarize the document in 100 words",
        "Summarize the document in 2 connecting paragraphs",
        "Summarize the document in 5 bullet points",
    ],
)

language = st.sidebar.selectbox(
    "Language",
    ["English", "Spanish", "French", "German", "Chinese", "Japanese", "Arabic"],
)

# Mini is the default (index=0): it is much cheaper and faster, and
# summaries are an easy task, so the quality is usually good enough.
# Choose the flagship model when you need the best possible summary.
model_choice = st.sidebar.selectbox(
    "Model",
    ["Mini (gpt-5-mini)", "Flagship (gpt-5)"],
    index=0,
)

if model_choice.startswith("Mini"):
    model = "gpt-5-mini"
else:
    model = "gpt-5"

# 4. Let the user upload a PDF
uploaded_file = st.file_uploader("Upload a document (.pdf)", type="pdf")

# 5. When a PDF is uploaded, read its text and ask OpenAI for the summary
if uploaded_file:
    reader = PdfReader(uploaded_file)
    document = ""
    for pdf_page in reader.pages:
        document += pdf_page.extract_text() + "\n"

    if not document.strip():
        st.warning("Couldn't find any text in this PDF. It may be a scanned image.")
        st.stop()

    # The type of summary and the language are part of the instructions
    instructions = f"{summary_type}. Write the summary in {language}."

    try:
        with st.spinner("Summarizing..."):
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You summarize documents. " + instructions},
                    {"role": "user", "content": f"Here is the document:\n\n{document}"},
                ],
            )
    except AuthenticationError:
        st.error("OpenAI rejected the API key. Check OPENAI_API_KEY in your secrets.")
        st.stop()

    # 6. Show the summary
    st.subheader("Summary")
    st.write(response.choices[0].message.content)
