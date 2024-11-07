#!/usr/bin/env python3

"""
Tool for asking a question about the model description.
"""

from typing import Type, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
import streamlit as st
from langchain_core.tools import BaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from ..models.basico_model import BasicoModel

@dataclass
class ModelData:
    """
    Dataclass for storing the model data.
    """
    modelid: Optional[int] = None
    sbml_file_path: Optional[str] = None
    model_object: Optional[BasicoModel] = None

class ModelDescriptionInput(BaseModel):
    """
    Input schema for the ModelDescription tool.
    """
    question: str = Field(description="question about the model description")
    sys_bio_model: ModelData = Field(description="model data", default=None)
    st_session_key: str = Field(description="Streamlit session key", default=None)


# Note: It's important that every field has type hints. BaseTool is a
# Pydantic class and not having type hints can lead to unexpected behavior.
class ModelDescriptionTool(BaseTool):
    """
    Tool for returning the description of the specified BioModel.
    """
    name: str = "model_description"
    description: str = '''A tool to ask about the description of the model.'''

    args_schema: Type[BaseModel] = ModelDescriptionInput
    return_direct: bool = True

    def _run(self,
             question: str,
             sys_bio_model: ModelData = ModelData(),
             st_session_key: str = None,
             run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Run the tool.

        Args:
            question (str): The question to ask about the model description.
            st_session_key (str): The Streamlit session key.
            run_manager (Optional[CallbackManagerForToolRun]): The CallbackManagerForToolRun object.

        Returns:
            str: The answer to the question.
        """
        # Check if sys_bio_model is provided
        if sys_bio_model.modelid or sys_bio_model.sbml_file_path or sys_bio_model.model_object:
            if sys_bio_model.modelid:
                model_object = BasicoModel(model_id=sys_bio_model.modelid)
            elif sys_bio_model.sbml_file_path:
                model_object = BasicoModel(sbml_file_path=sys_bio_model.sbml_file_path)
            else:
                model_object = sys_bio_model.model_object
            if st_session_key:
                st.session_state[st_session_key] = model_object
        else:
            # If the model_object is not provided,
            # get it from the Streamlit session state
            if st_session_key:
                if st_session_key not in st.session_state:
                    return f"Session key {st_session_key} " \
                            "not found in Streamlit session state."
                model_object = st.session_state[st_session_key]
            else:
                return "Please provide a valid model object or Streamlit "\
                    "session key that contains the model object."
        # check if model_object is None
        if model_object is None:
            return "Please provide a BioModels ID or an SBML file path for the model."
        description = model_object.description
        if description in [None, ""]:
            return "No description found for the model."
        # Append the BioModel ID of the model to the description
        description = f"{description} (BioModel ID: {model_object.model_id})"
        llm = ChatOpenAI(model="gpt-3.5-turbo")
        # Check if run_manager's metadata has the key 'prompt_content'
        if run_manager and 'prompt' in run_manager.metadata:
            prompt_content = run_manager.metadata['prompt']
        else:
            prompt_content = '''
                            Given the description of a System biology model:
                            {description},
                            answer the user question:
                            {question}.
                            '''
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", prompt_content),
             ("user", "{description} {question}")]
        )
        parser = StrOutputParser()
        chain = prompt_template | llm | parser
        return chain.invoke({"description": description,
                             "question": question})

    def call_run(self,
            question: str,
            sys_bio_model: ModelData = ModelData(),
            st_session_key: str = None,
            run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Run the tool.

        Args:
            question (str): The question to ask about the model description.
            sys_bio_model (ModelData): The model data.
            st_session_key (str): The Streamlit session key.
            run_manager (Optional[CallbackManagerForToolRun]): The CallbackManagerForToolRun object.
        
        Returns:
            str: The answer to the question
        """
        return self._run(question=question,
                         sys_bio_model=sys_bio_model,
                         st_session_key=st_session_key,
                         run_manager=run_manager)

    def get_metadata(self):
        """
        Get metadata for the tool.

        Returns:
            dict: The metadata for the tool.
        """
        return {
            "name": self.name,
            "description": self.description
        }
