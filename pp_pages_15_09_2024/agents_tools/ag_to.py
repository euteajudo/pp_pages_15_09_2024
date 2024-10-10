import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import pandas as pd


def criar_agente_dataframe(df, model_choice):
    # Garantir que df é um DataFrame
    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df)
    
    chat = ChatOpenAI(temperature=0, model=model_choice)
    agent = create_pandas_dataframe_agent(
        chat,
        df,
        verbose=True,
        agent_type='tool-calling',
        max_iterations=None,
        allow_dangerous_code=True,
        prefix="Você é um assistente de análise de dados que responde sempre em português. Sua tarefa é analisar os dados fornecidos e responder às perguntas do usuário de forma clara e concisa em português."
    )
    return agent

def get_or_create_agent(df, model_choice):
    if "agent" not in st.session_state or st.session_state.agent is None:
        st.session_state.agent = criar_agente_dataframe(df, model_choice)
    return st.session_state.agent

def update_agent(df, model_choice):
    # Verificar o conteúdo do DataFrame
    print(df.head())  # Adicione esta linha para depuração
    st.session_state.agent = criar_agente_dataframe(df, model_choice)

# Aqui você pode adicionar mais funções para criar outros tipos de agentes ou ferramentas
