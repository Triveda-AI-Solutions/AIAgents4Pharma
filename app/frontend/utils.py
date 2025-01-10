import hmac
import streamlit as st
import plotly.express as px
import pandas as pd
import random
from langsmith import Client
# Define error message
ERROR_MSG = "Sorry, your request could not be \
            processed due to an error. I have logged \
            the error and reported it to the developers. \
            Please try again with a different prompt."

def check_login():
    """Returns `True` if the user is logged in."""

    def entered_values():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

        if " " not in st.session_state["user_name"] and '@' not in st.session_state["user_name"]:
            st.session_state["user_name_correct"] = True
        else:
            st.session_state["user_name_correct"] = False
    # Return True if the password and username are validated.
    if st.session_state.get("password_correct", False) and \
        st.session_state.get("user_name_correct", False):
        return True
    # Show input for user name.
    st.text_input(
                "Username",
                key="user_name",
                help="Please enter a name without spaces and @ symbol. \
                    This will be used to personalize the app and for feedback.",
                # on_change=entered_values
                )
    # Show input for password.
    st.text_input(
                "Password",
                type="password",
                key="password",
                help="Please enter the password shared with you.",
                # on_change=entered_values
                )
    st.button("Login", on_click=entered_values)
    if "user_name_correct" in st.session_state:
        if not st.session_state["user_name_correct"]:
            st.error("😕 Please enter a username without spaces and @ symbol")
    if "password_correct" in st.session_state:
        if not st.session_state["password_correct"]:
            st.error("😕 Password incorrect")
    return False

def render_plotly(df_simulation_results: pd.DataFrame) -> px.line:
    """
    Function to visualize the dataframe using Plotly.

    Args:
        df: pd.DataFrame: The input dataframe
    """
    df_simulation_results = df_simulation_results.melt(id_vars='Time',
                            var_name='Parameters',
                            value_name='Concentration')
    fig = px.line(df_simulation_results,
                    x='Time',
                    y='Concentration',
                    color='Parameters',
                    title="Concentration of parameters over time",
                    height=500,
                    width=600
            )
    return fig

def get_random_spinner_text():
    """
    Function to get a random spinner text.
    """
    spinner_texts = [
        "Your request is being carefully prepared. one moment, please.",
        "Working on that for you now—thanks for your patience.",
        "Hold tight! I’m getting that ready for you.",
        "I’m on it! Just a moment, please.",
        "Running algorithms... your answer is on its way.",
        "Processing your request. Please hold on...",
        "One moment while I work on that for you...",
        "Fetching the details for you. This won’t take long.",
        "Sit back while I take care of this for you."]
    return random.choice(spinner_texts)

def _submit_feedback(user_response):
    '''
    Function to submit feedback to the developers.
    '''
    client = Client()
    client.create_feedback(
        st.session_state.run_id,
        key="feedback",
        score=1 if user_response['score'] == "👍" else 0,
        comment=user_response['text']
    )
    st.info("Your feedback is on its way to the developers. Thank you!", icon="🚀")
    # return user_response.update({"some metadata": 123})
