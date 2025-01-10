
import sys
import os
current_dir = os.path.dirname(__file__)
package_path = os.path.join(current_dir, "..", "..")
package_path = os.path.abspath(os.path.normpath(package_path))
sys.path.append(package_path)

from dotenv import load_dotenv
load_dotenv()
from aiagents4pharma.talk2biomodels.agent_t2b import app
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage,ChatMessage
import uuid
import pandas as pd
import plotly.express as px
from langchain_core.tracers.context import collect_runs
import streamlit as st
from streamlit_feedback import streamlit_feedback
from utils import check_login, render_plotly, get_random_spinner_text, _submit_feedback, ERROR_MSG
st.set_page_config(page_title="Talk2BioModels", page_icon="🤖", layout="wide")
st.logo(image="./app/frontend/VPE.png", link="https://www.github.com/virtualpatientengine")

# Set the streamlit session key for the sys bio model
ST_SYS_BIOMODEL_KEY = "last_model_object"

# Check loging if .streamlit/secrets.toml exists
if os.path.exists(".streamlit/secrets.toml"):
    if not check_login():
        st.stop()  # Do not continue if check_login is not True.
else:
    # Set the default user_name as default
    st.session_state.user_name = "default"

# Generate a unique project name for the session
# Set the project name as the user_name + a unique identifier
# This will be used to track the user's session and feedback
if "project_name" not in st.session_state:
    st.session_state.project_name = str(st.session_state.user_name) + '@' + str(uuid.uuid4())

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize run_id
if "run_id" not in st.session_state:
    st.session_state.run_id = None

# Check if env variable OPENAI_API_KEY exists
if "OPENAI_API_KEY" not in os.environ:
    st.error("Please set the OPENAI_API_KEY environment \
        variable in the terminal where you run the app.")
    st.stop()





# Title
st.write("""
    <h3 style='margin: 0px;font-weight: bold;'>
    🤖 Talk2BioModels
    </h3>
    """,
    unsafe_allow_html=True)

sel_col1,sel_col2 = st.columns([4, 7]) 
with sel_col1:
    # LLM panel
    llms = ["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
    llm_option = st.selectbox(
        "Pick an LLM to power the agent",
        llms,
        index=0,
        key="st_selectbox_llm"
    )
with sel_col2:
    # Upload files
    uploaded_file = st.file_uploader(
        "Upload an XML/SBML file",
        accept_multiple_files=False,
        type=["xml", "sbml"],
        help='''Upload an XML/SBML file to simulate a biological model, \
            and ask questions about the simulation results.'''
        )

# Main layout of the app split into two columns
main_col2,main_col3 = st.columns([4, 7])  

prompt = st.chat_input("Say something ...", key="st_chat_input")
# Second column
with main_col2:
    # Chat history panel
    with st.container(border=True, height=575):
        st.write("#### 💬 Chat History")

        # Display chat messages
        for count, message in enumerate(st.session_state.messages):
            if message["type"] == "message":
                with st.chat_message(message["content"].role,
                                     avatar="🤖" 
                                     if message["content"].role != 'user'
                                     else "👩🏻‍💻"):
                    st.markdown(message["content"].content)
                    st.empty()
            elif message["type"] == "plotly":
                st.plotly_chart(render_plotly(message["content"]),
                                use_container_width = True,
                                key=f"plotly_{count}")
            elif message["type"] == "dataframe":
                st.dataframe(message["content"],
                            use_container_width = True,
                            key=f"dataframe_{count}")
        if prompt:
            if ST_SYS_BIOMODEL_KEY not in st.session_state:
                st.session_state[ST_SYS_BIOMODEL_KEY] = None
            # Create a key 'uploaded_file' to read the uploaded file
            if uploaded_file:
                st.session_state.sbml_file_path = uploaded_file.read().decode("utf-8")

            # Display user prompt
            prompt_msg = ChatMessage(prompt, role="user")
            st.session_state.messages.append(
                {
                    "type": "message",
                    "content": prompt_msg
                }
            )
            with st.chat_message("user", avatar="👩🏻‍💻"):
                st.markdown(prompt)
                st.empty()

            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner(get_random_spinner_text()):
                    ERROR_FLAG = False
                    with collect_runs() as cb:
                        # Call the agent
                        try:
                            response = app.invoke({
                                                    "messages": [HumanMessage(content=prompt)]},
                                                    config={"configurable": {"thread_id": 16}})
                            print("************ response ************")
                            for k,v in response.items():
                                if k == "messages":
                                    print("+++ messages +++")
                                    for msg in v:
                                        print("+++")
                                        print(msg)
                                        print("+++")
                                print(k , " ::: ", v)
                                print("-"*25)
                        except Exception as e:
                            ERROR_FLAG = True
                        st.session_state.run_id = cb.traced_runs[0].id

                    # Check if there was an error
                    # If there was an error, display an error message
                    # Otherwise, display the response
                    if ERROR_FLAG:
                        # Add assistant response to chat history
                        assistant_msg = ChatMessage(ERROR_MSG, role="assistant")
                        st.session_state.messages.append({
                                        "type": "error_message",
                                        "content": ERROR_MSG
                                    })
                        # Display the error message
                        st.error(ERROR_MSG, icon="🚨")
                        st.empty()
                        # st.stop()
                    else:
                        # Add assistant response to chat history
                        assistant_msg = ChatMessage(response["messages"][-1].content, role="assistant")
                        st.session_state.messages.append({
                                        "type": "message",
                                        "content": assistant_msg
                                    })
                        # Display the response
                        st.markdown(response["messages"][-1].content)
                        st.empty()
        # Collect feedback and display the thumbs feedback
        if st.session_state.get("run_id"):
            feedback = streamlit_feedback(
                feedback_type="thumbs",
                optional_text_label="[Optional] Please provide an explanation",
                on_submit=_submit_feedback,
                key=f"feedback_{st.session_state.run_id}"
            )
            # print (feedback)
    
with main_col3:
    st.write("#### 📊 Model Simulation Results")
    # check the csv file
    if os.path.exists("simulation_results.csv"):
        df = pd.read_csv("simulation_results.csv")
        fig = px.line(df,
                        x='Time',
                        y='Concentration',
                        color='Species',
                        title=f"Concentration of Species over Time in the model",
                        height=600,
                        width=800
        )
        st.plotly_chart(fig,use_container_width = True)
        df_pivot = df.pivot(index='Time', columns='Species', values='Concentration')
        st.dataframe(df_pivot)
    else:
        st.write("No simulation results to display.")