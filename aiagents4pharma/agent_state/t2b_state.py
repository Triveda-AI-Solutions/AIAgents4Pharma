from typing import Annotated, Any
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

import pandas as pd 
import plotly.express as px

class T2bState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    model_id: str
    sbml_file_path: str