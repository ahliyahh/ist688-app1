import streamlit as st
from openai import OpenAI

# 1. Add a title to the page
st.title("My Document Q&A")
st.write("Upload a .txt document and ask a question about it.")

# 2. Ask for the user's OpenAI API key.
#    type="password" hides what they type. The key is only kept in memory
#    while the page runs. It is never saved or printed.
api_key = st.text_input("OpenAI API key", type="password")

if not api_key:
    st.info("Enter your OpenAI API key to continue.")
    st.stop()

# 3. Let the user upload a .txt document
uploaded_file = st.file_uploader("Upload a document (.txt)", type="txt")

# 4. Let the user type a question about the document
question = st.text_input(
    "Ask a question about the document",
    placeholder="Can you give me a short summary?",
    disabled=not uploaded_file,
)

# 5. When we have both a document and a question, ask OpenAI
if uploaded_file and question:
    # Turn the uploaded file into plain text
    document = uploaded_file.read().decode("utf-8")

    client = OpenAI(api_key=api_key)

    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": f"Here is a document:\n\n{document}\n\n---\n\n{question}",
                }
            ],
        )

    # 6. Show the answer
    st.subheader("Answer")
    st.write(response.choices[0].message.content)
