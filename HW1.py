import streamlit as st
from openai import OpenAI
import pymupdf


def read_pdf(uploaded_file):
    pdf = pymupdf.open(stream=uploaded_file.getvalue(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text


st.title("My Document Q&A")
st.write("Upload a .txt or .pdf document and ask a question about it.")

api_key = st.text_input("OpenAI API key", type="password")

if not api_key:
    st.info("Enter your OpenAI API key to continue.")
    st.stop()

model = st.selectbox("Choose a model", ["gpt-5", "gpt-5-mini", "gpt-5-nano"])

uploaded_file = st.file_uploader("Upload a document (.txt or .pdf)", type=["txt", "pdf"])

question = st.text_input(
    "Ask a question about the document",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

if uploaded_file and question:
    file_extension = uploaded_file.name.split(".")[-1].lower()

    if file_extension == "txt":
        document = uploaded_file.getvalue().decode("utf-8", errors="replace")
    elif file_extension == "pdf":
        document = read_pdf(uploaded_file)
    else:
        st.error("Unsupported file type.")
        st.stop()

    client = OpenAI(api_key=api_key)

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": f"Here is a document:\n\n{document}\n\n---\n\n{question}",
                }
            ],
        )

    st.subheader("Answer")
    st.write(response.choices[0].message.content)