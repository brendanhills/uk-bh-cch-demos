

import streamlit as st
import os
from google.cloud import dialogflowcx_v3beta1 as dialogflowcx
from google.oauth2 import credentials
import uuid


# Replace with your Dialogflow CX project ID and agent ID
PROJECT_ID = "uk-bh-experiments-argolis"  # Replace with your actual project ID
AGENT_ID = "a1054063-fcb0-4e85-8716-5148a643a995"      # Replace with your actual agent ID
LOCATION_ID = "us-central1"     #  Dialogflow CX Location

def get_dialogflow_response(text, session_id, project_id, agent_id, location_id="us-central1"):
    """
    Sends a text query to the Dialogflow CX agent and returns the response.

    Args:
        text: The text query to send.
        session_id: The unique session ID for this conversation.
        project_id: The ID of the Google Cloud project.
        agent_id: The ID of the Dialogflow CX agent.
        location_id: The location of the agent.

    Returns:
        The text response from Dialogflow CX.
    """
    # Initialize a session client.
    session_client = dialogflowcx.SessionsClient(
        client_options={"api_endpoint": f"{location_id}-dialogflow.googleapis.com"}
    )

    # Construct the session path.
    session_path = session_client.session_path(
        project=project_id,
        location=location_id,
        agent=agent_id,
        session=session_id,
    )

    # Construct the text input.
    text_input = dialogflowcx.TextInput(text=text)

    # Construct the query input.
    query_input = dialogflowcx.QueryInput(
        text=text_input, language_code="en"
    )

    # Construct the request object.
    request = dialogflowcx.DetectIntentRequest(
        session=session_path, query_input=query_input
    )

    # Make the API request.
    response = session_client.detect_intent(request=request) # Use the request object

    # Extract and return the response text.
    return response.query_result.response_messages[0].text.text[0] if response.query_result.response_messages else "No response from Dialogflow agent."


def run_healthconnect_app():
    """
    Main function to run the HealthConnect Streamlit app.
    """
    st.set_page_config(
        page_title="HealthConnect",
        page_icon=":hospital:",
        layout="wide",
        initial_sidebar_state="auto",
    )

    # --- Header Section ---
    st.markdown(
        """
        <div style="background-color: #3b82f6; color: white; padding: 1rem; border-radius: 0.5rem;">
            <h1 style="font-size: 1.875rem; font-weight: bold; margin-bottom: 0;">HealthConnect</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Hero Section ---
    st.markdown(
        """
        <div style="background: linear-gradient(to bottom right, #60a5fa, #3b82f6); color: white; padding: 4rem 0; border-radius: 0.5rem; text-align: center; margin-bottom: 2rem;">
            <h2 style="font-size: 2.25rem; font-weight: bold; margin-bottom: 1rem;">Your Health, Connected.</h2>
            <p style="font-size: 1.25rem; margin-bottom: 2rem;">Experience seamless telehealth services with HealthConnect. Connect with doctors, manage prescriptions, and monitor your health from the comfort of your home.</p>
            <a href="#services" style="background-color: white; color: #3b82f6; padding: 0.75rem 1.5rem; border-radius: 2rem; font-weight: 600; text-decoration: none; hover:bg-gray-100;">Explore Services</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Services Section ---
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 id="services" style="font-size: 1.75rem; font-weight: bold; color: #4b5563; margin-bottom: 2rem;">Our Services</h2>
            <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 2rem;">
                <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1); padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between; width: 20rem;">
                    <h3 style="font-size: 1.25rem; font-weight: bold; color: #3b82f6; margin-bottom: 1rem;">Virtual Consultations</h3>
                    <p style="color: #4b5563; margin-bottom: 1rem;">Connect with licensed physicians for real-time video consultations.</p>
                    <button style="background-color: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 1.5rem; text-decoration: none; hover:bg-blue-600; border: none; cursor: pointer;">Book a Consultation</button>
                </div>
                <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1); padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between; width: 20rem;">
                    <h3 style="font-size: 1.25rem; font-weight: bold; color: #3b82f6; margin-bottom: 1rem;">Prescription Management</h3>
                    <p style="color: #4b5563; margin-bottom: 1rem;">Get your prescriptions filled and delivered to your doorstep.</p>
                    <button style="background-color: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 1.5rem; text-decoration: none; hover:bg-blue-600; border: none; cursor: pointer;">Manage Prescriptions</button>
                </div>
                <div style="background-color: white; border-radius: 0.5rem; box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.1); padding: 1.5rem; display: flex; flex-direction: column; justify-content: space-between; width: 20rem;">
                    <h3 style="font-size: 1.25rem; font-weight: bold; color: #3b82f6; margin-bottom: 1rem;">Chronic Care Monitoring</h3>
                    <p style="color: #4b5563; margin-bottom: 1rem;">Manage your chronic conditions with personalized monitoring and support.</p>
                    <button style="background-color: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 1.5rem; text-decoration: none; hover:bg-blue-600; border: none; cursor: pointer;">Learn More</button>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- About Us Section ---
    st.markdown(
        """
        <div style="background-color: #eff6ff; padding: 4rem 0; border-radius: 0.5rem; text-align: center; margin-bottom: 2rem;">
            <h2 id="about" style="font-size: 1.75rem; font-weight: bold; color: #4b5563; margin-bottom: 2rem;">About Us</h2>
            <p style="font-size: 1.25rem; color: #4b5563; line-height: 2rem; max-width: 60%; margin: 0 auto;">HealthConnect is committed to providing accessible and affordable healthcare through cutting-edge telehealth technology. Our mission is to improve the health and well-being of our patients by delivering convenient, high-quality medical care.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Contact Section ---
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 id="contact" style="font-size: 1.75rem; font-weight: bold; color: #4b5563; margin-bottom: 2rem;">Contact Us</h2>
            <p style="font-size: 1.25rem; color: #4b5563; margin-bottom: 1rem;">Email: support@healthconnect.com<br/>Phone: +1 (555) 123-4567</p>
            <a href="#support" style="background-color: #16a34a; color: white; padding: 0.75rem 1.5rem; border-radius: 2rem; font-weight: 600; text-decoration: none; hover:bg-green-600;">Contact Support</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Support Section ---
    st.markdown(
        """
        <div style="background-color: #f3f4f6; padding: 4rem 0; border-radius: 0.5rem; text-align: center; margin-bottom: 2rem;">
            <h2 id="support" style="font-size: 1.75rem; font-weight: bold; color: #4b5563; margin-bottom: 2rem;">Support</h2>
            <p style="font-size: 1.25rem; color: #4b5563; margin-bottom: 1rem;">For immediate assistance, please visit our <a href="#" style="color: #3b82f6; text-decoration: underline;">FAQ</a> or use our live chat.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Chatbot Interaction ---
    st.subheader("Live Chat Support")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from Dialogflow CX
        try:
            response = get_dialogflow_response(
                prompt,
                session_id=st.session_state.session_id,
                project_id=PROJECT_ID,
                agent_id=AGENT_ID,
                location_id=LOCATION_ID
            )
        except Exception as e:
            response = f"An error occurred: {e}"
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    # --- Initialize session ID ---
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

if __name__ == "__main__":
    run_healthconnect_app()
