import streamlit as st

# 1. Add a title to the web page
st.title("Tip Calculator")

# 2. Get input from the user and save to variables
bill = st.number_input("Bill amount", min_value=0.0, value=50.0)
service = st.selectbox("Service", ["Good", "Average", "Low"])
# 3. Make a decision: choose a tip percentage based on service level
if service == "Good":
    tip_percent = 0.18
elif service == "Average":
    tip_percent = 0.15
else:
    tip_percent = 0.10

# 4. Do the math calculation
tip = bill * tip_percent

# 5. Control the layout: put results next to each other in columns
col1, col2 = st.columns(2)

with col1:
    st.write("Bill")
    st.write(f"${bill:.2f}")

with col2:
    st.write("Tip")
    st.write(f"${tip:.2f}")
