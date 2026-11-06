import streamlit as st

# This file is the entry point. It lists the pages and runs the one
# the user picks from the sidebar. The newest lab is the default page.
lab3_page = st.Page("lab3.py", title="Lab 3 - Chatbot", default=True)
lab2_page = st.Page("lab2.py", title="Lab 2 - PDF Summarizer")
lab1_page = st.Page("document_qa.py", title="Lab 1 - Document Q&A")
tip_page = st.Page("tip_calculator.py", title="Tip Calculator")

page = st.navigation([lab3_page, lab2_page, lab1_page, tip_page])
page.run()
