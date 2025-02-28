import streamlit as st
import google.genai as genai

# Set up the title of the app
st.title("Textbook Syllabus Checker")

# Add a text input for the textbook content
textbook_content = st.text_area("Enter the textbook content here:", height=300)

# Add a text input for the syllabus
syllabus = st.text_area("Enter the syllabus here:", height=150)

# Add a button to check the syllabus
if st.button("Check Syllabus"):
    # Check if the textbook content and syllabus are empty
    if not textbook_content or not syllabus:
        st.error("Please enter both the textbook content and the syllabus.")
    else:
        # Use Gemini to check if the textbook matches the syllabus
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        model = genai.GenerativeModel('gemini-1.0-pro')
        prompt = f"""
        You are a helpful assistant that can check if a textbook matches a syllabus.
        I will provide you with the textbook content and the syllabus.
        You need to check if the textbook covers all the topics in the syllabus.
        If the textbook covers all the topics, you should say "Yes".
        If the textbook does not cover all the topics, you should say "No" and list the topics that are missing.
        Here is the textbook content:
        {textbook_content}
        Here is the syllabus:
        {syllabus}
        Does the textbook match the syllabus?
        """
        response = model.generate_content(prompt)
        # Display the response
        st.success(response.text)
