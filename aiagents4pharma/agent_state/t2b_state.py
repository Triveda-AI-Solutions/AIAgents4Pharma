from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages

import pandas as pd 
import plotly.express as px

class T2bState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    dataframe: pd.DataFrame
    plot: px.line