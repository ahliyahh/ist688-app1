import streamlit as st

# This file is the entry point. It lists the pages and runs the one
# the user picks from the sidebar. The newest lab is the default page.
lab3_page = st.Page("lab3.py", title="Lab 3 - Chatbot", default=True)
lab2_page = st.Page("lab2.py", title="Lab 2 - PDF Summarizer")
lab1_page = st.Page("document_qa.py", title="Lab 1 - Document Q&A")
tip_page = st.Page("tip_calculator.py", title="Tip Calculator")

hw1_page = st.Page("HW1.py", title="HW 1 - Document Q&A")
hw2_page = st.Page("HW2.py", title="HW 2 - URL Summarizer")

# The sidebar groups the pages under "Labs" and "Homework"
page = st.navigation(
    {
        "Labs": [lab3_page, lab2_page, lab1_page, tip_page],
        "Homework": [hw1_page, hw2_page],
    }
)
page.run()
