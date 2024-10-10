import streamlit as st
from langchain_openai import ChatOpenAI
import pandas as pd
from agents_tools.ag_to import get_or_create_agent



st.set_page_config(page_title="Analista de Dados", page_icon="🤖", layout="wide")

st.title("Analista de Dados")

# Verificar se o DataFrame está no estado da sessão
if "df" in st.session_state and isinstance(st.session_state.df, pd.DataFrame):
    df = st.session_state.df
    
    # Verificar se model_choice está no estado da sessão, caso contrário, usar um valor padrão
    model_choice = st.session_state.get("model_choice", "gpt-3.5-turbo")
    
    # Criação do agente DataFrame usando a função de ag_to.py
    agent = get_or_create_agent(df, model_choice)

    # Inicialização do histórico de mensagens
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Container para o histórico de mensagens
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Campo de input
    prompt = st.chat_input("Faça uma pergunta sobre os dados")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                with st.spinner("Analisando..."):
                    response = agent.invoke({'input': prompt})
                    full_response = response['output']
                message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

else:
    st.warning("Nenhum dado carregado. Por favor, carregue os dados na página principal antes de usar o agente.")

with st.sidebar:
    if st.button("Limpar Histórico"):
        st.session_state.messages = []
        st.rerun()


if "agent" in st.session_state:
    agent = st.session_state.agent
else:
    st.error("Agente não encontrado. Por favor, carregue os dados na página principal primeiro.")

