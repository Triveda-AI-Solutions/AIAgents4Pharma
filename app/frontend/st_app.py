
import sys
import os
current_dir = os.path.dirname(__file__)
package_path = os.path.join(current_dir, "..", "..")
package_path = os.path.abspath(os.path.normpath(package_path))
sys.path.append(package_path)

from dotenv import load_dotenv
load_dotenv()
from aiagents4pharma.talk2biomodels.agent_t2b import app
from langchain_core.messages import HumanMessage

final_state = app.invoke(
    {"messages": [HumanMessage(content="Can you give me more details about the model with ID BIOMD0000000001?")]}, 
     config={"configurable": {"thread_id": 42}}
     )

print(final_state["messages"][-1].content)